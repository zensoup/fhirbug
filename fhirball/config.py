import importlib
from types import SimpleNamespace

from fhirball.exceptions import ConfigurationError


class FhirSettings:
    pass

settings = None

def configure_from_path(path):
    global settings
    if not settings:
        settings = FhirSettings()
    try:
        settings_module = importlib.import_module(path)
    except Exception as e:
        print(e)
    for key in dir(settings_module):
        if not key.startswith('__'):
            setattr(settings, key, getattr(settings_module, key))

def configure_from_dict(dict):
    global settings
    if not settings:
        settings = FhirSettings()
    for key, value in dict.items():
        setattr(settings, key, value)
    return settings

def configure(config):
    if isinstance(config, str):
        return configure_from_path(config)
    if isinstance(config, dict):
        return configure_from_dict(config)
    raise ConfigurationError('Invlid configuration object, you must provide a dict or string representing the path to a configuration file')

def import_models():
    global settings
    if not settings:
        raise ConfigurationError('Fhirball settings have not been initialized. Use fhirball.config.configure before using fhirball.')
    try:
        models_path = getattr(settings, 'MODELS_PATH')
    except AttributeError:
        raise ConfigurationError('settings.MODELS_PATH has not been defined.')
    return importlib.import_module(models_path)

def import_searches():
    global settings
    if not settings:
        raise ConfigurationError('Fhirball settings have not been initialized. Use fhirball.config.configure before using fhirball.')
    try:
        db_backend = getattr(settings, 'DB_BACKEND')
    except AttributeError:
        raise ConfigurationError('settings.DB_BACKEND has not been defined.')

    if db_backend.lower() == 'sqlalchemy':
          return importlib.import_module('fhirball.db.backends.SQLAlchemy.searches')
    elif db_backend.lower() == 'djangoorm':
        return importlib.import_module('fhirball.db.backends.DjangoORM.searches')
