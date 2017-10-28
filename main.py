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

import models  # Don't do from models import bla, stuff will break


def main():
  # pat = session.query(models.Patient).first()
  pat = models.Patient.query.first()

  print(pat.to_fhir().as_json())

  o = models.ProcedureRequest.query.first()
  print(o.to_fhir().as_json())
  pat.bla()

if __name__ == '__main__':
  main()
