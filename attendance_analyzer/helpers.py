import datetime as dt
import typing


def parse_datetime(text: str, datetime_regex: str) -> dt.datetime:
    """:raises ValueError"""
    return dt.datetime.strptime(text, datetime_regex)


class PersonWithTime(typing.NamedTuple):
    full_name: str
    start: dt.datetime
    end: dt.datetime
