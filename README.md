**PixToChatBot**
===============

This is a Twitch IRC Bot based on Ehsankia's SimpleTwitchBot written in Python.
It is mostly hacked together to offer a means of using RevloBot currency [Revlo.co](https://www.revlo.co) to allow user generated/sourced
content in your stream.

If you like what you see here, go checkout [SimpleTwitchBot](https://github.com/EhsanKia/SimpleTwitchBot)
If you want something even more barebone than that, checkout [BareboneTwitchBot](https://github.com/EhsanKia/BareboneTwitchBot).

# Installation and usage
You will need Python 2.7+ with [Twisted](https://twistedmatrix.com/trac/), [Revlo](https://github.com/teamrevlo/revlo-python-client), [Flask](https://pypi.python.org/pypi/Flask/0.12), and [SocketIO](https://pypi.python.org/pypi/python-socketio) installed.
You then copy this project in a folder, configure the bot and run `twitch_irc.py`.

#### Configuration:
Make sure to modify the following values in `bot_config.json`:
- `channel`: Twitch channel which the bot will run on
- `username`: The bot's Twitch user
- `oauth_key`: IRC oauth_key for the bot user (from [here](http://twitchapps.com/tmi/))
- `owner_list`: List of Twitch users which have admin powers on bot
- `revlo_key`: Your RevloBot API key (from [here](https://www.revlo.co/settings/api))
- `ignore_list`: List of Twitch users which will be ignored by the bot

**Warning**: Make sure all channel and user names above are in lowercase.

#### Usage:
The main command-line window will show chat log and other extra messsages.

You can enter commands by pressing CTRL+C on the command line:
- `q`: Closes the bot
- `r`: Reloads the code in `bot.py` and reconnects
- `ra`: reloads the code in `commands.py` and reloads commands
- `p`: Pauses bot, ignoring commands from non-admins
- `t <msg>`: Runs a test command with the bot's reply not being sent to the channel
- `s <msg>`: Say something as the bot in the channel

As you can see, the bot was made to be easy to modify live.
You can simply modify most of the code and quickly reload it.
The bot will also auto-reconnect if the connection is lost.

Of note for the RevloBot images to work are the OBS embed that will be found at http://localhost:3000/
and the Moderation page found at http://localhost:3000/mod once the bot is up and running.

# Code Overview

#####`twitch_irc.py`
This is the file that you run. It just starts up a Twisted IRC connection with the bot protocol.
The bot is currently built to only run in one channel, but you can still open all the files over
to another folder with a different config and run it in parallel.

#####`bot.py`
Contains the bot IRC protocol. The main guts of the bot are here.

#####`commands.py`
This is where the commands are stored. The code is built to be modular.
Each "Command" class has:
- `perm` variable from the Permission Enum to set access level
- `__init__` function that initializes the command
- `match` function that checks if this command needs to run
- `run` function which actually runs the command
- `close` function which is used to cleanup and save things

All commands are passed the bot instance where they can get list of mods, subs and active users.
`match` and `run` are also passed the name of the user issuing the command and the message.
