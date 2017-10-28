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

  table = Table('CS_PATIENTS_TABLE', Base.metadata, autoload=True, autoload_with=engine)
  __table__ = table

  def to_fhir(self):
    ident  = R.AMKA(self.opat_amka).as_json()
    name = R.HumanName({'family': self.opat_last_name, 'given': [self.opat_first_name]}).as_json()
    return R.Patient({'id': str(self.opat_id), 'name': [name], 'identifier': [ident]})

  '''
    opat_id = models.FloatField(primary_key=True)
    opat_code = models.CharField(unique=True, max_length=20)
    opat_code2 = models.CharField(max_length=20, blank=True, null=True)
    opat_code3 = models.CharField(max_length=20, blank=True, null=True)
    opat_code4 = models.CharField(max_length=20, blank=True, null=True)
    opat_old_code = models.CharField(max_length=256, blank=True, null=True)
    opat_eama_code = models.CharField(max_length=256, blank=True, null=True)
    opat_first_name = models.CharField(max_length=256, blank=True, null=True)
    opat_last_name = models.CharField(max_length=256)
    opat_father_name = models.CharField(max_length=256, blank=True, null=True)
    opat_mother_name = models.CharField(max_length=256, blank=True, null=True)
    opat_spouse = models.CharField(max_length=256, blank=True, null=True)
    opat_identity = models.CharField(max_length=256, blank=True, null=True)
    opat_irs = models.ForeignKey(CsIrs, models.DO_NOTHING, blank=True, null=True)
    opat_afm = models.CharField(max_length=256, blank=True, null=True)
    opat_insc = models.ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, blank=True, null=True)
    opat_reg_code = models.CharField(max_length=256, blank=True, null=True)
    opat_handbook = models.CharField(max_length=256, blank=True, null=True)
    opat_insc_id2 = models.ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, db_column='opat_insc_id2', blank=True, null=True)
    opat_reg_code2 = models.CharField(max_length=256, blank=True, null=True)
    opat_handbook2 = models.CharField(max_length=256, blank=True, null=True)
    opat_insc_id3 = models.ForeignKey(CsInsuranceCompanies, models.DO_NOTHING, db_column='opat_insc_id3', blank=True, null=True)
    opat_reg_code3 = models.CharField(max_length=256, blank=True, null=True)
    opat_handbook3 = models.CharField(max_length=256, blank=True, null=True)
    opat_sex_cd = models.CharField(max_length=1, blank=True, null=True)
    opat_birthday = models.CharField(max_length=256, blank=True, null=True)
    opat_address = models.CharField(max_length=256, blank=True, null=True)
    opat_city = models.CharField(max_length=256, blank=True, null=True)
    opat_zip = models.CharField(max_length=256, blank=True, null=True)
    opat_tel = models.CharField(max_length=256, blank=True, null=True)
    opat_liable_last_name = models.CharField(max_length=256, blank=True, null=True)
    opat_liable_first_name = models.CharField(max_length=256, blank=True, null=True)
    opat_marital_stat_cd = models.CharField(max_length=1, blank=True, null=True)
    opat_nat = models.ForeignKey(CsNationalities, models.DO_NOTHING, blank=True, null=True)
    opat_prof = models.ForeignKey('CsProfessions', models.DO_NOTHING, blank=True, null=True)
    opat_birth_perf = models.ForeignKey('CsPerfectures', models.DO_NOTHING, blank=True, null=True)
    opat_stay_perf = models.ForeignKey('CsPerfectures', models.DO_NOTHING, blank=True, null=True)
    opat_organ_donor_cd = models.CharField(max_length=1, blank=True, null=True)
    opat_cat_cd = models.CharField(max_length=4, blank=True, null=True)
    opat_remarks = models.CharField(max_length=4000, blank=True, null=True)
    opat_op_occur_orga = models.CharField(max_length=30, blank=True, null=True)
    opat_op_occur_comp = models.CharField(max_length=30, blank=True, null=True)
    opat_op_occurence = models.FloatField(blank=True, null=True)
    opat_op_occur_date = models.DateField(blank=True, null=True)
    opat_ip_occur_orga = models.CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_comp = models.CharField(max_length=30, blank=True, null=True)
    opat_ip_occurence = models.FloatField(blank=True, null=True)
    opat_ip_occur_dept_in = models.CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_dept_out = models.CharField(max_length=30, blank=True, null=True)
    opat_ip_occur_date_in = models.DateField(blank=True, null=True)
    opat_ip_occur_date_out = models.DateField(blank=True, null=True)
    opat_result_cd = models.CharField(max_length=4, blank=True, null=True)
    opat_exit_cd = models.CharField(max_length=4, blank=True, null=True)
    opat_synchro_cd = models.CharField(max_length=4)
    orga_create = models.CharField(max_length=30, blank=True, null=True)
    comp_create = models.CharField(max_length=30, blank=True, null=True)
    user_create = models.CharField(max_length=30, blank=True, null=True)
    date_create = models.DateField(blank=True, null=True)
    orga_update = models.CharField(max_length=30, blank=True, null=True)
    comp_update = models.CharField(max_length=30, blank=True, null=True)
    user_update = models.CharField(max_length=30, blank=True, null=True)
    date_update = models.DateField(blank=True, null=True)
    opat_indirect_cd1 = models.CharField(max_length=1, blank=True, null=True)
    opat_indirect_cd2 = models.CharField(max_length=1, blank=True, null=True)
    opat_indirect_cd3 = models.CharField(max_length=1, blank=True, null=True)
    opat_insc1_date_to = models.DateField(blank=True, null=True)
    opat_insc2_date_to = models.DateField(blank=True, null=True)
    opat_insc3_date_to = models.DateField(blank=True, null=True)
    opat_amka = models.CharField(max_length=20, blank=True, null=True)
    opat_old_insc_id = models.FloatField(blank=True, null=True)
    opat_old_reg_code = models.CharField(max_length=256, blank=True, null=True)
    opat_old_handbook = models.CharField(max_length=256, blank=True, null=True)
    opat_old_indirect_cd = models.CharField(max_length=1, blank=True, null=True)
    opat_old_insc_date_to = models.DateField(blank=True, null=True)
    opat_liable_amka = models.CharField(max_length=11, blank=True, null=True)
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
