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
                timestamp TEXT DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%f', 'now', 'localtime')
                )
            )""")
        self.uuids = []
    
    def _validate_prospective_record(self, task: TaskType, action: ActionType):
        """Validates that this record can be added to ClockRecords.
        Raises errors when the prospective record cannot be added.
        """

        # The same action cannot be repeated twice in a row
        self.c.execute("SELECT action FROM ClockRecords WHERE task=? \
            ORDER BY timestamp DESC LIMIT 1", (task.value,)
        )
        res = self.c.fetchone()
        if res is not None:
            if action.value == res[0]:
                utils.raise_user_error(f'ERROR: already clocked {action.name} for {task.name}; ' +
                    f'cannot clock {action.name} again'
                )
        elif action == ActionType.OUT:
            utils.raise_user_error(f'ERROR: cannot clock OUT for {task.name} ' +
                f'when not clocked IN for {task.name}'
            )

        # If clocking IN for BREAK/LUNCH, the last WORK must be IN (not OUT)
        # (no BREAK/LUNCH w/o WORK active)
        if task != TaskType.WORK and action == ActionType.IN:
            self.c.execute("SELECT action FROM ClockRecords WHERE task=? \
                ORDER BY timestamp DESC LIMIT 1", (TaskType.WORK.value,)
            )
            res = self.c.fetchone()
            if res is None or res[0] == ActionType.OUT.value:
                utils.raise_user_error(f'ERROR: cannot clock IN for {task.name} ' +
                    'when not clocked IN for WORK'
                )
    
    def add_record(self, task: TaskType, action: ActionType):
        """Adds a record to the ClockRecords table."""

        self._validate_prospective_record(task, action)
        uuid_ = utils.get_uuid()
        with self.conn:
            self.c.execute("INSERT INTO ClockRecords (uuid, task, action) \
                VALUES (?, ?, ?)", (uuid_, task.value, action.value)
            )
        self.c.execute("SELECT uuid, timestamp, task, action \
            FROM ClockRecords WHERE uuid=?", (uuid_,)
        )
        
        return self.c.fetchone()
    
    def dropall(self):
        """Drops the ClockRecord table."""
        with self.conn:
            self.c.execute("DROP TABLE ClockRecords")
    
    def remove_records(self, idx_list):
        """Deletes multiple records from the ClockRecords table."""

        self.c.execute("SELECT uuid FROM ClockRecords ORDER BY timestamp ASC")
        self.uuids = self.c.fetchall()
        for i in idx_list:
            if i - 1 < 0 or i - 1 > len(self.uuids):
                utils.raise_user_error('the index is out of range')
            self.remove_record(self.uuids[i-1][0])
        self.uuids = []
    
    def remove_record(self, uuid_: str):
        with self.conn:
            self.c.execute("DELETE FROM ClockRecords WHERE uuid=?", (uuid_,))
    
    def get_record(self, uuid_: str):
        self.c.execute("SELECT * FROM ClockRecords WHERE uuid=?", (uuid_,))
        return self.c.fetchone()

    def display_record(self, tstamp, task: TaskType, action: ActionType, show_date: bool=True):
        """Displays the given record from the ClockRecords table."""

        if show_date:
            print(f'{utils.tstamp_to_tstr(tstamp)} | {task.name} {action.name}')
        else:
            print(f'{utils.tstamp_to_timestr(tstamp): >23} | {task.name} {action.name}')

    def display(self):
        """Displays all records from the ClockRecords table."""

        self.c.execute("SELECT timestamp, task, action, uuid FROM ClockRecords \
            ORDER BY timestamp ASC"
        )
        i = 1
        last_tstamp = None
        for record in self.c.fetchall():
            print(f'{i:02}', end=': ')
            tstamp = utils.tstr_to_tstamp(record[0])
            if last_tstamp is not None and tstamp.date() == last_tstamp.date():
                self.display_record(tstamp, TaskType(record[1]), ActionType(record[2]), show_date=False)
            else:
                self.display_record(tstamp, TaskType(record[1]), ActionType(record[2]))
            last_tstamp = tstamp
            i += 1
    
    def display_summary_for_day(self, date: datetime):
        print(f'Summary for {utils.tstamp_to_datestr(date)}:')

        end_date = date + timedelta(days=1)
        q_date = date.strftime('%Y-%m-%dT00:00:00.000')
        q_end_date = end_date.strftime('%Y-%m-%dT00:00:00.000')
        
        # Get the work hours for today
        self.c.execute("SELECT timestamp, task, action FROM ClockRecords \
                WHERE timestamp > (?) \
                    AND timestamp < (?) \
                ORDER BY timestamp ASC", (q_date, q_end_date))
        
        task_sums = {
            TaskType.WORK: 0,
            TaskType.LUNCH: 0,
            TaskType.BREAK: 0
        }

        prev_task_in = {
            TaskType.WORK: None,
            TaskType.LUNCH: None,
            TaskType.BREAK: None
        }

        for record in self.c.fetchall():
            tstamp = utils.tstr_to_tstamp(record[0])
            task = TaskType(record[1])
            action = ActionType(record[2])
            
            if action == ActionType.OUT:  # clocking OUT (record time)
                if prev_task_in[task] is None:  # action not clocked IN yet (add time from start of day)
                    task_sums[task] += (tstamp - date).total_seconds()
                else:  # action IN record exists (not None)
                    task_sums[task] += (tstamp - prev_task_in[task]).total_seconds()

            prev_task_in[task] = tstamp

        task_sums[TaskType.WORK] -= task_sums[TaskType.LUNCH]
        task_sums[TaskType.WORK] -= task_sums[TaskType.BREAK]

        for task in task_sums.keys():
            task_time = utils.get_time_parts(int(task_sums[task]))
            print(f'{task.name:<5}: {task_time["hours"]:02}:{task_time["minutes"]:02}:{task_time["seconds"]:02}')
        
    def display_summary_today(self):
        self.display_summary_for_day(datetime.today())

    def display_summary_week(self):
        week_ago = datetime.now().date() - timedelta(days=6)
        for i in range(7):
            day = week_ago + timedelta(days=i)
            self.display_summary_for_day(day)
