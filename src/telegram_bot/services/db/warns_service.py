import logging

from telegram_bot.repositories.warn import (
    add_warning as repo_add_warning,
)
from telegram_bot.repositories.warn import (
    get_warnings as repo_get_warnings,
)
from telegram_bot.repositories.warn import (
    reset_warnings as repo_reset_warnings,
)


async def get_user_warnings(chat_id: int, user_id: int) -> int:
    """Return the number of warnings a user has in a chat."""
    try:
        return await repo_get_warnings(chat_id, user_id)
    except Exception:
        logging.exception(
            f"Failed to get warnings (chat_id={chat_id}, user_id={user_id})"
        )
        return 0


async def add_user_warning(chat_id: int, user_id: int) -> None:
    """Increment a user's warning count in a chat."""
    try:
        await repo_add_warning(chat_id, user_id)
    except Exception:
        logging.exception(
            f"Failed to add warning (chat_id={chat_id}, user_id={user_id})"
        )


async def reset_user_warnings(chat_id: int, user_id: int) -> None:
    """Clear all warnings for a user in a chat."""
    try:
        await repo_reset_warnings(chat_id, user_id)
    except Exception:
        logging.exception(
            f"Failed to reset warnings (chat_id={chat_id}, user_id={user_id})"
        )
