import sys
import doctest

# The modules to be tested
from fhirbug.Fhir.Resources import fhirabstractbase
from fhirbug.Fhir.Resources import extensions
from fhirbug.Fhir import resources
from fhirbug.server import requestparser
from fhirbug.db.backends import SQLAlchemy
from fhirbug.models import attributes, pagination


def testResourceContructor(verbose=False):

    # Create the extra globals
    context = {"Patient": resources.Patient, "Identifier": resources.Identifier}

    # Run the tests!
    doctest.testmod(
        fhirabstractbase,
        extraglobs=context,
        optionflags=doctest.NORMALIZE_WHITESPACE,
        verbose=verbose,
    )
    doctest.testmod(
        extensions,
        extraglobs=context,
        optionflags=doctest.NORMALIZE_WHITESPACE,
        verbose=verbose,
    )
    doctest.testmod(
        resources, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose
    )
    doctest.testmod(
        requestparser, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose
    )
    doctest.testmod(
        SQLAlchemy, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose
    )
    doctest.testmod(
        attributes, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose
    )
    doctest.testmod(
        pagination, optionflags=doctest.NORMALIZE_WHITESPACE, verbose=verbose
    )


if __name__ == "__main__":
    verbose = True if "-v" in sys.argv else False
    testResourceContructor(verbose)
