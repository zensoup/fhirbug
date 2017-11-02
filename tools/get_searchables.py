import json
import os


j = None
searchables = {}

path = os.path.dirname(os.path.abspath(__file__))
with open (os.path.join(path, 'fhir_parser/downloads/search-parameters.json'), 'r') as f:
  j = json.loads(f.read())

for entry in j['entry']:
  resource = entry['resource']
  for base in resource['base']:
    searchables[base] = searchables.get(base, []) + [resource['name']]

import pprint
pprint.pprint(searchables)
