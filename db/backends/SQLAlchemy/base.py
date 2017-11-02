import os
import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# Create the db connection
os.environ["NLS_LANG"] = "GREEK_GREECE.AL32UTF8"
engine = create_engine(settings.SQLALCHEMY_CONFIG['URI'])
session = scoped_session(sessionmaker(bind=engine))

# Provide the base class for AbstractBaseClass to inherit
# You must do this BEFORE importing any models
Base.query = session.query_property()
Base.session = property(lambda instance: session.object_session(instance))
