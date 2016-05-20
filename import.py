#!/usr/bin/env python

import sys, ConfigParser
import psycopg2 as rdb

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def main(argv):
    """
    Read config file, open db connection, creates table and imports data
    """
    Config = ConfigParser.ConfigParser()
    Config.read("./config.ini")
    
    host = ConfigSectionMap("Database")['host']
    database = ConfigSectionMap("Database")['database']
    port = ConfigSectionMap("Database")['port']
    user = ConfigSectionMap("Database")['user']
    password = ConfigSectionMap("Database")['password']
    
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
