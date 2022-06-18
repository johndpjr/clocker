import sqlite3
from datetime import datetime, timedelta

from enums import TaskType, ActionType
import utils


class ClockerDatabase:
    """Models a SQLite Database for clocker."""

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
    
    def _validate_prospective_record(self, task: TaskType, action: ActionType):
        """Validates that this record can be added to ClockRecords.
        * The same action for a task cannot be repeated twice in a row
        * No lunch or break without work
        """
        # The same action cannot be repeated twice in a row
        self.c.execute("SELECT action FROM ClockRecords WHERE task=? ORDER BY timestamp DESC LIMIT 1", (task.value,))
        res = self.c.fetchone()
        if res is not None:
            if action.value == res[0]:
                print(f'ERROR: already clocked {action.name} for {task.name}; cannot clock {action.name} again')
        elif action == ActionType.OUT:
            print(f'ERROR: cannot clock OUT for {task.name} when not clocked IN for {task.name}')

        # If clocking IN for BREAK/LUNCH, the last WORK must be IN (not OUT)
        # (no BREAK/LUNCH w/o WORK active)
        if task != TaskType.WORK and action == ActionType.IN:
            self.c.execute("SELECT action FROM ClockRecords WHERE task=? ORDER BY timestamp DESC LIMIT 1", (TaskType.WORK.value,))
            res = self.c.fetchone()
            if res is None or res[0] == ActionType.OUT.value:
                print(f'ERROR: cannot clock IN for {task.name} when not clocked IN for WORK')
    
    def add_record(self, task: TaskType, action: ActionType):
        """Adds a record to the ClockRecords table."""

        self._validate_prospective_record(task, action)
        uuid_ = utils.get_uuid()
        with self.conn:
            self.c.execute("INSERT INTO ClockRecords (uuid, task, action) VALUES (?, ?, ?)", (uuid_, task.value, action.value))
        self.c.execute("SELECT uuid, timestamp, task, action FROM ClockRecords WHERE uuid=?", (uuid_,))
        
        return self.c.fetchone()
    
    def clear_record(self):
        """Drops the ClockRecord table."""
        with self.conn:
            self.c.execute("DROP TABLE ClockRecords")
    
    def remove_records(self, idx_list):
        """Deletes multiple records from the ClockRecords table."""

        self.c.execute("SELECT uuid FROM ClockRecords ORDER BY timestamp ASC")
        self.uuids = self.c.fetchall()
        for i in idx_list:
            if i - 1 < 0 or i - 1 > len(self.uuids):
                print('the index is out of range')
            self.remove_record(self.uuids[i-1][0])
        self.uuids = []
    
    def remove_record(self, uuid_: str):
        with self.conn:
            self.c.execute("DELETE FROM ClockRecords WHERE uuid=?", (uuid_,))
    
    def get_record(self, uuid_: str):
        self.c.execute("SELECT * FROM ClockRecords WHERE uuid=?", (uuid_,))
        return self.c.fetchone()

    def display_record(self, tstamp, task: TaskType, action: ActionType):
        """Displays the given record."""

        if tstamp is not None:
            print(f'{utils.tstamp_to_tstr(tstamp)} | {task.name} {action.name}')
        else:
            print(f'{" ": <23} | {task.name} {action.name}')

    def display(self):
        """Displays all records from the ClockRecords table."""

        self.c.execute("SELECT timestamp, task, action, uuid FROM ClockRecords \
            ORDER BY timestamp ASC")
        i = 1
        last_tstamp = None
        for record in self.c.fetchall():
            print(f'{i:02}', end=': ')
            tstamp = utils.tstr_to_tstamp(record[0])
            if tstamp.date == last_tstamp:
                self.display_record(None, TaskType(record[1]), ActionType(record[2]))
            else:
                self.display_record(tstamp, TaskType(record[1]), ActionType(record[2]))
            last_tstamp = tstamp
            i += 1
    
    def display_summary_for_day(self, date):
        # Get the work hours for today
        self.c.execute("SELECT timestamp, task, action FROM ClockRecords \
                WHERE timestamp > (strftime('%Y-%m-%dT00:00:00.000', 'now', 'localtime')) \
                    AND timestamp < (strftime('%Y-%m-%dT00:00:00.000', 'now', 'localtime', '+1 day')) \
                ORDER BY timestamp ASC")
        
        work_sum = 0
        lunch_sum = 0
        break_sum = 0

        prev_work_in = None
        prev_lunch_in = None
        prev_break_in = None

        # TODO: turn these into seperate functions (reduce code repitition)
        for record in self.c.fetchall():
            tstamp = utils.tstr_to_tstamp(record[0])
            if record[1] == TaskType.WORK.value:  # WORK
                if record[2] == ActionType.OUT.value:  # Clocking OUT
                    if prev_work_in is None:  # WORK not clocked IN yet, (add time from start of day)
                        work_sum += (tstamp - date).total_seconds()
                    else:  # WORK IN record exists
                        work_sum += (tstamp - prev_work_in).total_seconds()
                prev_work_in = tstamp
            
            if record[1] == TaskType.LUNCH.value:  # LUNCH
                if record[2] == ActionType.OUT.value:  # Clocking OUT
                    if prev_lunch_in is None:  # LUNCH not clocked IN yet, (add time from start of day)
                        lunch_sum += (tstamp - date).total_seconds()
                    else:  # LUNCH IN record exists
                        lunch_sum += (tstamp - prev_lunch_in).total_seconds()
                prev_lunch_in = tstamp
            
            if record[1] == TaskType.BREAK.value:  # BREAK
                if record[2] == ActionType.OUT.value:  # Clocking OUT
                    if prev_break_in is None:  # BREAK not clocked IN yet, (add time from start of day)
                        break_sum += (tstamp - date).total_seconds()
                    else:  # BREAK IN record exists
                        break_sum += (tstamp - prev_break_in).total_seconds()
                prev_break_in = tstamp

        work_sum -= lunch_sum
        work_sum -= break_sum
         
        work_mins, work_seconds = divmod(int(work_sum), 60)
        work_hrs, work_mins = divmod(work_mins, 60)
        print(f'Total WORK : {work_hrs} hrs, {work_mins} mins, {work_seconds} seconds')
        # FEATURE: add pay based on how many hours you worked (round to 15 mins too!)
        lunch_mins, lunch_seconds = divmod(int(lunch_sum), 60)
        lunch_hrs, lunch_mins = divmod(lunch_mins, 60)
        print(f'Total LUNCH: {lunch_hrs} hrs, {lunch_mins} mins, {lunch_seconds} seconds')
        
        break_mins, break_seconds = divmod(int(break_sum), 60)
        break_hrs, break_mins = divmod(break_mins, 60)
        print(f'Total BREAK: {break_hrs} hrs, {break_mins} mins, {break_seconds} seconds')

    def display_summary_today(self):
        self.display_summary_for_day(datetime.today())

    def display_summary_week(self):
        pass