from uuid import uuid4
from datetime import datetime


def get_uuid():
    """Returns a Version 4 UUID."""
    return str(uuid4()).replace('-', '')

def tstamp_to_datestr(tstamp):
    return tstamp.strftime('%x (%a)')

def tstamp_to_timestr(tstamp):
    return tstamp.strftime('%I:%M %p')

def tstamp_to_tstr(tstamp):
    return f'{tstamp_to_datestr(tstamp)} {tstamp_to_timestr(tstamp)}'

def tstr_to_tstamp(tstr):
    """Converts a timestamp string to the appropriate timestamp object."""
    return datetime.strptime(tstr[:-4], '%Y-%m-%dT%H:%M:%S')

def get_time_parts(total_secs: int):
    """Returns hours, minutes, and seconds from total_secs in a dictionary."""

    time_parts = {}
    minutes, seconds = divmod(total_secs, 60)
    time_parts['seconds'] = seconds
    hours, minutes = divmod(minutes, 60)
    time_parts['minutes'] = minutes
    time_parts['hours'] = hours

    return time_parts

def raise_user_error(msg: str):
    """Raises an error that the user is using the program incorrectly
    and quits the program quietly.
    """

    print(msg)
    exit()
