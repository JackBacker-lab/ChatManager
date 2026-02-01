import logging

from telegram_bot.models.filters import FiltersConfig
from telegram_bot.repositories.chat_settings import (
    get_filters,
    get_language,
    save_filters,
    set_language,
)


async def set_chat_language(chat_id: int, lang: str) -> None:
    """Set the language for a chat"""
    try:
        await set_language(chat_id, lang)
    except Exception:
        logging.exception("Failed to set chat language")


async def get_chat_language(chat_id: int) -> str:
    """Return the language for a chat with a safe default."""
    try:
        return await get_language(chat_id)
    except Exception:
        logging.exception("Failed to get chat language")
        return "en"


async def get_chat_filters(chat_id: int) -> FiltersConfig:
    """Return filter configuration for a chat with a safe default."""
    try:
        return await get_filters(chat_id)
    except Exception:
        logging.exception("Failed to get chat filters")
        return FiltersConfig()


async def save_chat_filters(chat_id: int, filters: FiltersConfig) -> None:
    """Persist filter configuration for a chat"""
    try:
        await save_filters(chat_id, filters)
    except Exception:
        logging.exception("Failed to get chat filters")


# High-level helpers that work on top of get/save_chat_filters
# and do not talk to the repository directly.
async def set_chat_censorship(chat_id: int, enabled: bool) -> None:
    """Enable or disable text censorship filters for a chat."""
    filters = await get_chat_filters(chat_id)
    filters.censorship.enabled = enabled
    await save_chat_filters(chat_id, filters)


async def set_chat_antispam(chat_id: int, enabled: bool) -> None:
    """Enable or disable spam detection filters for a chat."""
    filters = await get_chat_filters(chat_id)
    filters.spam.enabled = enabled
    await save_chat_filters(chat_id, filters)


async def set_chat_ai_censorship(chat_id: int, enabled: bool) -> None:
    """Enable or disable AI-based censorship for a chat."""
    filters = await get_chat_filters(chat_id)
    filters.censorship.ai.enabled = enabled
    await save_chat_filters(chat_id, filters)
