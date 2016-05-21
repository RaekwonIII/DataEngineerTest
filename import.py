#!/usr/bin/env python

import sys, ConfigParser, psycopg2, logging

def main():
    """
    Read config file, open db connection, creates table and imports data
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',filename='import.log', level=logging.INFO)
    
    Config = ConfigParser.ConfigParser()
    Config.read("./config.ini")

    logging.info("Reading config file...")

    conn_string = Config.get("Database",'conn_string')
    host = Config.get("Database",'host')
    database = Config.get("Database",'database')
    port = Config.getint("Database",'port')
    user = Config.get("Database",'user')
    password = Config.get("Database",'password')
    conn_string = Config.get("Database",'conn_string')
    compressed_dataset_s3 = Config.get("Import",'compressed_dataset_s3')
    create_events_query = Config.get("Import",'create_events_query')
    import_query = Config.get("Import",'import_query')
    metrics_table = Config.get("Metrics",'metrics_table')
    create_metrics_query = Config.get("Metrics",'create_metrics_query')

    logging.info("Configuration complete")

    conn = psycopg2.connect(conn_string % (database, port, user, password, host))

    logging.info("Opened connection with DB")
    
    try:
        with conn:
            cur = conn.cursor()
            logging.info("Creating events table")
            cur.execute(create_events_query)
            logging.info("Importing data from file")
            cur.execute(import_query % (compressed_dataset_s3))
            logging.info("Creting metrics_table")
            cur.execute(create_metrics_query % (metrics_table))
    
    except psycopg2.Error, e:
        if conn:
            conn.rollback()
        logging.error("Error description: %s" % (e.pgerror))
        sys.exit(1)
    finally:
        if cur:
            cur.close()

if __name__ == "__main__":
   main()
