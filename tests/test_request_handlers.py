import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch, Mock
from fhirbug.server.requestparser import parse_url, split_join
from fhirbug.server.requesthandlers import (
    AbstractRequestHandler,
    GetRequestHandler,
    PostRequestHandler,
    PutRequestHandler,
    DeleteRequestHandler,
)
from fhirbug.exceptions import (
    QueryValidationError,
    OperationError,
    ConfigurationError,
    AuthorizationError,
    MappingValidationError,
    DoesNotExistError,
)


class TestAbstractRequestHandler(unittest.TestCase):
    def test_parse_url_success(self):
        """
        parse_url should pass the url to ``requesthandlers.parse_url`` and assign the result
        to the handler instance as handler.query
        """
        with patch("fhirbug.server.requesthandlers.parse_url") as query:
            handler = AbstractRequestHandler()
            handler.parse_url("Patient")
            query.assert_called_with("Patient")
            self.assertEqual(handler.query, query())

    def test_parse_url_failure(self):
        """
        When ``requesthandlers.parse_url`` throws a QueryValidationError,
        it should throw an OperationError
        """
        mock_parser = Mock(side_effect=QueryValidationError)
        with patch(
            "fhirbug.server.requesthandlers.parse_url", new=mock_parser
        ) as query:
            handler = AbstractRequestHandler()
            with self.assertRaises(OperationError) as e:
                handler.parse_url("Patient")
            self.assertEqual(e.exception.status_code, 400)

    def test_import_models_success(self):
        """
        import_models should call ``fhirbug.config.import_models`` and return the result
        """
        with patch("fhirbug.server.requesthandlers.import_models") as importMock:
            handler = AbstractRequestHandler()
            models = handler.import_models()
            importMock.assert_called_once()
            self.assertEqual(models, importMock())

    def test_import_models_failure(self):
        """
        When ``fhirbug.config.import_models`` throws a ConfigurationError,
        it should throw an OperationError
        """
        mock_parser = Mock(side_effect=ConfigurationError)
        with patch(
            "fhirbug.server.requesthandlers.import_models", new=mock_parser
        ) as query:
            handler = AbstractRequestHandler()
            with self.assertRaises(OperationError) as e:
                handler.import_models()
            self.assertEqual(e.exception.status_code, 500)

    def test_get_resource_success(self):
        """
        get_resource should try to get the resource class from the imported models
        module and return it
        """
        handler = AbstractRequestHandler()
        query = SimpleNamespace(resource="Test")
        handler.query = query
        modelsMock = Mock()
        resource = handler.get_resource(modelsMock)
        self.assertEqual(resource, modelsMock.Test)

    def test_get_resource_failure(self):
        """
        When the specified resource does not exist in the models module, an
        OperationError should be thrown
        """
        handler = AbstractRequestHandler()
        query = SimpleNamespace(resource="Test")
        models = SimpleNamespace()
        handler.query = query
        with self.assertRaises(OperationError) as e:
            handler.get_resource(models)
        self.assertEqual(e.exception.status_code, 404)

    def test_log_request_success(self):
        """
        log_request should return a ``fhirbug.Fhir.resources.AuditEvent``
        """
        with patch("fhirbug.server.requesthandlers.AuditEvent") as AuditEventMock:
            with patch("fhirbug.server.requesthandlers.FHIRDate") as FHIRDateMock:
                handler = AbstractRequestHandler()
                audit_event = handler.log_request(
                    url="url",
                    status=200,
                    query=None,
                    method="GET",
                    time=datetime(2000, 2, 2),
                )
                AuditEventMock.assert_called_once()
                FHIRDateMock.assert_called_with(datetime(2000, 2, 2))

    def test__audit_request_notsetup(self):
        """
        _audit_request should do nothing if ``audit_request`` has not been implemented
        """
        handler = AbstractRequestHandler()
        handler._audit_request(Mock())

    def test__audit_request_success(self):
        """
        _audit_request should call ``audit_request`` if it is implemented and check
        if the ``outcome`` attribute of the return value is equal to "0"
        """
        handler = AbstractRequestHandler()
        queryMock = Mock()

        AuditEventMock = Mock()
        AuditEventMock.outcome = Mock()

        AuditEventMock.outcome.__ne__ = Mock(return_value=False)
        audit_requestMock = Mock(return_value=AuditEventMock)

        handler.audit_request = audit_requestMock

        handler._audit_request(queryMock)
        audit_requestMock.assert_called_with(queryMock)
        AuditEventMock.outcome.__ne__.assert_called_with("0")

    def test__audit_request_fail(self):
        """
        If the ``outcome`` attribute of the return value is not equal to "0", it
        should throw an OperationError containing info passed from the Audit event
        """
        handler = AbstractRequestHandler()
        queryMock = Mock()

        AuditEventMock = Mock()
        AuditEventMock.outcome = Mock()

        AuditEventMock.outcome.__ne__ = Mock(return_value=True)
        audit_requestMock = Mock(return_value=AuditEventMock)

        handler.audit_request = audit_requestMock

        with self.assertRaises(OperationError) as e:
            handler._audit_request(queryMock)
        self.assertEqual(e.exception.status_code, 403)
        self.assertEqual(e.exception.diagnostics, AuditEventMock.outcomeDesc)


