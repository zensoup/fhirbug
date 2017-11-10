'''
Load all classes defined inside the Resources package
and export them via the resources namespace.
'''
import os
import importlib
import inspect

from fhirball.Fhir import resources

dir = os.path.dirname(__file__)
for module_file in os.listdir(os.path.join(dir, 'Resources')):
    if module_file != '__init__.py' and module_file[-3:] == '.py':
        module_name = module_file[:-3]
        # TODO I would like this path to be dynamically retrieved but now is not the time
        module = importlib.import_module('fhirball.Fhir.Resources.' + module_name)
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for cls_name, cls in clsmembers:
          setattr(resources, cls_name, cls)

# Import extensions
ext_module = importlib.import_module('fhirball.Fhir.Resources.extensions')
clsmembers = inspect.getmembers(ext_module, inspect.isclass)
for cls_name, cls in clsmembers:
  setattr(resources, cls_name, cls)
