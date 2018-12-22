.. _`FHIR Resources`:

FHIR Resources
==============

Fhirbug uses `fhir-parser`_ to automatically parse the Fhir specification and
generate classes for resources based on resource definitions. It's an excellent
tool that downloads the Resource Definition files from the official website
of FHIR and generates classes automatically. For details on how that works, check
out the `repository`_.

Fhirbug comes with pre-generated classes for all FHIR Resources, which live
inside :mod:`fhirbug.Fhir.resources`. You can generate your own resource classes
based on a subset or extension of the default resource definitions but this is not currently covered by this documentation.

.. TODO: Standardize and describe the process of generating resources using fhir-parser

Uses of FHIR Resources in Fhirbug
---------------------------------

As return values of ``mapper.to_fhir()``
________________________________________

FHIR Resource classes are used when a mapper instance is converted to a FHIR
Resource using ``.to_fhir()``.
So, supposing we have defined a mapper for the Location resource, we could
see the following:

    >>> Location
    mappings.Location
    >>> location = Location.query.first()
    <mappings.Location>
    >>> location.to_fhir()
    <fhirbug.Fhir.Resources.patient.Patient>


As values for mapper Attributes
_______________________________

FHIR Resources are also used as values for mapper attributes that are either
references to other Resources, `Backbone Elements`_ or `complex datatypes`_.

For example, let's return back to the Location example. As we can see in the
FHIR specification, the Location.address attribute is of type Address_.
This would mean something like this:

    >>> location.Fhir.address
    <fhirbug.Fhir.Resources.address.Address>
    >>> location.Fhir.address.as_json()
    {
        'use': 'work',
        'type': 'physical',
        [...]
    }
    >>> location.Fhir.address.use
    'work'


The FhirAbstractBase
--------------------

The abstract class used as a base to provide common functionality to all produced
Resource classes has been modified in order to provide a convenient API for
creating resources.


.. _`fhir-parser`: https://github.com/smart-on-fhir/fhir-parser
.. _`repository`: `fhir-parser`_
.. _`complex datatypes`: https://www.hl7.org/fhir/datatypes.html#complex
.. _`Backbone Elements`: https://www.hl7.org/fhir/backboneelement.html
.. _Address: https://www.hl7.org/fhir/datatypes.html#Address
