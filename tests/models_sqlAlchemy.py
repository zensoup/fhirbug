from fhirball.models.mixins import FhirBaseModelMixin, FhirAbstractBaseMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()

class DatabaseModel(Base, FhirAbstractBaseMixin, FhirBaseModelMixin):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
