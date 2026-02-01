"""Integration hooks for sending data to an external backend API.

These helpers are intentionally implemented as no-ops so the bot can run without
a backend, but can be patched or extended in deployments that provide their own API.
"""

from telegram_bot.models.log import Log


async def safe_post_groups(chat_id: int, user_id: int) -> None:
    return


async def safe_post_log(log: Log) -> None:
    return
