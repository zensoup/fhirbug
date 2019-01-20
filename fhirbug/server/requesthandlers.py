import threading
import traceback

from fhirbug.server.requestparser import parse_url
from fhirbug.exceptions import (
    MappingValidationError,
    QueryValidationError,
    ConfigurationError,
    OperationError,
    DoesNotExistError,
    AuthorizationError,
)

from fhirbug.Fhir.resources import OperationOutcome, FHIRValidationError
from fhirbug.config import import_models, settings


ctx = threading.local()

def register_request_context(context):
    ctx.context = context

def get_request_context():
    return getattr(ctx, 'context', None)


class AbstractRequestHandler:
    """
    Base class for request handlers
    """

    def parse_url(self, url, context=None):
        try:
            self.query = parse_url(url)
            self.query.context = context
            register_request_context(self.query)
        except QueryValidationError as e:
            raise OperationError(
                severity="error",
                code="invalid",
                diagnostics="{}".format(e),
                status_code=400,
            )

    def import_models(self):
        try:
            models = import_models()
        except ConfigurationError:
            raise OperationError(
                severity="error",
                code="exception",
                diagnostics="The server is improprly configured",
                status_code=500,
            )
        return models

    def get_resource(self, models):
        resource_name = self.query.resource
        try:
            # TODO: handle mapper names different then the resource
            # Maybe a dict in the settings?
            Resource = getattr(models, resource_name)
        except AttributeError:
            raise OperationError(
                severity="error",
                code="not-found",
                diagnostics=f'Resource "{resource_name}" does not exist.',
                status_code=404,
            )
        return Resource

    def _audit_request(self, query):
        if hasattr(self, "audit_request"):
            auditEvent = self.audit_request(query)
            if auditEvent.outcome != "0":
                raise OperationError(
                    severity="error",
                    code="security",
                    diagnostics=getattr(auditEvent, "outcomeDesc", None),
                    status_code=403,
                )


class GetRequestHandler(AbstractRequestHandler):
    """
    Receive a request url as a string and handle it. This includes parsing the string into a
    :class:`fhirbug.server.requestparser.FhirRequestQuery`, finding the model for the requested
    resource and calling `Resource.get` on it.
    It returns a tuple (response json, status code).
    If an error occurs during the process, an OperationOutcome is returned.

    :param url: a string containing the path of the request. It should not contain the server
                path. For example: `Patients/123?name:contains=Jo`

    :returns: A tuple ``(response json, status code)`` where response_json may be the requested resource,
              a Bundle or an OperationOutcome in case of an error.
    :rtype: tuple

    """

    def handle(self, url, query_context=None):
        try:
            self.parse_url(url, query_context)
            # Authorize the request if implemented
            self._audit_request(self.query)
            # Import the model mappings
            models = self.import_models()
            # Get the Resource
            Model = self.get_resource(models)

            # Audit the request if needed

            return self.fetch_items(Model)

        except OperationError as e:
            return e.to_fhir().as_json(), e.status_code

    def fetch_items(self, Model):
        # Try to fetch the requested resource(s)
        try:
            res = Model.get(query=self.query)
            return res, 200
        except (MappingValidationError, FHIRValidationError) as e:
            raise OperationError(
                severity="error",
                code="not-found",
                diagnostics="{}".format(e),
                status_code=404,
            )
        except AuthorizationError as e:
            raise OperationError(
                severity="error",
                code="security",
                diagnostics="{}".format(e.auditEvent.as_json()),
                status_code=500,
            )
        except Exception as e:
            diag = "{}".format(e)
            if settings.DEBUG:
                tb = traceback.format_exc()
                diag += " {}".format(tb)
            raise OperationError(
                severity="error",
                code="exception",
                diagnostics="{}".format(diag),
                status_code=500,
            )


