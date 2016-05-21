#!/usr/bin/env python

import sys, ConfigParser
import psycopg2

def main():
    """
    Read config file, open db connection, creates table and imports data
    """
    Config = ConfigParser.ConfigParser()
    Config.read("./config.ini")
    
    host = Config.get("Database",'host')
    database = Config.get("Database",'database')
    port = Config.getint("Database",'port')
    user = Config.get("Database",'user')
    password = Config.get("Database",'password')
    metrics_table = Config.get("Metrics",'metrics_table')
    
    conn_string = "dbname='%s' port='%s' user='%s' password='%s' host='%s'"
    conn = psycopg2.connect(conn_string % (database, port, user, password, host))
    
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS events ( 
                event_id VARCHAR(36) PRIMARY KEY NOT NULL, 
                timestamp DATETIME NOT NULL, 
                user_fingerprint BIGINT, 
                domain_userid VARCHAR(16), 
                network_userid VARCHAR(36) NOT NULL, 
                page_id varchar(13) NOT NULL); 
                COPY events FROM 's3://gousto-test/events.gz' 
                credentials 'aws_iam_role=arn:aws:iam::882822032425:role/goustoTest' 
                delimiter ',' 
                removequotes 
                timeformat 'YYYY-MM-DD HH:MI:SS' 
                GZIP region 'eu-west-1';""")
            cur.execute("""CREATE TABLE IF NOT EXISTS %s ( 
                date DATE PRIMARY KEY NOT NULL, 
                active BIGINT, 
                inactive BIGINT, 
                churned BIGINT, 
                reactivated BIGINT);""" % (metrics_table))
    
    except rdb.Error, e:
        if conn:
            conn.rollback()
        print "Error description %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
    finally:
        if cur:
            cur.close()

if __name__ == "__main__":
   main()
