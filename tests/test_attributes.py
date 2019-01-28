import unittest
from types import SimpleNamespace
from unittest.mock import call
from fhirbug.config import settings
from fhirbug.exceptions import UnsupportedOperationError, MappingValidationError, MappingException

settings._reset()
settings.configure(
    {"DB_BACKEND": "SQLAlchemy", "SQLALCHEMY_CONFIG": {"URI": "sqlite:///memory"}}
)
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

    def test_setter_error_handling(self):
        """
        Setter can be a property
        """
        inst = models.AttributeWithPropertyGetter()
        self.assertEquals(inst.name, "my_name")
        inst.name = "a_new_name"
        self.assertEquals(inst.name, "my_name")
        settings._wrapped.STRICT_MODE = {"set_attribute_without_setter": True}
        with self.assertRaises(UnsupportedOperationError):
            inst.name = "a_new_name"

    def test_getter_setter_property(self):
        """
        Setter can be a property
        """
        inst = models.AttributeWithPropertyGetterAndSetter()
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
    def test_const(self):
        """
        Attributes with const values always return the same value
        """
        inst = models.AttributeWithConst()
        self.assertEquals(inst.name, "the_name")
        inst.name = "asdasdasd"
        self.assertEquals(inst.name, "the_name")

    def test_const_setter(self):
        """
        Attributes with const setter always set the same value
        """
        inst = models.AttributeWithConstSetter()
        self.assertEquals(inst.name, 12)
        inst.name = 'hello'
        self.assertEquals(inst.name, "the_name")


class TestDateAttributes(unittest.TestCase):
    def test_date_getter(self):
        """
        Date getter converts to fhir date automatically
        """
        inst = models.WithDateAttribute()
        self.assertEquals(inst.date.as_json(), "2012-12-12T00:00:00")

    def test_date_setter(self):
        """
        Date setter converts to and from fhir date automatically
        """
        from datetime import datetime

        inst = models.WithDateAttribute()
        self.assertEquals(inst.date.as_json(), "2012-12-12T00:00:00")
        inst.date = datetime(2013, 3, 3)
        self.assertEquals(inst.date.as_json(), "2013-03-03T00:00:00")
        inst.date = "1989-05-05"
        self.assertEquals(inst.date.as_json(), "1989-05-05")
        from fhirbug.Fhir.resources import FHIRDate

        inst.date = FHIRDate("1989-04-04T12:34")
        self.assertEquals(inst.date.as_json(), "1989-04-04T12:34:00")
        inst.date = "invalid"
        self.assertEquals(inst.date.as_json(), None)
        inst.date = 420
        self.assertEquals(inst.date.as_json(), None)


class TestReferenceAttributes(unittest.TestCase):
    def test_getter(self):
        """
        A referencedAttribute should return a proper reference json containing
        the target resource path as the reference field
        """
        inst = models.WithReference()
        self.assertEqual(
            inst.ref,
            {
                "reference": "ReferenceTarget/12",
                "identifier": {"system": "ReferenceTarget", "value": "12"},
            },
        )

    def test_with_display(self):
        """
        If `force_display` has been passed to the ReferenceAttribute,
        we will try to retreive the referenced object an call _as_display
        on it if it exists
        """
        inst = models.WithReferenceAndDisplay()
        reference = inst.ref
        self.assertEqual(reference["reference"], "ReferenceTarget/12")
        self.assertEqual(
            reference["identifier"], {"system": "ReferenceTarget", "value": "12"}
        )
        self.assertEqual(
            reference["identifier"], {"system": "ReferenceTarget", "value": "12"}
        )
        models.ReferenceTarget_get_orm_query.assert_has_calls(
            [call(), call().get(12), call().get()._as_display()]
        )

    def test_with_contained(self):
        """
        If the attribue's name is the model's `_contained_names` list, we
        should return an internal reference, retreive the item and append it
        in the model's `_contained_items` list to be used in the final json.
        """
        inst = models.WithReferenceAndContained()
        reference = inst.ref
        mock = models.ReferenceTarget_get_orm_query

        self.assertEquals(reference["reference"], "#ref1")
        mock.assert_has_calls(
            [call(), call().get(12), call().get().to_fhir(), call().get()._as_display()]
        )
        self.assertEqual(inst._model._contained_items, [mock().get().to_fhir()])

    def test_setter(self):
        inst = models.WithReference()
        with self.assertRaises(MappingValidationError):
            inst.ref = ["wrong input"]

        mock_val = SimpleNamespace(reference="Patient/")
        # assert types don't match
        # inst.ref = mock_val

        mock_val = SimpleNamespace(reference="ReferenceTarget/12")
        # assert the value is actually set
        # inst.ref = mock_val

        mock_val = SimpleNamespace(reference="ReferenceTarget/does-not-exist")
        # assert resource does not exist
        # inst.ref = mock_val

        # assert it accepts a list

        # assert is checks if the ref exists if its set in strict mode


class TestBooleanAttribute(unittest.TestCase):
    def test_getters(self):
        inst = models.BooleanAttributeModel()

        self.assertEquals(inst.toast, False)
        self.assertEquals(inst.yellow, False)
        self.assertEquals(inst.feather, True)
        self.assertEquals(inst.true, True)
        self.assertEquals(inst.deflt, False)
        self.assertEquals(inst.something, None)

    def test_setters(self):
        inst = models.BooleanAttributeModel()

        self.assertEquals(inst.toast, False)
        inst.toast = True
        self.assertEquals(inst.toast, True)
        inst.toast = False
        self.assertEquals(inst.toast, False)


class TestNameAttribute(unittest.TestCase):
    def test_param_validation(self):
        ''' It should not allow one to set both ``join_given_names`` and ``pass_given_names``
        '''
        from fhirbug.models.attributes import NameAttribute
        a = NameAttribute(join_given_names=True)
        a = NameAttribute(pass_given_names=True)
        with self.assertRaises(MappingException):
            a = NameAttribute(pass_given_names=True, join_given_names=True)

    def test_getter_setter(self):
        from fhirbug.Fhir.resources import HumanName
        inst = models.NameAttibuteModel()
        self.assertTrue(isinstance(inst.withSetters, HumanName))
        self.assertEqual(
            inst.withSetters.as_json(), {"family": "squarepants", "given": ["sponge"]}
        )

        inst.withSetters = [HumanName({"family": "Squarepants", "given": ["SpongeBob"]})]
        self.assertEqual(inst._model._family, "Squarepants")
        self.assertEqual(inst._model._given1, "SpongeBob")

        inst.withJoin =  [HumanName({"family": "Squarepants", "given": ["Sponge", "bob"]})]
        self.assertEqual(inst._model._family, "Squarepants")
        self.assertEqual(inst._model._given1, "Sponge bob")

        inst.withPass =  [HumanName({"family": "Someone", "given": ["Some", "One"]})]
        self.assertEqual(inst._model._family, "Someone")
        inst.givenSetterMock.assert_called_with(inst, ["Some", "One"])
        self.assertEqual(inst._model._given1, "Sponge bob")
