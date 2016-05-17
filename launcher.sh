#!/bin/sh

# Resets config variables
data_mysql_db_host=""
data_mysql_db_name=""
data_mysql_db_user=""
data_mysql_db_user_password=""
data_mysql_root_password=""
data_source_url=""

ETL_SOURCE=./data_engineer_test.py
CONFIG_FILE=./config.cfg
BOOTSTRAP=false

while [[ $# > 0 ]]
do
key="$1"

case $key in
    -b|--bootstrap)
    BOOTSTRAP=true
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

# Imports config from file
source $CONFIG_FILE

# Checks configuration has been loaded
if [[ -z $data_mysql_db_host ]] || [[ -z $data_mysql_db_name ]] || [[ -z $data_mysql_db_user ]] || \
    [[ -z $data_mysql_db_user_password ]] || [[ -z $data_mysql_root_password ]] || [[ -z $data_source_url ]]; then
    echo "Configuration has not been loaded, exiting"; exit(2);
fi

# Executes bootstrap if requested
if [[ $BOOTSTRAP ]]; then
    . ./bootstrap.sh
fi

# Downloads source file
wget $data_source_url

# Sets python script executable, if not already
if [[ ! -x "$ETL_SOURCE" ]]; then
    chmod +x $ETL_SOURCE
fi

# Executes Python script to import data into the DB
. $ETL_SOURCE -i events.gz -H $data_mysql_db_host -d $data_mysql_db_name -u $data_mysq_db_user -p $data_mysql_db_user_password

