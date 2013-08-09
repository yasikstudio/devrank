#!/bin/bash

# clear all virtualenv resources if exists
#rm -rf env

# setup virtualenv
virtualenv --distribute env
source env/bin/activate

# install packages with pip
pip install -r requirements.txt
