'''
  SQLAlchemy backend.
  ==================

  A declarative base class must be provided via the 'BASE_CLASS' setting.
  All models inherit from this class.
  Provides AbstractBaseModel as an abstract base for resource mappings to
  inherit from.

  Settings:

  SQLALCHEMY_CONFIG = {
    'URI':  # The connection string for xc_Oracle
    'BASE_CLASS':  # A string containing the module path to a declarative base class.
  }


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

import importlib

from db.backends.SQLAlchemy.pagination import paginate
from db.backends.SQLAlchemy.base import Base

## TODO: I'm pretty sure this shouldn't be happening here
from Fhir.resources import PaginatedBundle


import settings


class MappingValidationError(Exception):
  pass


class Attribute:

  def __init__(self, getter=None, setter=None, searcher=None):
    self.getter = getter
    self.setter = setter
    self.searcher = searcher

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
        res = func(getattr(instance._model, column), value)
        setattr(instance._model, column, res)

class const:
  def __init__(self, value):
    self.value = value


class ContainableAttribute(Attribute):
  def __init__(self, cls, id, name, force_display=False):
    self.cls = cls
    self.id = id
    self.name = name
    self.force_display = force_display
    self.searcher = None

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

class AbstractBaseModel(Base):
  '''
  The base class to provide functionality to
  our models.
  '''
  __abstract__ = True

  ## Lifecycle

  def to_fhir(self, *args, query=None, **kwargs):
    '''
    Convert from a BaseModel to a Fhir Resource and return it.

    If param `query` is passed and is of type server.FhirRequestQuery, it is used to
    allow for additional functionality like contained resources.
    '''

    # Initialize attributes
    self._searchables = []
    self._contained_names = query.modifiers.get('_include', []) if query else []
    self._contained_items = []
    self._refcount = 0

    # Read the attributes
    attributes = [prop for prop in dir(self.Fhir) if not prop.startswith('_')]

    # Use __Resource__ if it has been defined else the dame of the class
    resource_name = getattr(self, '__Resource__', self.__class__.__name__)

    # TODO: module_path = getattr(settings, 'Resource_Path', 'Fhir.resources')
    package = importlib.import_module('Fhir.resources')

    Resource = getattr(package, resource_name)

    # Filter the matching fields
    mock = Resource()
    self._Fhir._query = query
    param_dict = {attribute: getattr(self.Fhir, f'{attribute}') for attribute in attributes if hasattr(mock, attribute)}

    resource = Resource(param_dict, strict=kwargs.get('strict', True))

    # Add any contained items that have been generated
    if self._contained_items:
      resource.contained = self._contained_items

    return resource

  @classmethod
  def create_from_resource(cls, resource, query=None):
    '''
    Creates and saves a new row from a Fhir.Resource object
    '''

    # Read the attributes of the FhirMap class
    own_attributes = [prop for prop, type in cls.FhirMap.__dict__.items() if isinstance(type, Attribute)]

    obj = cls()
    obj.Fhir._query = query

    # for path in own_attributes:
    for path in own_attributes:
      value = getattr(resource, path.replace('_', '.'), None)
      if value:
        setattr(obj.Fhir, path, value)

    return obj

  @classmethod
  def update_from_resource(cls, resource, query=None):
    '''
    Edits an existing row from a Fhir.Resource object
    '''

    # Read the attributes of the FhirMap class
    own_attributes = [prop for prop, type in cls.FhirMap.__dict__.items() if isinstance(type, Attribute)]

    obj = cls()
    obj.Fhir._query = query

    # for path in own_attributes:
    for path in own_attributes:
      value = getattr(resource, path.replace('_', '.'), None)
      if value:
        setattr(obj.Fhir, path, value)

    return obj

class FhirBaseModel(AbstractBaseModel):
  __abstract__ = True

  @classmethod
  def get(cls, query, *args, **kwargs):
    '''
    Handle a GET request
    '''
    if query.resourceId:
      item = cls.query.get(query.resourceId)
      if not item:
        raise MappingValidationError(f'Resource \"{query.resource}/{query.resourceId}\" does not exist.')
      res = item.to_fhir(*args, query=query, **kwargs)
      return res.as_json()

    else:
      # Handle search
      # apply_search_filters(query, search_params)
      sql_query = cls.query
      for search in [*query.search_params, *query.modifiers]:  # TODO: Do we really need to check the modifiers here?
        if search in cls.searchables():
          values = query.search_params.get(search, query.modifiers.get(search))
          for value in values:
            sql_query = cls.searchables()[search](cls, search, value, sql_query, query)

      # TODO: Handle sorting

      # Handle pagination
      count = int(query.modifiers.get('_count', [settings.DEFAULT_BUNDLE_SIZE])[0])
      count = min(count, settings.MAX_BUNDLE_SIZE)
      offset = query.search_params.get('search-offset', ['1'])
      offset = int(offset[0])
      page = offset // count + 1
      ## TODO: We skip one result between pages here
      pagination = paginate(sql_query, page, count)
      url_queries = '&'.join([f'{param}={value}' for param, values in query.search_params.items() for value in values if param != 'search-offset'])
      url_queries = '&' + url_queries if url_queries else ''
      params = {
          'items': [item.to_fhir(*args, query=query, **kwargs) for item in pagination.items],
          'total': pagination.total,
          'pages': pagination.pages,
          'has_next': pagination.has_next,
          'has_previous': pagination.has_previous,
          'next_page': f'{cls.__name__}/?_count={count}&search-offset={offset+count}{url_queries}',
          'previous_page': f'{cls.__name__}/?_count={count}&search-offset={max(offset-count,1)}{url_queries}',
      }
      return PaginatedBundle(pagination=params).as_json()

  @classmethod
  def searchables(cls):
    '''
    Returns a list od two-tuples containing the name of a searchable attribute and the function that searches for it based
    on the Attribute definitions in the FhirMap subclass.
    '''
    return {name: prop.searcher for name, prop in cls.FhirMap.__dict__.items() if isinstance(prop, Attribute) and prop.searcher}


  @property
  def Fhir(self):
    '''
    Wrapper property that initializes an instance of FhirMap.
    '''
    # Initialize the FhirMap instance
    ## TODO: should we use a base class instead and implement __init__?
    if not hasattr(self, '_Fhir'):
      self._Fhir = self.FhirMap()
      self._Fhir._model = self
      self._Fhir._properties = [prop for prop, typ in self.FhirMap.__dict__.items()
                                    if isinstance(typ, Attribute)]
      # self._Fhir._searchables = [(name, prop.searcher) for name, prop in self.FhirMap.__dict__.items() if name in self._Fhir._properties and prop.searcher]

    # Return the singleton
    return self._Fhir
