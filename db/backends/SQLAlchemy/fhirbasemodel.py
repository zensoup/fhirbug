from db.backends.SQLAlchemy.pagination import paginate

import settings
from .abstractbasemodel import AbstractBaseModel

## TODO: I'm pretty sure this shouldn't be happening here
from Fhir.resources import PaginatedBundle

class FhirBaseModel(AbstractBaseModel):
  __abstract__ = True

  @classmethod
  def get(cls, query, *args, **kwargs):
    '''
    Handle a GET request
    '''
    if query.resourceId:
      item = cls.query.get(query.resourceId)
      res = item.to_fhir(*args, query=query, **kwargs)
      return res.as_json()

    else:
      # Handle search
      # apply_search_filters(query, search_params)
      sql_query = cls.query
      if hasattr(cls, '_apply_searches_'):
        sql_query = cls._apply_searches_(sql_query, query)

      # Handle pagination
      count = int(query.modifiers.get('_count', [settings.DEFAULT_BUNDLE_SIZE])[0])
      count = min(count, settings.MAX_BUNDLE_SIZE)
      offset = query.search_params.get('search-offset', ['1'])
      offset = int(offset[0])
      pagination = paginate(sql_query, offset, offset+count)
      params = {
          'items': [item.to_fhir(query, *args, **kwargs) for item in pagination.items],
          'total': pagination.total,
          'pages': pagination.pages,
          'has_next': pagination.has_next,
          'has_previous': pagination.has_previous,
          'next_page': f'{cls.__name__}/?_count={count}&search-offset={offset+count}',
          'previous_page': f'{cls.__name__}/?_count={count}&search-offset={max(offset-count,1)}',
      }
      return PaginatedBundle(pagination=params).as_json()

  @property
  def Fhir(self):
    if not hasattr(self, '_Fhir'):
      self._Fhir = self.FhirMap()
      self._Fhir._model = self
    return self._Fhir
