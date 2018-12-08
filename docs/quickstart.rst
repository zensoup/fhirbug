.. _quickstart:

Quickstart
==========

This section contains a brief example of creating a simple application using
fhirball. It's goal is to give the reader a general idea of how fhirball
works, not to provide them with in-depth knowledge about it.

For a more detailed guide check out the :ref:`overview` and the :ref:`api` docs.

Preparation
-----------

In this example we will use an sqlite3_ database with SQLAlchemy. The first is
in the standard library, you can install SQLAlchemy using `pip`:

.. code-block:: bash

    $ pip install sqlalchemy

Let's say we have a very simple database schema, containing a table for Patients
and one for hospital admissions. The SQLAlchemy models look like this:

.. code-block:: python
    :caption: models.py

    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
    from sqlalchemy.orm import relationship

    Base = declarative_base()
    metadata = Base.metadata


    class Patient(Base):
        __tablename__ = 'patients'

        patient_id = Column(Integer, primary_key=True)
        first_name = Column(String)
        last_name = Column(String)
        dob = Column(DateTime)    # date of birth
        gender = Column(Integer)  # 0: female, 1: male, 2: other, 3: unknown


    class Admission(Base):
        __tablename__ = 'admissions'

        id = Column(Integer, primary_key=True)
        status = Column(String) # 'a': active, 'c': closed
        patient_id = Column(Integer, ForeignKey('patients.patient_id'))
        date_start = Column(DateTime)  # date and time of admission
        date_end = Column(DateTime)    # date and time of release

        patient = relationship("patient", back_populates="admissions")


To create the database and tables, open an interactive python shell and
type the following:

.. code-block:: python

    >>> from sqlalchemy import create_engine
    >>> from models import Base

    >>> engine = create_engine('sqlite:///fhirball_demo.db')
    >>> Base.metadata.create_all(engine)


Creating your first Mappings
----------------------------

We will start by creating mappings between our Patient and Admission models and
the Patient_ and Encounter_ FHIR resources. In our simple example the mapping
we want to create looks something like this:


.. table:: Relationships between db columns and fhir attributes for the Patient

    =====================   ==============      ==================
    DB column               FHIR attribute      notes
    =====================   ==============      ==================
    patient_id              id
    first_name, last_name   name                first and last
                                                name must be combined
                                                into a HumanName resource
    dob                     birthDate           must be converted to
                                                FHIRDate
    gender                  gender              values must be translated
                                                between the two systems
                                                (eg: 0 -> 'female')
    =====================   ==============      ==================


Mapping in fhirball is pretty straightforward. All we need to do is:

1. Subclass the model class, inheriting from FhirBaseModel
2. Add a member class called **FhirMap**
3. Inside it, add class attributes using the names of the fhir attributes of the
   resource you are setting up.
4. Use :ref:`Attributes <attributes>` to describe how the conversion between
   db columns and FHIR attributes should happen

Since we are using SQLAlchemy, we will use the :mod:`fhirball.db.backends.SQLAlchemy`
module, and more specifically inherit our Mappings from
:class:`fhirball.db.backends.SQLAlchemy.models.FhirBaseModel`

So, we start describing our mapping for the Patient resource from the id field
which is the simplest:

.. code-block:: python
    :caption: mappings.py

    from models import Patient as PatientModel
    from fhirball.db.backends.SQLAlchemy.models import FhirBaseModel
    from fhirball.models.attributes import Attribute

    class Patient(PatientModel, FhirBaseModel):
        class FhirMap:
            id = Attribute('patient_id')


.. note:: The fact that we named the mapper class `Patient` is important, since
         when fhirball looks for a mapper, it looks by default for a class
         with the same name as the fhir resource.

By passing the column name as a string to the ``Attribute`` we tell fhirball
that the id attribute of the Patient FHIR resource should be retrieved from the
``patient_id`` column.

For the ``birthDate`` attribute we get the information from a single database column,
but it must be converted to and from a FHIR DateTime datatype. So, we will use the
:class:`~fhirball.models.attributes.DateAttribute` helper and let it handle
conversions automatically.

