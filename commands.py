from threading import Thread
from revlo.client import RevloClient
import json
import time
import random
import re

global raffleEntrants
global runningRaffle
raffleEntrants = []
runningRaffle = 0

with open('bot_config.json') as fp:
    CONFIG = json.load(fp)

# Set of permissions for the commands
class Permission:
    User, Subscriber, Moderator, Admin = range(4)

# Base class for a command
class Command(object):
    perm = Permission.Admin

    def __init__(self, bot):
        pass

    def match(self, bot, user, msg):
        return False

    def run(self, bot, user, msg):
        pass

    def close(self, bot):
        pass


class EnterRaffle(Command):
    '''Enter a raffle. We re-init on every raffle run,
    so it's only valid to enter while a raffle is
    running'''

    perm = Permission.User

    def match(self, bot, user, msg):
        return msg.lower().startswith("!enter")

    def run(self, bot, user, msg):
        global runningRaffle
        global raffleEntrants
        rafUser = user.lower().strip()

        if rafUser not in raffleEntrants and runningRaffle > 0:
            raffleEntrants.append(rafUser)
        elif runningRaffle is 0:
            bot.write("No Raffle is currently open {}, try again later?".format(rafUser))
        else:
            bot.write("{} has already entered.".format(rafUser))

class PixToChat(Command):
    '''Send an image to chat'''

    perm = Permission.User

    def match(self, bot, user, msg):
        regexcheck = re.compile(r'^\!pix2chat\ (http(?:|s)://i.imgur.com.*(?:.png|.jpg|.gif))$')
        if regexcheck.search(msg):
            return True
        else:
            if msg.lower().startswith("!pix2chat"):
                bot.write("Hey {}, you have to submit an Imgur link with that command".format(picUser))
            return False

    def run(self, bot, user, msg):
        regexcheck = re.compile(r'^\!pix2chat\ (http(?:|s)://i.imgur.com.*(?:.png|.jpg|.gif))$')
        url = regexcheck.match(msg).group(1)
        picUser = user.lower().strip()
        pointsRedeem = 120
        redeem = False
        revkey = CONFIG['revlo_key']
        client = RevloClient(api_key=revkey)
        userPoints = client.get_loyalty(picUser)['loyalty']['current_points']
        if userPoints >= pointsRedeem:
            try:
                redeem = client.bonus(picUser, -pointsRedeem)
            except:
                bot.write("I'm sorry {}. I was unable to redeem your points. Please try again.".format(picUser))
        else:
            bot.write("Sorry {}, you haven't got the {} points needed to PixtoChat".format(picUser,pointsRedeem))
            redeem = False
        if redeem:
            bot.sendimgurmsg(user, url)
            bot.write("{} has redeemed a PixtoChat image!".format(picUser))


class SimpleReply(Command):
    '''Simple meta-command to output a reply given
    a specific command. Basic key to value mapping.'''

    perm = Permission.User

    replies = {
        "!ping": "pong",
        "!headset": "Logitech G930 Headset",
        "!rts": "/me REAL TRAP SHIT",
        "!nfz": "/me NO FLEX ZONE!",
    }

    def match(self, bot, user, msg):
        cmd = msg.lower().strip()
        for key in self.replies:
            if cmd == key:
                return True
        return False

    def run(self, bot, user, msg):
        cmd = msg.lower().strip()

        for key, reply in self.replies.items():
            if cmd == key:
                bot.write(reply)
                break


class General(Command):
    '''Some miscellaneous commands in here'''
    perm = Permission.User

    def match(self, bot, user, msg):
        cmd = msg.lower()
        if cmd.startswith("!active"):
            return True
        return False

    def run(self, bot, user, msg):
        reply = None
        cmd = msg.lower()

        if cmd.startswith("!active"):
            active = len(bot.get_active_users())
            if active == 1:
                reply = "{}: There is {} active user in chat"
            else:
                reply = "{}: There are {} active users in chat"
            reply = reply.format(user, active)

        if reply:
            bot.write(reply)


