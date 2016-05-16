#!/usr/bin/env python

import fileinput, gzip, sys, getopt, wget
import MySQLdb as mdb

help_message = 'data_engineer_test.py -c <configfile>'

def read_config(configfile):
    """
    Opens a config file and reads configurations in key="val" form. Only accepted keys are processed
    """
    with fileinput.input(configfile) as fileobject:
        for line in fileobject:
            [key,val] = line.split(',')
            if key ==  "data_mysql_db_host":
                db_host = val.strip('"')
            if key ==  "data_mysql_db_name":
                db_host = val.strip('"')
            if key == "data_mysql_db_user":
                db_user = val.strip('"')
            if key == "data_mysql_db_user_password":
                db_pass = val.strip('"')
            if key == "data_mysql_root_password":
                db_root_pass = val.strip('"')
            if key == "events_url":
                events_url = val.strip('"')

    return (db_host, db_name, db_user, db_pass, db_root_pass, events_url)

def etl(inputfile, db_con):
    """
    Opens the file as an iterator and processes it line by line, 
    so it's not loaded entirely in memory
    """
    with gzip.open(inputfile) as fileobject:
        for line in fileobject:
            process_line(line, db_con)

def process_line(line, db_con):
    """
    Parses fields from a single line, inserts them into the table
    """
    # parse fields from the line
    fields = [x.strip('"') for x in line.split(',')]
    
    # insert record into the table, doing necessary transform
    try:
        cur = db_con.cursor()
        cur.execute("INSERT INTO events VALUES (unhex(replace( %s ,'-','')), %s, %s, %s , unhex(replace( %s ,'-','')), %s);" \
                    (fields[0].replace('-',''), fields[1], fields[2], fields[3], fields[4], fields[5].replace('-',''),, fields[6].replace('/page',''),, )) 
        db_con.commit()
    
    except mdb.Error, e:
        if db_con:
            db_con.rollback()
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    
    finally:
        if cur:
            cur.close()

def main(argv):
    """
    Parse arguments, open db connection and starts ETL process
    """
    # config file is mandatory argument
    try:
        opts, args = getopt.getopt(argv,"hc:",["conf="])
    except getopt.GetoptError:
        print help_message 
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_message
            sys.exit()
        elif opt in ("-c", "--conf"):
            configfile = arg
    
    # process config file and extract config params
    (host, database, user, password, root_password, input_url) = read_config(configfile)
    
    # Fetch records archive
    inputfile = wget.download(input_url)
    
    # create root connection to the DB
    root_con = mdb.connect(host, 'root', root_password)
    # create database and user if necessary
    with root_con:
        cur = root_con.cursor()
        cur.execute("CREATE DATABASE %s IF NOT EXISTS;GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s' IDENTIFIED BY '%s';", \
                (database, database, user, host, password))

    # now create user connection
    db_con = mdb.connect(host, user, password, database)
    # create table
    with db_con:
        cur = db_con.cursor()
        cur.execute("CREATE TABLE IF NOT EXIST events(event_id BINARY(16) PRIMARY KEY NOT NULL, \
            event_id_text VARCHAR(36) GENERATED ALWAYS as \
                (insert( \
                    insert( \
                        insert( \
                            insert(hex(id_bin),9,0,'-'), \
                            14,0,'-'), \
                        19,0,'-'), \
                    24,0,'-') \
                ), \
            timestamp DATETIME NOT NULL, \
            user_fingerprint INT NOT NULL, \
            domain_userid BINARY(8) NOT NULL, \
            domain_userid_text VARCHAR(16) GENERATED ALWAYS as \
            network_userid BINARY(16) NOT NULL, \
            network_userid_text VARCHAR(36) GENERATED ALWAYS as \ 
                (insert( \
                    insert( \
                        insert( \
                            insert(hex(id_bin),9,0,'-'), \
                            14,0,'-'), \
                        19,0,'-'), \
                    24,0,'-') \
                ), \
            page_id INT NOT NULL)")
        
        # start ETL process with connection active.
        etl(inputfile, db_con)

if __name__ == "__main__":
   main(sys.argv[1:])
