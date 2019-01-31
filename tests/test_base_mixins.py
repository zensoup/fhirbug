import unittest
from unittest.mock import Mock, patch, call
from types import SimpleNamespace
from fhirbug.config import settings

if settings.is_configured():
    settings._reset()
settings.configure(
    {"DB_BACKEND": "SQLAlchemy", "SQLALCHEMY_CONFIG": {"URI": "sqlite:///memory"}}
)
from . import models
from fhirbug.constants import AUDIT_SUCCESS, AUDIT_MINOR_FAILURE
from fhirbug.Fhir.resources import Patient, Observation
from fhirbug.exceptions import (
    AuthorizationError,
    DoesNotExistError,
    MappingValidationError,
)
from fhirbug.models.mixins import (
    FhirAbstractBaseMixin,
    FhirBaseModelMixin,
    get_pagination_info,
)


class TestAbstractBaseMixin(unittest.TestCase):
    def test_get_resource_cls(self):
        cls = models.BaseMixinModel._get_resource_cls()
        self.assertEqual(cls, Patient)

        del(models.BaseMixinModel.__Resource__)
        with self.assertRaises(AttributeError):
            cls = models.BaseMixinModel._get_resource_cls()


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
            inst.get_params_dict(Patient, ["active", "name"]),
            {"active": True, "name": "hello"},
        )
        self.assertEquals(inst.get_params_dict(Patient, ["active"]), {"active": True})
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
        from fhirbug.server.requestparser import parse_url

        q = parse_url("Patient?_elements=active,name")

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

        q = parse_url("Patient?_elements=active")
        inst_as_fhir = inst.to_fhir(query=q)
        self.assertEquals(
            inst_as_fhir.as_json(), {"active": True, "resourceType": "Patient"}
        )

    @patch("fhirbug.models.mixins.import_models")
    def test_rev_includes(self, import_modelsMock):
        from fhirbug.server.requestparser import parse_url

        itemMock = Mock()

        searcherMock = Mock()
        searcherMock().all = Mock(return_value=[itemMock])
        import_modelsMock().Observation.searchables = Mock(
            return_value={"subject": searcherMock}
        )

        q = parse_url("Patient?_revinclude=Observation:subject")
        model = FhirAbstractBaseMixin()
        model.Fhir = Mock()
        model._contained_items = []

        model.get_rev_includes(q)

        searcherMock.assert_called_with(
            import_modelsMock().Observation,
            "subject",
            model.Fhir.id,
            import_modelsMock().Observation._get_orm_query(),
            q,
        )
        self.assertEqual(model._contained_items, [itemMock.to_fhir()])


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


