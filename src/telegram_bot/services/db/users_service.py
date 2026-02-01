import logging
from datetime import datetime

from telegram_bot.models.user import UserDTO
from telegram_bot.repositories.users import (
    get_user_by_id,
    get_user_by_username,
    upsert_user,
)


async def get_user(
    *, username: str | None = None, user_id: int | None = None
) -> UserDTO | None:
    """Return a user record by username or user id."""
    if not user_id and not username:
        raise ValueError("Either user_id or username must be provided")
    try:
        if user_id:
            return await get_user_by_id(user_id)
        if username:
            return await get_user_by_username(username)
    except Exception as e:
        logging.exception(f"Failed to resolve user {user_id or username}: {e}")
        return None


async def register_user(user: UserDTO) -> None:
    """Create or update a user record in the database."""
    try:
        await upsert_user(
            user_id=user.id,
            username=user.username or "",
            full_name=user.full_name,
            updated_at=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        )
    except Exception as e:
        logging.exception(
            f"Failed to register user: {e}",
            extra={
                "user_id": getattr(user, "id", None),
                "username": getattr(user, "username", None),
            },
        )
