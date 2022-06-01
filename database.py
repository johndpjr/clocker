import sqlite3
from uuid import uuid4
from datetime import datetime

from enums import TaskType, ActionType
import utils


class ClockerDatabase:
    """Models a SQLite Database for clocker"""

    def __init__(self):
        self.conn = sqlite3.connect('test.db')
        self.c = self.conn.cursor()

        # Initial table creation sequence
        with self.conn:
            # Create ClockRecords table
            self.c.execute("""CREATE TABLE IF NOT EXISTS ClockRecords (
                uuid TEXT,
                task INT,
                action INT,
                timestamp TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime'))
            )""")
        self.uuids = []
    
    def _get_uuid(self):
        """Returns a Version 4 UUID"""
        return str(uuid4()).replace('-', '')
    
    def _validate_prospective_record(self, task: TaskType, action: ActionType):
        """Throws an error if the most recent record (if one exists) has the same
        action as this record's action
        """
        self.c.execute("SELECT action, uuid FROM ClockRecords WHERE task=? ORDER BY timestamp DESC LIMIT 1", (task.value,))
        res = self.c.fetchone()
        if res is not None:
            if action.value == res[0]:
                raise RuntimeError(f'already clocked {action.name} for {task.name}; cannot clock {action.name} again')
        elif action == ActionType.OUT:
            raise RuntimeError(f'cannot clock OUT for {task.name} when not clocked IN for {task.name}')
    
    def add_clk_record(self, task: TaskType, action: ActionType):
        """Adds a clock record to the ClockRecords table"""
        self._validate_prospective_record(task, action)
        uuid_ = self._get_uuid()
        with self.conn:
            self.c.execute("INSERT INTO ClockRecords (uuid, task, action) VALUES (?, ?, ?)", (uuid_, task.value, action.value))
        self.c.execute("SELECT uuid, timestamp, task, action FROM ClockRecords WHERE uuid=?", (uuid_,))
        
        return self.c.fetchone()
    
    def clear_clk_record(self):
        """Drops the ClockRecord from the table"""
        with self.conn:
            self.c.execute("DROP TABLE ClockRecords")
    
    def remove_clk_records(self, idx_list):
        """Deletes multiple records"""
        self.c.execute("SELECT uuid FROM ClockRecords ORDER BY timestamp ASC")
        self.uuids = self.c.fetchall()
        for i in idx_list:
            if i - 1 < 0 or i - 1 > len(idx_list):
                raise IndexError('the index is out of range')
            self.remove_clk_record(self.uuids[i-1][0])
        self.uuids = []
    
    def remove_clk_record(self, uuid_: str):
        with self.conn:
            self.c.execute("DELETE FROM ClockRecords WHERE uuid=?", (uuid_,))
    
    def get_record(self, uuid_: str):
        self.c.execute("SELECT * FROM ClockRecords WHERE uuid=?", (uuid_,))
        return self.c.fetchone()

    def display_record(self, tstamp, task: TaskType, action: ActionType):
        """Displays the given clock record"""
        print(f'{utils.tstamp_to_tstr(tstamp)} | {task.name} {action.name}')

    def display(self):
        """Displays the entire clock record"""
        self.c.execute("SELECT timestamp, task, action, uuid FROM ClockRecords ORDER BY timestamp ASC")
        i = 1
        for record in self.c.fetchall():
            print(f'{i:02}', end=': ')
            tstamp = utils.tstr_to_tstamp(record[0])
            self.display_record(tstamp, TaskType(record[1]), ActionType(record[2]))
            i += 1