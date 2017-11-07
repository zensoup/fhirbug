import re
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy.base import Base, engine
from db.backends.SQLAlchemy.searches import NumericSearch, NameSearch
from db.backends.SQLAlchemy import FhirBaseModel, Attribute, const, ContainableAttribute, MappingValidationError

from Fhir import resources as R

import settings


class Patient(FhirBaseModel):
  #
  # Use autoload to automaticaly populate the mapping's fields
  # TODO: This seems slower, should we use a tool to autogenerate definitions?
  #

  __table__ = Table('CARE_PERSON', Base.metadata,
                    autoload=True, autoload_with=engine)

  @property
  def get_name(self):
    return R.HumanName(family=self.name_last, given=self.name_first)

  class FhirMap:
    def get_telecom(self):
      if self._model.phone_1_nr:
        nr = f'{self._model.phone_1_code}-{self._model.phone_1_nr}' if self._model.phone_1_code != '0' else self._model.phone_1_nr
        return R.ContactPoint(system='phone', value=nr, use='home', rank=1)

    def get_gender(self):
      return {'m': 'male', 'f': 'female'}.get(self._model.sex, 'unknown')

    def get_deceased(self):
      return R.FHIRDate(self._model.death_date) if self._model.death_date != datetime(1, 1, 1) else None

    id = Attribute(getter=('pid', str), searcher=NumericSearch('id'))
    name = Attribute('get_name', searcher=NameSearch('name_last'))
    active = Attribute(const(True))
    birthDate = Attribute(('date_birth', R.FHIRDate))
    telecom = Attribute(get_telecom)
    gender = Attribute(get_gender)
    deceasedDateTime = Attribute(get_deceased)

    given = Attribute(searcher=NameSearch('name_last'))
    family =  Attribute(searcher=NameSearch('name_first'))


class Encounter(FhirBaseModel):
  __table__ = Table('CARE_ENCOUNTER', Base.metadata,
                    autoload=True, autoload_with=engine)

  class FhirMap:

    def get_status(self):
      return 'finished' if self._model.is_discharged else 'in-progress'

    def get_period(self):
      return R.Period(start=R.FHIRDate(self._model.encounter_date), end=R.FHIRDate(self._model.discharge_date))

    id = Attribute(getter=('encounter_nr', str), searcher=NumericSearch('encounter_nr'))
    status = Attribute(get_status)
    period = Attribute(get_period)
    subject = ContainableAttribute(cls=Patient, id='pid', name='subject')


class Condition(FhirBaseModel):

  __table__ = Table('DIAG_V', Base.metadata,
                    Column('nr', Integer, primary_key=True),
                    autoload=True, autoload_with=engine)

  @property
  def patient(self):
    enc = Encounter.query.get(self.encounter_nr)
    pat = Patient.query.get(enc.pid)
    return pat.pid

  class FhirMap:
    def get_code(self):
      codeRes = R.CodeableConcept(text=self._model.notes)

      res = re.search(r'([\w\d.]+) - .*', self._model.notes)
      if res:
        code, = res.groups()
        codeRes.coding = [R.Coding(**{'system': 'ICD-10', 'code': code})]

      return codeRes

    id = Attribute(getter=('nr', str), searcher=NumericSearch('nr'))
    category = Attribute(const({'text':'encounter-diagnosis'}))
    subject = ContainableAttribute(cls=Patient, id='patient', name='subject')
    context = ContainableAttribute(cls=Encounter, id='encounter_nr', name='context')
    code = Attribute(get_code)


'''
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
        raise MappingValidationError('Invalid date')

      self.date_create = res.date

    class FhirMap:

      def get_status(self):
        try:
          return ['active', 'unknown', 'cancelled', 'completed'][self._model.lisor_status]
        except:
          return ''

      def set_status(self, value):
        map = {'active': 0, 'unknown': 1, 'cancelled': 2, 'completed': 3}
        if value not in map:
          raise MappingValidationError('Invalid status value')
        self._model.lisor_status = map.get(value)


      id = Attribute(('lisor_id', str), None, NumericSearch('lisor_id'))
      status = Attribute(get_status, set_status, None)
      intent = Attribute(const('order'), None, True)
      # subject = Attribute('get_subject', set_subject, None)
      subject = ContainableAttribute(cls=Patient, id='opat_id', name='subject')
      authoredOn = Attribute(('date_create', R.FHIRDate), 'set_date', None)


  class Observation(FhirBaseModel):
    __table__ = Table('LIS_TESTS',
                      Base.metadata,
                      Column('listest_id', Integer, primary_key=True),
                      Column('lisor_id', Integer, primary_key=True),
                      autoload=True,
                      autoload_with=engine)

    class FhirMap:
      def get_status(self):
        return ['registered', 'preliminary', 'final', 'final', 'ammended'][self._model.listest_status -1]
      def set_status(self):
        pass
      def get_code(self):
        return {'coding': [{'system': 'CSSA', 'code': str(int(self._model.srch_id))}]}
      def search_based_on(cls, field_name, value, sql_query, query):
        col = getattr(cls, 'lisor_id')
        sql_query = sql_query.filter(col == value)
        return sql_query


      id = Attribute(getter=('listest_id', str))
      basedOn = ContainableAttribute(cls=ProcedureRequest, id='lisor_id', name='basedOn')
      status = Attribute(get_status, set_status)
      value = Attribute('listest_result')
      code = Attribute(get_code)
      based = Attribute(searcher=search_based_on)
'''