class TestCRUDMethods(unittest.TestCase):
    def test_update_from_resource(self):
        """
        When _update_from_resource(resource) is called on an instance,
        its fields should be updated and inst._after_update should be called with the instance as a parameter
        """
        _after_update_mock = models.MixinModelWithSetters_after_update
        inst = models.MixinModelWithSetters()
        resource = SimpleNamespace(active=False)
        inst.update_from_resource(resource)

        self.assertEquals(inst._active, False)
        self.assertEquals(inst.Fhir.active, False)
        _after_update_mock.assert_called_with(inst)

    def test_update_with_auditing(self):
        """
        When calling update_from_resource, if the class has a method called `audit_update`, the method should be called
        """
        inst = models.MixinModelWithSettersAndAuditing()
        resource = SimpleNamespace(active=False)
        query = "query"

        # Update should be successfull if the AuditEvent has outcome = fhirbug.constants.AUDIT_SUCCESS
        inst.update_from_resource(resource, query=query)
        models.Auditing_audit_update_success.assert_called_with(query)

        # If the AuditEvent has outcome != fhirbug.constants.AUDIT_SUCCESS, it should throw an AuthorizationError
        models.MixinModelWithSettersAndAuditing.audit_update = (
            models.Auditing_audit_update_failure
        )
        inst = models.MixinModelWithSettersAndAuditing()
        with self.assertRaises(AuthorizationError):
            inst.update_from_resource(resource, query=query)

    def test_update_with_protected_attributes(self):
        """
        When the auditing method makes a call to ``self.protect_attributes()``, the protected values should not change
        """
        from fhirbug.Fhir.resources import HumanName

        inst = models.MixinModelWithSettersAndAuditingProtected()
        resource = SimpleNamespace(
            active=False, name=HumanName(family="Family name", given="Given name")
        )
        inst.update_from_resource(resource)

        # Name should have changed
        self.assertEquals(
            inst.Fhir.name.as_json(), {"family": "Family name", "given": ["Given name"]}
        )

        # Active should not have changed
        self.assertEquals(inst.Fhir.active, None)

    def test_update_with_hidden_attributes(self):
        """
        When the auditing method makes a call to ``self.hide_attributes()``, the values should change but the attributes
        should not be returned
        """
        from fhirbug.Fhir.resources import HumanName

        inst = models.MixinModelWithSettersAndAuditingProtected()
        inst.audit_update = inst.audit_update2
        resource = SimpleNamespace(
            active=False, name=HumanName(family="Family name", given="Given name")
        )
        inst.update_from_resource(resource)

        self.assertEqual(
            inst.to_fhir().as_json(),
            {
                "name": [{"family": "Family name", "given": ["Given name"]}],
                "resourceType": "Patient",
            },
        )

        # Name should have changed
        self.assertEqual(
            inst.Fhir.name.as_json(), {"family": "Family name", "given": ["Given name"]}
        )

        # Active should not have changed
        self.assertEqual(inst.Fhir.active, False)

    def test_create_from_resource(self):
        """
        When _create_from_resource(resource) is called on an instance,
        its fields should be updated and inst._after_update should be called with the instance as a parameter
        """
        from fhirbug.Fhir.resources import HumanName

        _after_create_mock = models.MixinModelWithSetters_after_create
        cls = models.MixinModelWithSetters
        resource = SimpleNamespace(
            active=False, name=HumanName(family="family name", given="given name")
        )
        inst = cls.create_from_resource(resource)

        self.assertEqual(inst._active, False)
        self.assertEqual(inst.Fhir.active, False)
        self.assertEqual(
            inst._name.as_json(), {"family": "family name", "given": ["given name"]}
        )
        _after_create_mock.assert_called_with(inst)

    def test_create_with_auditing(self):
        """
        When calling create_from_resource, if the class has a method called `audit_create`, the method should be called
        """
        from fhirbug.Fhir.resources import HumanName

        _after_create_mock = models.Auditing_after_create
        _audit_create_mock = models.Auditing_audit_create_success
        cls = models.MixinModelWithSettersAndAuditing

        resource = SimpleNamespace(
            active=False, name=HumanName(family="family_name", given="given_name")
        )
        query = unittest.mock.Mock()

        # If auditing is successful an instance should be created
        inst = cls.create_from_resource(resource, query)
        # After creat should be properly called
        _after_create_mock.assert_called_with(inst)
        self.assertEqual(
            inst._name.as_json(), {"family": "family_name", "given": ["given_name"]}
        )
        # The audit_method should have been called with the query as a parameter
        _audit_create_mock.assert_called_with(query)

        _after_create_mock.reset_mock()
        cls.audit_create = models.Auditing_audit_create_failure
        with self.assertRaises(AuthorizationError):
            inst = cls.create_from_resource(resource, query)
        _after_create_mock.assert_not_called()

    def test_create_with_protected_attributes(self):
        """
        When the auditing method makes a call to ``self.protect_attributes()``, the protected values should not be set
        """
        from fhirbug.Fhir.resources import HumanName

        cls = models.MixinModelWithSettersAndAuditingProtected
        resource = SimpleNamespace(
            active=False, name=HumanName(family="fam", given="giv")
        )

        inst = cls.create_from_resource(resource)
        self.assertEqual(inst._active, None)
        self.assertEqual(inst.Fhir.name.as_json(), {"family": "fam", "given": ["giv"]})

    def test_delete_item(self):
        """
        When calling cls.delete_item, the call should be forwarded to cls._delete_item to handle backend specific tasks
        """
        cls = models.DeletableMixinModel
        inst = cls()
        query = unittest.mock.Mock()
        cls.delete_item(inst, query)
        models.DeletableMixinModel_delete_method.assert_called_with(cls, inst)

    def test_delete_with_auditing(self):
        """
        cls.delete_item should be audited when ``audit_delete`` is implemented
        """
        audit_success_mock = models.Auditing_audit_delete_success
        audit_fail_mock = models.Auditing_audit_delete_failure

        cls = models.DeletableMixinModelAudited
        inst = cls()
        query = unittest.mock.Mock()

        # With success auditor
        cls.delete_item(inst, query)
        models.DeletableMixinModelAudited_delete_method.assert_called_with(cls, inst)
        audit_success_mock.assert_called_with(query)

        # With failure auditor
        models.DeletableMixinModelAudited_delete_method.reset_mock()
        cls.audit_delete = audit_fail_mock

        with self.assertRaises(AuthorizationError):
            cls.delete_item(inst, query)
        audit_fail_mock.assert_called_with(query)
        models.DeletableMixinModelAudited_delete_method.assert_not_called()


