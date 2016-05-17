#!/bin/sh

unset CC
unset CXX

rerun="YES"

# pyCurl needs to know the SSL backend used in libcurl
# TODO - Detect backend used rather than basing on OS used
OS=`uname`
if [ $OS = "FreeBSD" ]; then
    export PYCURL_SSL_LIBRARY=openssl
else
    # NSS used by default on Linux
    export PYCURL_SSL_LIBRARY=nss
fi

requirements_file="requirements.pip"
pip_upgrade_option=""

if [ $# -gt 0 ]; then
    while getopts "um:" optname
    do
        case $optname in
            u)
                pip_upgrade_option="--upgrade"
                ;;
            m)
                if [ "$OPTARG" = "oxygen_production" ]; then
                    # Include Oxygeneditor's requirements if that's the run mode
                    requirements_file="requirements-oxygen-production.pip"
                elif [ "$OPTARG" = "test" ]; then
                    # Include Tests's requirements if that's the run mode
                    requirements_file="requirements-test.pip"
                fi
                ;;
        esac
    done
fi

if [ ! -d "environ" ]; then
    virtualenv environ || (echo "Exiting; virtualenv failed" && exit 1) 
    rerun=
fi

ln -sf environ/bin/activate

. ./activate

PYTHON_VERSION=`python -c 'import sys; print sys.version[:3]'`
PYTHON_LIB=$VIRTUAL_ENV/lib/python${PYTHON_VERSION}/site-packages

[ -z "${rerun}" ] && (easy_install -q http://nfs-server/python/pip-0.7.2.tar.gz)

pip install $pip_upgrade_option --index-url http://nfs-server/python --find-links http://nfs-server/python -r $requirements_file
status=$?

if test $status -eq 0
then
    echo "Run 'source activate' to activate the virtual environment, and 'deactivate' to switch back to the system Python."
else
    echo "PIP failed to install all packages."
    exit $status
fi

#Hack to make sure we can run Django with MySQL 4 client installed (and all of our live databases are MySQL 4). Rather than doing
#this manually every time i'm putting it in bootstrap so that we try to automatically take care of it. We have a few locations
#with MySQL 5 client installed (dev London, dev Shanghai and production London) and we shouldn't change the file for them
#TODO: my suspicion is that this is down to the MySQLdb installation and not the MySQL client one. They tend to be bundled
#on boxes, so checking for one likely tells us about the other, but this should be investigated.
mysql --version | fgrep 'Distrib 4' > /dev/null
if [ $? -eq 0 ]; then
    MYSQL_DJANGO_FILE="environ/lib/python2.5/site-packages/django/db/backends/mysql/base.py"
    if [ -f $MYSQL_DJANGO_FILE ]; then
        /usr/bin/sed -i bak -e "s/                'charset': 'utf8',/                #'charset': 'utf8',/g" $MYSQL_DJANGO_FILE
        if [ $? -eq 0 ]; then
            echo "N.B. MySQL python file in the Django setup has been hacked to allow for MySQL 4 compatibility. The file changed is '$MYSQL_DJANGO_FILE' and a pre-change version of that file has been preserved with the 'pybak' extension."
        else
            echo "Couldn't change the MySQL connection arguments in the Django checkout, file is: '$MYSQL_DJANGO_FILE'. This setup won't work with MySQL 4 client."
        fi
    else
        echo "ERROR: '$MYSQL_DJANGO_FILE' doesn't exist, couldn't prepare this Django checkout for MySQL 4 compatibility."
    fi
fi