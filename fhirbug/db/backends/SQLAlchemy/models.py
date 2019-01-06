"""
  SQLAlchemy backend.
  ==================

  A declarative base class must be provided via the 'BASE_CLASS' setting.
  All models inherit from this class.
  Provides AbstractBaseModel as an abstract base for resource mappings to
  inherit from.

  Settings:

  SQLALCHEMY_CONFIG = {
    'URI':  # The connection string for xc_Oracle
    'BASE_CLASS':  # A string containing the module path to a declarative base class.
  }


"""


from fhirbug.db.backends.SQLAlchemy.pagination import paginate
from fhirbug.db.backends.SQLAlchemy.base import Base, session

from fhirbug.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin
from fhirbug.exceptions import DoesNotExistError


class AbstractBaseModel(Base, FhirAbstractBaseMixin):
    """
  The base class to provide functionality to
  our models.
  """

    __abstract__ = True

    @classmethod
    def _get_orm_query(cls):
        return cls.query

    @classmethod
    def _get_item_from_pk(cls, pk):
        item = cls.query.get(pk)
        if item is None:
            raise DoesNotExistError(pk, cls.__name__)
        return item


class FhirBaseModel(AbstractBaseModel, FhirBaseModelMixin):
    __abstract__ = True

    @classmethod
    def _after_create(cls, instance):
        session.add(instance)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        return instance

    @classmethod
    def _after_update(cls, instance):
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        return instance

    @classmethod
    def paginate(cls, *args, **kwargs):
        return paginate(*args, **kwargs)
