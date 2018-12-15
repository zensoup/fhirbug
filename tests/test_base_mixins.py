import unittest
from fhirball.config import settings
if settings.is_configured():
    settings._reset()
settings.configure({'DB_BACKEND': 'SQLAlchemy', 'SQLALCHEMY_CONFIG': {'URI': 'sqlite:///memory'}})
from . import models
from fhirball.Fhir.resources import Patient, Observation


class TestAbstractBaseMixin(unittest.TestCase):
    def test_get_params_dict(self):
        """
        get_params_dict should retun a dict containing the FhirMap Attributes that match the Fhir resource
        """
        inst = models.BaseMixinModel()
        self.assertEquals(
            inst.get_params_dict(Patient), {"active": True, "name": "hello"}
        )
        self.assertEquals(inst.get_params_dict(Observation), {})

    def test_get_params_dict_with_elements(self):
        """
        get_params_dict should retun a dict containing the FhirMap Attributes that match the Fhir resource, containing only the elements spectified in the parameter
        """
        inst = models.BaseMixinModel()
        self.assertEquals(
            inst.get_params_dict(Patient, ['active', 'name']), {"active": True, "name": "hello"}
        )
        self.assertEquals(
            inst.get_params_dict(Patient, ['active']), {"active": True}
        )
        self.assertEquals(inst.get_params_dict(Observation), {})

    def test_get_rev_includes(self):
        # TODO
        pass

    def test_to_fhir_simple(self):
        """
        to_fhir should convert to a Fhir Resource
        """
        inst = models.BetterBaseMixinModel()
        inst_as_fhir = inst.to_fhir()
        self.assertIsInstance(inst_as_fhir, Patient)
        self.assertEquals(
            inst_as_fhir.as_json(),
            {
                "active": True,
                "name": [{"family": "sponge", "given": ["bob"]}],
                "resourceType": "Patient",
            },
        )

    def test_to_fhir_with_elements(self):
        """
        to_fhir should convert to a Fhir Resource, containing only the attributes specified in elements
        """
        from fhirball.server.requestparser import parse_url
        q = parse_url('Patient?_elements=active,name')

        inst = models.BetterBaseMixinModel()
        inst_as_fhir = inst.to_fhir(query=q)
        self.assertEquals(
            inst_as_fhir.as_json(),
            {
                "active": True,
                "name": [{"family": "sponge", "given": ["bob"]}],
                "resourceType": "Patient",
            },
        )

        q = parse_url('Patient?_elements=active')
        inst_as_fhir = inst.to_fhir(query=q)
        self.assertEquals(
            inst_as_fhir.as_json(),
            {
                "active": True,
                "resourceType": "Patient",
            },
        )


class TestBaseModelMixin(unittest.TestCase):
    def test_searchables(self):
        """
        searchables() should return a dictionary containing the name of the attribute and the search function
        """
        inst = models.WithSearcher()
        searchables = inst.searchables()
        self.assertEquals(
            searchables, {"name": models.WithSearcher.FhirMap.search_name}
        )

    def test_searchables_empty(self):
        """
        searchables() should return an empty dictionary if no searchables are found
        """
        inst = models.BaseMixinModel()
        searchables = inst.searchables()
        self.assertEquals(searchables, {})

    def test_searchables_regex(self):
        """
        searchables() should return a dictionary containing the search_regex of the
        attribute and the search function if search_regex is provided
        """
        inst = models.WithSearcherAndRegex()
        searchables = inst.searchables()
        self.assertEquals(
            searchables,
            {"(name|NAME)": models.WithSearcherAndRegex.FhirMap.search_name},
        )

    def test_has_searcher(self):
        """
        has_searcher() should return True if an attribute with the given name is searchable and False if it is not
        """
        inst = models.WithSearcher()
        self.assertEquals(inst.has_searcher("name"), True)
        self.assertEquals(inst.has_searcher("NAME"), False)

    def test_has_searcher_regex(self):
        """
        has_searcher() should return True if an attribute with search_regex matches the given name is searchable and False if not
        """
        inst = models.WithSearcherAndRegex()
        self.assertEquals(inst.has_searcher("name"), True)
        self.assertEquals(inst.has_searcher("NAME"), True)
        self.assertEquals(inst.has_searcher("NaMe"), False)

    def test_get_searcher(self):
        """
        get_searcher() should return the search function if the name matches or raise
        """
        inst = models.WithSearcher()
        self.assertEquals(
            inst.get_searcher("name"), models.WithSearcher.FhirMap.search_name
        )
        with self.assertRaises(AttributeError):
            inst.get_searcher("NAME")

    def test_get_searcher_regex(self):
        """
        get_searcher() should return the search function if the name matches or raise
        """
        inst = models.WithSearcherAndRegex()
        self.assertEquals(
            inst.get_searcher("name"), models.WithSearcherAndRegex.FhirMap.search_name
        )
        self.assertEquals(
            inst.get_searcher("NAME"), models.WithSearcherAndRegex.FhirMap.search_name
        )
        with self.assertRaises(AttributeError):
            inst.get_searcher("NaMe")

    def test_Fhir_property(self):
        """
        The first time model.Fhir is accessed, it should create a ._Fhir singleton
        """
        inst = models.BaseMixinModel()
        self.assertFalse(hasattr(inst, "_Fhir"))
        inst.Fhir
        self.assertTrue(hasattr(inst, "_Fhir"))
        self.assertTrue(hasattr(inst.Fhir, "_model"))
        self.assertTrue(hasattr(inst.Fhir, "_properties"))
