import logging

from telegram_bot.models.log import Log
from telegram_bot.repositories.logs import add_log


async def register_log(log: Log) -> None:
    """Store a moderation log entry in the database."""
    try:
        await add_log(log)
    except Exception as e:
        logging.exception(f"Failed to register log: {e}")
