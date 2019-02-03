import isodate
import calendar
from datetime import timedelta, datetime
from fhirbug.exceptions import QueryValidationError


def to_float(str):
    try:
        return float(str)
    except ValueError:
        raise QueryValidationError("{} is an invalid numerical parameter".format(str))


def NumericSearch(column):
    def search(cls, field_name, value, sql_query, query):

        if value.startswith("lt"):  # Less than
            return sql_query.raw({column: {"$lt": to_float(value[2:])}})
        if value.startswith("gt"):  # Greater than
            return sql_query.raw({column: {"$gt": to_float(value[2:])}})
        if value.startswith("le"):  # Less or equal
            return sql_query.raw({column: {"$lte": to_float(value[2:])}})
        if value.startswith("ge"):  # Greater or equal
            return sql_query.raw({column: {"$gte": to_float(value[2:])}})
        if value.startswith("eq"):  # Equals
            return sql_query.raw({column: to_float(value[2:])})
        if value.startswith("ne"):  # Not Equal
            return sql_query.raw({column: {"$ne": to_float(value[2:])}})
        if value.startswith("ap"):  # Approximately (+- 10%)
            val = to_float(value[2:])
            return sql_query.raw({column: {"$gte": val - val * 0.1}}).raw(
                {column: {"$lte": val + val * 0.1}}
            )

        return sql_query.raw({column: to_float(value)})

    return search


def NumericSearchWithQuantity(column, convert_value=None, alter_query=None):
    def search(cls, field_name, value, sql_query, query):
        parts = value.split("|", 1)
        if len(parts) == 2:
            value, quantity = parts
            if convert_value:
                value = convert_value(value, quantity)
            if alter_query:
                sql_query = alter_query(query, value, quantity)
        return NumericSearch(column).search(cls, field_name, value, sql_query, query)

    return search


def transform_date(value, trim=True):
    if trim:
        value = value[2:]
    try:
        value = isodate.parse_datetime(value)
        return value
    except:
        try:
            value = isodate.parse_date(value)
            # We must convert to datetime or pymongo can't handle it
            return datetime.combine(value, datetime.min.time())
        except:
            raise QueryValidationError(f"{value} is not a valid ISO date")

def get_equality_date_range(value, trim=True):
    ''' If an incomplete date is provided convert the equality to a renge search.
    For example if the query is ``date=1990`` we should convert it to 1990-01-01 <= date <= 1990-12-31
    '''
    length = len(value)
    if trim:
        length -= 2
    value = transform_date(value, trim)
    search = value
    if length == 4:
        search = {"$gte": value, "$lte": datetime(value.year, 12, 31, 23, 59, 59, 59)}
    elif length == 7:
        first, last = calendar.monthrange(value.year, value.month)
        search = {"$gte": value, "$lte": value + timedelta(days=last-1, hours=23, minutes=59, seconds=59)}
    elif length == 10:
        search = {"$gte": value, "$lte": value + timedelta(days=1, hours=23, minutes=59, seconds=59)}
    return search

def DateSearch(column):
    def search_datetime(cls, field_name, value, sql_query, query):
        # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
        # value = value.pop()
        if value.startswith("lt"):  # Less than
            return sql_query.raw({column: {"$lt": transform_date(value)}})
        if value.startswith("gt"):  # Greater than
            return sql_query.raw({column: {"$gt": transform_date(value)}})
        if value.startswith("le"):  # Less or equal
            return sql_query.raw({column: {"$lte": transform_date(value)}})
        if value.startswith("ge"):  # Greater or equal
            return sql_query.raw({column: {"$gte": transform_date(value)}})
        if value.startswith("eq"):  # Equals
            return sql_query.raw({column: get_equality_date_range(value)})
        if value.startswith("ne"):  # Not Equal
            return sql_query.raw({column: {"$not": get_equality_date_range(value)}})
        if value.startswith("ap"):  # Approximately (+- 10%)
            floor = transform_date(value) - timedelta(30)
            ceil = transform_date(value) + timedelta(30)
            return sql_query.raw({column: {"$gte": floor, "$lte": ceil}})
        return sql_query.raw({column: get_equality_date_range(value, trim=False)})

    return search_datetime


def StringSearch(*column_names):
    """
  Search for string types, supports :contains and :exact modifiers.

  If string search should be performed in multiple columns using OR
  multiple columns can be passed.
  """
    if len(column_names) == 0:
        raise TypeError("StringSearch takes at least one positional argument (0 given)")

    def search(cls, field_name, value, sql_query, query):
        if ":contains" in field_name:
            value = value.replace(":contains", "")
            filter = Q(**{"{}__contains".format(column_names[0]): value})
            for col in column_names[1:]:
                filter |= Q(**{"{}__contains".format(col): value})
            return sql_query.filter(filter)
        if ":exact" in field_name:
            value = value.replace(":exact", "")
            filter = Q(**{"{}".format(column_names[0]): value})
            for col in column_names[1:]:
                filter |= Q(**{"{}".format(col): value})
            return sql_query.filter(filter)
        # Default: startswith
        filter = Q(**{"{}__startswith".format(column_names[0]): value})
        for col in column_names[1:]:
            filter |= Q(**{"{}__startswith".format(col): value})
        return sql_query.filter(filter)

    return search


def NameSearch(column):
    def search_name(cls, field_name, value, sql_query, query):
        # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
        # value = value.pop()
        # col = getattr(cls, column)
        # if value.startswith('lt'):  # Less than
        #   return sql_query.filter(col < value[2:])
        # if value.startswith('gt'):  # Greater than
        #   return sql_query.filter(col > value[2:])
        # if value.startswith('le'):  # Less or equal
        #   return sql_query.filter(col <= value[2:])
        # if value.startswith('ge'):  # Greater or equal
        #   return sql_query.filter(col >= value[2:])
        # if value.startswith('eq'):  # Equals
        #   return sql_query.filter(col == value[2:])
        # if value.startswith('ne'):  # Not Equal
        #   return sql_query.filter(col != value[2:])
        # if value.startswith('ap'):  # Approximately (+- 10%)
        #   val = float(value[2:])
        #   return sql_query.filter(col >= val-val*0.1).filter(col <= val+val*0.1)

        return sql_query.filter({column: {"$text": value}})

    return search_name


def SimpleSearch(column):
    def search(cls, field_name, value, sql_query, query):
        return sql_query.filter(**{"{}".format(column): value})

    return search
