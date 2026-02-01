import json
from collections.abc import Iterable
from pathlib import Path

from telegram_bot.i18n.types import LOCALES_DIR, SOURCE_LANG, I18nNode

OUTPUT_FILE = Path(__file__).parent / "keys.py"


def _walk(prefix: str, data: dict[str, I18nNode]) -> Iterable[str]:
    """Walk through a nested i18n dictionary and return all keys.

    Go through nested translation dictionaries and return
    dotted key paths for every translation entry.
    """
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from _walk(full_key, value)
        else:
            yield full_key


def generate_keys() -> None:
    """Generate a Python type that contains all i18n keys.

    Read the source locale JSON file, collect all keys, and write
    them as a Literal type into a Python module.
    """
    with open(LOCALES_DIR / f"{SOURCE_LANG}.json", encoding="utf-8") as f:
        data = json.load(f)

    keys = sorted(_walk("", data))

    content = [
        "# AUTO-GENERATED FILE. DO NOT EDIT.",
        "from typing import Literal",
        "",
        "I18nKey = Literal[",
    ]

    content.extend(f'    "{key}",' for key in keys)
    content.extend(("]", ""))

    new_text = "\n".join(content)

    if OUTPUT_FILE.exists():
        old_text = OUTPUT_FILE.read_text(encoding="utf-8")
        if old_text == new_text:
            return

    OUTPUT_FILE.write_text(new_text, encoding="utf-8")
