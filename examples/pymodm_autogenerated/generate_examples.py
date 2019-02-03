from collections import defaultdict
from pathlib import Path
from bson import ObjectId
import json
import sys

try:
    import fhirbug
except ModuleNotFoundError:
    # Allow execution from a git clone without having fhirball installed.
    if Path("./fhirbug").is_dir():  # Executed from the example's directory`
        sys.path.append("./")
    elif Path("../../fhirbug").is_dir():  # Executed from the project's root directory`
        sys.path.append("../../")


VERBOSE = True

# Relative or absolute path to a directory that contains resource profile files
profile_folder = Path(__file__).parent / "test_cache"


def generate(files=profile_folder):
    result = defaultdict(list)
    files = Path(files).glob("*-example*.json")
    for file in files:
        with open(file, "r") as f:
            # Parse json
            resource = json.loads(f.read())
            resourceType = resource["resourceType"]
            result[resourceType].append(resource)
    return result


def find(examples, type, id):
    try:
        return next(filter(lambda e: e["id"] == id, examples[type]))
    except StopIteration:
        return None


references = {}


def replaceReference(ref):
    if ref not in references:
        try:
            resource, oldId = ref.split("/")
        except:
            if VERBOSE:
                print(ref)
            return ref
        id = ObjectId(oldId[:12].zfill(12).encode())
        references[ref] = resource + "/" + str(id)
    return references[ref]


def replaceAllReferences(examples):
    def replace(resource):
        if type(resource) is list:
            return list(map(replace, resource))
        elif type(resource) is dict:
            for val in resource.values():
                if type(val) in (dict, list):
                    if "reference" in val:
                        val["reference"] = replaceReference(val["reference"])
                    else:
                        replace(val)

    for ex_list in examples.values():
        for ex in ex_list:
            replace(ex)


def replaceIds(examples):
    for cls, ex_list in examples.items():
        for ex in ex_list:
            try:
                id = ex["id"]
                type = ex["resourceType"]
                ref = type + "/" + id
                if ref in references:
                    ex["id"] = references[ref].split("/")[1]
            except:
                if VERBOSE:
                    print(ex)


def clean_examples(verbose):
    if verbose == False:
        global VERBOSE
        VERBOSE = False
    examples = generate()
    replaceAllReferences(examples)
    replaceIds(examples)
    return examples


def generate_examples(verbose=True):
    if verbose == False:
        global VERBOSE
        VERBOSE = False

    from fhirbug.Fhir import resources
    from fhirbug.config import import_models

    examples = clean_examples(verbose)
    models = import_models()

    total = 0
    for cls_examples in examples.values():
        total += len(cls_examples)

    print('Generating fixtures...')
    print(f'0 / {total}', end='\r')
    count = 0
    for cls_name, ex_list in examples.items():
        ResourceCls = getattr(resources, cls_name)
        MapperCls = getattr(models, cls_name)
        for index, example in enumerate(ex_list):
            try:
                resource = ResourceCls(example)
            except resources.FHIRValidationError as e:
                if VERBOSE:
                    print(f"{cls_name}[{index}] - Invalid FHIR structure", e)
            Item = MapperCls.from_resource(resource)
            if (ObjectId.is_valid(resource.id)):
                Item._id = resource.id
            Item.save()
            count += 1
            print(f'{count} / {total}  {cls_name}' + 20 * ' ', end='\r')
    print('Fixtures generated' + 20 * ' ')
    return examples


if __name__ == "__main__":
    import sys
    wait = sys.argv[-1] == '-w'
    import pymongo
    import pymodm
    from fhirbug.config import settings, import_models
    settings.configure('settings')
    server, db_name = settings.PYMODM_CONFIG["URI"].rsplit("/", 1)
    while True:
        try:
            client = pymongo.MongoClient(server)
            client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            if not wait:
                sys.exit(1)
        else:
            break
    pymodm.connect(settings.PYMODM_CONFIG["URI"])

    # Clear the database
    client.drop_database(db_name)
    generate_examples(False)
