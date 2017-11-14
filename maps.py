from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from fhirball.db.backends.SQLAlchemy.base import Base, engine


class Patient():
  __table__ = Table('CARE_PERSON', Base.metadata,
                    autoload=True, autoload_with=engine)
