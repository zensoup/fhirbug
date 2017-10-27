import importlib

from sqlalchemy.ext.declarative import declarative_base
from settings import SQLALCHEMY_CONFIG
from . import TEST

def importStuff():
  module_path, _, class_name = SQLALCHEMY_CONFIG['BASE_CLASS'].rpartition('.')

  module = importlib.import_module(module_path)

  return getattr(module, class_name)

Base = importStuff()

class ResourceMapping(Base):
  '''
  The base class to provide functionality to
  our models.
  '''
  __abstract__ = True

  def bla(self):
    print(TEST)
