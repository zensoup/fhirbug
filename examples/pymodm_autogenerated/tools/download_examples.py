import sys
from types import SimpleNamespace

from fhirloader import FHIRLoader

FHIRLoader.needs = {"profiles-resources.json": "examples-json.zip"}


force = len(sys.argv) > 1 and sys.argv[1] == "-f"
l = FHIRLoader(
    SimpleNamespace(specification_url="http://hl7.org/fhir/R4"), "test_cache"
)
l.load(force)
