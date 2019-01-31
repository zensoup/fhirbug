import re
import sys
from pathlib import Path
from generate_ref_types import generate

try:
    from fhirbug.Fhir import resources
except ModuleNotFoundError:
    # Allow execution from a git clone without having fhirball installed.
    if Path('./fhirbug').is_dir(): # Executed from the example's directory`
        sys.path.append("./")
    elif Path('../../fhirbug').is_dir(): # Executed from the project's root directory`
        sys.path.append("../../")
    from fhirbug.Fhir import resources


# Unfortunately, information on the possible types of related resources
# is not included in fhir_parser models, so we have to generate it ourselves
reftypes = generate()
reftypes = {key.lower().replace(".", ""): value for key, value in reftypes.items()}


def generate_resource_list():
    """
    Get all the fhir resource classes available
    """
    FHIRAbstractBase = resources.FHIRAbstractBase
    classes = []
    for member_name in dir(resources):
        member = getattr(resources, member_name)
        try:
            if issubclass(member, FHIRAbstractBase):
                classes.append((member_name, member))
        except:
            pass
    return classes


###
# The following generate code for properties of specific types
###
def generate_string_prop(_, name, typ, islist, ofmany, mandatory, parent, FHIRResource):
    # We let mongo geverate ids automatically
    if name == "id" and parent == "MongoModel":
        fhirMap_prop = f'{name} = Attribute(getter=("_{name}", str), searcher=StringSearch("{name}"))'
        model_prop = ""
    else:
        if islist:
            model_prop = f"{name} = fields.ListField(fields.CharField(), blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        else:
            model_prop = f"{name} = fields.CharField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        fhirMap_prop = f'{name} = Attribute(getter="{name}", setter="{name}", searcher=StringSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_int_prop(_, name, typ, islist, ofmany, mandatory, parent, FHIRResource):
    if islist:
        model_prop = f"{name} = fields.ListField(fields.IntegerField(), blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
    else:
        model_prop = (
            f"{name} = fields.IntegerField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        )
    fhirMap_prop = f'{name} = Attribute(getter="{name}", setter="{name}", searcher=NumericSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_float_prop(_, name, typ, islist, ofmany, mandatory, parent, FHIRResource):
    if islist:
        model_prop = f"{name} = fields.ListField(fields.FloatField(), blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
    else:
        model_prop = (
            f"{name} = fields.FloatField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        )
    fhirMap_prop = f'{name} = Attribute(getter="{name}", setter="{name}", searcher=NumericSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_bool_prop(_, name, typ, islist, ofmany, mandatory, parent, FHIRResource):
    if islist:
        model_prop = f"{name} = fields.ListField(fields.BooleanField(), blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
    else:
        model_prop = (
            f"{name} = fields.BooleanField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        )
    fhirMap_prop = f'{name} = Attribute(getter="{name}", setter="{name}", searcher=StringSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_reference_prop(
    _, name, typ, islist, ofmany, mandatory, parent, FHIRResource
):
    path = f"{FHIRResource.__name__}{name}".lower()
    path_with_x = f"{FHIRResource.__name__}{name}".replace("Reference", "[x]").lower()
    nested_path = re.sub(
        r"([a-z])([A-Z])([a-z])", r"\1.\2\3", f"{FHIRResource.__name__}{name}"
    ).lower()
    if path in reftypes or path_with_x in reftypes or nested_path in reftypes:
        if path in reftypes:
            acceptable_types = reftypes[path]
        elif path_with_x in reftypes:
            acceptable_types = reftypes[path_with_x]
        elif nested_path in reftypes:
            acceptable_types = reftypes[nested_path]
        acceptable_types = sorted(list(acceptable_types))
        model_prop = f"{name} = fields.ObjectIdField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        fhirMap_prop = f'{name} = ObjectIdReferenceAttribute({acceptable_types}, ("{name}", str), "{name}", pk_setter="{name}")'
    else:
        # print('Unknown ref: name', f'{FHIRResource.__name__}.{name}')
        model_prop = f"# {name} = fields.ReferenceField(, blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
        fhirMap_prop = f'# {name} = ObjectIdReferenceAttribute(getter="{name}", setter="{name}", searcher=StringSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_element_prop(
    _, name, typ, islist, ofmany, mandatory, parent, FHIRResource
):
    if islist:
        fieldtype = "EmbeddedDocumentListField"
    else:
        fieldtype = "EmbeddedDocumentField"

    model_prop = f'{name} = fields.{fieldtype}("{typ.__name__}", blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})'
    fhirMap_prop = f'{name} = EmbeddedAttribute(type="{typ.__name__}", getter="{name}", setter="{name}", searcher=StringSearch("{name}"))'
    return model_prop, fhirMap_prop


def generate_date_prop(_, name, typ, islist, ofmany, mandatory, parent, FHIRResource):
    model_prop = (
        f"{name} = fields.DateTimeField(blank={not (mandatory if not ofmany else False)}, required={(mandatory if not ofmany else False)})"
    )
    fhirMap_prop = f'{name} = DateAttribute("{name}")'
    return model_prop, fhirMap_prop

###
# This is the main code generator.
###
def generate_class_definition(resource_name, FHIRResource, not_found):
    """
    Generates code for a pymodm class with a FhirMap member class for
    the given resource
    """

    # Until the bug with pymodm circular reference is fixed, Extensions are not supported.
    # see: https://jira.mongodb.org/projects/PYMODM/issues/PYMODM-93?filter=allopenissues
    if resource_name == "Extension":
        return ""

    Element = resources.Element
    FHIRReference = resources.FHIRReference
    FHIRDate = resources.FHIRDate

    if issubclass(FHIRResource, Element):
        parent = "EmbeddedMongoModel"
    else:
        parent = "MongoModel"

    model = [f"class {resource_name}(FhirBaseModel, {parent}):"]
    fhirMap = ["    class FhirMap:"]

    r = FHIRResource(strict=False)
    properties = r.elementProperties()

    TYPEMAP = {
        str: generate_string_prop,
        int: generate_int_prop,
        float: generate_float_prop,
        bool: generate_bool_prop,
        FHIRReference: generate_reference_prop,
        Element: generate_element_prop,
        FHIRDate: generate_date_prop,
    }

    for _, name, typ, islist, ofmany, mandatory in properties:

        # Append an underscore to reserved names
        if name in ["class", "import", "except", "global", "for", "assert", "from"]:
            name += "_"

        # There is no need to map contained attributes, since Fhirbug
        # generates them automatically
        if name == "contained":
            continue

        if typ in TYPEMAP:
            generator = TYPEMAP.get(typ)
        elif issubclass(typ, Element):
            generator = TYPEMAP.get(Element)
        else:
            print("Not found: ", typ.__name__, name)
            not_found.add(typ)

        if generator:
            prop_model, prop_fhirMap = generator(
                _, name, typ, islist, ofmany, mandatory, parent, FHIRResource
            )
            model.append(prop_model)
            fhirMap.append(prop_fhirMap)

    if len(model) == len(fhirMap) == 1:
        return ""

    final = "\n    ".join(model) + "\n" + "\n        ".join(fhirMap)
    return final


imports = [
    "# Automatically Generated for use with the fhirbug pymodm demo server",
    "",
    "from bson.objectid import ObjectId",
    "from pymodm import fields, MongoModel, EmbeddedMongoModel, ListField",
    "from fhirbug.models.attributes import Attribute, ReferenceAttribute, EmbeddedAttribute, DateAttribute",
    "from fhirbug.db.backends.pymodm.attributes import ObjectIdReferenceAttribute",
    "from fhirbug.db.backends.pymodm.models import FhirBaseModel",
    "from fhirbug.db.backends.pymodm.searches import StringSearch, NumericSearch",
    "",
    "",
    "class Extension(MongoModel):",
    "    pass",
]

if __name__ == "__main__":
    resource_list = generate_resource_list()
    not_found = set()
    Element = resources.Element
    BackboneElement = resources.BackboneElement
    FHIRReference = resources.FHIRReference

    elements = []

    for name, cls in resource_list:
        code = generate_class_definition(name, cls, not_found)
        elements.append((name, code))

    generated = "\n".join(imports) + "\n" * 3
    generated += "\n\n".join([e[1] for e in elements])

    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        from pathlib import Path
        target = Path(__file__).parent / "mappings.py"
        # target = "generated_pymodm.py"
    with open(target, "w") as f:
        f.write(generated)
