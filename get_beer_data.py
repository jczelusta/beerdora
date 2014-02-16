#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import config
import os
import sqlite3


# A directory containing beer rating files.

_DIR = "/Users/admin/Documents/Beerdora/beeradvocate/user/beers/"

# Prefix of beer rating files

_PREFIX = "index.html?"

# Identifying html from just before first row of data

_PRECEDING_LINE = "rDev</a></td></tr>"

# Identifying html from just after last row of data

_TRAILING_LINE = '<span style="color: #999999">'

# Path to sqlite db

_DB = config._DB

# Name of table to hold ratings

_TABLE = config._TABLE


def get_rows(filename):
    """Returns a list of all rows in rating table."""
    
    with open(_DIR + filename, "r") as f:
        last_half = f.read().decode("utf-8", errors="ignore").replace("\n", 
            "").split(_PRECEDING_LINE)[1]
        table = last_half.split(_TRAILING_LINE)[0]
        rows = table.split("<tr>")[1:]
    return rows


def process_rows(rows, result):
    """Returns a dict with information from row added."""
    
    for row in rows:
        cols = row.split("</td>")
        username = row.split("?ba=")[1].split('"><b>')[0]
        result["username"].append(username)        
        result["has_written_review"].append("1" if cols[0][-1] == "R" else 0)
        result["date"].append(cols[1].split(">")[1])
        result["beer"].append(cols[2].split("</b>")[0].split("<b>")[1])
        result["ba_beer_id"].append(cols[2].split('<a href="')[1].split("/?ba=" 
            + username)[0].split("/")[-1])
        result["brewery"].append(cols[2].split('</a>')[1].split(">")[-1])
        result["ba_brewery_id"].append(cols[2].split('<a href="')[2].split(
            '">')[0].split("/")[-1])
        result["style"].append(cols[2].split("</a>")[-2].split('">')[-1])
        result["ba_style_id"].append(cols[2].split(
            '<a href="/beer/style/')[1].split('">')[0])
        abv = cols[3].split(">")[-1]
        result["abv"].append(abv if abv != "?" else "NULL")
        result["rating"].append(cols[4].split("</b>")[-2].split("<b>")[-1])
        result["rdev"].append(cols[5].split("%")[-2].split('">')[-1].replace(
            "+", ""))
    return result


def create_table(db, table):
    """Creates a table to store ratings."""

    with sqlite3.connect(db) as con:
        c = con.cursor()
        c.execute("DROP TABLE " + table)
        create = """CREATE TABLE ba_ratings (
            ba_rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username, 
            has_written_review, 
            date, 
            beer, 
            ba_beer_id INTEGER, 
            brewery, 
            ba_brewery_id INTEGER,
            style,
            ba_style_id INTEGER,
            abv FLOAT,
            rating FLOAT,
            rdev FLOAT)"""
        c.execute(create)       


def write_to_db(result, db, table):
    """Writes a DataFrame to a db."""
    
    keys = result.keys()
    query = "INSERT OR REPLACE INTO " + table + " (" + ",".join(keys) + ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    rows = []
    for i in range(0, len(result[keys[0]])):
        row = []
        for key in keys:
            row.append(result[key][i])
        rows.append(tuple(row))
    with sqlite3.connect(db) as con:
        c = con.cursor()
        c.executemany(query, rows)


def main():
    result = {
        "username": [],
        "has_written_review": [],
        "date": [],
        "beer": [],
        "ba_beer_id": [],
        "brewery": [],
        "ba_brewery_id": [],
        "style": [],
        "ba_style_id": [],
        "abv": [],
        "rating": [],
        "rdev": []
    }
    for filename in os.listdir(_DIR):
        prefix_length = len(_PREFIX)
        if (filename[:prefix_length] == _PREFIX and len(filename) > 5 and 
           "&view" not in filename):
            print(filename)
            try:
                rows = get_rows(filename)
                result = process_rows(rows, result)
            except:
                print("The following file raised an exception: %s" % filename)
    create_table(_DB, _TABLE)
    write_to_db(result, _DB, _TABLE)


if __name__=="__main__":
    main()