class TestGetMethodSingleItem(unittest.TestCase):
    def test_get_single_item(self):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        cls = FhirBaseModelMixin
        queryMock = Mock()
        cls._get_item_from_pk = Mock()
        del (cls._get_item_from_pk().audit_read)

        res = cls.get(queryMock)
        cls._get_item_from_pk.assert_called_with(queryMock.resourceId)
        self.assertEqual(res, cls._get_item_from_pk().to_fhir().as_json())

    def test_get_single_item_audit(self):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        cls = FhirBaseModelMixin
        queryMock = Mock()
        cls._get_item_from_pk = Mock()
        cls._get_item_from_pk().audit_read = Mock(
            return_value=SimpleNamespace(outcome=AUDIT_SUCCESS)
        )

        res = cls.get(queryMock)
        cls._get_item_from_pk.assert_called_with(queryMock.resourceId)
        cls._get_item_from_pk().audit_read.assert_called_with(queryMock)
        self.assertEqual(res, cls._get_item_from_pk().to_fhir().as_json())

    def test_get_single_item_audit_fail(self):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        cls = FhirBaseModelMixin
        queryMock = Mock()
        cls._get_item_from_pk = Mock()
        cls._get_item_from_pk().audit_read = Mock(
            return_value=SimpleNamespace(outcome=AUDIT_MINOR_FAILURE)
        )

        with self.assertRaises(AuthorizationError) as e:
            res = cls.get(queryMock)
        cls._get_item_from_pk.assert_called_with(queryMock.resourceId)

    def test_get_single_item_does_not_exist(self):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        cls = FhirBaseModelMixin
        queryMock = Mock()
        cls._get_item_from_pk = Mock(side_effect=DoesNotExistError)

        with self.assertRaises(MappingValidationError) as e:
            res = cls.get(queryMock)
        cls._get_item_from_pk.assert_called_with(queryMock.resourceId)


