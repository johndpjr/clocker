from datetime import datetime


def tstamp_to_tstr(tstamp):
    """Converts a timestamp to the appropriate string for the user view"""
    return tstamp.strftime("%x (%a) %I:%M %p")

def tstr_to_tstamp(tstr):
    """Converts a timestamp string to the appropriate timestamp object"""
    return datetime.strptime(tstr[:-4], '%Y-%m-%dT%H:%M:%S')