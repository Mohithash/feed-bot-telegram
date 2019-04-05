import os
from aiogram import Bot
from telethon import TelegramClient
from configparser import ConfigParser

dir_path = os.path.dirname(os.path.realpath(__file__))
_cfg = ConfigParser()
if not _cfg.read([dir_path + '/configs.ini']):
    raise SystemError('Error: configs.ini file is missing')
client = TelegramClient(dir_path + '/feed_session',
                        _cfg['CLIENT'].getint('api_id'),
                        _cfg['CLIENT']['api_hash'])
bot = Bot(token=_cfg['BOT']['API_TOKEN'])
user_id: int = _cfg['USER'].getint('id')
mark_as_unread: bool = _cfg['FEED'].getboolean('mark_as_unread')
