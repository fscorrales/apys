import datetime as dt
import argparse

def valid_date(s):
    try:
        return dt.datetime.strptime(s, "%d-%m-%Y")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)
