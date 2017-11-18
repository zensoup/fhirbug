import isodate
from datetime import timedelta
from fhirball.exceptions import QueryValidationError


def NumericSearch(column):
  def search_id(cls, field_name, value, sql_query, query):
    # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
    # value = value.pop()
    col = getattr(cls, column)
    if value.startswith('lt'):  # Less than
      return sql_query.filter(col < value[2:])
    if value.startswith('gt'):  # Greater than
      return sql_query.filter(col > value[2:])
    if value.startswith('le'):  # Less or equal
      return sql_query.filter(col <= value[2:])
    if value.startswith('ge'):  # Greater or equal
      return sql_query.filter(col >= value[2:])
    if value.startswith('eq'):  # Equals
      return sql_query.filter(col == value[2:])
    if value.startswith('ne'):  # Not Equal
      return sql_query.filter(col != value[2:])
    if value.startswith('ap'):  # Approximately (+- 10%)
      val = float(value[2:])
      return sql_query.filter(col >= val-val*0.1).filter(col <= val+val*0.1)

    return sql_query.filter(col == value)
  return search_id

def DateSearch(column):
  def transform(value, trim=True):
    if trim:
      value = value[2:]
    try:
      value = isodate.parse_datetime(value)
      return value
    except:
      try:
        value = isodate.parse_date(value)
        return value
      except:
        raise QueryValidationError(f'{value} is not a valid ISO date')

  def search_datetime(cls, field_name, value, sql_query, query):
    # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
    # value = value.pop()
    col = getattr(cls, column)
    if value.startswith('lt'):  # Less than
      return sql_query.filter(col < transform(value))
    if value.startswith('gt'):  # Greater than
      return sql_query.filter(col > transform(value))
    if value.startswith('le'):  # Less or equal
      return sql_query.filter(col <= transform(value))
    if value.startswith('ge'):  # Greater or equal
      return sql_query.filter(col >= transform(value))
    if value.startswith('eq'):  # Equals
      return sql_query.filter(col == transform(value))
    if value.startswith('ne'):  # Not Equal
      return sql_query.filter(col != transform(value))
    ## TODO load from settings
    if value.startswith('ap'):  # Approximately (+- 1month)
      floor = transform(value) - timedelta(30)
      ceil = transform(value) + timedelta(30)
      return sql_query.filter(col >= floor).filter(col <= ceil)

    return sql_query.filter(col == transform(value, trim=False))
  return search_datetime


def NameSearch(column):
  def search_name(cls, field_name, value, sql_query, query):
    # value = query.search_params[field_name] if field_name in query.search_params else query.modifiers[field_name]
    # value = value.pop()
    col = getattr(cls, column)
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

    return sql_query.filter(col.contains(value))
  return search_name

def SimpleSearch(column):
  def search(cls, field_name, value, sql_query, query):
    col = getattr(cls, column)
    return sql_query.filter(col==value)
  return search
