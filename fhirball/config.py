import importlib
import settings


def import_models():
    return importlib.import_module(settings.models_path)
