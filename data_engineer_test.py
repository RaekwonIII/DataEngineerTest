#!/usr/bin/env python

import gzip, sys, getopt
import MySQLdb as mdb

help_message = 'data_engineer_test.py -i <npufile> -H <host> -d <database> -t <table> -u <user> -p <password>'

def process_line(line, db_con, table):
    """
    Parses fields from a single line, inserts them into the table
    """
    # parse fields from the line
    fields = [x.strip('"') for x in line.split(',')]
    
    # insert record into the table, doing necessary transform
    try:
        cur = db_con.cursor()
        cur.execute("INSERT INTO %s VALUES (%s, %s, %d, %s , %s, %s);" \
                    (table, fields[0], fields[1], fields[2], fields[3], fields[4], fields[5],, fields[6].replace('/page',''))) 
        db_con.commit()
    
    except mdb.Error, e:
        if db_con:
            db_con.rollback()
        print "Failed to process record: %s\nError description %d: %s" % (field[0],e.args[0],e.args[1])
        sys.exit(1)
    
    finally:
        if cur:
            cur.close()

def main(argv):
    """
    Parse arguments, open db connection, opens the file as an iterator 
    and processes it line by line, so it's not loaded entirely in memory
    """
    config = {}
    try:
        opts, args = getopt.getopt(argv,"hi:H:d:t:u:p:",["input=","host=","database=","table=","user=","password="])
    except getopt.GetoptError:
        print help_message 
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print help_message
            sys.exit()
        elif opt in ("-i", "--input"):
            config['inputfile'] = arg
        elif opt in ("-H", "--host"):
            config['host'] = arg
        elif opt in ("-d", "--database"):
            config['database'] = arg
        elif opt in ("-t", "--table"):
            config['table'] = arg
        elif opt in ("-u", "--user"):
            config['user'] = arg
        elif opt in ("-p", "--password"):
            config['password'] = arg
    
    db_con = mdb.connect(config['host'], config['user'], config['password'], config['database'])
    
    with db_con:
        with gzip.open(config['inputfile']) as fileobject:
            for line in fileobject:
                process_line(line, db_con, config['table'])

if __name__ == "__main__":
   main(sys.argv[1:])
