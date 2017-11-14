from fhirball.server.requestparser import parse_url
from fhirball.exceptions import MappingValidationError, QueryValidationError

from fhirball.Fhir.resources import OperationOutcome, FHIRValidationError

import models  # Don't do from models import bla, stuff will break

def handle_get_request(url):
  # Try to parse the url
  try:
    query = parse_url(url)
  except QueryValidationError as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'bad-request', 'diagnostics': f'{e}'}]})
    return op.as_json(), 400

  resource = query.resource
  # Try to import the resource map class
  try:
    Resource = getattr(models, resource)
  except Exception as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'Resource type \"{resource}\" does not exist or is not supported.'}]})
    return op.as_json(), 404

  # Try to fetch the requested resource(s)
  try:
    res = Resource.get(query=query)
    return res, 200
  except (MappingValidationError, FHIRValidationError) as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'{e}'}]})
    return op.as_json(), 404
  except Exception as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'server-error', 'diagnostics': f'{e}'}]})
    return op.as_json(), 500


def handle_post_request(url, body):
    query = parse_url(url)
    resource_name = query.resource
    # Get the Resource
    try:
        from fhirball.Fhir import resources
        Resource = getattr(resources, resource_name)
    except Exception as e:
        op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'Resource \"{resource_name}\" does not exist.'}]})
        return op.as_json(), 404
    # Validate the incoming json
    try:
        resource = Resource(body)
    except Exception as e:
        op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'validation', 'diagnostics': f'{e}'}]})
        return op.as_json(), 400
    # Import the model
    try:
        Model = getattr(models, resource_name)
    except Exception as e:
        return {'error': 'This shouldn\'t happen', 'exception': str(e)}, 404

    new_resource = Model.create_from_resource(resource, query=query)
    # new_resource.save()
    return new_resource.to_fhir().as_json(), 201


