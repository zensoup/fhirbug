from urllib.parse import urlparse, parse_qs

from fhirball.exceptions import QueryValidationError

class FhirRequestQuery:
  '''
  Represents parsed parameters from reqests.
  '''
  def __init__(self, resource, resourceId, operation, operationId, modifiers, search_params, body=None, request=None):
    self.resource = resource
    self.resourceId = resourceId
    self.operation = operation
    self.operationId = operationId
    self.modifiers = modifiers
    self.search_params = search_params
    self.body = body
    self.request = request


def parse_url(url):
  '''
  Parse an http request string and produce an option dict.

  >>> p = parse_url('Patient/123/$validate?_format=json')
  >>> p.resource
  'Patient'
  >>> p.resourceId
  '123'
  >>> p.operation
  '$validate'
  >>> p.modifiers
  {'_format': ['json']}
  >>> p.search_params
  {}

  '''

  # Supported operations that may be applied straight on a resource type
  base_operations = ['_search', '_history']

  parsed = urlparse(url)

  # Parse the path
  path = parsed.path.split('/')

  # Remove the empty string from the end if the path ends with a slash
  if path[-1] == '':
      path.pop(-1)

  # Remove the empty string from the start if the path is only a slash
  if path and path[0] == '':
      path.pop(0)

  resource = path.pop(0) if path else None
  # The second item may be a resource id or a base operator. We check if it exists in base_operations
  if path and path[0] in base_operations:
      resourceId = None
      operation = path.pop(0) if path else None
  else:
      resourceId = path.pop(0) if path else None
      operation = path.pop(0) if path else None
  operationId = path.pop(0) if operation and path else None

  # parse the query strings
  qs = parse_qs(parsed.query)

  # Get the built-in `_keywords`
  modifiers = {param: value for param, value in qs.items() if param.startswith('_')}

  # Get the rest of the search parameters
  search_params = {param: value for param, value in qs.items() if not param in modifiers}

  # We accept both id and _id params, but transfer _id to search_params as id
  id_param = modifiers.pop('_id', None)
  if id_param:
    search_params['id'] = id_param

  params = {'resource': resource,
          'resourceId': resourceId,
          'operation': operation,
          'operationId': operationId,
          'modifiers': modifiers,
          'search_params': search_params,
          }
  validate_params(params)
  return FhirRequestQuery(**params)


def validate_params(params):
  """
  Validate a parameter dictionary

  :param params: Parameter dictionary produced by parse_url
  :return:
  """

  if params['resourceId'] is not None:
    try:
      int(params['resourceId'])
    except ValueError:
      raise QueryValidationError(f'Invalid request string: \'{params["resourceId"]}\' is not a valid resource id')
