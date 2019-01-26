import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch, Mock
from fhirbug.server.requestparser import parse_url, split_join
from fhirbug.server.requesthandlers import AbstractRequestHandler
from fhirbug.exceptions import QueryValidationError, OperationError, ConfigurationError


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
                self.assertEqual(e.status_code, 400)

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
                self.assertEqual(e.status_code, 500)

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
            self.assertEqual(e.status_code, 404)

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
            self.assertEqual(e.status_code, 403)
            self.assertEqual(e.diagnostics, AuditEventMock.outcomeDesc)
