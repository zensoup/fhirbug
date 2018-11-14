import importlib
import settings

from fhirball.exceptions import ConfigurationException


def import_models():
    try:
        models_path = getattr(settings, 'MODELS_PATH')
    except AttributeError:
        raise ConfigurationException('settings.MODELS_PATH has not been defined.')
    return importlib.import_module(models_path)

def import_searches():
    try:
        db_backend = getattr(settings, 'DB_BACKEND')
    except AttributeError:
        raise ConfigurationException('settings.DB_BACKEND has not been defined.')

    if db_backend.lower() == 'sqlalchemy':
          return importlib.import_module('fhirball.db.backends.SQLAlchemy.searches')
    elif db_backend.lower() == 'djangoorm':
        return importlib.import_module('fhirball.db.backends.DjangoORM.searches')
