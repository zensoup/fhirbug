import sys
import doctest

# The modules to be tested
from fhirball.Fhir.Resources import fhirabstractbase
from fhirball.Fhir.Resources import extensions
from fhirball.Fhir import resources
from fhirball.server import requestparser
from fhirball.db.backends import SQLAlchemy
from fhirball.models import attributes, pagination

def testResourceContructor(verbose=False):
  from fhirball.Fhir import resources

  # Create the extra globals
  context = {
      'Patient': resources.Patient,
      'Identifier': resources.Identifier,
  }

  # Run the tests!
  doctest.testmod(fhirabstractbase, extraglobs=context, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(extensions, extraglobs=context, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(resources, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(requestparser, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(SQLAlchemy, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(attributes, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)
  doctest.testmod(pagination, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose)

if __name__ == '__main__':
  verbose = True if '-v' in sys.argv else False
  testResourceContructor(verbose)
