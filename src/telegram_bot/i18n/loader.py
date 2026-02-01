import json
import logging
from typing import Any, cast

from telegram_bot.i18n.generate_keys import generate_keys
from telegram_bot.i18n.types import LOCALES_DIR, SOURCE_LANG, I18nTree

I18N: dict[str, I18nTree] = {}


def _extract_keys(data: I18nTree, prefix: str = "") -> set[str]:
    """Collect and return all translation key paths from an i18n tree."""
    keys: set[str] = set()

    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= _extract_keys(v, full_key)
        else:
            keys.add(full_key)

    return keys


def _validate_language_keys(
    base: I18nTree,
    other: I18nTree,
    lang: str,
) -> None:
    """Validate that an i18n language tree has the same keys as the base language.

    Compare the sets of translation key path
    and log an error if any keys are missing or extra.
    """
    base_keys = _extract_keys(base)
    other_keys = _extract_keys(other)

    missing = base_keys - other_keys
    extra = other_keys - base_keys

    if missing or extra:
        messages: list[str] = []

        if missing:
            messages.append(f"Missing keys in '{lang}': {sorted(missing)}")
        if extra:
            messages.append(f"Extra keys in '{lang}': {sorted(extra)}")

        message = "\n".join(messages)
        logging.error(message)

        # In strict mode we raise an error
        # if locale keys are out of sync with the base language.
        # During development you can relax this by toggling the flag below
        STRICT_I18N = True
        if STRICT_I18N:
            raise ValueError(message)


def load_i18n() -> None:
    """Load i18n locale data from JSON files.

    Validate keys and generate typed i18n keys.
    """
    langs = ("en", "ru", "ua")

    for lang in langs:
        path = LOCALES_DIR / f"{lang}.json"
        if not path.exists():
            raise FileNotFoundError(f"I18n file not found: {path}")

        with path.open(encoding="utf-8") as f:
            raw: Any = json.load(f)

        if not isinstance(raw, dict):
            raise TypeError(f"I18n root must be object: {path}")

        I18N[lang] = cast(I18nTree, raw)

    base_data = I18N[SOURCE_LANG]

    for lang in langs:
        if lang == SOURCE_LANG:
            continue
        _validate_language_keys(base_data, I18N[lang], lang)

    generate_keys()
