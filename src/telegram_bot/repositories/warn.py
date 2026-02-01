import aiosqlite

from telegram_bot.repositories.db import DB_PATH


async def get_warnings(chat_id: int, user_id: int) -> int:
    async with (
        aiosqlite.connect(DB_PATH) as db,
        db.execute(
            "SELECT warning_count FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ) as cursor,
    ):
        row = await cursor.fetchone()
    return row[0] if row else 0


async def add_warning(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
        INSERT INTO warnings (chat_id, user_id, warning_count)
        VALUES (?, ?, 1)
        ON CONFLICT(chat_id, user_id)
        DO UPDATE SET warning_count = warning_count + 1
        """,
            (chat_id, user_id),
        )
        await db.commit()


async def reset_warnings(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
        )
        await db.commit()
