from .abstractbasemodel import AbstractBaseModel

class FhirBaseModel(AbstractBaseModel):
  __abstract__ = True

  @classmethod
  def get(cls, id, *args, **kwargs):
    '''
    Handle a GET request
    '''
    item = cls.query.get(id)
    res = item.to_fhir(*args, **kwargs)
    return res.as_json()
