#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import config
import sqlite3

from datetime import datetime
from random import randint


def fetch_data(db, table):
    """Returns a list of tuples of ratings data."""

    with sqlite3.connect(db) as con:
        c = con.cursor()
        query = "SELECT username, ba_beer_id, rating, date from " + table
        rows = c.execute(query)
    result = []
    users = {}
    for row in rows:
        user = row[0]
        if user not in users.keys():
            users[user] = randint(1, 9999999)
        ba_beer_id = row[1]
        rating = row[2]
        date = datetime.strptime(row[3], "%m-%d-%Y").strftime("%s")
        result.append((users[user], ba_beer_id, rating, date))
    return result


def main():
    rows = fetch_data(config._DB, config._TABLE)
    N = len(rows)*config._TRAIN_PERCENT
    with open(config._TRAIN, 'w') as f:
        i = 0
        for row in rows:
            f.write(
                str(row[0]) + "\t" + 
                str(row[1]) + "\t" + 
                str(row[2]) + "\t" + 
                row[3] + "\n"
            )
            i += 1
            if i > N:
                break
    with open(config._TEST, 'w') as f:
        for row in rows[i:]:
            f.write(
                str(row[0]) + "\t" + 
                str(row[1]) + "\t" + 
                str(row[2]) + "\t" + 
                row[3] + "\n"
            )

    
    
if __name__=="__main__":
    main()
