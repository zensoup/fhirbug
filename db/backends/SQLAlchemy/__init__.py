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
TEST='hoho'
