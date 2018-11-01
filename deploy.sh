#!/usr/bin/env bash

# Delete previous distribution archives
rm -rf ./dist/
rm -rf ./build/
rm -rf ./fcli.egg-info/

# Generate distribution archives
python setup.py sdist bdist_wheel

# Upload archives to PyPI
twine upload ./dist/*
