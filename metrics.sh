#!/bin/sh

# Executes bootstrap
. ./bootstrap.sh

# Executes Python script to import data into the DB
python metrics.py -d $(date -d "1 day ago" '+%Y-%m-%d')
