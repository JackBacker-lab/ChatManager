import logging

from telegram_bot.repositories.chats import add_chat as repo_add_chat


async def add_chat(chat_id: int, title: str | None, type: str) -> None:
    """Create or update a chat record in the database."""
    try:
        await repo_add_chat(chat_id, title, type)
    except Exception:
        logging.exception(f"Failed to add chat ({chat_id}).")
