class Attribute:

  def __init__(self, getter=None, setter=None, searcher=None, search_regex=None):
    self.getter = getter
    self.setter = setter
    self.searcher = searcher
    if search_regex:
      self.search_regex = search_regex

  def __get__(self, instance, owner):
    ## HERE
    getter = self.getter
    # Strings are column names
    if isinstance(getter, str):
      return getattr(instance._model, getter)
    # Consts provide a constant value
    if isinstance(getter, const):
      return getter.value
    # Callables should be called
    if callable(getter):
      return getter(instance)
    # Two-tuples contain a column name and a callable. Pass the column value to the callable
    if isinstance(getter, (tuple, list)):
      column, func = getter
      return func(getattr(instance._model, column))

  # def __set__(self, instance, owner, value):
  def __set__(self, instance, value):
    setter = self.setter
    # Strings are column names
    if isinstance(setter, str):
      setattr(instance._model, setter, value)
    # Callables should be called
    if callable(setter):
      setter(instance, value)
    # Two-tuples contain a column name and a callable or const. Set the column to the result of the callable or const
    if isinstance(setter, (tuple, list)):
      column, func = setter
      if isinstance(func, const):
        setattr(instance._model, column, func.value)
      else:
        res = func(getattr(instance._model, column), value)  ## TODO: Do we need to pass the current value here?
        setattr(instance._model, column, res)

class const:
  def __init__(self, value):
    self.value = value
