from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy.base import Base, engine
from db.backends.SQLAlchemy.searches import NumericSearch
from db.backends.SQLAlchemy import FhirBaseModel, Attribute, const, ContainableAttribute

from Fhir import resources as R

import settings


class Patient(FhirBaseModel):
  #
  # Use autoload to automaticaly populate the mapping's fields
  # TODO: This seems slower, should we use a tool to autogenerate definitions?
  #

  __table__ = Table('CS_PATIENTS_TABLE', Base.metadata,
                    Column('opat_id', Integer, primary_key=True),
                    autoload=True, autoload_with=engine)

  @property
  def get_name(self):
    return R.HumanName(family=self.opat_last_name, given=self.opat_first_name)

  class FhirMap:
    id = Attribute(('opat_id', str), None,  NumericSearch('opat_id'))
    name = Attribute('get_name', None, None)
    active = Attribute(const(True), None, None)


class ProcedureRequest(FhirBaseModel):
  __table__ = Table('LIS_ORDERS',
                    Base.metadata,
                    Column('lisor_id', Integer, primary_key=True),
                    Column('opat_id', Integer, ForeignKey('CS_PATIENTS_TABLE')),
                    Column('lisor_status', Integer),
                    autoload=True,
                    autoload_with=engine)

  @property
  def set_date(self):
    pass

  @set_date.setter
  def set_date(self, value):
    if isinstance(value, (dict, str)):
      res = R.FHIRDate(value)
    elif isinstance(value, R.FHIRDate):
      res = value
    else:
      raise Exception('Invalid date')

    self.date_create = res.as_json()

  class FhirMap:

    def get_status(self):
      try:
        return ['active', 'unknown', 'cancelled', 'completed'][self._model.lisor_status]
      except:
        return ''

    def set_status(self, value):
      map = {'active': 0, 'unknown': 1, 'cancelled': 2, 'completed': 3}
      if value not in map:
        raise Exception('Invalid status value')
      self._model.lisor_status = map.get(value)


    id = Attribute(('lisor_id', str), None, NumericSearch('lisor_id'))
    status = Attribute(get_status, set_status, None)
    intent = Attribute(const('order'), None, True)
    # subject = Attribute('get_subject', set_subject, None)
    subject = ContainableAttribute(cls=Patient, id='opat_id', name='subject')
    authoredOn = Attribute(('date_create', R.FHIRDate), 'set_date', None)


class Observation(FhirBaseModel):
  __tablename__  = 'LIS_TESTS'

  id = Column('listest_id', Integer, primary_key=True)
  lisor_id = Column('lisor_id', ForeignKey('LIS_ORDERS.lisor_id'))

  def to_fhir(self):
    return observation.Observation()
