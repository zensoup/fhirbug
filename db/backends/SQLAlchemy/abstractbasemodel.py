import importlib

from sqlalchemy.ext.declarative import declarative_base
# from settings import SQLALCHEMY_CONFIG
from . import Base, engine

# def importStuff():
#   module_path, _, class_name = SQLALCHEMY_CONFIG['BASE_CLASS'].rpartition('.')
#
#   module = importlib.import_module(module_path)
#
#   return getattr(module, class_name)
#
# Base = importStuff()

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
      reference = {'reference': f'{cls_name}/{id}'}

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

    self._map_() must be defined and return a Resource.
    '''

    # Initialize attributes
    self._contained_names = []
    self._searchables = []

    if query:
      self._contained_names = query.modifiers.get('_include', [])

    self._contained_items = []
    self._refcount = 0

    # Run _map_
    resource = self._map_(self, *args, query=query, **kwargs)

    # Add any contained items that have been generated
    if self._contained_items:
      resource.contained = self._contained_items

    return resource

  def to_fhir2(self, *args, query=None, **kwargs):
    # Initialize attributes
    self._contained_names = []
    self._searchables = []

    if query:
      self._contained_names = query.modifiers.get('_include', [])

    self._contained_items = []
    self._refcount = 0

    # Map the attributes
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

  def update_from_fhir(self, resource):
    pass
