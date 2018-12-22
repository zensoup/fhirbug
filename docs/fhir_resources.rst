.. _`FHIR Resources`:

FHIR Resources
==============

.. contents:: Contents:


Fhirbug uses `fhir-parser`_ to automatically parse the Fhir specification and
generate classes for resources based on resource definitions. It's an excellent
tool that downloads the Resource Definition files from the official website
of FHIR and generates classes automatically. For more details, check
out the project's `repository`_.

Fhirbug comes with pre-generated classes for all FHIR Resources, which live
inside :mod:`fhirbug.Fhir.resources`. You can generate your own resource classes
based on a subset or extension of the default resource definitions but this is
not currently covered by this documentation.

.. TODO: Standardize and describe the process of generating resources using fhir-parser

Uses of FHIR Resources in Fhirbug
---------------------------------

As return values of ``mapper.to_fhir()``
________________________________________

FHIR Resource classes are used when a mapper instance is converted to a FHIR
Resource using ``.to_fhir()``.

Supposing we have defined a mapper for the Location resource, we could
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


.. _creating-resources:

Creating resources
------------------

You will be wanting to use the Resource classes to create return values for your
mapper attributes.

The default way for creating resource instances is by passing a json object to
the constructor:

    >>> from fhirbug.Fhir.resources import Observation
    >>> o = Observation({
    ...     'id': '2',
    ...     'status': 'final',
    ...     'code': {'coding': [{'code': '5', 'system': 'test'}]},
    ... })

As you can see, this may get a but verbose so there are several shortcuts to help
with that.

Resource instances can be created:

    - by passing a dict with the proper json structure as we already saw
    - by passing the same values as keyword arguments:

      >>> o = Observation(
      ...     id='2', status='final', code={'coding': [{'code': '5', 'system': 'test'}]}
      ... )

    - when an attribute's type is a Backbone Element or a complex type, we can
      pass a resource:

      >>> from fhirbug.Fhir.resources import CodeableConcept
      >>> test_code = CodeableConcept(coding=[{'code': '5', 'system': 'test'}])
      >>> o = Observation(id='2', status='final', code=test_code)

    - When an attribute has a cardinality larger than one, that is its values
      are part of an array, but we only want to pass one value, we can skip
      the array:

      >>> test_code = CodeableConcept(coding={'code': '5', 'system': 'test'})
      >>> o = Observation(id='2', status='final', code=test_code)

Fhirbug tries to make it as easy to create resources as possible by providing
several shortcuts with the base contructor.


Ignore missing required Attributes
----------------------------------

If you try to initialize a resource without providing a value for a required
attribute you will get an error:

    >>> o = Observation(id='2', status='final')
    FHIRValidationError: {root}:
    'Non-optional property "code" on <fhirbug.Fhir.Resources.observation.Observation object>
    is missing'

You can suppress errors into warnings by passing the ``strict=False`` argument:

    >>> o = Observation(id='2', status='final', strict=False)

Fhirbug will display a warning but it will not complain again if you try to save
or serve the instance. It's up to you  make sure that your data is well defined.


The base Resource class
-----------------------

Tis is the abstract class used as a base to provide common functionality to all
produced Resource classes. It has been modified in order to provide a convenient
API for :ref:`creating-resources`.

.. class:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.__init__

        Parameters that are not defined in FHIR for this resource are ignored.

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.as_json

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.elementProperties

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.mandatoryFields

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.owningResource

    .. automethod:: fhirbug.Fhir.base.fhirabstractbase.FHIRAbstractBase.owningBundle


.. _`fhir-parser`: https://github.com/smart-on-fhir/fhir-parser
.. _`repository`: `fhir-parser`_
.. _`complex datatypes`: https://www.hl7.org/fhir/datatypes.html#complex
.. _`Backbone Elements`: https://www.hl7.org/fhir/backboneelement.html
.. _Address: https://www.hl7.org/fhir/datatypes.html#Address
