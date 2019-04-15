from __future__ import annotations
from typing import Callable, Dict
from collections import namedtuple

from utils import Signal

try:
    import ujson as json
except ImportError:
    import json


class Channel(list):
    __slots__ = []

    def __init__(self, link: str, last_id: int, feed: str):
        super().__init__([link, last_id, feed])

    @property
    def link(self):
        return self[0]

    @property
    def last_id(self):
        return self[1]

    @last_id.setter
    def last_id(self, id_: int):
        self[1] = id_

    @property
    def feed(self):
        return self[2]


class Database:
    __slots__ = ['_path', '_signal', '_db']

    Event = namedtuple('Event', ['type', 'feed', 'link'])

    def __init__(self, path: str):
        self._path = path
        self._signal = Signal()
        self._db = self._load_db()

    def __getitem__(self, key):
        return self._db[key]

    def feeds(self):
        return self._db.keys()

    def channels(self):
        return (ch for chs in self._db.values() for ch in chs.values())

    def channels_of_feed(self, feed: str, links: bool = True):
        origin = self._db[feed].keys if links else self._db[feed].values
        return (ch for ch in origin())

    def add_feed(self, link: str):
        self._db[link] = {}
        self.flush()

    def add_channel(self, link: str, last_id: int, feed: str):
        self._db[feed][link] = Channel(link, last_id, feed)
        self.flush()
        self._publish(self.Event('add', feed, link))

    def remove_channel(self, link: str, feed: str):
        del self._db[feed][link]
        self.flush()
        self._publish(self.Event('remove', feed, link))

    def remove_feed(self, feed: str):
        for link in self._db[feed].keys():
            self._publish(self.Event('remove', feed, link))
        del self._db[feed]
        self.flush()

    def feed_nonempty(self, feed: str):
        return bool(self._db[feed].keys())

    def feed_exists(self, link: str):
        return link in self._db.keys()

    def channel_exists(self, link: str, feed: str = None):
        return link in self._db[feed].keys() if feed else any(
            link in chs.keys() for chs in self._db.values())

    def flush(self):
        with open(self._path, 'w') as db:
            json.dump(self._db, db)

    def subscribe(self, receiver: Callable[[Database.Event], None]):
        self._signal.connect(receiver)

    def _publish(self, event: Database.Event):
        self._signal(event)

    def _load_db(self) -> Dict[str, Dict[str, Channel]]:
        try:
            with open(self._path) as db:
                _db = json.load(db)
                for channels in _db.values():
                    for link in channels.keys():
                        channels[link] = Channel(*channels[link])
                return _db
        except FileNotFoundError:
            return {}
