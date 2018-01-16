import os
import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


class AbstractModelMeta(DeclarativeMeta):
  # def __new__(mcs, name, bases, attrs, **kwargs):
  #   ret = super().__new__(mcs, name, bases, attrs)
  #   print(name, 'query' in bases[0].__dict__)
  #   if '__get_query__' in attrs:
  #     cc = [cl for cl in bases[0].mro() if 'query' in cl.__dict__]
  #     import ipdb; ipdb.set_trace()
  #     ret.query = ret.__get_query__(bases[0].query)
  #   return ret
  def __getattribute__(self, item):
    if item == 'query':
      if hasattr(self, '__get_query__'):
        query = super(AbstractModelMeta, self).__getattribute__('query')
        return self.__get_query__(self, query)
    return super(AbstractModelMeta, self).__getattribute__(item)



Base = declarative_base(metaclass=AbstractModelMeta)
# Base = declarative_base()

# Create the db connection
os.environ["NLS_LANG"] = "GREEK_GREECE.AL32UTF8"
engine = create_engine(settings.SQLALCHEMY_CONFIG['URI'])
session = scoped_session(sessionmaker(bind=engine))

# Provide the base class for AbstractBaseClass to inherit
# You must do this BEFORE importing any models
Base.query = session.query_property()
Base.session = property(lambda instance: session.object_session(instance))

def get_base(connection_str='sqlite:///sqlite.db'):
  Base = declarative_base(metaclass=AbstractModelMeta)
  # Create the db connection
  os.environ["NLS_LANG"] = "GREEK_GREECE.AL32UTF8"
  engine = create_engine(connection_str)
  session = scoped_session(sessionmaker(bind=engine))

  # Provide the base class for AbstractBaseClass to inherit
  # You must do this BEFORE importing any models
  Base.query = session.query_property()
  Base.session = property(lambda instance: session.object_session(instance))
  return Base
