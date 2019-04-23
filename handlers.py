from html import escape
from aiogram import Dispatcher
from telethon.tl.types import Channel
from telethon.errors import ChannelPrivateError, RPCError

from database import Database
from broadcaster import Broadcaster
from globals import client, bot, DIR_PATH
from filters import *
from utils import get_entity, answer, provide_client_connection, \
    inline_feed_ls, inline_channel_ls, clean_query, get_title

dp = Dispatcher(bot)
db = Database(DIR_PATH + '/database.json')
bc = Broadcaster(db)
db.subscribe(bc)

# region Message handlers


@dp.message_handler(from_me, commands=['start'])
async def start(message: types.Message):
    await answer('Hello ' + message.from_user.first_name + '\n'
                 + 'Use /addfeed <link_to_channel> to add channel which will '
                 + 'serve as your feed.\nThen send me a link to '
                 + 'channel you want to add to your feed or use /add '
                 + '<link_to_channel>.\n You can add as many feeds and '
                 + 'channels as you wish. Use /help for additional commands',
                 parse_mode=None)


@dp.message_handler(from_me, commands=['help'])
async def help_(_: types.Message):
    await answer('/addfeed <link> - add channel which will serve as feed\n'
                 '/add <link> - add channel to feed\n'
                 '<link> - same as /add <link>\n'
                 '/rm - remove channel from feed\n'
                 '/rmfeed - remove feed from database\n'
                 '/ls - list feeds and channels of each feed\n'
                 '/help - list all commands')


@dp.message_handler(from_me, channel_link, commands=['addfeed'])
async def add_feed(_: types.Message, link: str):
    await provide_client_connection()
    if link in db.feeds():
        await answer('Already in database')
        return
    if db.channel_exists(link):
        await answer('This channel was already added to one of your feeds. '
                     'You can\'t add it as feed')
        return
    channel = await get_entity(link, Channel)
    if not channel:
        await answer('Not a channel')
        return
    if not channel.creator:
        await answer('User account used by bot have to be creator of channel')
    else:
        db.add_feed(link)
        feed_title = await get_title(link)
        await answer(f"Successfully added '{feed_title}' to database")


@dp.message_handler(from_me, channel_link, commands=['add'])
@dp.message_handler(from_me, not_command, channel_link)
async def add_channel(message: types.Message, link: str):
    await provide_client_connection()
    if link in db.feeds():
        await answer('This channels serves as one of your feeds. You can\'t '
                     'add it')
        return
    if not db.feeds():
        await answer('You have to add feed first')
    elif len(db.feeds()) > 1:
        await message.reply(
            'Choose feed:',
            reply_markup=await inline_feed_ls(db.feeds(), ADD_CHANNEL))
    else:
        feed = list(db.feeds())[0]
        await _add_channel(link, feed)


@dp.message_handler(from_me, commands=['rm'])
async def remove_channel(_: types.Message):
    await provide_client_connection()
    if not db.feeds():
        await answer('No feed have been added yet')
    elif len(db.feeds()) > 1:
        await answer('Choose feed:',
                     reply_markup=await inline_feed_ls(db.feeds(),
                                                       RM_CH_STEP1))
    else:
        feed = list(db.feeds())[0]
        if db.feed_nonempty(feed):
            await answer(
                f'{feed}\nChoose channel: ',
                reply_markup=await inline_channel_ls(
                    db.channels_of_feed(feed), RM_CH_STEP2))
        else:
            await answer('No channels in this feed')


@dp.message_handler(from_me, commands=['rmfeed'])
async def remove_feed(_: types.Message):
    await provide_client_connection()
    if db.feeds():
        await answer('Choose feed:',
                     reply_markup=await inline_feed_ls(db.feeds(),
                                                       REMOVE_FEED))
    else:
        await answer('No feed have been added yet')


@dp.message_handler(from_me, commands=['ls'])
async def list_channels(_: types.Message):
    await provide_client_connection()
    ch_list = ''
    for feed in db.feeds():
        title = escape(await get_title(feed))
        ch_list += f'<a href="{feed}">{title}</a>\n'
        for channel in db[feed].keys():
            title = escape(await get_title(channel))
            ch_list += f'<b>--</b> <a href="{channel}">{title}</a>\n'
    await answer(ch_list or 'Feed list is empty', parse_mode='HTML')

# endregion

# region CallbackQuery handlers


@dp.callback_query_handler(query_valid, query_add_channel, query_feed_link)
async def add_channel_query(query: types.CallbackQuery, feed: str):
    link = re.sub('/+$', '', query.message.reply_to_message.get_args() or
                  query.message.reply_to_message.text)
    await _add_channel(link, feed, query)
    await clean_query(query)


@dp.callback_query_handler(query_valid,
                           query_remove_channel_step1,
                           query_feed_link)
async def rm_channel_step1_query(query: types.CallbackQuery, feed: str):
    if db.feed_nonempty(feed):
        await query.message.reply(
            f'{feed}\nChoose channel: ',
            reply_markup=await inline_channel_ls(db.channels_of_feed(feed),
                                                 RM_CH_STEP2))
        await query.answer()
    else:
        await query.answer('No channels in this feed', show_alert=True)
        await clean_query(query)


@dp.callback_query_handler(query_valid,
                           query_remove_channel_step2,
                           query_channel_link)
async def rm_channel_step2_query(query: types.CallbackQuery, link: str):
    feed = re.search(t_link, query.message.text, re.IGNORECASE)[0]
    await _remove_channel(link, feed, query)
    await clean_query(query)


@dp.callback_query_handler(query_valid, query_remove_feed, query_feed_link)
async def remove_feed_query(query: types.CallbackQuery, feed: str):
    db.remove_feed(feed)
    await query.answer(f"'{await get_title(feed)}' successfully removed from"
                       f" database",
                       show_alert=True)
    await clean_query(query)

# endregion


async def _remove_channel(link: str,
                          feed: str,
                          query: types.CallbackQuery = None):
    if query or db.channel_exists(link, feed):
        db.remove_channel(link, feed)
        await answer('Successfully removed channel from feed', query)
    else:
        await answer(f'No channel with such link in feed', query)


async def _add_channel(link: str,
                       feed: str,
                       query: types.CallbackQuery = None):
    channel = await get_entity(link, Channel)
    if not channel:
        await answer('Not a channel', query, show_alert=True)
        return
    if db.channel_exists(link, feed):
        await answer('This channel is already in feed', query, True)
        return
    try:
        msgs = await client.get_messages(channel, 1)
    except ChannelPrivateError:
        await answer('Channel is private', query, show_alert=True)
    except RPCError as e:
        await answer(e.message + '\nerror code: ' + str(e.code), query, True)
    else:
        db.add_channel(link, msgs[0].id, feed)
        await answer(f'Successfully added channel to '
                     f'{await get_title(feed)}',
                     query)