class TestGetRequestHandler(unittest.TestCase):
    def test_fetch_items_success(self):
        handler = GetRequestHandler()
        mockQuery = Mock()
        handler.query = mockQuery
        modelMock = Mock()
        res = handler.fetch_items(modelMock)
        modelMock.get.assert_called_with(query=mockQuery)
        self.assertEqual(res, modelMock.get())

    def test_fetch_items_exceptions(self):
        handler = GetRequestHandler()
        mockQuery = Mock()
        handler.query = mockQuery

        modelMock = Mock()
        modelMock.get = Mock(side_effect=MappingValidationError)
        with self.assertRaises(OperationError) as e:
            res = handler.fetch_items(modelMock)
        self.assertEqual(e.exception.status_code, 404)

        modelMock = Mock()
        modelMock.get = Mock(side_effect=AuthorizationError(Mock()))
        with self.assertRaises(OperationError) as e:
            res = handler.fetch_items(modelMock)
        self.assertEqual(e.exception.status_code, 403)

        modelMock = Mock()
        modelMock.get = Mock(side_effect=Exception)
        with self.assertRaises(OperationError) as e:
            res = handler.fetch_items(modelMock)
        self.assertEqual(e.exception.status_code, 500)

        with patch("fhirbug.server.requesthandlers.settings") as settingsMock:
            modelMock = Mock()
            modelMock.get = Mock(side_effect=Exception)
            with self.assertRaises(OperationError) as e:
                res = handler.fetch_items(modelMock)
            self.assertEqual(e.exception.status_code, 500)
            self.assertTrue("Traceback" in e.exception.diagnostics)

    def test_handle_success(self):
        handler = GetRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.fetch_items = Mock()
        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock)

        handler.parse_url.assert_called_with(urlMock, None)
        handler._audit_request.assert_called_with(handler.query)
        handler.import_models.assert_called_once()
        handler.get_resource.assert_called_with(handler.import_models())
        handler.fetch_items.assert_called_with(handler.get_resource())
        handler.log_request.assert_called_once()

        self.assertEqual(ret, handler.fetch_items())
        self.assertEqual(status, 200)

    def test_handle_failure(self):
        handler = GetRequestHandler()
        handler.parse_url = Mock(side_effect=OperationError)
        handler.log_request = Mock()

        urlMock = Mock()
        contextMock = Mock()
        ret, status = handler.handle(urlMock, contextMock)

        handler.parse_url.assert_called_with(urlMock, contextMock)
        handler.log_request.assert_called_once()

        self.assertEqual(
            ret,
            {
                "issue": [
                    {"code": "exception", "diagnostics": "", "severity": "error"}
                ],
                "resourceType": "OperationOutcome",
            },
        )
        self.assertEqual(status, 500)


class TestPostRequestHandler(unittest.TestCase):
    def test_request_body_to_resource(self):
        handler = PostRequestHandler()
        handler.body = Mock()
        resourceClassMock = Mock()
        ret = handler.request_body_to_resource(resourceClassMock)

        self.assertEqual(ret, resourceClassMock(handler.body))

    def test_request_body_to_resource_failure(self):
        handler = PostRequestHandler()
        handler.body = Mock()
        resourceClassMock = Mock(side_effect=Exception)
        with self.assertRaises(OperationError) as e:
            ret = handler.request_body_to_resource(resourceClassMock)

        self.assertEqual(e.exception.status_code, 404)

    def test_create_success(self):
        handler = PostRequestHandler()
        handler.query = Mock()
        modelClassMock = Mock()
        resourceMock = Mock()

        ret = handler.create(modelClassMock, resourceMock)
        modelClassMock.create_from_resource.assert_called_with(
            resourceMock, query=handler.query
        )
        self.assertEqual(ret, modelClassMock.create_from_resource())

    def test_create_failure(self):
        handler = PostRequestHandler()
        handler.query = Mock()
        modelClassMock = Mock()
        modelClassMock.create_from_resource = Mock(side_effect=Exception)
        resourceMock = Mock()

        with patch("fhirbug.server.requesthandlers.settings") as settingsMock:
            with self.assertRaises(OperationError) as e:
                ret = handler.create(modelClassMock, resourceMock)

        self.assertEqual(e.exception.status_code, 422)

    @patch("fhirbug.Fhir.resources")
    def test_handle_success(self, resourcesMock):
        handler = PostRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.request_body_to_resource = Mock()
        handler.create = Mock()

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.parse_url.assert_called_with(urlMock, None)
        handler._audit_request.assert_called_with(handler.query)
        handler.import_models.assert_called_once()
        handler.get_resource.assert_called_with(resourcesMock)
        handler.create.assert_called_with(
            handler.get_resource(), handler.request_body_to_resource()
        )
        handler.log_request.assert_called_once()

        self.assertEqual(ret, handler.create().to_fhir().as_json())
        self.assertEqual(status, 201)

    def test_handle_failure(self):
        handler = PostRequestHandler()
        handler.query = Mock()
        handler.body = Mock()
        handler.parse_url = Mock(side_effect=OperationError)

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.log_request.assert_called_once()
        self.assertEqual(status, 500)


