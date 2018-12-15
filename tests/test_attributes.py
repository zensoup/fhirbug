import unittest
from fhirball.config import settings
settings._reset()
settings.configure({'DB_BACKEND': 'SQLAlchemy', 'SQLALCHEMY_CONFIG': {'URI': 'sqlite:///memory'}})
from . import models



class TestAttributes(unittest.TestCase):
    def test_getter_string(self):
        """
        Getter can be a string representing the name of an attribute of _model
        """
        inst = models.AttributeWithStringGetter()

        self.assertEquals(inst.name, "my_name")

    def test_getter_setter_string(self):
        """
        Getter and setter can be a string representing the name of an attribute of _model
        """
        inst = models.AttributeWithStringGetterAndSetter()

        self.assertEquals(inst.name, "my_name")
        inst.name = "new_name"
        self.assertEquals(inst.name, "new_name")

    def test_getter_property(self):
        """
        Getter can be a property
        """
        inst = models.AttributeWithPropertyGetter()
        self.assertEquals(inst.name, "my_name")

    def test_getter_setter_property(self):
        """
        Setter can be a property
        """
        inst = models.AttributeWithPropertyGetterAndGetter()
        self.assertEquals(inst.name, "my_name")
        inst.name = "a_new_name"
        self.assertEquals(inst.name, "a_new_name")

    def test_getter_setter_callables(self):
        """
        Getter and setter can be callables
        """
        inst = models.AttributeWithCallables()
        self.assertEquals(inst.name, "my_name")
        inst.name = "a_new_name"
        self.assertEquals(inst.name, "a_new_name")

    def test_getter_transformer(self):
        """
        Getter can be a tuple (attr, callable) and should return callable(_model.attr)
        """
        inst = models.AttributeWithTransformerGetter()
        self.assertEquals(inst.name, "MY_NAME")

    def test_setter_transformer(self):
        """
        Setter can be a tuple (attr, callable) and should store callable(value) into _model.attr
        """
        inst = models.AttributeWithTransformerSetter()
        self.assertEquals(inst.name, "my_name")
        inst.name = "a_new_name"
        self.assertEquals(inst.name, "A_NEW_NAME")

class TestAttributeWithConst(unittest.TestCase):
    def test_const_getter(self):
        '''
        Attributes with const values always return the same value
        '''
        inst = models.AttributeWithConst()
        self.assertEquals(inst.name, 'the_name')
        inst.name = 'new_name'
        self.assertEquals(inst.name, 'the_name')

class TestDateAttributes(unittest.TestCase):
    def test_date_getter(self):
        '''
        Date getter converts to fhir date automatically
        '''
        inst = models.WithDateAttribute()
        self.assertEquals(inst.date.as_json(), '2012-12-12T00:00:00')

    def test_date_setter(self):
        '''
        Date setter converts to and from fhir date automatically
        '''
        from datetime import datetime
        inst = models.WithDateAttribute()
        self.assertEquals(inst.date.as_json(), '2012-12-12T00:00:00')
        inst.date = datetime(2013, 3, 3)
        self.assertEquals(inst.date.as_json(), '2013-03-03T00:00:00')
