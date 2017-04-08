import sqlite3 as lite
import sys

conDB = lite.connect('users.db')

with conDB:
    cur = conDB.cursor()
    cur.execute("CREATE TABLE UserPoints(username TEXT NOT NULL UNIQUE, active INT NOT NULL, points INT NOT NULL)")