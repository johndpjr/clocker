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
    """Converts a timestamp string to the appropriate timestamp object"""
    return datetime.strptime(tstr[:-4], '%Y-%m-%dT%H:%M:%S')
