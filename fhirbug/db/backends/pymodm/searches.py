import isodate
import calendar
from datetime import timedelta, datetime
from fhirbug.exceptions import QueryValidationError
from fhirbug.utils import date_ceil, transform_date


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


def DateSearch(column):
    def search_datetime(cls, field_name, value, sql_query, query):
        # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
        # value = value.pop()
        if value.startswith("lt"):  # Less than
            return sql_query.raw({column: {"$lt": transform_date(value, to_datetime=True)}})
        if value.startswith("gt"):  # Greater than
            return sql_query.raw({column: {"$gt": date_ceil(value)}})
        if value.startswith("le"):  # Less or equal
            return sql_query.raw({column: {"$lte": date_ceil(value)}})
        if value.startswith("ge"):  # Greater or equal
            return sql_query.raw({column: {"$gte": transform_date(value, to_datetime=True)}})
        if value.startswith("eq"):  # Equals
            return sql_query.raw({column: {"$gte": transform_date(value, to_datetime=True), "$lte": date_ceil(value)}})
        if value.startswith("ne"):  # Not Equal
            return sql_query.raw({column: {"$not": {"$gte": transform_date(value, to_datetime=True), "$lte": date_ceil(value)}}})
        if value.startswith("ap"):  # Approximately (+- 10%)
            floor = transform_date(value, to_datetime=True) - timedelta(30)
            ceil = transform_date(value, to_datetime=True) + timedelta(30)
            return sql_query.raw({column: {"$gte": floor, "$lte": ceil}})
        return sql_query.raw({column: {"$gte": transform_date(value, to_datetime=True), "$lte": date_ceil(value, trim=False)}})

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
