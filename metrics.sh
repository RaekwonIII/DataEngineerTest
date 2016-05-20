#!/bin/sh

# Executes bootstrap
. ./bootstrap.sh

# Executes Python script to import data into the DB
python metrics.py
