#!/bin/bash

# clear all virtualenv resources if exists
rm -rf bin include lib .Python

# setup virtualenv
virtualenv --distribute .
source bin/activate

# install packages with pip
pip install -r requirements.txt

# copy settings.py
cp icecream/settings-sample.py icecream/settings.py
