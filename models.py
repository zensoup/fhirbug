from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy.AbstractBaseModel import ResourceMapping
from Fhir import resources as R
from main import Base, engine



# class Patient():
class Patient(ResourceMapping):
  #
  # Use autoload to automaticaly populate the mapping's fields
  # TODO: This seems slower, should we use a tool to autogenerate definitions?
  #

  __table__ = Table('CS_PATIENTS_TABLE', Base.metadata, autoload=True, autoload_with=engine)

  def to_fhir(self):
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

    '''
    opat_id = FloatField(primary_key=True)
    opat_code = CharField(unique=True, max_length=20)
    opat_code2 = CharField(max_length=20, blank=True, null=True)
    opat_code3 = CharField(max_length=20, blank=True, null=True)
    opat_code4 = CharField(max_length=20, blank=True, null=True)
    opat_old_code = CharField(max_length=256, blank=True, null=True)
    opat_eama_code = CharField(max_length=256, blank=True, null=True)
    opat_first_name = CharField(max_length=256, blank=True, null=True)
    opat_last_name = CharField(max_length=256)
    opat_father_name = CharField(max_length=256, blank=True, null=True)
    opat_mother_name = CharField(max_length=256, blank=True, null=True)
    opat_spouse = CharField(max_length=256, blank=True, null=True)
    opat_identity = CharField(max_length=256, blank=True, null=True)
    opat_irs = ForeignKey(CsIrs, models.DO_NOTHING, blank=True, null=True)
    opat_afm = CharField(max_length=256, blank=True, null=True)
    opat_insc = ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, blank=True, null=True)
    opat_reg_code = CharField(max_length=256, blank=True, null=True)
    opat_handbook = CharField(max_length=256, blank=True, null=True)
    opat_insc_id2 = ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, db_column='opat_insc_id2', blank=True, null=True)
    opat_reg_code2 = CharField(max_length=256, blank=True, null=True)
    opat_handbook2 = CharField(max_length=256, blank=True, null=True)
    opat_insc_id3 = ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, db_column='opat_insc_id3', blank=True, null=True)
    opat_reg_code3 = CharField(max_length=256, blank=True, null=True)
    opat_handbook3 = CharField(max_length=256, blank=True, null=True)
    opat_sex_cd = CharField(max_length=1, blank=True, null=True)
    opat_birthday = CharField(max_length=256, blank=True, null=True)
    opat_address = CharField(max_length=256, blank=True, null=True)
    opat_city = CharField(max_length=256, blank=True, null=True)
    opat_zip = CharField(max_length=256, blank=True, null=True)
    opat_tel = CharField(max_length=256, blank=True, null=True)
    opat_liable_last_name = CharField(max_length=256, blank=True, null=True)
    opat_liable_first_name = CharField(max_length=256, blank=True, null=True)
    opat_marital_stat_cd = CharField(max_length=1, blank=True, null=True)
    opat_nat = ForeignKey(CsNationalities, models.DO_NOTHING, blank=True, null=True)
    opat_prof = ForeignKey('CsProfessions', models.DO_NOTHING, blank=True, null=True)
    opat_birth_perf = ForeignKey('CsPerfectures', models.DO_NOTHING, blank=True, null=True)
    opat_stay_perf = ForeignKey('CsPerfectures', models.DO_NOTHING, blank=True, null=True)
    opat_organ_donor_cd = CharField(max_length=1, blank=True, null=True)
    opat_cat_cd = CharField(max_length=4, blank=True, null=True)
    opat_remarks = CharField(max_length=4000, blank=True, null=True)
    opat_op_occur_orga = CharField(max_length=30, blank=True, null=True)
    opat_op_occur_comp = CharField(max_length=30, blank=True, null=True)
    opat_op_occurence = FloatField(blank=True, null=True)
    opat_op_occur_date = DateField(blank=True, null=True)
    opat_ip_occur_orga = CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_comp = CharField(max_length=30, blank=True, null=True)
    opat_ip_occurence = FloatField(blank=True, null=True)
    opat_ip_occur_dept_in = CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_dept_out = CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_date_in = DateField(blank=True, null=True)
    opat_ip_occur_date_out = DateField(blank=True, null=True)
    opat_result_cd = CharField(max_length=4, blank=True, null=True)
    opat_exit_cd = CharField(max_length=4, blank=True, null=True)
    opat_synchro_cd = CharField(max_length=4)
    orga_create = CharField(max_length=30, blank=True, null=True)
    comp_create = CharField(max_length=30, blank=True, null=True)
    user_create = CharField(max_length=30, blank=True, null=True)
    date_create = DateField(blank=True, null=True)
    orga_update = CharField(max_length=30, blank=True, null=True)
    comp_update = CharField(max_length=30, blank=True, null=True)
    user_update = CharField(max_length=30, blank=True, null=True)
    date_update = DateField(blank=True, null=True)
    opat_indirect_cd1 = CharField(max_length=1, blank=True, null=True)
    opat_indirect_cd2 = CharField(max_length=1, blank=True, null=True)
    opat_indirect_cd3 = CharField(max_length=1, blank=True, null=True)
    opat_insc1_date_to = DateField(blank=True, null=True)
    opat_insc2_date_to = DateField(blank=True, null=True)
    opat_insc3_date_to = DateField(blank=True, null=True)
    opat_amka = CharField(max_length=20, blank=True, null=True)
    opat_old_insc_id = FloatField(blank=True, null=True)
    opat_old_reg_code = CharField(max_length=256, blank=True, null=True)
    opat_old_handbook = CharField(max_length=256, blank=True, null=True)
    opat_old_indirect_cd = CharField(max_length=1, blank=True, null=True)
    opat_old_insc_date_to = DateField(blank=True, null=True)
    opat_liable_amka = CharField(max_length=11, blank=True, null=True)
    '''

# class RequestGroup(ResourceMapping):
class ProcedureRequest(ResourceMapping):
  __tablename__ = 'LIS_ORDERS'
  order_id = Column('lisor_id', Integer, primary_key=True)
  _status = Column('lisor_status', Integer)
  intent = 'order'
  date_create = Column('date_create', Date)
  subject = Column('opat_id', ForeignKey('CS_PATIENTS_TABLE.opat_id'))
  comments = Column('lisor_comments', String(256))

  def to_fhir(self, *args, **kwargs):
    # import ipdb; ipdb.set_trace()
    result = R.ProcedureRequest({
      'status': self.status,
      'intent': self.intent,
      'subject': R.Reference({'reference': f'Patient/{self.subject}'}).as_json(),
      'authoredOn': self.date_create.strftime('%Y-%m-%d'),
      # 'action': self.tests
    }, False)
    result.action = self.tests
    if self.comments:
      result['note'] = R.Annotation({'text': self.comments}).as_json()
    return result

  @property
  def status(self):
    return ['active', 'unknown', 'cancelled', 'completed'][self._status]

  @property
  def tests(self, contained=False):
    tests = Observation.query.filter(Observation.lisor_id==self.order_id)
    return [test.id for test in tests]

class Observation(ResourceMapping):
  __tablename__  = 'LIS_TESTS'

  id = Column('listest_id', Integer, primary_key=True)
  lisor_id = Column('lisor_id', ForeignKey('LIS_ORDERS.lisor_id'))

  def to_fhir(self):
    return observation.Observation()
