import sys
import argparse
from types import SimpleNamespace

from fhirloader import FHIRLoader

FHIRLoader.needs = {"profiles-resources.json": "examples-json.zip"}


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--force", help="Force re-downloading of the files",
                    action="store_true")
parser.add_argument("-t", "--target", help="Target directory", default="test_cache")

args = parser.parse_args()
force = args.force
target = args.target

print(f'Downloading examples to {target}')
l = FHIRLoader(
    SimpleNamespace(specification_url="http://hl7.org/fhir/R4"), target
)
l.load(force)
