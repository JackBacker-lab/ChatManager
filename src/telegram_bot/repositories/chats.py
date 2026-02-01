import aiosqlite

from telegram_bot.repositories.db import DB_PATH


async def add_chat(chat_id: int, title: str | None, type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO chats (chat_id, title, type, bot_member)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(chat_id) DO UPDATE
            SET bot_member=1, type=excluded.type, title=excluded.title
            """,
            (chat_id, title, type),
        )
        await db.commit()
