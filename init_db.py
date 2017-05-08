import sqlite3 as lite
import sys

conDB = lite.connect('bot.db')

with conDB:
    cur = conDB.cursor()
    cur.execute("CREATE TABLE UserPoints(username TEXT NOT NULL UNIQUE, active INT NOT NULL, points INT NOT NULL,\
                redemption INT, unmoderated INT)")
    cur.execute("CREATE TABLE Quotes(quote TEXT NOT NULL UNIQUE, addedby TEXT NOT NULL, timestamp TEXT NOT NULL)")
    cur.execute("CREATE TABLE Messages(message TEXT NOT NULL, interval INT NOT NULL, last TEXT NOT NULL)")
    cur.execute("CREATE TABLE Games(id TEXT, title TEXT NOT NULL, release_date TEXT NOT NULL, cover TEXT, genre TEXT,\
                complete_date TEXT, complete_time TEXT, total_time TEXT, comments TEXT)")
    conDB.commit()
