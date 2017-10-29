import importlib

from sqlalchemy.ext.declarative import declarative_base
from settings import SQLALCHEMY_CONFIG

def importStuff():
  module_path, _, class_name = SQLALCHEMY_CONFIG['BASE_CLASS'].rpartition('.')

  module = importlib.import_module(module_path)

  return getattr(module, class_name)

Base = importStuff()

class FhirBaseModel(Base):
  '''
  The base class to provide functionality to
  our models.
  '''
  __abstract__ = True

  def ContainableResource(self, cls, id, name, force_display=False):
    cls_name = cls.__name__
    if name in self._contained_names:
      item = cls.query.get(id)
      self._contained_items = getattr(self, '_contained_items', []) + [item.to_fhir()]
      self._refcount = getattr(self, '_refcount', 0) + 1
      reference = {'reference': f'#ref{self._refcount}'}
      if hasattr(item, '_as_display'):
        reference['display'] = item._as_display
      return reference
    else:
      reference = {'reference': f'{cls_name}/{id}'}
      if force_display:
        item = cls.query.get(id)
        if hasattr(item, '_as_display'):
          reference['display'] = item._as_display
      return reference


  ## Lifecycle

  def to_fhir(self, *args, contained=[], **kwargs):
    self._contained_names = contained
    self._contained_items = []
    self._refcount = 0
    # self.pre_transform(*args, **kwargs)
    resource = self._map_(self, *args, **kwargs)
    if self._contained_items:
      resource.contained = self._contained_items

    return resource
