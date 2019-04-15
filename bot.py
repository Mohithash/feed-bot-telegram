import signal
from globals import client, bot
from aiogram import executor

from handlers import dp as dispatcher, bc as broadcaster


def run():
    try:
        with client:
            executor.start_polling(dispatcher,
                                   on_startup=broadcaster.start,
                                   on_shutdown=broadcaster.stop)
    finally:
        bot.loop.run_until_complete(bot.close())


def on_sigterm(_, __):
    dispatcher.loop.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, on_sigterm)
    run()
