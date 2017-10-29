import importlib

from sqlalchemy.ext.declarative import declarative_base
from settings import SQLALCHEMY_CONFIG

def importStuff():
  module_path, _, class_name = SQLALCHEMY_CONFIG['BASE_CLASS'].rpartition('.')

  module = importlib.import_module(module_path)

  return getattr(module, class_name)

Base = importStuff()

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
      self._contained_items.append(item.to_fhir())

      self._refcount += 1

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

  def to_fhir(self, *args, contained=[], **kwargs):
    '''
    Convert from a BaseModel to a Fhir Resource and return it.

    self._map_() must be defined and return a Resource.
    '''

    # Initialize attributes
    self._contained_names = contained
    self._contained_items = []
    self._refcount = 0

    # Run _map_
    resource = self._map_(self, *args, **kwargs)

    # Add any contained items that have been generated
    if self._contained_items:
      resource.contained = self._contained_items

    return resource
