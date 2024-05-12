import asyncio
import logging
import sys
import os

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import Update


# session = AiohttpSession(proxy={
#        'http': 'proxy.server:3128',
#        'https': 'proxy.server:3128',
#  })

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.user import UserMiddleware
from tgbot.services.db_observer.loader import start_observers, observers
from cachetools import TTLCache
from tgbot.misc.cache import _cache

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler




def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        UserMiddleware(),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging configurated")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        logging.log(30, config.redis.dsn())
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


def restart_bot():
    logging.info("Перезапуск бота...")
    python = sys.executable
    os.execl(python, python, *sys.argv)
    

class MyFileSystemEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):  # Можно настроить фильтр на конкретные файлы, если нужно
            logging.info("Обнаружено изменение в коде. Перезапуск бота...")
            restart_bot()


async def main():
    setup_logging()


    config = load_config(".env")
    storage = get_storage(config)
    cache = _cache

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config)
    
    await asyncio.gather(
        dp.start_polling(bot, cache = cache, dp = dp),
        start_observers(cache)
    )
   


if __name__ == "__main__":
    config = load_config(".env")
    if config.tg_bot.dev_mode:
        path_to_watch = 'tgbot'
        event_handler = MyFileSystemEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path=path_to_watch, recursive=True)
        observer.start()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped")

    if config.tg_bot.dev_mode:
        observer.stop()
        observer.join()
