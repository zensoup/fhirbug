import sys
import doctest

# The modules to be tested
from Fhir.Resources import fhirabstractbase
from Fhir.Resources import extensions
from Fhir import resources
from server import requestparser

def testResourceContructor(verbose=False):
  from Fhir import resources

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

if __name__ == '__main__':
  verbose = True if '-v' in sys.argv else False
  testResourceContructor(verbose)
