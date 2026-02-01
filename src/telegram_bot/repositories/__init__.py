"""Low-level helpers for database access.

These modules read and write chat settings, users, logs, and other data
directly from the SQLite database.
"""

from .db import init_db

__all__ = ("init_db",)
