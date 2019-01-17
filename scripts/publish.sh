#!/usr/bin/env bash

scriptpath=$(cd `dirname $0`; pwd)
basepath=$(cd `dirname $0`; cd ..; pwd)

rm -rf build
rm -rf dist
rm -rf tcplite.egg-info

source venv/bin/activate

python setup.py sdist build
#python setup.py bdist_wheel --universal

twine upload dist/*