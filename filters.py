import re
from aiogram import types
from globals import user_id

# region InlineButton action types

ADD_CHANNEL = '01'
RM_CH_STEP1 = '02'
RM_CH_STEP2 = '03'
REMOVE_FEED = '04'

# endregion

t_link = r'https?:\/\/(t(elegram)?\.me|telegram\.org)(\/joinchat)?' \
         r'\/([a-z0-9\_]{5,32})'

# region Message filters


async def from_me(message: types.Message):
    return message.from_user.id == user_id


async def not_command(message: types.Message):
    return not message.get_command()


async def channel_link(message: types.Message):
    valid_link = re.fullmatch(t_link,
                              message.get_args() or message.text,
                              re.IGNORECASE)
    if valid_link:
        return {'link': valid_link[0]}

# endregion

# region CallbackQuery filters


async def query_valid(query: types.CallbackQuery):
    return query.from_user.id == user_id and query.message


async def query_channel_link(query: types.CallbackQuery):
    return {'link': query.data[2:]}


async def query_feed_link(query: types.CallbackQuery):
    return {'feed': query.data[2:]}


async def query_add_channel(query: types.CallbackQuery):
    return query.data.startswith(ADD_CHANNEL)


async def query_remove_channel_step1(query: types.CallbackQuery):
    return query.data.startswith(RM_CH_STEP1)


async def query_remove_channel_step2(query: types.CallbackQuery):
    return query.data.startswith(RM_CH_STEP2)


async def query_remove_feed(query: types.CallbackQuery):
    return query.data.startswith(REMOVE_FEED)

# endregion
