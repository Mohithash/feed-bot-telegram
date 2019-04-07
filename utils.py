import asyncio
from typing import Callable, Dict
from telethon.errors import RPCError
from globals import client, bot, user_id


async def answer(text: str, parse_mode='Markdown'):
    await bot.send_message(user_id,
                           text,
                           disable_web_page_preview=True,
                           parse_mode=parse_mode)


async def provide_client_connection():
    if not client.is_connected():
        sleep_time = 10
        while 1:
            try:
                await client.connect()
            except (ConnectionError, OSError):
                await asyncio.sleep(sleep_time)
                sleep_time *= 1.5
            else:
                return


async def get_entity(type_, link: str):
    try:
        channel = await client.get_entity(link)
    except (ValueError, RPCError):
        return None
    if isinstance(channel, type_):
        return channel


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

    def disconnect(self, id: int):
        del self._slots[id]

    def disconnect_all(self):
        self._slots.clear()

    def empty(self) -> bool:
        return len(self._slots) == 0

    def num_slots(self) -> int:
        return len(self._slots)