class TestPaginationInfo(unittest.TestCase):
    def test_from_query(self):
        """
        If ``_count`` and ``search-offset``  have been provided in the query
        use those
        """
        from fhirbug.server.requestparser import FhirRequestQuery

        query = FhirRequestQuery("resource", modifiers={"_count": [69]})
        page, count, next_offset, prev_offset = get_pagination_info(query)
        self.assertEqual((page, count, next_offset, prev_offset), (1, 69, 70, 1))

        query = FhirRequestQuery(
            "resource",
            modifiers={"_count": [69]},
            search_params={"search-offset": [70]},
        )
        page, count, next_offset, prev_offset = get_pagination_info(query)
        self.assertEqual((page, count, next_offset, prev_offset), (2, 69, 139, 1))

    @patch("fhirbug.models.mixins.settings")
    def test_defaults(self, settingsMock):
        """
        If no options have been provided in the query or the settings load the defaults
        """
        from fhirbug.server.requestparser import FhirRequestQuery

        settingsMock.DEFAULT_BUNDLE_SIZE = 18
        settingsMock.MAX_BUNDLE_SIZE = 20

        query = FhirRequestQuery("resource")
        page, count, next_offset, prev_offset = get_pagination_info(query)
        self.assertEqual((page, count, next_offset, prev_offset), (1, 18, 19, 1))

        query = FhirRequestQuery(
            "resource",
            modifiers={"_count": [69]},
            search_params={"search-offset": [70]},
        )
        page, count, next_offset, prev_offset = get_pagination_info(query)
        self.assertEqual((page, count, next_offset, prev_offset), (4, 20, 90, 50))


@patch("fhirbug.models.mixins.get_pagination_info", return_value=(1, 2, 3, 4))
@patch("fhirbug.models.mixins.generate_query_string", return_value="mock")
@patch("fhirbug.models.mixins.PaginatedBundle")
class TestGetMethodBundledItems(unittest.TestCase):
    def test_bundle(
        self, paginatedBundleMock, generate_query_stringMock, get_pagination_infoMock
    ):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        from fhirbug.server.requestparser import FhirRequestQuery

        query = FhirRequestQuery("resource")
        cls = FhirBaseModelMixin
        cls._get_orm_query = Mock()
        cls.paginate = Mock()
        cls.paginate().items = [Mock(), Mock()]

        res = cls.get(query)

        get_pagination_infoMock.assert_called_with(query)
        cls.paginate.assert_called_with(cls._get_orm_query(), 1, 2)
        generate_query_stringMock.assert_called_with(query)

        paginatedBundleMock.assert_called_with(
            pagination={
                "items": [],
                "total": cls.paginate().total,
                "pages": cls.paginate().pages,
                "has_next": cls.paginate().has_next,
                "has_previous": cls.paginate().has_previous,
                "next_page": "FhirBaseModelMixin/?_count=2&search-offset=3mock",
                "previous_page": "FhirBaseModelMixin/?_count=2&search-offset=4mock",
            }
        )
        self.assertEqual(res, paginatedBundleMock().as_json())

    def test_bundle_with_searches(
        self, paginatedBundleMock, generate_query_stringMock, get_pagination_infoMock
    ):
        """ If the provided query object contains a resource_id, it should call
        ``_get_item_from_pk`` for that id and return the result in json form
        """
        from fhirbug.server.requestparser import FhirRequestQuery

        query = FhirRequestQuery("resource", search_params={"one": [1], "two": [2, 3]})
        cls = FhirBaseModelMixin
        cls._get_orm_query = Mock()
        cls.paginate = Mock()
        cls.paginate().items = [Mock(), Mock()]

        cls.has_searcher = Mock(return_value=True)
        cls.get_searcher = Mock()

        res = cls.get(query)

        cls.get_searcher.assert_has_calls(
            [
                call("one"),
                call()(cls, "one", 1, cls._get_orm_query(), query),
                call("two"),
                call()(cls, "two", 2, cls.get_searcher()(), query),
                call("two"),
                call()(cls, "two", 3, cls.get_searcher()(), query),
            ]
        )

        get_pagination_infoMock.assert_called_with(query)
        cls.paginate.assert_called_with(cls.get_searcher()(), 1, 2)
        generate_query_stringMock.assert_called_with(query)

        paginatedBundleMock.assert_called_with(
            pagination={
                "items": [],
                "total": cls.paginate().total,
                "pages": cls.paginate().pages,
                "has_next": cls.paginate().has_next,
                "has_previous": cls.paginate().has_previous,
                "next_page": "FhirBaseModelMixin/?_count=2&search-offset=3mock",
                "previous_page": "FhirBaseModelMixin/?_count=2&search-offset=4mock",
            }
        )
