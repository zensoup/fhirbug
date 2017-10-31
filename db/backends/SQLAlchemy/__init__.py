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
Base.session = property(lambda instance: session.object_session(instance))

## Don't move this, it's black magic!
from .fhirbasemodel import FhirBaseModel


## Mappings
class Attribute2:
  def __init__(self, getter, setter, searcher):
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
    if isinstance(getter, (tuple, list)):
      column, func = getter
      return func(getattr(instance, column))

  # def __set__(self, instance, owner, value):
  def __set__(self, instance, value):
    setter = self.setter
    if isinstance(setter, str):
      setattr(instance, setter, value)
    if callable(setter):
      setter(instance, value)
    if isinstance(setter, (tuple, list)):
      column, func = setter
      if isinstance(func, const):
        setattr(instance, column, func.value)
      else:
        res = func(getattr(instance, column))
        setattr(instance, column, res)
      # setattr(instance, setter, value)
    # if isinstance(setter, const):
    #   setattr(instance, , setter.value)

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
