from twisted.internet import protocol, reactor
from collections import defaultdict

import sys, json
import socketio
#import eventlet
from flask import Flask, render_template
from threading import Thread
import bot
import time
import logging
import logging.config
import requests
logging.config.fileConfig('logging.conf')

global sio

global raffleEntrants
raffleEntrants = []

class chatSocket(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        from flask import Flask, render_template
        from flask_socketio import SocketIO, emit

        app = Flask(__name__)
        socketio = SocketIO(app)
        @app.route("/")
        def index():
            return render_template('imgloader.html',)

        @app.route("/mod")
        def mod():
            return render_template('mod.html',)

        @socketio.on('image')
        def test_connect(message):
            emit('image', message, broadcast=True)

        socketio.run(app, port=3000)

class trackUserPoints(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        import sqlite3 as lite
        import sys
        with open('bot_config.json') as fp:
            CONFIG = json.load(fp)

        USERLIST_API = "http://tmi.twitch.tv/group/user/{}/chatters".format(CONFIG['channel'])

        conDB = lite.connect('bot.db')

        while True:
            current_users = []
            with conDB:
                cur = conDB.cursor()
                cur.execute("UPDATE UserPoints SET active = 0")
                conDB.commit()
            usrapi = requests.get(url=USERLIST_API)
            usrjson = usrapi.json()['chatters']
            for cat in usrjson:
                for usr in usrjson[cat]:
                    with conDB:
                        cur = conDB.cursor()
                        cur.execute("INSERT OR IGNORE INTO UserPoints(username,active,points,redemption,unmoderated) VALUES(?,?,?,?,?);",\
                                    (str(usr).lower().strip(), 1, 0, 0, 0))
                        cur.execute("UPDATE UserPoints SET active = 1 WHERE username=:username;",\
                                    {"username": str(usr).lower().strip()})
                        conDB.commit()

            with conDB:
                cur = conDB.cursor()
                cur.execute("UPDATE UserPoints SET points = points + 1 WHERE active = 1")
                conDB.commit()
            logging.warning("All active users increased One (1) loyalty point.")
            time.sleep(60)

class BotFactory(protocol.ClientFactory):
    protocol = bot.TwitchBot

    tags = defaultdict(dict)
    activity = dict()
    wait_time = 1

    def clientConnectionLost(self, connector, reason):
        logging.error("Lost connection, reconnecting")
        self.protocol = reload(bot).TwitchBot
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        msg = "Could not connect, retrying in {}s"
        logging.warning(msg.format(self.wait_time))
        time.sleep(self.wait_time)
        self.wait_time = min(512, self.wait_time * 2)
        connector.connect()

if __name__ == "__main__":
    thread = chatSocket()
    thread.daemon = True
    thread.start()
    pthread = trackUserPoints()
    pthread.daemon = True
    pthread.start()
    reactor.connectTCP('irc.twitch.tv', 6667, BotFactory())
    reactor.run()
