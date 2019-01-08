
Welcome to fhirbug's documentation!
====================================

Fhirbug intends to be a full-featured `FHIR`_ server for python >= **3.6**. It has been
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

- Handles many of the FHIR REST operations and searches like creating and updating resources, performing advanced queries such as reverse includes, paginated bundles, contained or referenced resources, and more.

- Provides the ability to audit each request, at the granularity that you desire, all the way down to limiting which of the attributes for each model should be accessible for each user.

**What fhirbug does not do:**

- Provide a ready to use solution for a Fhir server. Fhirbug is a framework, we want things to be as easy as possible but you will still have to write code.

- Contain a web server. Fhirbug takes over once there is a request string and request body and returns a json object. You have to handle the actual requests and responses.

- Handle authentication and authorization. It supports it, but you must write the implementation.

- A ton of smaller stuff, which you can find in the Roadmap_.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   quickstart
   overview
   api_index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _fhir: https://www.hl7.org/fhir/
.. _flask: http://flask.pocoo.org/
.. _DjangoORM: https://www.djangoproject.com/
.. _PyMODM: https://github.com/mongodb/pymodm
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _`search parameters`: https://www.hl7.org/fhir/searchparameter-registry.html
.. _`Documents`: https://www.hl7.org/fhir/documents.html
.. _`_at`: https://www.hl7.org/fhir/http.html#history
