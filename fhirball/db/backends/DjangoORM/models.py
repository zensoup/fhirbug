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

  @classmethod
  def _get_item_from_pk(cls, pk):
      return cls.objects.get(pk)


class FhirBaseModel(AbstractBaseModel, FhirBaseModelMixin):
  class Meta:
    abstract = True

  @classmethod
  def paginate(cls, *args, **kwargs):
    return paginate(*args, **kwargs)

  @classmethod
  def _after_create(cls, instance):
      try:
          instance.save()
      except Exception as e:
          raise e
      return instance

  @classmethod
  def _after_update(cls, instance):
      try:
          instance.save()
      except Exception as e:
          raise e
      return instance
