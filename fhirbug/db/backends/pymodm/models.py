from pymodm.errors import DoesNotExist
from bson.objectid import ObjectId
from bson.errors import InvalidId
from fhirbug.db.backends.pymodm.pagination import paginate
from fhirbug.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin
from fhirbug.exceptions import DoesNotExistError


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

    @classmethod
    def _get_item_from_pk(cls, pk):
        try:
            return cls.objects.get({"_id": ObjectId(pk)})
        except (DoesNotExist, InvalidId):
            raise DoesNotExistError(resource_type=cls.__name__, pk=pk)


class FhirBaseModel(AbstractBaseModel, FhirBaseModelMixin):
    class Meta:
        abstract = True

    @classmethod
    def paginate(cls, *args, **kwargs):
        return paginate(*args, **kwargs)

    @classmethod
    def _after_create(cls, instance):
        instance.save()
        return instance

    @classmethod
    def _after_update(cls, instance):
        instance.save()
        return instance