We will also add the name attribute, using the :class:`~fhirball.models.attributes.NameAttribute`
helper. We tell it that we get and set the family name from the column ``last_name`` and
the given name from ``first_name``

.. code-block:: python
    :caption: mappings.py
    :emphasize-lines: 3,8-12

    from models import Patient as PatientModel
    from fhirball.db.backends.SQLAlchemy.models import FhirBaseModel
    from fhirball.models.attributes import Attribute, DateAttribute, NameAttribute

    class Patient(PatientModel, FhirBaseModel):
        class FhirMap:
            id = Attribute('patient_id')
            birthDate = DateAttribute('dob')
            name = NameAttribute(family_getter='last_name',
                                 family_setter='last_name',
                                 given_getter='first_name',
                                 given_setter='first_name')


Letting the magic happen
------------------------

Let's test what we have so far. First, we must provide fhirball with some
basic configuration:

    >>> from fhirball.config import settings
    >>> settings.configure({
    ...     'DB_BACKEND': 'SQLAlchemy',
    ...     'SQLALCHEMY_CONFIG': {
    ...         'URI': 'sqlite:///:memory:'
    ...     }
    ... })

Now, we import or mapper class and create an item just as we would if it were a
simple SQLAlchemy model:

    >>> from datetime import datetime
    >>> from mappings import Patient
    >>> patient = Patient(dob=datetime(1980, 11, 11),
    ...                   first_name='Alice',
    ...                   last_name='Alison')

This ``patient`` object we have created here is a classic SQLAlchemy model.
We can save it, delete it, change values for its columns, etc. **But** it has
also been enhanced by fhirball.

Here's some stuff that we can do with it:

    >>> to_fhir = patient.to_fhir()
    >>> to_fhir.as_json()
    {
        'birthDate': '1980-11-11T00:00:00',
        'name': [{'family': 'Alison', 'given': ['Alice']}],
        'resourceType': 'Patient'
    }

The same way that all model attributes are accessible from the ``patient`` instance,
all FHIR attributes are accessible from ``patient.Fhir``:

    >>> patient.Fhir.name
    <fhirball.Fhir.Resources.humanname.HumanName at 0x7fc62e1cbcf8>
    >>> patient.Fhir.name.as_json()
    {'family': 'Alison', 'given': ['Alice']}
    >>> patient.Fhir.name.family
    'Alison'
    >>> patient.Fhir.name.given
    ['Alice']

If you set an attribute on the FHIR resource:

    >>> patient.Fhir.name.family = 'Walker'

The change is applied to the actual database model!

    >>> patient.last_name
    'Walker'

    >>> patient.Fhir.birthDate = datetime(1970, 11, 11)
    >>> patient.dob
    datetime.datetime(1970, 11, 11, 0, 0)


Handling requests
-----------------

We will finish this quick introduction to fhirball with a look on how requests
are handled. First, let's create a couple more entries:

    >>> from datetime import datetime
    >>> from fhirball.config import settings
    >>> settings.configure({
    ...     'DB_BACKEND': 'SQLAlchemy',
    ...     'SQLALCHEMY_CONFIG': {
    ...         'URI': 'sqlite:///:memory:'
    ...     }
    ... })
    >>> from mappings import Patient
    >>> Patient.session.add_all([
    ...     Patient(first_name='Some', last_name='Guy', dob=datetime(1990, 10, 10)),
    ...     Patient(first_name='Someone', last_name='Else', dob=datetime(1993, 12, 18)),
    ...     Patient(first_name='Not', last_name='Me', dob=datetime(1985, 6, 6)),
    ... ])
    >>> Patient.session.commit()

Great! Now we can simulate some requests. The mapper class we defined earlier
is enough for us to get some nice FHIR functionality like searches.

Let's start by saking for all Patient entries:

    >>> from fhirball.server.requestparser import parse_url
    >>> query = parse_url('Patient')
    >>> Patient.get(query)


.. _sqlite3: https://docs.python.org/3/library/sqlite3.html
.. _Patient: https://www.hl7.org/fhir/patient.html
.. _Encounter: https://www.hl7.org/fhir/encounter.html
