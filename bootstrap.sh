#!/bin/sh

if [ ! -d "etl_env" ]; then
    virtualenv etl_env || (echo "Exiting; virtualenv failed" && exit 1) 
fi

. ./etl_env/bin/activate

pip install --upgrade MySQL-python 
status=$?

if test $status -eq 0
then
    echo "Run 'source activate' to activate the virtual environment, and 'deactivate' to switch back to the system Python."
else
    echo "PIP failed to install all packages."
    exit $status
fi

# Creates database if necessary
mysql -u root -p $data_mysql_root_password -e \
    "CREATE DATABASE IF NOT EXISTS $data_mysql_db_name; \
    GRANT ALL PRIVILEGES ON $data_mysql_db_name.* TO \
    '$data_mysql_db_user'@'$data_mysql_db_host' IDENTIFIED BY '$data_mysql_db_user_password';"

# Creates table if necessary
mysql -u $data_mysql_db_user -p $data_mysql_db_user_password -e \
    "CREATE TABLE IF NOT EXISTS events(event_id VARCHAR(36) PRIMARY KEY NOT NULL, \
    timestamp DATETIME NOT NULL, \
    user_fingerprint INT UNSIGNED NOT NULL, \
    domain_userid VARCHAR(16) NOT NULL, \
    network_userid VARCHAR(36) NOT NULL, \
    page_id INT UNSIGNED NOT NULL);"


