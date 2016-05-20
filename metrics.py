#!/usr/bin/env python

from datetime import date, datetime, timedelta
import sys, argparse, ConfigParser
import psycopg2 as rdb

def main(argv):
    """
    Parse arguments, open db connection
    """
     
    today = date.today()
    conn_string = "dbname='%s' port='%s' user='%s' password='%s' host='%s'"
    
    parser = argparse.ArgumentParser(description='Extracts daily metrics from database')
    parser.add_argument('-d','--date', metavar='DATE', dest='date', 
        help='Optional date, if not provided, date.today() will be used')
    
    args = parser.parse_args()
   
    if args.date != None:
        print "Setting current date with provided argument"
        today = datetime.strptime(args.date, "%Y-%m-%d %H:%M:%S.%f").date()
    
    yesterday = today - timedelta(1)    
    
    today_str = today.strftime("%Y-%m-%d %H:%M:%S.%f")
    yesterday_str = yesterday.strftime("%Y-%m-%d %H:%M:%S.%f")
    
    Config = ConfigParser.ConfigParser()
    Config.read("./config.ini")
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
        db_con = rdb.connect(conn_string % (database, port, user, password, host))
        db_con.autocommit = True
    except:
        print "Couldn't connect to database"
    
    cur = db_con.cursor()
    
    try:
        cur.execute(active_query % (today_str, yesterday_str))
        active_users=cur.fetchone()[0]
        print "Found %d active users in last two days" % (active_users)
    except:
        print "Error querying active users"
    
    try:
        cur.execute(inactive_query % (today_str, yesterday_str, yesterday_str))
        inactive_users=cur.fetchone()[0]
        print "Found %d inactive users in last two days" % (inactive_users)
    except:
        print "Error querying inactive users"
    
    try: 
        cur.execute(churned_query % (yesterday_str, today_str))
        churned_users=cur.fetchone()[0]
        print "Found %d churned users in last two days" % (churned_users)
    except:
        print "Errory querying churned users"
    
    try: 
        cur.execute(reactivated_query % (today_str, yesterday_str, today_str))
        reactivated_users=cur.fetchone()[0]
        print "Found %d reactivated users in last two days" % (reactivated_users)
    except:
        print "Error querying reactivated users"
   
    #try: 
    #    print "Attempting update table"
    #    cur.execute(update_query, (metrics_table, active_users, inactive_users, 
    #        churned_users, reactivated_users, today))
    #except:
    #    db_con.rollback()
    #    print "Error trying to update table"
    #finally:
    #    db_con.commit()
    
    try:    
        print "Attempting safe insert"
        #cur.execute(insert_query, (metrics_table, today, active_users, 
        #    inactive_users, churned_users, reactivated_users, metrics_table, today))
        cur.execute(insert_query, (metrics_table, today, active_users, 
            inactive_users, churned_users, reactivated_users))
    except:
        db_con.rollback()
        print "Error inserting into metrics table"
    finally:
        db_con.commit()
    
    cur.close()
    db_con.close()
if __name__ == "__main__":
   main(sys.argv[1:])
