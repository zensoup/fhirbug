import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from fhirbug.config import settings


class AbstractModelMeta(DeclarativeMeta):
    def __getattribute__(self, item):
        if item == "query":
            if hasattr(self, "__get_query__"):
                query = super(AbstractModelMeta, self).__getattribute__("query")
                return self.__get_query__(self, query)
        return super(AbstractModelMeta, self).__getattribute__(item)


Base = declarative_base(metaclass=AbstractModelMeta)

# Create the db connection
engine = create_engine(settings.SQLALCHEMY_CONFIG["URI"])
session = scoped_session(sessionmaker(bind=engine))

# Provide the base class for AbstractBaseClass to inherit
# You must do this BEFORE importing any models
Base.query = session.query_property()
Base.session = property(lambda instance: session.object_session(instance))
