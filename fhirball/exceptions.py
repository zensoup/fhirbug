class QueryValidationError(Exception):
    pass


class MappingValidationError(Exception):
    pass


class ConfigurationException(Exception):
    '''
    Something is wrong with the settings
    '''
    pass
