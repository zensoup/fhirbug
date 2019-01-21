"""
Parse all ``*.profile.json`` inside the profile_folder and generate a dictionary
{'resource.path': set(possible reference types)}.

For example, since the valid referenced resources for the *definition* attribute of
a *ReferralRequest* resource can be of type *ActivityDefinition* or *PlanDefinition*,
the generated dictionary would contain the following entry:
`{'ReferralRequest.definition': {'ActivityDefinition', 'PlanDefinition'}, ...}`
"""

from pathlib import Path
import json
import sys

# Relative or absolute path to a directory that contains resource profile files
profile_folder = "tools/fhir_parser/downloads"


def generate(files=profile_folder):
    result = {}
    files = Path(files).glob("*.profile.json")
    for file in files:
        with open(file, "r") as f:
            # Parse json
            resource = json.loads(f.read())
            # Example of great code
            elements = resource["snapshot"]["element"]
            for elem in elements:
                if "type" not in elem:
                    continue
                types = elem["type"]
                for t in types:
                    if "code" not in t or "targetProfile" not in t:
                        continue
                    if t["code"] == "Reference":
                        if f'{elem["path"]}' not in result:
                            result[f'{elem["path"]}'] = set()
                        result[f'{elem["path"]}'].add(t["targetProfile"].split("/")[-1])
    return result


if "__main__" == __name__:
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_dir():
        reftypes = generate(sys.argv[1])
    else:
        reftypes = generate()

    print(reftypes)
