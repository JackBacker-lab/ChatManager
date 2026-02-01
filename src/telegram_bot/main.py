import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.session.middlewares.request_logging import RequestLogging
from aiogram.enums import ParseMode
from aiogram.methods import GetUpdates

from telegram_bot.config import load_config
from telegram_bot.handlers import routers
from telegram_bot.i18n import load_i18n
from telegram_bot.repositories import init_db


async def main() -> None:
    """Start the bot and run the polling event loop.

    Initialize configuration, dependencies, and handlers before processing updates.
    """
    config = load_config()
    await init_db()
    load_i18n()

    session = AiohttpSession()
    session.middleware(RequestLogging(ignore_methods=[GetUpdates]))

    bot = Bot(
        token=config.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    for router in routers:
        dp.include_router(router)

    await dp.start_polling(bot)  # type: ignore[reportUnknownMemberType]


def run() -> None:
    """Synchronous entry point used by the console script."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


if __name__ == "__main__":
    run()
