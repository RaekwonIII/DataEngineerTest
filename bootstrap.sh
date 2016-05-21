#!/bin/sh

echo "Checking if virtual environment is present"
if [ ! -d "etl_env" ]; then
    echo "Creating new virtual environment"
    virtualenv etl_env || (echo "Exiting; virtualenv failed" && exit 1) 
fi

echo "Activating virtual environment"
. ./etl_env/bin/activate

echo "Checking dependencies with pip"
pip install --upgrade psycopg2 python-dateutil
exit_status=$?

if test $exit_status -eq 0
then
    echo "Run 'source activate' to activate the virtual environment, and 'deactivate' to switch back to the system Python."
else
    echo "PIP failed to install all packages."
    exit $exit_status
fi


# Sets python script executable, if not already
for f in $(ls *{py,sh})
do 
    if [[ ! -x $f ]]; then
        echo "File $f is not executable, setting it now"
        chmod +x $f
    fi
done