class TestPutRequestHandler(unittest.TestCase):
    def test_update(self):
        handler = PutRequestHandler()
        handler.query = Mock()
        instanceMock = Mock()
        resourceMock = Mock()
        ret = handler.update(instanceMock, resourceMock)
        instanceMock.update_from_resource.assert_called_with(
            resourceMock, query=handler.query
        )
        self.assertEqual(ret, instanceMock.update_from_resource())

    def test_update_failure(self):
        handler = PutRequestHandler()
        handler.query = Mock()
        instanceMock = Mock()
        instanceMock.update_from_resource = Mock(side_effect=Exception)
        resourceMock = Mock()
        with self.assertRaises(OperationError) as e:
            ret = handler.update(instanceMock, resourceMock)

        self.assertEqual(e.exception.status_code, 422)

    @patch("fhirbug.Fhir.resources")
    def test_handle_success(self, resourcesMock):
        handler = PutRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.request_body_to_resource = Mock()
        handler.update = Mock()

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.parse_url.assert_called_with(urlMock, None)
        handler._audit_request.assert_called_with(handler.query)
        handler.import_models.assert_called_once()
        handler.get_resource.assert_called_with(resourcesMock)
        handler.update.assert_called_with(
            handler.get_resource()._get_item_from_pk(),
            handler.request_body_to_resource(),
        )
        handler.log_request.assert_called_once()

        self.assertEqual(ret, handler.update().to_fhir().as_json())
        self.assertEqual(status, 202)

    def test_handle_failure(self):
        handler = PutRequestHandler()
        handler.query = Mock()
        handler.body = Mock()
        handler.parse_url = Mock(side_effect=OperationError)

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.log_request.assert_called_once()
        self.assertEqual(status, 500)

    def test_handle_not_found(self):
        handler = PutRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.get_resource()._get_item_from_pk = Mock(side_effect=DoesNotExistError)

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.log_request.assert_called_once()
        self.assertEqual(status, 404)
        self.assertEqual(
            ret,
            {
                "issue": [
                    {
                        "code": "not-found",
                        "diagnostics": "None/None was not found on the server.",
                        "severity": "error",
                    }
                ],
                "resourceType": "OperationOutcome",
            },
        )


class TestDeleteRequestHandler(unittest.TestCase):
    def test_handle(self):
        handler = DeleteRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.get_resource()._delete_item = Mock()
        handler.log_request = Mock()

        urlMock = Mock()
        query_context = Mock()
        ret, status = handler.handle(urlMock, query_context=query_context)

        handler.parse_url.assert_called_with(urlMock, query_context)
        handler._audit_request.assert_called_with(handler.query)
        handler.import_models.assert_called_once()
        handler.get_resource.assert_called_with(handler.import_models())
        handler.get_resource()._get_item_from_pk.assert_called_with(
            handler.query.resourceId
        )
        handler.log_request.assert_called_once()

        self.assertEqual(
            ret,
            {
                "issue": [
                    {
                        "code": "informational",
                        "details": {"text": "All ok"},
                        "severity": "information",
                    }
                ],
                "resourceType": "OperationOutcome",
            },
        )
        self.assertEqual(status, 200)

    def test_handle_not_found(self):
        handler = DeleteRequestHandler()
        handler.parse_url = Mock()
        handler.query = Mock()
        handler._audit_request = Mock()
        handler.import_models = Mock()
        handler.get_resource = Mock()
        handler.get_resource()._get_item_from_pk = Mock(side_effect=DoesNotExistError)

        handler.log_request = Mock()

        urlMock = Mock()
        ret, status = handler.handle(urlMock, Mock())

        handler.log_request.assert_called_once()
        self.assertEqual(status, 404)
        self.assertEqual(
            ret,
            {
                "issue": [
                    {
                        "code": "not-found",
                        "diagnostics": "None/None was not found on the server.",
                        "severity": "error",
                    }
                ],
                "resourceType": "OperationOutcome",
            },
        )
