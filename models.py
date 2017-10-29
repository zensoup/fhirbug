from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy import FhirBaseModel
from Fhir import resources as R
from main import Base, engine



class Patient(FhirBaseModel):
  #
  # Use autoload to automaticaly populate the mapping's fields
  # TODO: This seems slower, should we use a tool to autogenerate definitions?
  #

  __table__ = Table('CS_PATIENTS_TABLE', Base.metadata, autoload=True, autoload_with=engine)

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


class ProcedureRequest(FhirBaseModel):
  __table__ = Table('LIS_ORDERS',
                    Base.metadata,
                    Column('opat_id', Integer, ForeignKey('CS_PATIENTS_TABLE')),
                    Column('lisor_status', Integer),
                    autoload=True,
                    autoload_with=engine)

  def _map_(self, *args, **kwargs):

    resource = R.ProcedureRequest({
      'id': str(int(self.lisor_id)),
      'status': self.status,
      'intent': 'order',
      'subject': self.ContainableResource(cls=Patient, id=self.opat_id, name='subject'),
      'authoredOn': R.FHIRDate(self.date_create),
    }, False)

    if self.lisor_comments:
      resource.note = R.Annotation({'text': self.lisor_comments})

    return resource

  @property
  def status(self):
    try:
      return ['active', 'unknown', 'cancelled', 'completed'][self.lisor_status]
    except:
      return ''


class Observation(FhirBaseModel):
  __tablename__  = 'LIS_TESTS'

  id = Column('listest_id', Integer, primary_key=True)
  lisor_id = Column('lisor_id', ForeignKey('LIS_ORDERS.lisor_id'))

  def to_fhir(self):
    return observation.Observation()
