import pytimeparse
import datetime
import arrow


def str_iso8601_to_datetime(str_date):
    return str_to_datetime(str_date)


def str_to_datetime(str_date):
    return arrow.get(str_date).datetime


def str_to_timedelta(str_td):
    seconds = pytimeparse.parse(str_td)
    td = datetime.timedelta(seconds=seconds)
    return td


def timedelta_to_str(td):
    return str(td)