class Raffle(Command):
    '''Start a raffle that will be run in x seconds.'''
    perm = Permission.Moderator

    def match(self, bot, user, msg):
        return msg.lower().startswith("!raffle")

    def run(self, bot, user, msg):
        cmd = msg.lower()
        if cmd == "!raffle":
            bot.write("Usage: !raffle 300s")
            return

        arg = cmd[8:].replace(' ', '')
        match = re.match("([\d\.]+)([sm]).*", arg)
        if match and runningRaffle is not 1:
            d, u = match.groups()
            t = float(d) * (60 if u == 'm' else 1)
            thread = RaffleThread(bot, user, t)
            thread.start()
        elif runningRaffle > 0:
            bot.write("Sorry {}, you can't start a raffle when one is already running".format(user))
        else:
            bot.write("{}: Invalid argument".format(user))


class RaffleThread(Thread):
    def __init__(self, b, u, t):
        Thread.__init__(self)
        self.bot = b
        self.user = u
        if int(t) < 10:
            self.time = int(t) + 10
        else:
            self.time = int(t)

    def run(self):
        global raffleEntrants
        global runningRaffle
        cd = 10
        msg = "{} started a raffle. Type '!enter' (sans apostrophes) to enter the raffle.".format(self.user)
        randomHurry = ["hurry up!", "be quick about it!", "get a move on!", "move like lightning!", "make haste!",
                       "shake a leg!", "step on it!", "put the pedal to the metal!", "get the lead out!", "chop chop!",
                       "get your wiggle on!", "let's go!", "don't take all day!", "with a hustle please!",
                       "arriba, arriba, andale, andale!", "you haven't got all day!", "don't be fooling around now!",
                       "time's a-wasting!", "less Pokey, more PK Rockin!"]
        random.shuffle(randomHurry)
        raffleEntrants = []
        runningRaffle = 1
        self.bot.write(msg)
        time.sleep(self.time - cd)
        while cd:
            if cd > 1:
                self.bot.write("{} seconds left, {}".format(cd,randomHurry[cd]))
                cd -= 1
                time.sleep(1)
            else:
                self.bot.write("{} second left, you're probably too late at this point but TriHard anyway.".format(cd))
                cd -= 1
                time.sleep(1)
        if not raffleEntrants:
            runningRaffle = 0
            msg = "Nobody entered the raffle. :( Congratulations, you're all losers!"
        else:
            runningRaffle = 0
            msg = "{} is the winner of this raffle. Congratulations!".format(random.choice(raffleEntrants))
        self.bot.write(msg)


class Timer(Command):
    '''Sets a timer that will alert you when it runs out'''
    perm = Permission.Moderator

    def match(self, bot, user, msg):
        return msg.lower().startswith("!timer")

    def run(self, bot, user, msg):
        cmd = msg.lower()
        if cmd == "!timer":
            bot.write("Usage: !timer 30s or !timer 5m")
            return

        arg = cmd[7:].replace(' ', '')
        match = re.match("([\d\.]+)([sm]).*", arg)
        if match:
            d, u = match.groups()
            t = float(d) * (60 if u == 'm' else 1)
            thread = TimerThread(bot, user, t)
            thread.start()
        elif arg.isdigit():
            thread = TimerThread(bot, user, int(arg) * 60)
            thread.start()
        else:
            bot.write("{}: Invalid argument".format(user))


class TimerThread(Thread):
    def __init__(self, b, u, t):
        Thread.__init__(self)
        self.bot = b
        self.user = u
        self.time = int(t)

    def run(self):
        secs = self.time % 60
        mins = self.time / 60

        msg = "{}: Timer started for".format(self.user)
        if mins > 0:
            msg += " {}m".format(mins)
        if secs > 0:
            msg += " {}s".format(secs)

        self.bot.write(msg)
        time.sleep(self.time)
        self.bot.write("{}: Time is up!".format(self.user))


class OwnerCommands(Command):
    '''Some miscellaneous commands for bot owners'''

    perm = Permission.Admin

    def match(self, bot, user, msg):
        cmd = msg.lower().replace(' ', '')
        if cmd.startswith("!sleep"):
            return True
        elif cmd.startswith("!wakeup"):
            return True

        return False

    def run(self, bot, user, msg):
        cmd = msg.lower().replace(' ', '')
        if cmd.startswith("!sleep"):
            bot.write("Going to sleep... bye!")
            bot.pause = True
        elif cmd.startswith("!wakeup"):
            bot.write("Good morning everyone!")
            bot.pause = False
