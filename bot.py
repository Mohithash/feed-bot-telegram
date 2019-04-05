import re
import signal

from globals import client, bot, user_id, dir_path
from utils import get_entity, answer, provide_client_connection
from database import Database
from broadcaster import Broadcaster

from telethon.errors import ChannelPrivateError
from telethon.errors import RPCError
from telethon.tl.types import Channel

from aiogram import Dispatcher, executor, types
from aiogram.dispatcher.filters import RegexpCommandsFilter

dp = Dispatcher(bot)
db = Database(dir_path + '/database.json')
bc = Broadcaster(db)
db.subscribe(bc)
current_feed = ''
t_link = r'https?:\/\/(t(elegram)?\.me|telegram\.org)\/([a-z0-9\_]{5,32})\/?'

# region Filters


async def from_me(message: types.Message):
    return message.from_user.id == user_id


async def not_command(message: types.Message):
    return not message.get_command()

# endregion

# region Handlers


@dp.message_handler(from_me, commands=['help'])
@dp.message_handler(from_me, commands=['start'])
async def hello_help(message: types.Message):
    await answer('Hello ' + message.from_user.first_name + '\n'
                 + '/set <link> - set channel as feed to add channels to\n'
                 + '/now - display current feed\n'
                 + '/add <link> - add channel to current feed\n'
                 + '<link> - same as /add <link>\n'
                 + '/rm <link> - remove channel from feed\n'
                 + '/ls - list channels in feeds\n\n'
                 + 'You can\'t add same channel to several feeds\n'
                 + 'So you don\'t need to specify feed to remove channel')


@dp.message_handler(RegexpCommandsFilter(regexp_commands=[t_link]),
                    from_me,
                    commands=['set'])
async def set_feed(message: types.Message):
    await provide_client_connection()
    link = re.sub('/+$', '', message.get_args())
    channel = await get_entity(Channel, link)
    if not channel:
        await answer('Not a channel')
        return
    if not channel.creator:
        await answer('You have to be creator of channel to set it as feed')
    else:
        global current_feed
        current_feed = link
        await answer('Successfully set feed ' + link)


@dp.message_handler(from_me, commands=['now'])
async def feed_now(_: types.Message):
    if current_feed:
        await answer('Feed now set to ' + current_feed)
    else:
        await answer('You haven\'t set feed yet')


@dp.message_handler(RegexpCommandsFilter(regexp_commands=[t_link]),
                    from_me,
                    commands=['add'])
@dp.message_handler(not_command, from_me, regexp=t_link)
async def add_channel(message: types.Message):
    await provide_client_connection()
    if not current_feed:
        await answer('You have to set feed first')
        return
    link = re.sub('/+$', '', message.get_args() or message.text)
    channel = await get_entity(Channel, link)
    if not channel:
        await answer('Not a channel')
        return
    if link in db:
        await answer('This channel is already in one of your feeds')
        return
    try:
        msgs = await client.get_messages(channel, 1)
    except ChannelPrivateError:
        await answer('Channel is private')
    except RPCError as e:
        await answer(e.message + '\nerror code: ' + str(e.code))
    else:
        db.add(link, msgs[0].id, current_feed)
        await answer(f'Successfully added channel to [feed]({current_feed})')


@dp.message_handler(RegexpCommandsFilter(regexp_commands=[t_link]),
                    from_me,
                    commands=['rm'])
async def remove_channel(message: types.Message):
    try:
        db.remove(re.sub('/+$', '', message.get_args()))
    except ValueError:
        await answer('No channel with such link in feed')
    else:
        await answer('Successfully removed channel from feed')


@dp.message_handler(from_me, commands=['ls'])
async def list_channels(_: types.Message):
    await provide_client_connection()
    db.sort()
    channels = ''
    feed = ''
    for r in db:
        if feed != r.feed:
            feed = r.feed
            feed_title = (await client.get_entity(
                await client.get_input_entity(r.feed))).title
            channels += feed_title + '\n'
        channel_title = (await client.get_entity(
            await client.get_input_entity(r.link))).title
        channels += f"'{channel_title}'" \
                    + ' ' \
                    + f'[link]({r.link})' + '\n'

    await answer(channels or 'Channels list is empty')

# endregion


def run():
    try:
        with client:
            executor.start_polling(dp,
                                   skip_updates=True,
                                   on_startup =bc.start,
                                   on_shutdown=bc.stop)
    finally:
        bot.loop.run_until_complete(bot.close())


def on_sigterm(_, __):
    dp.loop.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, on_sigterm)
    run()
