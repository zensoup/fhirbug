'''
Load all classes defined inside the Resources package
and export them via the resources namespace.
'''
import os
import importlib
import inspect

from fhirbug.Fhir import resources
from fhirbug.config import settings

dir = os.path.dirname(__file__)
for module_file in os.listdir(os.path.join(dir, 'Resources')):
    if module_file != '__init__.py' and module_file[-3:] == '.py':
        module_name = module_file[:-3]
        # TODO I would like this path to be dynamically retrieved but now is not the time
        module = importlib.import_module('fhirbug.Fhir.Resources.' + module_name)
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for cls_name, cls in clsmembers:
          setattr(resources, cls_name, cls)

# Import internal extensions
int_module = importlib.import_module('fhirbug.Fhir.Resources.extensions')
clsmembers = inspect.getmembers(int_module, inspect.isclass)
for cls_name, cls in clsmembers:
  setattr(resources, cls_name, cls)

# Import external extensions
if hasattr(settings, 'EXTENSIONS_PATH'):
    ext_module = importlib.import_module(settings.EXTENSIONS_PATH)
    clsmembers = inspect.getmembers(ext_module, inspect.isclass)
    for cls_name, cls in clsmembers:
        setattr(resources, cls_name, cls)
