from __future__ import annotations
from typing import Callable

from utils import Signal

try:
    import ujson as json
except ImportError:
    import json


class Database:
    __slots__ = ['_path', '_signal', '_db']

    def __init__(self, path: str):
        self._path = path
        self._signal = Signal()
        self._db: list = self._load_db()

    def __contains__(self, link):
        return link in self._db

    def __getitem__(self, key):
        return self._db[key]

    def __iter__(self):
        return self._db.__iter__()

    def add(self, link: str, last_id: int, feed: str):
        self._db.append(_DBRecord(link, last_id, feed))
        self.flush()
        self._publish('add', link)

    def remove(self, link: str):
        self._db.remove(link)
        self.flush()
        self._publish('remove', link)

    def flush(self):
        with open(self._path, 'w') as db:
            json.dump([[r.link, r.last_id, r.feed] for r in self._db], db)

    def subscribe(self, receiver: Callable[[str, str], None]):
        self._signal.connect(receiver)

    def sort(self):
        self._db.sort()

    def _publish(self, event: str, link: str):
        self._signal(event, link)

    def _load_db(self) -> list:
        try:
            with open(self._path) as db:
                return [_DBRecord(r[0], r[1], r[2]) for r in json.load(db)]
        except FileNotFoundError:
            return []


class _DBRecord:
    __slots__ = ['link', 'last_id', 'feed']

    def __init__(self, link: str, last_id: int, feed: str):
        self.link = link
        self.last_id = last_id
        self.feed = feed

    def _cmp_key(self) -> tuple:
        return self.feed, self.link

    def __lt__(self, other: _DBRecord):
        return self._cmp_key() < other._cmp_key()

    def __eq__(self, link):
        return self.link == link
