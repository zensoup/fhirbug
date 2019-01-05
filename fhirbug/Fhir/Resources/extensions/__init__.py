'''
Subclasses of Fhir Resources that provide som functionality shortcuts.
'''

from fhirbug.Fhir.Resources import bundle


class PaginatedBundle(bundle.Bundle):
  def __init__(self, *args, pagination=None, **kwargs):
    '''
    Override to accept a Pagination dict instead of a jsondict.
    '''
    jsondict = None
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
