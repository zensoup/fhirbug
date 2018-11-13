from fhirball.Fhir import resources as fhir
from fhirball.db.backends.SQLAlchemy.searches import DateSearch, StringSearch
from fhirball.exceptions import MappingValidationError
from fhirball.models.attributes import Attribute


class const:
  def __init__(self, value):
    self.value = value


class ContainableAttribute(Attribute):
  '''
  A Reference to some other Resource that may be contained.
  '''
  def __init__(self, cls, id, name, force_display=False, searcher=None):
    self.cls = cls
    self.id = id
    self.name = name
    self.force_display = force_display
    self.searcher = searcher

  def __get__(self, instance, owner):
    cls_name = self.cls.__name__
    id = getattr(instance._model, self.id)

    if self.name in instance._model._contained_names:  # The resource should be contained
      # Get the item
      item = self.cls.query.get(id)

      # TODO: try..catch
      as_fhir = item.to_fhir()

      instance._model._refcount += 1

      as_fhir.id = f'ref{instance._model._refcount}'
      instance._model._contained_items.append(as_fhir)

      # Build the reference dict
      reference = {'reference': f'#ref{instance._model._refcount}'}

      # Add a display if possible
      if hasattr(item, '_as_display'):
        reference['display'] = item._as_display

      return reference

    else:  # The resource is not contained, generate a url

      # Build the reference dict
      reference = {'reference': f'{cls_name}/{id}',
                   'identifier': {
                      'system': f'{cls_name}',
                      'value': str(id),
                   }}

      if self.force_display:  # Do a query to fetch the display
        # TODO: can we check if it supprts `_as_display` before querying?

        item = self.cls.query.get(id)

        if hasattr(item, '_as_display'):
          reference['display'] = item._as_display

      return reference

  def __set__(self, instance, reference):
    value = None
    try:
      # TODO: can we make this all a user-defined parameter for the entire identifier?
      sys = reference.identifier.system
      # assigner = reference.identifier.assigner
      # if assigner == getattr(settings, 'ORGANIZATION_NAME', 'CSSA') and sys == 'Patient':
      value = reference.identifier.value
    except AttributeError:
      pass

    if hasattr(reference, 'reference'):
      ref = reference.reference
      if ref.startswith('#'):
        # TODO read internal reference
        pass

    if value is None:
      raise MappingValidationError('Invalid subject')

    setattr(instance._model, self.id, value)


class DateAttribute(Attribute):
  def __init__(self, field):

    def setter(old_date_str, new_date_str):
      return fhir.FHIRDate(new_date_str).date

    self.getter = (field, fhir.FHIRDate)
    self.setter = (field, setter)
    self.searcher = DateSearch(field)


class NameAttribute(Attribute):
  def __init__(self, family, given):

    def getter(instance):
      return fhir.HumanName(family=instance._model.name_last, given=instance._model.name_first)
    def setter(old_date_str, new_date_str):
      return fhir.FHIRDate(new_date_str).date

    def searcher(cls, field_name, value, sql_query, query):
      if 'family' in field_name:
        return StringSearch(family)(cls, field_name, value, sql_query, query)
      if 'given' in field_name:
        return StringSearch(given)(cls, field_name, value, sql_query, query)
      return StringSearch(family, given)(cls, field_name, value, sql_query, query)

    self.getter = getter
    self.searcher = searcher
    self.search_regex = r'(family|given|name)(:\w*)?'
