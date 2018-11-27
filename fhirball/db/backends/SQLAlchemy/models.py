'''
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


'''


from fhirball.db.backends.SQLAlchemy.pagination import paginate
from fhirball.db.backends.SQLAlchemy.base import Base, session

from fhirball.models.mixins import FhirAbstractBaseMixin, FhirBaseModelMixin



class AbstractBaseModel(Base, FhirAbstractBaseMixin):
  """
  The base class to provide functionality to
  our models.
  """
  __abstract__ = True

  @classmethod
  def _get_orm_query(cls):
    return cls.query



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
