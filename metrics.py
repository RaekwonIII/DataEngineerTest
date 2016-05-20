#!/usr/bin/env python

import sys, getopt
import psycopg2 as rdb

help_message = 'setup.py -H <host> -P <port> -d <database> -t <table> -u <user> -p <password>'


def main(argv):
    """
    Parse arguments, open db connection, creates table and imports data
    """
    try:
        opts, args = getopt.getopt(argv,"hH:P:d:t:u:p:",["host=","port=","database=","table=","user=","password="])
    except getopt.GetoptError:
        print help_message 
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_message
            sys.exit()
        elif opt in ("-H", "--host"):
            host = arg
        elif opt in ("-P", "--port"):
            port = arg
        elif opt in ("-d", "--database"):
            database = arg
        elif opt in ("-t", "--table"):
            table = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg
    
    conn_string = "dbname='%s' port='%s' user='%s' password='%s' host='%s'"
    db_con = rdb.connect(conn_string % (database, port, user, password, host))
    
    try:
        with db_con:
            cur = db_con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS events ( \
                event_id VARCHAR(36) PRIMARY KEY NOT NULL, \
                timestamp DATETIME NOT NULL,\
                user_fingerprint bigint, \
                domain_userid VARCHAR(16), \
                network_userid VARCHAR(36) NOT NULL, \
                page_id varchar(13) NOT NULL);\
                copy events from 's3://gousto-test/events.gz' \ 
                credentials 'aws_iam_role=arn:aws:iam::882822032425:role/goustoTest' \
                delimiter ',' \
                removequotes \
                timeformat 'YYYY-MM-DD HH:MI:SS' \
                GZIP region 'eu-west-1';")
    
    except rdb.Error, e:
        if db_con:
            db_con.rollback()
        print "Error description %d: %s" % (field[0],e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if cur:
            cur.close()

if __name__ == "__main__":
   main(sys.argv[1:])
