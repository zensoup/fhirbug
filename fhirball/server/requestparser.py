from urllib.parse import urlparse, parse_qs

from fhirball.exceptions import QueryValidationError

def split_join(lst):
    """
    Accepts a list of comma separated strings, splits them and joins them in a new list

    >>> split_join(['a,b,c', 'd', 'e,f'])
    ['a', 'b', 'c', 'd', 'e', 'f']
    """
    return [e for elem in lst for e in elem.split(',')]

class FhirRequestQuery:
  '''
  Represents parsed parameters from requests.
  '''
  def __init__(self, resource, resourceId, operation, operationId, modifiers, search_params, body=None, request=None):
    #: A string containing the name of the requested Resource. eg: ``'Procedure'``
    self.resource = resource

    #: The id of the requested resource if a specific resource was requested else ``None``
    self.resourceId = resourceId

    #: A string holding the requested `operation <http://google.com>`_ such as ``$meta`` or ``$validate``
    self.operation = operation

    #: Extra parameters passed after the operation. For example if ``Patient/123/_history/2`` was requested,
    #: ``operation`` would be ``_history`` and ``operationId`` would be ``2``
    self.operationId = operationId

    #: Dictionary. Keys are modifier names and values are the provided values. Holds search parameters
    #: that start with an underscore.
    #: For example ``Patient/123?_format=json`` would have a modifiers value of ``{'_format': 'json'}``
    self.modifiers = modifiers

    #: Dictionary. Keys are parameter names and values are the provided values. Holds search parameters
    #: that are not modifiers
    #: For example ``Patient/123?_format=json`` would have a modifiers value of ``{'_format': 'json'}``
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

  :param url: a string containing the path of the request. It should not contain the server
              path. For example: `Patients/123?name:contains=Jo`
  :returns: A :class:`FhirRequestQuery` object


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
  modifiers = {param: split_join(value) for param, value in qs.items() if param.startswith('_')}

  # Get the rest of the search parameters
  search_params = {param: split_join(value) for param, value in qs.items() if not param in modifiers}

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
  :raises: :exc:`fhirball.exceptions.QueryValidationError`
  """

  if params['resourceId'] is not None:
    try:
      int(params['resourceId'])
    except ValueError:
      raise QueryValidationError(f'Invalid request string: \'{params["resourceId"]}\' is not a valid resource id')
