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