class PostRequestHandler(AbstractRequestHandler):
    """
    Receive a request url and the request body of a POST request and handle it. This includes parsing the string into a
    :class:`fhirbug.server.requestparser.FhirRequestQuery`, finding the model for the requested
    resource and creating a new instance.
    It returns a tuple (response json, status code).
    If an error occurs during the process, an OperationOutcome is returned.

    :param url: a string containing the path of the request. It should not contain the server
                path. For example: `Patients/123?name:contains=Jo`
    :type url: string
    :param body: a dictionary containing all data that was sent with the request
    :type body: dict

    :returns: A tuple ``(response_json, status code)``, where response_json may be the requested resource,
              a Bundle or an OperationOutcome in case of an error.
    :rtype: tuple

    """

    def handle(self, url, body, query_context=None):
        try:
            self.body = body
            self.parse_url(url, query_context)
            # Import the model mappings
            models = self.import_models()
            # Get the Model class
            Model = self.get_resource(models)

            from fhirbug.Fhir import resources

            # Get the Resource class
            Resource = self.get_resource(resources)
            # Validate the incoming json and instantiate the Fhir resource
            resource = self.request_body_to_resource(Resource)

            created_resource = self.create(Model, resource)
            return created_resource.to_fhir().as_json(), 201

        except OperationError as e:
            return e.to_fhir().as_json(), e.status_code

    def request_body_to_resource(self, Resource):
        # Validate the incoming json
        try:
            resource = Resource(self.body)
            return resource
        except Exception as e:
            raise OperationError(
                severity="error",
                code="value",
                diagnostics="{}".format(e),
                status_code=404,
            )

    def create(self, Model, resource):
        try:
            new_resource = Model.create_from_resource(resource, query=self.query)
        except Exception as e:
            diag = "{}".format(e)
            if settings.DEBUG:
                tb = traceback.format_exc()
                diag += " {}".format(tb)
            raise OperationError(
                severity="error",
                code="invalid",
                diagnostics="{}".format(diag),
                status_code=422,
            )
        return new_resource


class PutRequestHandler(PostRequestHandler):
    """
    Receive a request url and the request body of a POST request and handle it. This includes parsing the string into a
    :class:`fhirbug.server.requestparser.FhirRequestQuery`, finding the model for the requested
    resource and creating a new instance.
    It returns a tuple (response json, status code).
    If an error occurs during the process, an OperationOutcome is returned.

    :param url: a string containing the path of the request. It should not contain the server
                path. For example: `Patients/123?name:contains=Jo`
    :type url: string
    :param body: a dictionary containing all data that was sent with the request
    :type body: dict

    :returns: A tuple ``(response_json, status code)``, where response_json may be the requested resource,
              a Bundle or an OperationOutcome in case of an error.
    :rtype: tuple

    """

    def handle(self, url, body, query_context=None):
        try:
            self.body = body
            self.parse_url(url, query_context)
            # Import the model mappings
            models = self.import_models()
            # Get the Model class
            Model = self.get_resource(models)

            try:
                instance = Model._get_item_from_pk(self.query.resourceId)
            except DoesNotExistError as e:
                raise OperationError(
                    severity="error",
                    code="not-found",
                    diagnostics="{}/{} was not found on the server.".format(
                        e.resource_type, e.pk
                    ),
                    status_code=404,
                )

            from fhirbug.Fhir import resources

            # Get the Resource class
            Resource = self.get_resource(resources)
            # Validate the incoming json and instantiate the Fhir resource
            resource = self.request_body_to_resource(Resource)

            updated_resource = self.update(instance, resource)
            return updated_resource.to_fhir().as_json(), 202

        except OperationError as e:
            return e.to_fhir().as_json(), e.status_code

    def update(self, instance, resource):
        try:
            updated_resource = instance.update_from_resource(resource, query=self.query)
        except Exception as e:
            diag = "{}".format(e)
            if settings.DEBUG:
                tb = traceback.format_exc()
                diag += " {}".format(tb)
            raise OperationError(
                severity="error",
                code="invalid",
                diagnostics="{}".format(diag),
                status_code=422,
            )
        return updated_resource


class DeleteRequestHandler(AbstractRequestHandler):
    """
    Receive a request url and the request body of a DELETE request and handle it. This includes parsing the string into a
    :class:`fhirbug.server.requestparser.FhirRequestQuery`, finding the model for the requested
    resource and deleting it.
    It returns a tuple (response json, status code).
    If an error occurs during the process, an OperationOutcome is returned.

    :param url: a string containing the path of the request. It should not contain the server
                path. For example: `Patients/123?name:contains=Jo`
    :type url: string

    :returns: A tuple ``(response_json, status code)``, where response_json may be the requested resource,
              a Bundle or an OperationOutcome in case of an error.
    :rtype: tuple

    """

    def handle(self, url, query_context=None):
        try:
            self.parse_url(url, query_context)
            # Authorize the request if implemented
            self._audit_request(self.query)
            # Import the model mappings
            models = self.import_models()
            # Get the Resource
            Model = self.get_resource(models)

            try:
                instance = Model._get_item_from_pk(self.query.resourceId)
            except DoesNotExistError as e:
                raise OperationError(
                    severity="error",
                    code="not-found",
                    diagnostics="{}/{} was not found on the server.".format(
                        e.resource_type, e.pk
                    ),
                    status_code=404,
                )

            Model._delete_item(instance)

        except OperationError as e:
            return e.to_fhir().as_json(), e.status_code

        return (
            OperationOutcome(
                issue={
                    "severity": "information",
                    "code": "informational",
                    "details": {"text": "All ok"},
                }
            ).as_json(),
            200,
        )
