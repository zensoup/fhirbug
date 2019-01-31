import unittest
from types import SimpleNamespace
from unittest.mock import call, patch, Mock
from fhirbug.config import settings
from fhirbug.exceptions import UnsupportedOperationError, MappingValidationError, MappingException

settings._reset()
settings.configure(
    {"DB_BACKEND": "SQLAlchemy", "SQLALCHEMY_CONFIG": {"URI": "sqlite:///memory"}, 'MODELS_PATH': 'tests.models'}
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


@patch('fhirbug.models.attributes.import_models')
class TestEmbeddedAttribute(unittest.TestCase):

    def test_constructor(self, import_models):
        ''' Embeddedattribute must throw an error when initialized without a ``type`` argument
        '''
        from fhirbug.models.attributes import EmbeddedAttribute
        with self.assertRaises(MappingValidationError):
            a = EmbeddedAttribute()

    def test_accepts_class_or_string(self, import_models):
        ''' It should accept a class or a string as ``type``. Id a string is passed it should be imported
        '''
        from fhirbug.models.attributes import EmbeddedAttribute
        mockClass = Mock()
        a = EmbeddedAttribute(type=mockClass)
        self.assertEqual(a.type, mockClass)
        import_models.assert_not_called()

        b = EmbeddedAttribute(type="asstring")
        import_models.assert_called_once()
        self.assertEqual(b.type, import_models().asstring)

    @patch('fhirbug.models.attributes.Attribute.__init__', return_value=None)
    def test_calls_super(self, AttributeMock, import_models):
        ''' It must call the init method of ``Attribute`` when a type is provided
        '''
        from fhirbug.models.attributes import EmbeddedAttribute
        a = EmbeddedAttribute(type='hoh')
        AttributeMock.assert_called()

    def test_returns_none(self, import_models):
        ''' It sould return None if the relation is empty
        '''
        inst = models.EmbeddedAttributeModel()
        ret = inst.empty
        self.assertEqual(ret, None)

    def test_get_one(self, import_models):
        ''' When one item is returned from the getter, call ``to_fhir()`` on it and return it
        '''
        relationMock = models.relationMock
        relationMock.reset_mock()

        inst = models.EmbeddedAttributeModel()
        res = inst.first
        relationMock.to_fhir.assert_called_once()
        self.assertEqual(res, relationMock.to_fhir())

    def test_get_list(self, import_models):
        ''' When a list is returned from the getter, call ``to_fhir()`` on each item and return the new list
        '''
        relationMock = models.relationMock
        relationMock.reset_mock()
        relationMock2 = models.relationMock2
        relationMock2.reset_mock()

        inst = models.EmbeddedAttributeModel()
        res = inst.many

        relationMock.to_fhir.assert_called_once()
        relationMock2.to_fhir.assert_called_once()
        self.assertEqual(res, [relationMock.to_fhir(), relationMock2.to_fhir()])

    def test_dict_to_resource(self, import_models):
        ''' It should get the resource class from the type class an instantiate it from the dictionary
        '''
        from fhirbug.models.attributes import EmbeddedAttribute
        a = EmbeddedAttribute(type='hoh')
        ret = a.dict_to_resource({'one': 2})
        import_models().hoh._get_resource_cls.assert_called_once()
        import_models().hoh._get_resource_cls().assert_called_with({'one': 2})
        self.assertEqual(ret, import_models().hoh._get_resource_cls()())

    @patch('fhirbug.models.attributes.EmbeddedAttribute.dict_to_resource')
    @patch('fhirbug.models.attributes.Attribute.__set__', return_value=None)
    def test_set_one_dict(self, super_setter, dict_to_resource, import_models):
        inst = models.EmbeddedAttributeModel()
        inst.settable = {'new': 'value'}

        dict_to_resource.assert_called_with({'new': 'value'})
        models.fakeClass.from_resource.assert_called_with(dict_to_resource())
        super_setter.assert_called_with(inst, models.fakeClass.from_resource())

    @patch('fhirbug.models.attributes.Attribute.__set__', return_value=None)
    def test_set_one_mapping(self, super_setter, import_models):
        inst = models.EmbeddedAttributeModel()
        fakeVal = Mock()
        inst.settable = fakeVal

        models.fakeClass.from_resource.assert_called_with(fakeVal)
        super_setter.assert_called_with(inst, models.fakeClass.from_resource())

    @patch('fhirbug.models.attributes.EmbeddedAttribute.dict_to_resource')
    @patch('fhirbug.models.attributes.Attribute.__set__', return_value=None)
    def test_set_from_list(self, super_setter, dict_to_resource, import_models):
        ''' When it is passed a list, it should convert all dicts inside it to maps and set the new list
        '''
        inst = models.EmbeddedAttributeModel()
        fakeVal = Mock()
        inst.settable = [{'new': 'value'}, fakeVal]

        args, _ = super_setter.call_args
        instance, map_func = args
        self.assertEqual(instance, inst)
        map_list = list(map_func)

        dict_to_resource.assert_called_with({'new': 'value'})
        models.fakeClass.from_resource.assert_has_calls([call(dict_to_resource()), call(fakeVal)])
        self.assertEqual(map_list, [models.fakeClass.from_resource(), models.fakeClass.from_resource()])
