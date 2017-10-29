#!/bin/bash

# if [ ! -e fhir-parser ]; then
# 	git submodule update --init --recursive
# fi

TOOLS_DIR=$(dirname "$0")
cd $TOOLS_DIR
source fhir_parser/.venv/bin/activate

cp ../Fhir/base/settings.py fhir_parser/settings.py
cd fhir_parser
./generate.py $1
cd ..
