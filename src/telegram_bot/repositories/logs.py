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
                action_name,
                called_by_id,
                target_id,
                msg_text,
                msg_link,
                details,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log.chat_id,
                log.status.value,
                log.action_name,
                log.called_by_id,
                log.target_id,
                log.msg_text,
                log.msg_link,
                log.details,
                log.timestamp,
            ),
        )
        await db.commit()
