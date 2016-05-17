#!/bin/sh

echo "Creating database $data_mysql_db_name, if not exists"
# Creates database if necessary
mysql -u root -p$data_mysql_root_password -e \
    "CREATE DATABASE IF NOT EXISTS $data_mysql_db_name;"

echo "Granting user $data_mysql_db_user permissions on database"
# Grants user permissions (creates it and sets password if not set yet)
mysql -u root -p$data_mysql_root_password -e \
    "GRANT ALL PRIVILEGES ON $data_mysql_db_name.* TO \
    '$data_mysql_db_user'@'$data_mysql_db_host' IDENTIFIED BY '$data_mysql_db_user_password';"

echo "Dropping table $data_mysql_db_table and creating a new one in database $data_mysql_db_name"
# Creates table if necessary
mysql -u $data_mysql_db_user -p$data_mysql_db_user_password -e \
    "USE $data_mysql_db_name; \
    DROP TABLE $data_mysql_db_table;
    CREATE TABLE $data_mysql_db_table(event_id VARCHAR(36) PRIMARY KEY NOT NULL, \
    timestamp DATETIME NOT NULL, \
    user_fingerprint INT UNSIGNED NOT NULL, \
    domain_userid VARCHAR(16) NOT NULL, \
    network_userid VARCHAR(36) NOT NULL, \
    page_id INT UNSIGNED NOT NULL);"

echo "Checking if virtual environment is present"
# Check if virtual environment already present, if not creates it
if [ ! -d "etl_env" ]; then
    echo "Creating new virtual environment"
    virtualenv etl_env || (echo "Exiting; virtualenv failed" && exit 1) 
fi

echo "Activating virtual environment"
# Activates virtual environment
. ./etl_env/bin/activate

# Checks if dependencies are satisfied
echo "Checking dependencies with pip"
pip install --upgrade MySQL-python 
status=$?

if test $status -eq 0
then
    echo "Run 'source activate' to activate the virtual environment, and 'deactivate' to switch back to the system Python."
else
    echo "PIP failed to install all packages."
    exit $status
fi

