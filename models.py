from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table

from db.backends.SQLAlchemy.AbstractBaseModel import FhirBaseModel
from Fhir import resources as R
from main import Base, engine



# class Patient():
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
class ProcedureRequest(FhirBaseModel):
  __table__ = Table('LIS_ORDERS',
                    Base.metadata,
                    Column('opat_id', Integer, ForeignKey('CS_PATIENTS_TABLE')),
                    autoload=True,
                    autoload_with=engine)

  def _map_(self, *args, **kwargs):
    # import ipdb; ipdb.set_trace()

    resource = R.ProcedureRequest({
      'id': str(int(self.lisor_id)),
      'status': self.status,
      'intent': 'order',
      'subject': self.ContainableResource(cls=Patient, id=self.opat_id, name='subject'),
      'authoredOn': R.FHIRDate(self.date_create),
    }, False)

    if self.lisor_comments:
      ource.note = R.Annotation({'text': self.lisor_comments})

    return resource

  @property
  def status(self):
    try:
      return ['active', 'unknown', 'cancelled', 'completed'][self.lisor_status]
    except:
      return ''

'''
    lisor_id = FloatField(primary_key=True)
    lisor_dept = ForeignKey(CsDepartments, DO_NOTHING)
    opat = ForeignKey(CsPatientsTable, DO_NOTHING)
    opat_code = CharField(max_length=20, blank=True, null=True)
    opat_last_name = CharField(max_length=30, blank=True, null=True)
    opat_first_name = CharField(max_length=18, blank=True, null=True)
    opat_father_name = CharField(max_length=20, blank=True, null=True)
    opat_sex_cd = CharField(max_length=1, blank=True, null=True)
    opat_birthday = DateField(blank=True, null=True)
    opat_tel = CharField(max_length=30, blank=True, null=True)
    lisor_date = DateField()
    lab_dept = ForeignKey(CsDepartments, DO_NOTHING)
    lisor_orderid = FloatField()
    lisor_sender = BooleanField()
    lisor_comments = CharField(max_length=256, blank=True, null=True)
    user_create = CharField(max_length=30, blank=True, null=True)
    date_create = DateField(blank=True, null=True)
    user_update = CharField(max_length=30, blank=True, null=True)
    date_update = DateField(blank=True, null=True)
    lisor_status = FloatField()
    lisor_lab = FloatField()
    opat_insc_code = IntegerField(blank=True, null=True)
    opat_reg_code = CharField(max_length=20, blank=True, null=True)
    opat_amka = CharField(max_length=20, blank=True, null=True)
    oinv_id = FloatField(blank=True, null=True)
    oinv_data = CharField(max_length=30, blank=True, null=True)
    lisor_doctor = CharField(max_length=30, blank=True, null=True)
    old_opat_code = CharField(max_length=20, blank=True, null=True)
    pnur_date_in = DateField(blank=True, null=True)
'''


class Observation(FhirBaseModel):
  __tablename__  = 'LIS_TESTS'

  id = Column('listest_id', Integer, primary_key=True)
  lisor_id = Column('lisor_id', ForeignKey('LIS_ORDERS.lisor_id'))

  def to_fhir(self):
    return observation.Observation()
