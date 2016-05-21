#!/usr/bin/env python

from datetime import date, timedelta
from dateutil.parser import parse
import metrics

def main():
    base = parse('2014-09-02')
    numdays = 58
    date_list = [base + timedelta(days=x) for x in range(0, numdays)]
    for date in date_list:
        metrics.main(date.strftime("%Y-%m-%d"))


if __name__ == "__main__":
   main()
