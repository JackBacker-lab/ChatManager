from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from telegram_bot.config import load_config


def test_load_config_path_not_exists(monkeypatch: pytest.MonkeyPatch):
    def fake_path_exists(self: Path) -> bool:
        return False

    monkeypatch.setattr("telegram_bot.config.Path.exists", fake_path_exists)

    with pytest.raises(FileNotFoundError):
        load_config()


@patch("telegram_bot.config.load_dotenv")
def test_load_config_happy_path(
    mock_load_dotenv: Mock, monkeypatch: pytest.MonkeyPatch
):
    fake_token = "1a2b3c4d5e6f7g8h"

    def fake_getenv(key: str) -> str | None:
        return fake_token if key == "BOT_TOKEN" else None

    monkeypatch.setattr("telegram_bot.config.getenv", fake_getenv)

    config = load_config()
    mock_load_dotenv.assert_called_once()
    assert config.bot_token == fake_token


@patch("telegram_bot.config.load_dotenv")
def test_load_config_token_not_set(
    mock_load_dotenv: Mock, monkeypatch: pytest.MonkeyPatch
):
    def fake_getenv(key: str) -> str | None:
        return None

    monkeypatch.setattr("telegram_bot.config.getenv", fake_getenv)

    with pytest.raises(RuntimeError):
        load_config()

    mock_load_dotenv.assert_called_once()
