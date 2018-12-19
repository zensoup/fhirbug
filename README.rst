FHIRBALL
--------

Fhirbug intends to be a full-featured `FHIR`_ server for python. It has been
designed to be easy to set up and configure and be flexible when it comes to
the rest of tools it is combined with, like web frameworks and database interfaces.
In most simple cases, very little code has to be written apart from field
mappings.

**Fhirbug is still under development!** The API may still change at any time,
it probably contains heaps of bugs and has never been tested in production. If
you are interested in making it better, you are very welcome to contribute!

**What fhirbug does:**


- It provides the ability to create "real time" transformations between your ORM models to valid FHIR resources through an extensive mapping API.

- Has been designed to work with existing data-sets and database schemas but can of course be used with its own database.

- It's compatible with the SQLAlchemy_, DjangoORM_ and PyMODM_ ORMs, so if you can describe your database in one of them, you are good to go. It should also be pretty easy to extend to support any other ORM, feel free to submit a pull request!

- Handles many of the FHIR REST operations and searches like creating and updating resources, performing advanced queries such as reverse includes,paginated bundles, contained or referenced resources, and more.

- Provides the ability to audit each request, at the granularity that you desire, all the way down to limiting which of the attributes for each model should be accessible for each user.

**What fhirbug does not do:**

- Provide a ready to use solution for a Fhir server. Fhirbug is a framework, we want things to be as easy as possible but you will still have to write code.

- Contain a web server. Fhirbug takes over once there is a request string and request body and returns a json object. You have to handle the actual requests and responses.

- Handle authentication and authorization. It supports it, but you must write the implementation.

- A ton of smaller stuff, which you can find in the _Roadmap_.

___________________
Quick Overview
___________________

============
Writing Maps
============

Mapping from a database model to a Fhir resource is pretty simple.
Begin by declaring your models using the ORM of your choice. Subclass or extend your models to use fhirbug's mixins and declare a class called FhirMap.

Inside FhirMap, use Attributes to declare properties using the name of the corresponding Fhir resource.

Here's a simple example for SQLAlchemy:

.. code-block:: python

    from sqlalchemy import Column, Integet, String
    from fhirbug.db.backends.SQLAlchemy.base import Base, engine
    from fhirbug.db.backends.SQLAlchemy import FhirBaseModel


    class Location(FhirBaseModel):
        """
        Suppose we have a database table called `HospitalLocations`
        that we want to map to the FHIR resource type `Location`
        """

        __tablename__ = "HospitalLocations"

        location_id = Column(Integer, primary_key=True)
        location_name = Column(String)

        # So far we fad a normal SQLAlchemy model definition
        # Now we define the mapping:
        class FhirMap:
            id = Attribute(
                getter="location_id", setter=None, searcher=NumericSearch("patient_id")
            )
            name = Attribute(
                getter="location_name",
                setter="location_name",
                searcher=StringSearch("location_name"),
            )

The mapping we defined is as simple as it gets but lets see what it can do. The class we defined is still a normal SQLAlchemy class
and we can use it the way we would any other:

.. code-block:: python

    >>> location = Location.query.first()
    >>> location.location_name
    'Ward-1'

But it also has FHIR superpowers:

.. code-block:: python

    >>> from fhirbug.server.requestparser import parse_url
    >>> request = parse_url('Location?name:contains=storage')
    >>> Location.get(request)
    {
        'resourceType': 'Bundle',
        'total': 2,
        'entry': [
            {
                'resource': {
                    'resourceType': 'Location',
                    'id': 375,
                    'name': 'storage-1'
                }
            },
            {
                'resource': {
                    'resourceType': 'Location',
                    'id': 623,
                    'name': 'temp-storage'
                }
            }
        ]
    }

That probably seemed a bit magic, so let's dive a bit deeper in how fhirbug works.

By making a database model inherit from our base class instead of declarative_base
and defining a FhirMap, we gain the ability to handle it ad both a model and a
Fhir resource.

We we can interchangeably get and set attributes through the `.Fhir` magic property:

.. code-block:: python

    >>> location = Location.query.first()
    >>> location.location_name
    'Ward-1'

    >>> location.Fhir.name
    'Ward-1'

    >>> location.Fhir.name = 'Ward-2'
    >>> location.location_name
    'Ward-2'

And get the JSON representation:

.. code-block:: python

    >>> location.to_fhir()
    <fhirbug.Fhir.Resources.location.Location at 0x7fb2445c6080>
    >>> location.as_json()
    {
        'resourceType': 'Location',
        'id': 1,
        'name': 'Ward_1'
    }


.. _Roadmap:
___________________
Roadmap
___________________


::

    [ ] Complete unit test coverage
        [ ] pagination
        [ ] request handlers
    [ ] Integration tests
    [ ] Complete documentation coverage
    [ ] Add DELETE functionality
    [ ] Support all `search parameters`_
        [ ] _content
        [ ] _lastUpdated
        [ ] _profile
        [ ] _security
        [ ] _tag
        [ ] _text
        [ ] _list
        [ ] _has
        [ ] _summary
        [ ] _sort
        [ ] _count
        [ ] `_at`_
        [ ] _since
    [ ] logging
    [ ] `Documents`_
    [ ] More Searches
    [ ] More attributes
    [ ] If-Modified-Since header
    [ ] Support application/fhir+json and _format
    [ ] Html serving (?)
    [ ] Versions
    [ ] Versioned updates
    [ ] Auto-generate Capability Statement
    [ ] Auto-generate Structure Definition
    [ ] DateSearch should handle partial dates better (i.e. 1990 should mean > 1990-01-01 & < 1990-12-31)



.. _fhir: https://www.hl7.org/fhir/
.. _flask: http://flask.pocoo.org/
.. _DjangoORM: https://www.djangoproject.com/
.. _PyMODM: https://github.com/mongodb/pymodm
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _`search parameters`: https://www.hl7.org/fhir/searchparameter-registry.html
.. _`Documents`: https://www.hl7.org/fhir/documents.html
.. _`_at`: https://www.hl7.org/fhir/http.html#history
