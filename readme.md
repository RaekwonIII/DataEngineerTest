Pre-requisites:

This software uses python 2.7.
Packages for python, python-def, postgre-sql-dev, pip and virtualenv have tobe installed in the system.

Configuration for databse has to be set into 'config.ini'

Launch 'bootstrap.sh' to setup the virtual environment, activate it, check that necessary 
Python packages are installed, and set script files as executable

Launch 'import.py' to setup sample data in the database.

Launch 'metrics.sh' to extract metrics. This is a wrapper to 'metrics.py', and it calls 'bootstrap.sh' to 
make sure program is running in virtual environment.

