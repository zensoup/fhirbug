from django.db import models
from fhirball.db.backends.DjangoORM.pagination import paginate
from fhirball.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin



class AbstractBaseModel(models.Model, FhirAbstractBaseMixin):
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
