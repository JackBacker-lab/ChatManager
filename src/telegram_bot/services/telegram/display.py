from html import escape

from aiogram.types import User


def get_display_name(user: User) -> str:
    """Build and return either "@username" or an HTML mention link for the user."""
    if user.username:
        return f"@{user.username}"
    else:
        return f'<a href="tg://user?id={user.id}">{escape(user.full_name)}</a>'
