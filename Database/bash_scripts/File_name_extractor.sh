#!/bin/bash

SOURCE_DIR="submission"

cd ${SOURCE_DIR}

ls > ../input.txt

awk '{print $0}' ../input.txt |sed 's/^submission_//' > ../output.txt

# > ../output.txt
