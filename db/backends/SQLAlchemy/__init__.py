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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import settings


# Create the db connection
os.environ["NLS_LANG"] = "GREEK_GREECE.AL32UTF8"
engine = create_engine(settings.SQLALCHEMY_CONFIG['URI'])
session = scoped_session(sessionmaker(bind=engine))

# Provide the base class for AbstractBaseClass to inherit
# You must do this BEFORE importing any models
Base = declarative_base()
Base.query = session.query_property()

from .fhirbasemodel import FhirBaseModel

## Mappings
class Attribute:
  def __init__(self, attribute, getter, setter, searcher):
    self.attribute = attribute
    self.getter = getter
    self.setter = setter
    self.searcher = searcher

  def __get__(self, instance, owner):
    getter = self.getter
    if isinstance(getter, str):
      return getattr(instance, getter)
    if isinstance(getter, const):
      return getter.value
    if callable(getter):
      return getter()

  # def __set__(self, instance, owner, value):
  def __set__(self, instance, value):
    setter = self.setter
    if isinstance(setter, str):
      setattr(instance, setter, value)
    # if isinstance(setter, const):
    #   setattr(instance, , setter.value)


class const:
  def __init__(self, value):
    self.value = value
