import importlib
from fhirbug.exceptions import ConfigurationError
from fhirbug.config.utils import LazySettings


settings = LazySettings()

def import_models():
    """
    Dynamic import of the models module based on the backend selected in the configuration
    """
    global settings
    if not settings:
        raise ConfigurationError('Fhirbug settings have not been initialized. Use fhirbug.config.configure before using fhirbug.')
    try:
        models_path = getattr(settings, 'MODELS_PATH')
    except AttributeError:
        raise ConfigurationError('settings.MODELS_PATH has not been defined.')
    return importlib.import_module(models_path)

def import_searches():
    """
    Dynamic import of the searches module based on the backend selected in the configuration
    """
    global settings
    if not settings:
        raise ConfigurationError('Fhirbug settings have not been initialized. Use fhirbug.config.configure before using fhirbug.')
    try:
        db_backend = getattr(settings, 'DB_BACKEND')
    except AttributeError:
        raise ConfigurationError('settings.DB_BACKEND has not been defined.')

    if db_backend.lower() == 'sqlalchemy':
          return importlib.import_module('fhirbug.db.backends.SQLAlchemy.searches')
    elif db_backend.lower() == 'djangoorm':
        return importlib.import_module('fhirbug.db.backends.DjangoORM.searches')
    elif db_backend.lower() == 'pymodm':
        return importlib.import_module('fhirbug.db.backends.pymodm.searches')
