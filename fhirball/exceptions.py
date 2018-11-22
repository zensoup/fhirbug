class QueryValidationError(Exception):
    '''
    A http request query was malformed or not understood by the server
    '''
    pass


class MappingValidationError(Exception):
    '''
    A fhir mapping has been set up wrong
    '''
    pass


class ConfigurationError(Exception):
    '''
    Something is wrong with the settings
    '''
    pass

class InvalidOperationError(Exception):
    '''
    The requested opertion is not valid
    '''
    pass

class UnsupportedOperationError(Exception):
    '''
    The requested opertion is not supported by this server
    '''
    pass

class MappingException(Exception):
    '''
    A fhir mapping received data that was not correct
    '''
    pass
