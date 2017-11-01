from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy import Base, engine, Attribute, const
from db.backends.SQLAlchemy.fhirbasemodel import FhirBaseModel

from Fhir import resources as R



class Patient(FhirBaseModel):
  #
  # Use autoload to automaticaly populate the mapping's fields
  # TODO: This seems slower, should we use a tool to autogenerate definitions?
  #

  __table__ = Table('CS_PATIENTS_TABLE', Base.metadata, autoload=True, autoload_with=engine)

  @classmethod
  def _apply_searches_(cls, sql_query, rq_query):
    if 'address-city' in rq_query.search_params:
      sql_query = sql_query.filter(cls.opat_city == rq_query.search_params.get('address-city')[0])
    if 'id' in rq_query.search_params: # or '_id' in query.modifiers:
      value = rq_query.search_params.get('id', [''])[0]
      if value.startswith('gt'):
        sql_query = sql_query.filter(cls.opat_id > int(value[2:]))
      if value.startswith('lt'):
        sql_query = sql_query.filter(cls.opat_id < int(value[2:]))
      if not value.startswith('lt') and not value.startswith('gt'):
        sql_query = sql_query.filter(cls.opat_id == int(value))
    return sql_query

  def _map_(self, *args, **kwargs):
    return R.Patient({
        'id': str(int(self.opat_id)),
        'name': R.HumanName(family=self.opat_last_name, given=self.opat_first_name),
        'identifier': R.AMKA(self.opat_amka),
        'active': True,
        'address': R.Address({
            'use': 'home',
            'line': self.opat_address,
            'city': self.opat_city,
            'postalCode': self.opat_zip}),
        'telecom': R.ContactPoint(system='phone', value=self.opat_tel),
        'birthDate': self.opat_birthday,
        })


# class _ProcedureRequest(FhirBaseModel):
#   __table__ = Table('LIS_ORDERS',
#                     Base.metadata,
#                     Column('opat_id', Integer, ForeignKey('CS_PATIENTS_TABLE')),
#                     Column('lisor_status', Integer),
#                     autoload=True,
#                     autoload_with=engine)
#
#   def _map_(self, *args, **kwargs):
#
#     resource = R.ProcedureRequest({
#       'id': str(int(self.lisor_id)),
#       'status': self.status,
#       'intent': 'order',
#       'subject': self.ContainableResource(cls=Patient, id=self.opat_id, name='subject'),
#       'authoredOn': R.FHIRDate(self.date_create),
#     }, False)
#
#     if self.lisor_comments:
#       resource.note = R.Annotation({'text': self.lisor_comments})
#
#     return resource
#
#   @property
#   def status(self):
#     try:
#       return ['active', 'unknown', 'cancelled', 'completed'][self.lisor_status]
#     except:
#       return ''

class ProcedureRequest(FhirBaseModel):
  __table__ = Table('LIS_ORDERS',
                    Base.metadata,
                    Column('lisor_id', Integer, primary_key=True),
                    Column('opat_id', Integer, ForeignKey('CS_PATIENTS_TABLE')),
                    Column('lisor_status', Integer),
                    autoload=True,
                    autoload_with=engine)

  @property
  def get_date(self):
    return R.FHIRDate(self.date_create)

  @property
  def get_status(self):
    try:
      return ['active', 'unknown', 'cancelled', 'completed'][self.lisor_status]
    except:
      return ''

  def set_status(self, value):
    map = {'active': 0, 'unknown': 1, 'cancelled': 2, 'completed': 3}
    if value not in map:
      raise Exception('Invalid status value')
    self.lisor_status = map.get(value)

  @property
  def get_subject(self):
    return self.ContainableResource(cls=Patient, id=self.opat_id, name='subject')

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
    def set_subject(self, reference):
      if hasattr(reference, 'reference'):
        if reference.reference.startswith('#')
          # TODO read internal reference
          pass
        
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


    id = Attribute(('lisor_id', str), None, None)
    status = Attribute(get_status, set_status, None)
    intent = Attribute(const('order'), None, True)
    subject = Attribute('get_subject', 'opat_id', None)
    authoredOn = Attribute(('date_create', R.FHIRDate), 'set_date', None)



class Observation(FhirBaseModel):
  __tablename__  = 'LIS_TESTS'

  id = Column('listest_id', Integer, primary_key=True)
  lisor_id = Column('lisor_id', ForeignKey('LIS_ORDERS.lisor_id'))

  def to_fhir(self):
    return observation.Observation()
