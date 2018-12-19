.. _overview:

Overview
========

Creating Mappings
-----------------

Fhirbug offers a simple declarative way to map your database tables to
`Fhir Resources`_. You need to have created models for your tables using one of
the supported ORMs.

Let's see an example using SQLAlchemy. Suppose we have this model of our database
table where patient personal infrormation is stored.

(Note that we have named the model Patient. This allows Fhirbug to match it to the corresponding resource automatically. If we wanted to give it a different name, we would then have to define `__Resource__ = 'Patient'` after the `__tablename__`)

::

    from sqlalchemy import Column, Integer, String

    class Patient(Base):
        __tablename__ = "PatientEntries"

        id = Column(Integer, primary_key=True)
        name_first = Column(String)
        name_last = Column(String)
        gender = Column(Integer)  # 0: unknown, 1:female, 2:male
        ssn = Column(Integer)

To map this table to the `Patient`_ resource, we will make it inherit it :class:`fhirbug.db.backends.SQLAlchemy.FhirBaseModel` instead of Base.
Then we add a class named **FhirMap** as a member and add all fhir fields we want to support using :mod:`Attributes`:

.. note::
    You do not need to put your FhirMap in the same class as your models. You could just as well extend it in a second class while using FhirBaseModel as a mixin.

::

    from sqlalchemy import Column, Integer, String
    from fhirbug.db.backends.SQLAlchemy import FhirBaseModel
    from fhirbug.models import Attribute, NameAttribute
    from fhirbug.db.backends.SQLAlchemy.searches import NumericSearch

    class Patient(FhirBaseModel):
        __tablename__ = "PatientEntries"

        pat_id = Column(Integer, primary_key=True)
        name_first = Column(String)
        name_last = Column(String)
        gender = Column(Integer)  # 0: unknown, 1:female, 2:male, 3:other
        ssn = Column(Integer)

        @property
        def get_gender(self):
            genders = ['unknown', 'female', 'male', 'other']
            return genders[self.gender]

        @set_gender.setter
        def set_gender(self, value):
            genders = {'unknown': 0, 'female': 1, 'male': 2, 'other': 3}
            self.gender = genders[value]

        class FhirMap:
            id = Attribute('pat_id', searcher=NumericSearch('pid'))
            name = NameAttribute(given_getter='name_first', family_getter='name_last')
            def get_name(instance):
            gender = Attribute('get_gender', 'set_gender')




.. _`Fhir Resources`: https://www.hl7.org/fhir/resourcelist.html
.. _`Patient`: https://www.hl7.org/fhir/patient.html
