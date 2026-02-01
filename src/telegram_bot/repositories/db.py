"""Database initialization and global DB settings."""

import aiosqlite

DB_PATH = "settings.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                status TEXT,
                action TEXT,
                action_by_id INTEGER,
                target_id INTEGER,
                text TEXT,
                link TEXT,
                reason TEXT,
                details TEXT,
                timestamp TEXT
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                link TEXT,
                updated_at TEXT
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_chats (
                chat_id INTEGER,
                user_id TEXT,
                is_admin INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                type TEXT,
                bot_member INTEGER NOT NULL DEFAULT 0
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id            INTEGER PRIMARY KEY,
                language           TEXT NOT NULL DEFAULT 'en',
                filters            TEXT NOT NULL
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS warnings (
                chat_id INTEGER,
                user_id INTEGER,
                warning_count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS blacklist_words (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id  INTEGER NOT NULL,
                word     TEXT    NOT NULL,
                UNIQUE(chat_id, word),
                FOREIGN KEY(chat_id) REFERENCES chat_settings(chat_id) ON DELETE CASCADE
            )
        """
        )
        await db.commit()
