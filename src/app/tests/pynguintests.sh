#!/bin/bash

# Install Pynguin
pip install -r ..../requirements.txt
export PYNGUIN_DANGER_AWARE="pi"
pip install pynguin

# Create test directory
mkdir /tmp/pynguin-results

# Run Pynguin unit tests for main module
pynguin \
--project-path .. \
--output-path /tmp/pynguin-results \
--module-name main

# Run Pynguin unit tests for DistributionParser module
pynguin \
--project-path .. \
--output-path /tmp/pynguin-results \
--module-name DistributionParser

# Run Pynguin unit tests for Isopleth module
pynguin \
--project-path .. \
--output-path /tmp/pynguin-results \
--module-name Isopleth

# Run Pynguin unit tests for NomogramAxis module
pynguin \
--project-path .. \
--output-path /tmp/pynguin-results \
--module-name NomogramAxis

# Run Pynguin unit tests for maths_functions module
pynguin \
--project-path ../utils \
--output-path /tmp/pynguin-results \
--module-name maths_functions
