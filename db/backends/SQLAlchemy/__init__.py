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
'''

import os
import importlib

from db.backends.SQLAlchemy.pagination import paginate
from db.backends.SQLAlchemy.base import Base

## TODO: I'm pretty sure this shouldn't be happening here
from Fhir.resources import PaginatedBundle


import settings


class Attribute:
  def __init__(self, getter, setter, searcher):
    self.getter = getter
    self.setter = setter
    self.searcher = searcher

  def __get__(self, instance, owner):
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
        res = func(getattr(instance.parent, column))
        setattr(instance._model, column, res)

class const:
  def __init__(self, value):
    self.value = value


class AbstractBaseModel(Base):
  '''
  The base class to provide functionality to
  our models.
  '''
  __abstract__ = True

  def ContainableResource(self, cls, id, name, force_display=False):
    '''
    Provides a shortcut for creating references that may or not be contained.
      :param cls: The class of the model we are referring to (eg Patient)
      :param id: the system id of the resource
      :param name: the name of the field this reference occupies in the parent's Resources
      :param force_display: If left to False, resources that are not contained will not include
                            the `display` property since it requires an extra query.

      :returns: A dict representing a reference object
    '''

    # Name of the model of the resource
    # TODO: Assumes the model class has the same name as the resource endpoint
    cls_name = cls.__name__

    if name in self._contained_names:  # The resource should be contained
      # Get the item
      item = cls.query.get(id)

      # TODO: try..catch
      as_fhir = item.to_fhir()

      self._refcount += 1

      as_fhir.id = f'ref{self._refcount}'
      self._contained_items.append(as_fhir)

      # Build the reference dict
      reference = {'reference': f'#ref{self._refcount}'}

      # Add a display if possible
      if hasattr(item, '_as_display'):
        reference['display'] = item._as_display

      return reference

    else:  # The resource is not contained, generate a url

      # Build the reference dict
      reference = {'reference': f'{cls_name}/{id}',
                   'identifier': {
                      'system': 'Patient',
                      'value': str(id),
                   }}

      if force_display:  # Do a query to fetch the display
        # TODO: can we check if it supprts `_as_display` before querying?

        item = cls.query.get(id)

        if hasattr(item, '_as_display'):
          reference['display'] = item._as_display

      return reference

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
    param_dict = {attribute: getattr(self.Fhir, f'{attribute}') for attribute in attributes if hasattr(mock, attribute)}

    resource = Resource(param_dict, strict=kwargs.get('strict', True))

    # Add any contained items that have been generated
    if self._contained_items:
      resource.contained = self._contained_items

    return resource

  @classmethod
  def from_resource(cls, resource):
    '''
    Creates and saves a new row from a Fhir.Resource object
    '''

    params = {}

    # Read the attributes of the FhirMap class
    own_attributes = [prop for prop, type in cls.FhirMap.__dict__.items() if isinstance(type, Attribute)]

    obj = cls()

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
      res = item.to_fhir(*args, query=query, **kwargs)
      return res.as_json()

    else:
      # Handle search
      # apply_search_filters(query, search_params)
      sql_query = cls.query
      if hasattr(cls, '_apply_searches_'):
        sql_query = cls._apply_searches_(sql_query, query)

      # Handle pagination
      count = int(query.modifiers.get('_count', [settings.DEFAULT_BUNDLE_SIZE])[0])
      count = min(count, settings.MAX_BUNDLE_SIZE)
      offset = query.search_params.get('search-offset', ['1'])
      offset = int(offset[0])
      pagination = paginate(sql_query, offset, offset+count)
      params = {
          'items': [item.to_fhir(query, *args, **kwargs) for item in pagination.items],
          'total': pagination.total,
          'pages': pagination.pages,
          'has_next': pagination.has_next,
          'has_previous': pagination.has_previous,
          'next_page': f'{cls.__name__}/?_count={count}&search-offset={offset+count}',
          'previous_page': f'{cls.__name__}/?_count={count}&search-offset={max(offset-count,1)}',
      }
      return PaginatedBundle(pagination=params).as_json()

  @property
  def Fhir(self):
    # Initialize the FhirMap instance
    ## TODO: should we use a base class instead and implement __init__?
    if not hasattr(self, '_Fhir'):
      self._Fhir = self.FhirMap()
      self._Fhir._model = self
      self._Fhir._properties = [prop for prop, typ in self.FhirMap.__dict__.items()
                                    if isinstance(typ, Attribute)]

    # Return the singleton
    return self._Fhir
