import os
from aiogram import Bot
from telethon import TelegramClient
from configparser import ConfigParser

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
_cfg = ConfigParser()
if not _cfg.read([DIR_PATH + '/configs.ini']):
    raise SystemError('Error: configs.ini file is missing')
client = TelegramClient(DIR_PATH + '/feed_session',
                        _cfg['CLIENT'].getint('api_id'),
                        _cfg['CLIENT']['api_hash'])
bot = Bot(token=_cfg['BOT']['api_token'])
USER_ID: int = _cfg['USER'].getint('id')
MARK_AS_UNREAD: bool = _cfg['FEED'].getboolean('mark_as_unread')
