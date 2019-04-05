import asyncio
from collections import OrderedDict, namedtuple

from telethon.tl.types import Message
from telethon.errors import RPCError, ChannelPrivateError
from telethon.tl.functions.messages import MarkDialogUnreadRequest

from database import Database
from utils import answer
from globals import client, mark_as_unread


class Broadcaster:
    __slots__ = ['_db', '_queue', '_current']

    _Task = namedtuple('Task', ['link', 'task'])

    def __init__(self, db: Database):
        self._db = db
        self._queue = OrderedDict()
        self._current = None

    def __call__(self, event: str, link: str):
        if event == 'add':
            self._add_to_queue(self._db[-1])
            if not self._current:
                self._new_task()
        elif event == 'remove':
            if link in self._queue:
                self._queue.pop(link).close()
            else:
                self._current = None

    async def start(self, _=None):
        for rec in self._db:
            self._add_to_queue(rec)
        self._new_task()

    async def stop(self, _=None):
        if not self._current:
            return
        self._current.task.remove_done_callback(self._new_task)
        try:
            await asyncio.wait_for(self._current.task, timeout=1)
        except asyncio.TimeoutError:
            pass
        finally:
            for coro in self._queue.values():
                coro.close()
            self._queue.clear()
        self._current = None
        self._db.flush()

    async def _forward(self, rec):
        msgs = await self._messages(rec)
        if msgs:
            try:
                await client.forward_messages(rec.feed, msgs)
            except ConnectionError:
                await asyncio.sleep(60)
            except RPCError as e:
                await answer(f'RPCError occurred while forwarding messages'
                             f' from [channel]({rec.link}) to'
                             f' [feed]({rec.feed}): '
                             + e.message
                             + '\nerror code ->'
                             + str(e.code))
            else:
                rec.last_id = msgs[-1].id
                self._db.flush()
            if mark_as_unread:
                await client(MarkDialogUnreadRequest(rec.feed, True))
        return await asyncio.sleep(len(msgs) or 1, rec)

    async def _messages(self, rec):
        msgs = []
        try:
            msgs = await client.get_messages(rec.link,
                                             500,
                                             min_id=rec.last_id,
                                             wait_time=5,
                                             reverse=True)
        except ConnectionError:
            await asyncio.sleep(60)
        except (ValueError, ChannelPrivateError):
            await answer('Channel is no longer available by this link -> '
                         + rec.link
                         + f'\nAnd will be removed from [feed]({rec.feed})')
            self._db.remove(rec.link)
        except RPCError as e:
            await answer(f'RPCError occurred while getting new messages from'
                         f' [channel]({rec.link}): '
                         + e.message
                         + '\nerror code ->'
                         + str(e.code))
        return [m for m in msgs if isinstance(m, Message)]

    # TODO async def _forward_albums(self, msgs: TotalList):

    def _add_to_queue(self, rec):
        self._queue[rec.link] = self._forward(rec)

    def _new_task(self, future=None):
        if self._current:
            self._add_to_queue(future.result())
        if self._queue:
            link, coro = self._queue.popitem(last=False)
            self._current = self._Task(link, asyncio.create_task(coro))
            self._current.task.add_done_callback(self._new_task)
