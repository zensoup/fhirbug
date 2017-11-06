import xml
import importlib

from server.requestparser import parse_url
from db.backends.SQLAlchemy import MappingValidationError

from Fhir.resources import OperationOutcome, FHIRValidationError
import models  # Don't do from models import bla, stuff will break


def main():
  # pat = session.query(models.Patient).first()
  # pat = models.Patient.query.first()
  pat = models.Patient.get(940)

  # print(pat.to_fhir().as_json())
  print(pat)

  o = models.ProcedureRequest.get(16, contained=['subject'])
  print(o)

def handle_get_request(url):
  query = parse_url(url)
  resource = query.resource
  try:
    Resource = getattr(models, resource)
  except Exception as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'Resource type \"{resource}\" does not exist or is not supported.'}]})
    return op.as_json(), 404
  try:
    res = Resource.get(query=query)
    return res, 200
  except (MappingValidationError, FHIRValidationError) as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'{e}'}]})
    return op.as_json(), 404

def handle_post_request(url, body):
  query = parse_url(url)
  resource_name = query.resource
  # Get the Resource
  try:
    from Fhir import resources
    Resource = getattr(resources, resource_name)
  except Exception as e:
    op = OperationOutcome({'issue': [{'severity': 'error', 'code': 'not-found', 'diagnostics': f'Resource \"{resource_name}\" does not exist.'}]})
    return op.as_json(), 404
  print(Resource, body)
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

if __name__ == '__main__':
  main()
