#!/bin/bash

if [ ! -e fhir-parser ]; then
	git submodule update --init --recursive
fi

source tools/fhir_parser/.venv/bin/activate

cp Fhir/base/settings.py tools/fhir_parser/settings.py
cd tools/fhir_parser
./generate.py $1
cd ..
