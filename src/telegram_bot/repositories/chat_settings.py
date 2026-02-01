import json

import aiosqlite

from telegram_bot.models.filters import FiltersConfig
from telegram_bot.repositories.db import DB_PATH


async def get_filters(chat_id: int) -> FiltersConfig:
    async with aiosqlite.connect(DB_PATH) as db, db.execute(
        "SELECT filters FROM chat_settings WHERE chat_id=?",
        (chat_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if row is None or row[0] is None:
        return FiltersConfig()

    data = json.loads(row[0])
    return FiltersConfig.model_validate(data)


async def save_filters(chat_id: int, filters: FiltersConfig) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO chat_settings (chat_id, filters)
            VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET filters = excluded.filters
            """,
            (chat_id, filters.model_dump_json()),
        )
        await db.commit()


async def set_language(chat_id: int, lang: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        default_filters_json = FiltersConfig().model_dump_json()
        await db.execute(
            """
            INSERT INTO chat_settings(chat_id, language, filters)
            VALUES(?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET language = excluded.language
            """,
            (chat_id, lang, default_filters_json),
        )
        await db.commit()


async def get_language(chat_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db, db.execute(
        "SELECT language FROM chat_settings WHERE chat_id=?", (chat_id,)
    ) as cursor:
        row = await cursor.fetchone()
    return "en" if row is None else row[0]
