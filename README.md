# Feed bot

Feed bot is an asynchronous telegram bot written in python 3.7, using [telethon](https://github.com/LonamiWebs/Telethon) 
and [aiogram](https://github.com/aiogram/aiogram)

## Getting Started

This bot can forward messages from all your public channels to channel you set as your feed, thus making your chat list clean.
You can have several feeds if you wish to. Bot was created for personal use, i.e. bot works only for one telegram user 
and you have to run bot yourself on your PC/VPS etc. Bot should work fine in most cases, but some errors may still occur.

### Prerequisites

First of all, you need three things: 1) your app api_id and api_hash for telegram account to be used by bot, you can get them 
[here](https://my.telegram.org/apps); 2) your bot api token, you can get it by creating bot account using 
[@BotFather](https://t.me/BotFather), BotFather will give you a link to your bot as well; 3) telegram id of your main 
telegram account (feed bot will only respond to messages  that come from this telegram account, i.e. that have this 
telegram id), you can get it, for example, by writing to [@userinfobot](https://t.me/userinfobot) bot.

It is recommended to use a second telegram account for bot. In that case you don't need to get api_id, api_hash for your 
main account and your feed will have unread messages count.

In case you use only one account, both for yourself and for bot, your feed won't have unread messages count and there 
won't be any notifications for updates. But there is an option to make bot mark feed as unread, when updates come. 
You can turn this option on by editing *configs.ini*.

After that, you need to have python3 (>=3.7) installed to run the bot. You can google it, or use 
[this](https://realpython.com/installing-python/) or [this](https://www.python.org/downloads/)

### Installing

Download feed bot from github or use *git clone*. Then use terminal and *cd* to feed bot directory:

```bash
cd path/to/feed-bot-telegram
```
After that use *pip* or *pip3* to install required dependencies:

```bash
pip install -r requirements.txt
```
For best experience install optional dependencies:

```bash
pip install -r optional-requirements.txt
```
Now edit *configs.ini* with your preferred text editor and write your api_id, api_hash of telegram account to be used by bot, 
your bot account api token and telegram id of your main telegram account.

If you want to make bot mark feed as unread, when updates come, change *mark_as_unread = no* to *mark_as_unread = yes*.

Now bot is configured and ready to be run.

## Running bot

You can run bot with python3 like this:

```bash
cd path/to/feed-bot-telegram
python3 bot.py
```
You will be prompted to enter telephone number of telegram account for which you got api_id and api_hash. Bot will create 
active telegram session the same way it happens with standard telegram app. Bot will save session data to file 
*feed_session.session* in bot directory. Unless you delete this file or terminate session from telegram app, you won't
be prompted to enter telephone number anymore.

Press **Ctrl+C** to live python interpreter and stop bot.

If you have no Internet when starting bot, bot won't start.

You can use *run_bot.sh*, if you have *bash* installed. run_bot.sh will start bot after 60 seconds. It is a bash script that 
will keep bot running until you shutdown system. If critical error occurs (for example, no Internet connection) bot stops, 
in that case run_bot.sh will restart bot after 60 seconds. You can change time by editing this line *sleep 60 & wait* 
in run_bot.sh.

There are many ways to make bash script (*run_bot.sh*) or python script (*bot.py*) run at system startup, depending on your 
system. [google](https://www.google.com) may help to find that out.

## Usage

Start conversation with your feed bot. Bot will answer:

```
Use /addfeed <link_to_channel> to add channel which will serve as your feed.
Then send me a link to channel you want to add to your feed or use /add <link_to_channel>.
You can add as many feeds and channels as you wish. Use /help for additional commands
```
Create private channel which will serve as feed. Then use */addfeed* to add this channel as feed:

![add feed example](https://user-images.githubusercontent.com/42914399/56163318-b4a71680-5fd6-11e9-9aed-1e081d2b64f3.png)

Then send bot a link to a public channel you wish to add to feed or use */add*. For example:

![add channel example1](https://user-images.githubusercontent.com/42914399/56162227-2c277680-5fd4-11e9-8d26-a366db538892.png)

If you have added several feeds, you will be prompted to choose feed:

![add channel example2](https://user-images.githubusercontent.com/42914399/56162468-c1c30600-5fd4-11e9-9426-2fbce45a9784.png)

*/help* will show you all available commands:

```
/addfeed <link> - add channel which will serve as feed
/add <link> - add channel to feed
<link> - same as /add <link>
/rm - remove channel from feed
/rmfeed - remove feed from database
/ls - list feeds and channels of each feed
```
If you use a separate telegram account for bot, you have to create channel which will serve as feed from that account and 
add your main telegram user to this channel.

If you want the list of commands to be shown the same way it happens with usual bots, write */setcommands* to 
[@BotFather](https://t.me/BotFather). For example:
```
/addfeed - /addfeed
/add - /add
/rm - /rm
/rmfeed - /rmfeed
/ls - /ls
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
