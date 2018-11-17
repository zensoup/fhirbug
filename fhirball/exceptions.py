class QueryValidationError(Exception):
    pass


class MappingValidationError(Exception):
    pass


class ConfigurationError(Exception):
    '''
    Something is wrong with the settings
    '''
    pass
