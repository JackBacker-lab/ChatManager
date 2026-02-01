"""Core types and constants used by the i18n subsystem."""

from pathlib import Path

I18nNode = str | dict[str, "I18nNode"]
I18nTree = dict[str, I18nNode]

I18N: dict[str, I18nTree] = {}
LOCALES_DIR = Path(__file__).parent / "locales"
SOURCE_LANG = "en"
