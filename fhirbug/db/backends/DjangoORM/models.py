from django.db import models
from fhirbug.db.backends.DjangoORM.pagination import paginate
from fhirbug.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin
from fhirbug.exceptions import DoesNotExistError


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
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            raise DoesNotExistError(resource_type=cls.__name__, pk=pk)


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
