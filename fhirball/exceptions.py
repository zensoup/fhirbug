class DoesNotExistError(Exception):
    """
    A http request query was malformed or not understood by the server
    """

    def __init__(self, pk=None, resource_type=None):
        self.pk = pk
        self.resource_type = resource_type


class QueryValidationError(Exception):
    """
    A http request query was malformed or not understood by the server
    """

    pass


class MappingValidationError(Exception):
    """
    A fhir mapping has been set up wrong
    """

    pass


class ConfigurationError(Exception):
    """
    Something is wrong with the settings
    """

    pass


class InvalidOperationError(Exception):
    """
    The requested opertion is not valid
    """

    pass


class UnsupportedOperationError(Exception):
    """
    The requested opertion is not supported by this server
    """

    pass


class MappingException(Exception):
    """
    A fhir mapping received data that was not correct
    """

    pass


class OperationError(Exception):
    """
    An exception that happens during a requested operation that
    should be returned as an OperationOutcome to the user.
    """

    def __init__(
        self,
        severity="error",
        code="exception",
        diagnostics="",
        status_code=500,
    ):
        self.severity = severity
        self.code = code
        self.diagnostics = diagnostics
        self.status_code = status_code

    def to_fhir(self):
        from fhirball.Fhir.resources import OperationOutcome

        return OperationOutcome(
            {
                "issue": [
                    {
                        "severity": self.severity,
                        "code": self.code,
                        "diagnostics": self.diagnostics,
                    }
                ]
            }
        )
