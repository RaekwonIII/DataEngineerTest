#!/usr/bin/env python

from datetime import date, timedelta
from dateutil.parser import parse
import sys, argparse, ConfigParser, psycopg2, logging

def main(date_arg):
    """
    Reads config file, sets date variables, opens DB connection, 
    extracts data and inserts results into new table
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',filename='metrics.log', level=logging.INFO)
    
    today = date.today()
    
    if date_arg != None:
        logging.info("Setting current date with provided argument: %s" % date_arg)
        today = parse(date_arg).date()
    
    yesterday = today - timedelta(1)    
    
    today_str = today.strftime("%Y-%m-%d %H:%M:%S.%f")
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S.%f")
    
    Config = ConfigParser.ConfigParser()
    Config.read("./config.ini")
    conn_string = Config.get("Database",'conn_string')
    host = Config.get("Database",'host')
    database = Config.get("Database",'database')
    port = Config.get("Database",'port')
    user = Config.get("Database",'user')
    password = Config.get("Database",'password')
    metrics_table = Config.get("Metrics",'metrics_table')
    active_query = Config.get("Metrics",'active_query')
    inactive_query = Config.get("Metrics",'inactive_query')
    churned_query = Config.get("Metrics",'churned_query')
    reactivated_query = Config.get("Metrics",'reactivated_query') 
    update_query = Config.get("Metrics",'update_query')
    insert_query = Config.get("Metrics",'insert_query')
    
    try:
        conn = psycopg2.connect(conn_string % (database, port, user, password, host))
        conn.autocommit = True
    except psycopg2.Error as e:
        logging.error("Could not connect to database: %s" % e.pgerror)
    
    cur = conn.cursor()
    
    try:
        cur.execute(active_query % (today_str, yesterday_str))
        active_users=cur.fetchone()[0]
        logging.info("Found %d active users in last two days" % (active_users))
    except psycopg2.Error as e:
        logging.error("Error querying active users: %s" % e.pgerror)
    
    try:
        cur.execute(inactive_query % (today_str, yesterday_str, yesterday_str))
        inactive_users=cur.fetchone()[0]
        logging.info("Found %d inactive users in last two days" % (inactive_users))
    except psycopg2.Error as e:
        logging.error("Error querying inactive users: %s" % e.pgerror)
    
    try: 
        cur.execute(churned_query % (yesterday_str, today_str))
        churned_users=cur.fetchone()[0]
        logging.info("Found %d churned users in last two days" % (churned_users))
    except psycopg2.Error as e:
        logging.error("Error querying churned users: %s" % e.pgerror)
    
    try: 
        cur.execute(reactivated_query % (today_str, yesterday_str, today_str))
        reactivated_users=cur.fetchone()[0]
        logging.info("Found %d reactivated users in last two days" % (reactivated_users))
    except psycopg2.Error as e:
        logging.error("Error querying reactivated users: %s" % e.pgerror)
   
    try: 
        logging.info("Attempting update table")
        cur.execute(update_query % (metrics_table, active_users, inactive_users, 
            churned_users, reactivated_users, today))
    except psycopg2.Error as e:
        conn.rollback()
        logging.error("Error trying to update table: %s" % e.pgerror)
    finally:
        conn.commit()
    
    try:    
        logging.info("Attempting safe insert")
        cur.execute(insert_query % (metrics_table, today, active_users, 
            inactive_users, churned_users, reactivated_users, metrics_table, today))
    except psycopg2.Error as e:
        conn.rollback()
        logging.error("Error inserting into metrics table: %" % e.pgerror)
        print e.pgerror
    finally:
        conn.commit()
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    '''
    Parses command line arguments and passes them to main function
    '''
    parser = argparse.ArgumentParser(description='Extracts daily metrics from database')
    parser.add_argument('-d','--date', metavar='DATE', dest='date', 
        help='Optional date, if not provided, date.today() will be used')
    
    args = parser.parse_args()
    main(args.date)
