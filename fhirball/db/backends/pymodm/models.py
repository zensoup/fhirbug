from fhirball.db.backends.pymodm.pagination import paginate
from fhirball.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin


class AbstractBaseModel(FhirAbstractBaseMixin):
  """
  The base class to provide functionality to
  our models.
  """
  class Meta:
      abstract = True

  @classmethod
  def _get_orm_query(cls):
    return cls.objects


class FhirBaseModel(AbstractBaseModel, FhirBaseModelMixin):
  class Meta:
    abstract = True

  @classmethod
  def paginate(cls, *args, **kwargs):
    return paginate(*args, **kwargs)
