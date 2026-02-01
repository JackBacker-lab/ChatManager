from telegram_bot.i18n.keys import I18nKey
from telegram_bot.i18n.loader import I18N
from telegram_bot.i18n.types import I18nNode


class SafeDict(dict[str, str | None]):
    """Return placeholder tokens for missing keys."""

    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def t(key: I18nKey, lang: str = "en", **kwargs: str | None) -> str:
    """Translate an i18n key into a localized string for the given language.

    Return a formatted string with any provided keyword substitutions.
    """
    if lang not in I18N:
        raise ValueError(f"Unsupported language: {lang}")

    data: I18nNode = I18N[lang]

    try:
        for part in key.split("."):
            if not isinstance(data, dict):
                raise KeyError(key)
            data = data[part]
    except KeyError as e:
        raise KeyError(f"Missing i18n key: {key}") from e

    if not isinstance(data, str):
        raise TypeError(f"I18n key '{key}' does not resolve to string")

    return data.format_map(SafeDict(kwargs))
