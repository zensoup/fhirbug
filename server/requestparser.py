from urllib.parse import urlparse, parse_qs


def parse_url(url):
  '''
  Parse an http request string and produce an option dict.

  >>> parse_url('Patient/123/$validate?_format=json')
  {'resource': 'Patient',
  'resourceId': '123',
  'operation': '$validate',
  'modifiers': {'_format': ['json']},
  'search_params': {}}
  '''
  parsed = urlparse(url)

  # Parse the path
  path = parsed.path.split('/')

  resource = path.pop(0) if path else None
  resourceId = path.pop(0) if path else None
  operation = path.pop(0) if path else None

  # parse the query strings
  qs = parse_qs(parsed.query)

  # Get the built-in `_keywords`
  modifiers = {param: value for param, value in qs.items() if param.startswith('_')}

  # Get the rest of the search parameters
  search_params = {param: value for param, value in qs.items() if not param in modifiers}

  return {'resource': resource,
          'resourceId': resourceId,
          'operation': operation,
          'modifiers': modifiers,
          'search_params': search_params,
          }