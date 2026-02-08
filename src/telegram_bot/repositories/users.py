import aiosqlite

from telegram_bot.models.user import UserDTO
from telegram_bot.repositories.db import DB_PATH


async def get_user_by_username(username: str) -> UserDTO | None:
    async with (
        aiosqlite.connect(DB_PATH) as db,
        db.execute(
            """
            SELECT id, username, full_name, link, updated_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        ) as cursor,
    ):
        row = await cursor.fetchone()
    if not row:
        return None
    return UserDTO(
        id=row[0], username=row[1], full_name=row[2], link=row[3], updated_at=row[4]
    )


async def get_user_by_id(user_id: int) -> UserDTO | None:
    async with (
        aiosqlite.connect(DB_PATH) as db,
        db.execute(
            "SELECT id, username, full_name, link, updated_at FROM users WHERE id = ?",
            (user_id,),
        ) as cursor,
    ):
        row = await cursor.fetchone()
    if not row:
        return None
    return UserDTO(
        id=row[0], username=row[1], full_name=row[2], link=row[3], updated_at=row[4]
    )


async def upsert_user(
    user_id: int, username: str, full_name: str, updated_at: str
) -> None:
    link = f"https://t.me/{username}" if username else ""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
        INSERT INTO users (id, username, full_name, link, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name,
            link=excluded.link,
            updated_at=excluded.updated_at
        """,
            (user_id, username, full_name, link, updated_at),
        )
        await db.commit()


async def remove_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()


async def add_user_chat(chat_id: int, user_id: int, is_admin: int | None = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
        INSERT INTO user_chats (chat_id, user_id, is_admin)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, chat_id) DO UPDATE SET
            is_admin = CASE
                WHEN excluded.is_admin IS NOT NULL THEN excluded.is_admin
                ELSE user_chats.is_admin
            END
        """,
            (chat_id, user_id, is_admin if is_admin is not None else 0),
        )
        await db.commit()


async def remove_user_chat(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM user_chats WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )
        await db.commit()
