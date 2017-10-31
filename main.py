import xml
import importlib

from server.requestparser import parse_url

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
    return {'error': 'resource does not exist'}, 404
  return Resource.get(query=query), 200

def handle_post_request(url, body):
  query = parse_url(url)
  resource = query.resource
  # Get the Resource
  try:
    from Fhir import resources
    Resource = getattr(resources, resource)
  except Exception as e:
    return {'error': 'resource does not exist'}, 404
  print(Resource, body)
  # Validate the incoming json
  try:
    resource = Resource(body)
  except Exception as e:
    return {'error': 'validation error'}, 400
  # Import the model
  try:
    Model = getattr(models, resource)
  except Exception as e:
    return {'error': 'This shouldn\'t happen'}, 404

  new_resource = Model.create_from_resource(resource)
  return new_resource.as_json(), 201

if __name__ == '__main__':
  main()
