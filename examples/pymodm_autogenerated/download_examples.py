import sys
from types import SimpleNamespace

sys.path.append('tools/fhir_parser')
from fhirloader import FHIRLoader
FHIRLoader.needs = {
        'profiles-resources.json': 'examples-json.zip',
    }



l = FHIRLoader(SimpleNamespace(specification_url='http://hl7.org/fhir/R4'), 'test_cache')
l.load()
