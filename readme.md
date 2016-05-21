# Pre-requisites:
This software uses python 2.7.
Packages for python, python-dev, postgre-sql-dev, pip and virtualenv have tobe installed in the system.

# To perform a test against sample data
* Launch 'bootstrap.sh' to setup the virtual environment, activate it, check that necessary Python packages are installed, and set script files as executable.
* Change configuration in config.ini, this file includes config for
 - database connection details
 - table names
 - query templates
* Launch 'import.py' to setup sample data in the database.
* Launch 'test.py' to run metrics for each day in the sample data set

### Extras
* 'metrics.py' accepts a date string as argument 'python metrics.py -d '2014-09-02'' which can be use in case of failure.
* 'metrics.sh' is a wrapper for it's namesake python counterpart and is designed to be used for scheduling the ETL process
 - It invokes 'bootstrap.sh' to make sure virtual environment is active
 - The suggestion would be to execute this '(crontab -l ; echo "0 3 * * * /path/to/metrics.sh") | sort - | uniq - | crontab -' to launch this script after midnight
 - It uses yesterday's date to run the python script, so should be scheduled after midnight.





