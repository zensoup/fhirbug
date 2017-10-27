from sqlalchemy import Column, Integer, String, ForeignKey

from db.backends.SQLAlchemy.AbstractBaseModel import ResourceMapping
from Fhir.Resources import identifier, humanname, patient, requestgroup

class AMKA(identifier.Identifier):
  def __init__(self, value):
    super(AMKA, self).__init__()
    self.value = value
    self.system = 'AMKA'
    self.use = 'official'

  # def as_json(self():
  #   return {'system': 'AMKA', 'use': 'official', 'value': self.value}


# class Patient():
class Patient(ResourceMapping):
  __tablename__ = 'CS_PATIENTS_TABLE'

  patient_id = Column('opat_id', Integer, primary_key=True)
  patient_given_name = Column('opat_first_name', String(256))
  patient_family_name = Column('opat_last_name', String(256))
  patient_ssn = Column('opat_amka', String(20))


  def to_resource(self):
    ident  = AMKA(self.patient_ssn).as_json()
    name = humanname.HumanName({'family': self.patient_family_name, 'given': [self.patient_given_name]}).as_json()
    return patient.Patient({'id': str(self.patient_id), 'name': [name], 'identifier': [ident]})


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

class RequestGroup(ResourceMapping):
  __tablename__ = 'LIS_ORDERS'
  order_id = Column('lisor_id', Integer, primary_key=True)
  _status = Column('lisor_status', Integer)
  intent = 'order'
  subject = Column('opat_id', ForeignKey('CS_PATIENTS_TABLE.opat_id'))

  def to_resource(self):
    return requestgroup.RequestGroup({
      'status': self.status,
      'intent': self.intent,
      'subject': Patient.query.get(self.subject).to_resource().as_json()
      })

  @property
  def status(self):
    return ['active', 'unknown', 'cancelled', 'completed'][self._status]

class ProcedureRequest(ResourceMapping):
  __tablename__  = 'LIS_ORDERS'
