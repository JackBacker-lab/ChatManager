import aiosqlite

from telegram_bot.models.log import Log
from telegram_bot.repositories.db import DB_PATH


async def add_log(log: Log):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO logs (
                chat_id,
                status,
                action,
                action_by_id,
                target_id,
                text,
                link,
                reason,
                details,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log.chat_id,
                log.status,
                log.action,
                log.action_by_id,
                log.target_id,
                log.text,
                log.link,
                log.reason,
                log.details,
                log.timestamp,
            ),
        )
        await db.commit()
