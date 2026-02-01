import logging

from telegram_bot.repositories.blacklist import (
    add_blacklist_word as repo_add_blacklist_word,
)
from telegram_bot.repositories.blacklist import (
    get_blacklist_words as repo_get_blacklist_words,
)
from telegram_bot.repositories.blacklist import (
    remove_blacklist_word as repo_remove_blacklist_word,
)


async def add_blacklist_word(chat_id: int, word: str) -> None:
    """Add a word to the chat's blacklist."""
    try:
        await repo_add_blacklist_word(chat_id, word)
    except Exception:
        logging.exception(f"Failed to add word ({word}) to blacklist.")


async def remove_blacklist_word(chat_id: int, word: str) -> None:
    """Remove a word from the chat's blacklist."""
    try:
        await repo_remove_blacklist_word(chat_id, word)
    except Exception:
        logging.exception(f"Failed to remove word ({word}) from blacklist.")


async def get_blacklist_words(chat_id: int) -> list[str]:
    """Get all blacklisted words for a chat."""
    try:
        return await repo_get_blacklist_words(chat_id)
    except Exception:
        logging.exception("Failed to get blacklisted words.")
        return []
