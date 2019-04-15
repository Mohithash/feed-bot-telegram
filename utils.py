import asyncio
from typing import Callable, Dict

from telethon.errors import RPCError

from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton as Button
from aiogram.types import InlineKeyboardMarkup as Markup

from globals import client, bot, user_id


async def answer(text: str,
                 query: CallbackQuery = None,
                 show_alert: bool = None,
                 parse_mode='Markdown',
                 reply_markup=None):
    if query:
        await query.answer(text, show_alert)
    else:
        await bot.send_message(user_id,
                               text,
                               disable_web_page_preview=True,
                               parse_mode=parse_mode,
                               reply_markup=reply_markup)


async def clean_query(query: CallbackQuery):
    if query.message.reply_to_message:
        await query.message.reply_to_message.delete()
    await query.message.delete()


async def provide_client_connection():
    if not client.is_connected():
        sleep_time = 60
        while 1:
            try:
                await client.connect()
            except (ConnectionError, OSError):
                sleep = asyncio.create_task(asyncio.sleep(sleep_time))
                provide_client_connection.sleep_ls.add(sleep)
                try:
                    await sleep
                except asyncio.CancelledError:
                    provide_client_connection.sleep_ls.remove(sleep)
                    return
            else:
                for sleep in provide_client_connection.sleep_ls:
                    sleep.cancel()
                return


provide_client_connection.sleep_ls = set()


async def get_entity(link: str, type_=None):
    try:
        channel = await client.get_entity(await client.get_input_entity(link))
    except (ValueError, RPCError):
        return None
    if not type_ or isinstance(channel, type_):
        return channel


async def inline_feed_ls(feeds, action: str):
    return Markup(
        1,
        [
            [Button(f[0], callback_data=action + f[1])]
            async for f in (((await get_entity(f)).title, f) for f in feeds)
        ])


async def inline_channel_ls(channels, action: str):
    return Markup(
        1,
        [
            [Button(ch[0], callback_data=action + ch[1])]
            async for ch in
            (((await get_entity(ch)).title, ch) for ch in channels)
        ])


class Signal:
    __slots__ = ['_slots']

    def __init__(self):
        self._slots: Dict[int, Callable[..., None]] = {}

    def __call__(self, *args, **kwargs):
        for s in self._slots.values():
            s(*args, **kwargs)

    def connect(self, slot: Callable[..., None]) -> int:
        self._slots[id(slot)] = slot
        return id(slot)

    def disconnect(self, id_: int):
        del self._slots[id_]

    def disconnect_all(self):
        self._slots.clear()

    def empty(self) -> bool:
        return len(self._slots) == 0

    def num_slots(self) -> int:
        return len(self._slots)
