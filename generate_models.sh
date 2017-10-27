#!/bin/bash

if [ ! -e fhir-parser ]; then
	git submodule update --init --recursive
fi
cp Fhir/base/settings.py tools/fhir-parser/settings.py
cd tools/fhir-parser
./generate.py $1
cd ..
