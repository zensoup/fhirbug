'''
  Attribute
  =========

  The base class for declaring db to fhir mappings. Accepts three positional argumants, a getter, a setter and a searcher.

  Getting values
  --------------

  The getter parameter can be a string, a tuple, a callable or type const.

  - Using a string:

  >>> from types import SimpleNamespace as SN
  >>> class Bla:
  ...   _model = SN(column_name=12)
  ...   p = Attribute('column_name')
  ...
  >>> b = Bla()
  >>> b.p
  12

  - Strings can also be properties:

  >>> class Model:
  ...  column_name = property(lambda x: 13)
  >>> class Bla:
  ...   _model = Model()
  ...   p = Attribute('column_name')
  ...
  >>> b = Bla()
  >>> b.p
  13

  - Callables will be called:

  >>> class Bla:
  ...   _model = SN(column_name=12)
  ...   def get_col(self):
  ...     return 'test'
  ...   p = Attribute(get_col)
  ...
  >>> b = Bla()
  >>> b.p
  'test'

  - As a shortcut, a tuple (col_name, callable) can be passed. The result will be callable(_model.col_name)

  >>> import datetime
  >>> class Bla:
  ...  _model = SN(date='2012')
  ...  p = Attribute(('date', int))
  ...
  >>> b = Bla()
  >>> b.p
  2012

  Setting values
  --------------

  The setter parameter can be a string, a tuple, a callable or type const.

  - Using a string:

  >>> class Bla:
  ...  _model = SN(date='2012')
  ...  p = Attribute(setter='date')
  ...
  >>> b = Bla()
  >>> b.p = '2013'
  >>> b._model.date
  '2013'

  - Again, the string can point to a property with a setter:

  >>> class Model:
  ...  b = 12
  ...  def set_b(self, value):
  ...    self.b = value
  ...  column_name = property(lambda self: self.b, set_b)
  >>> class Bla:
  ...   _model = Model()
  ...   p = Attribute(getter='column_name', setter='column_name')
  ...
  >>> b = Bla()
  >>> b.p = 13
  >>> b.p == b._model.b == 13
  True

  - Callables will be called:

  >>> class Bla:
  ...   _model = SN(column_name=12)
  ...   def set_col(self, value):
  ...     self._model.column_name = value
  ...   p = Attribute(setter=set_col)
  ...
  >>> b = Bla()
  >>> b.p = 'test'
  >>> b._model.column_name
  'test'

  - Two-tuples contain a column name and a callable or const. Set the column to the result of the callable or const

  >>> def add(column, value):
  ...  return column + value

  >>> class Bla:
  ...   _model = SN(column_name=12)
  ...   p = Attribute(setter=('column_name', add))
  ...
  >>> b = Bla()
  >>> b.p = 3
  >>> b._model.column_name
  15
'''
from fhirball.Fhir import resources as fhir
from fhirball.db.backends.SQLAlchemy.searches import DateSearch


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


class ContainableAttribute(Attribute):
  '''
  A Reference to some other Resource that may be contained.
  '''
  def __init__(self, cls, id, name, force_display=False, searcher=None):
    self.cls = cls
    self.id = id
    self.name = name
    self.force_display = force_display
    self.searcher = searcher

  def __get__(self, instance, owner):
    cls_name = self.cls.__name__
    id = getattr(instance._model, self.id)

    if self.name in instance._model._contained_names:  # The resource should be contained
      # Get the item
      item = self.cls.query.get(id)

      # TODO: try..catch
      as_fhir = item.to_fhir()

      instance._model._refcount += 1

      as_fhir.id = f'ref{instance._model._refcount}'
      instance._model._contained_items.append(as_fhir)

      # Build the reference dict
      reference = {'reference': f'#ref{instance._model._refcount}'}

      # Add a display if possible
      if hasattr(item, '_as_display'):
        reference['display'] = item._as_display

      return reference

    else:  # The resource is not contained, generate a url

      # Build the reference dict
      reference = {'reference': f'{cls_name}/{id}',
                   'identifier': {
                      'system': f'{cls_name}',
                      'value': str(id),
                   }}

      if self.force_display:  # Do a query to fetch the display
        # TODO: can we check if it supprts `_as_display` before querying?

        item = self.cls.query.get(id)

        if hasattr(item, '_as_display'):
          reference['display'] = item._as_display

      return reference

  def __set__(self, instance, reference):
    value = None
    try:
      # TODO: can we make this all a user-defined parameter for the entire identifier?
      sys = reference.identifier.system
      # assigner = reference.identifier.assigner
      # if assigner == getattr(settings, 'ORGANIZATION_NAME', 'CSSA') and sys == 'Patient':
      value = reference.identifier.value
    except AttributeError:
      pass

    if hasattr(reference, 'reference'):
      ref = reference.reference
      if ref.startswith('#'):
        # TODO read internal reference
        pass

    if value is None:
      raise MappingValidationError('Invalid subject')

    setattr(instance._model, self.id, value)


class DateAttribute(Attribute):
  def __init__(self, field):

    def setter(old_date_str, new_date_str):
      return fhir.FHIRDate(new_date_str).date

    self.getter = (field, fhir.FHIRDate)
    self.setter = (field, setter)
    self.searcher = DateSearch(field)
