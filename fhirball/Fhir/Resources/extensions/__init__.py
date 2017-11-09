'''
Subclasses of Fhir Resources that provide som functionality shortcuts.
'''

from fhirball.Fhir.Resources import identifier, humanname, bundle
class AMKA(identifier.Identifier):
  '''
  Create an Identifier Resource representing the AMKA coding from a string
  containing the AMKA code.

  >>> a = AMKA('123')
  >>> isinstance(a, identifier.Identifier)
  True
  >>> a.as_json()
  {'system': 'AMKA', 'use': 'official', 'value': '123'}
  '''

  def __init__(self, jsondict, *args, **kwargs):
    # TODO: validate

    amka_dict = {
      'value': jsondict,
      'system': 'AMKA',
      'use': 'official',
    }
    return super(AMKA, self).__init__(amka_dict, *args, **kwargs)


class HumanName(humanname.HumanName):
  '''
  This subclass can be instantiated with kwargs instead of
  '''
  pass


class PaginatedBundle(bundle.Bundle):
  def __init__(self, *args, pagination=None, **kwargs):
    '''
    Override to accept a Pagination dict instead of a jsondict.
    '''
    if 'jsondict' not in args and pagination:

      jsondict = {
        'type': 'searchset',
        'total': pagination['total'],
        'entry': [{'resource': item} for item in pagination['items']],
        'link': [],
      }
      if pagination['has_next']:
        jsondict['link'].append({'relation': 'next', 'url': pagination['next_page']})
      if pagination['has_previous']:
        jsondict['link'].append({'relation': 'previous', 'url': pagination['previous_page']})

    return super(PaginatedBundle, self).__init__(jsondict, *args, **kwargs)
