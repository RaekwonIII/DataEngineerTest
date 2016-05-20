#!/bin/sh

echo "Checking if virtual environment is present"
# Check if virtual environment already present, if not creates it
if [ ! -d "etl_env" ]; then
    echo "Creating new virtual environment"
    virtualenv etl_env || (echo "Exiting; virtualenv failed" && exit 1) 
fi

echo "Activating virtual environment"
# Activates virtual environment
. ./env_etl/bin/activate

# Checks if dependencies are satisfied
echo "Checking dependencies with pip"
pip install --upgrade psycopg2
status=$?

if test $status -eq 0
then
    echo "Run 'source activate' to activate the virtual environment, and 'deactivate' to switch back to the system Python."
else
    echo "PIP failed to install all packages."
    exit $status
fi


# Sets python script executable, if not already
for f in $(ls *{py,sh})
do 
    if [[ ! -x $f ]]; then
        chmod +x $f
    fi
done

# Executes Python script to import data into the DB
python $SETUP_SOURCE -H $data_mysql_db_host -d $data_mysql_db_name -t $data_mysql_db_table -u $data_mysql_db_user -p $data_mysql_db_user_password

