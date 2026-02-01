import aiosqlite

from telegram_bot.repositories.db import DB_PATH


async def add_blacklist_word(chat_id: int, word: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO blacklist_words(chat_id, word) VALUES(?, ?)",
            (chat_id, word),
        )
        await db.commit()


async def remove_blacklist_word(chat_id: int, word: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM blacklist_words WHERE chat_id=? AND word=?", (chat_id, word)
        )
        await db.commit()


async def get_blacklist_words(chat_id: int) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db, db.execute(
        "SELECT word FROM blacklist_words WHERE chat_id=?", (chat_id,)
    ) as cursor:
        rows = await cursor.fetchall()
    return [row[0] for row in rows]
