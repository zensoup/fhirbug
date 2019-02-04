import isodate
import calendar
from datetime import datetime
from fhirbug.exceptions import QueryValidationError


def transform_date(value, trim=True, to_datetime=False):
    """ Receive an date search string, trim the first to letters if needed
    (for example for a serach like ``date=le1990``) and return a date or datetime
    instance

    :param str value: date search string [xx]YYYY[-MM[-DD[Thh[:mm[:ss]]]]], where xx is a search modifiler (lt, gt, ne, ...)
    :param bool trim: Wether to trim the first two digits of the string
    """
    if trim:
        value = value[2:]
    try:
        value = isodate.parse_datetime(value)
        return value
    except:
        try:
            value = isodate.parse_date(value)
            return (
                datetime.combine(value, datetime.min.time()) if to_datetime else value
            )
        except:
            raise QueryValidationError(f"{value} is not a valid ISO date")


def date_ceil(value, trim=True):
    """ Receive a date search string and return a ceiling value for period-based
    date searches.
    """
    length = len(value)
    if trim:
        length -= 2

    value = transform_date(value, trim)

    if length == 4:
        return datetime(value.year, 12, 31, 23, 59, 59, 59)
    elif length == 7:
        first, last = calendar.monthrange(value.year, value.month)
        return datetime(value.year, value.month, last, 23, 59, 59, 59)
    elif length == 10:
        return datetime(value.year, value.month, value.day, 23, 59, 59, 59)
    elif length == 13:
        return datetime(value.year, value.month, value.day, value.hour, 59, 59, 59)
    elif length == 16:
        return datetime(
            value.year, value.month, value.day, value.hour, value.minute, 59, 59
        )
    elif length == 19:
        return datetime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            59,
        )
    else:
        return value
