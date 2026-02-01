from unittest.mock import AsyncMock, Mock

import pytest

from telegram_bot.handlers.moderation.filters.base import FilterStatus
from telegram_bot.handlers.moderation.filters.censorship import AICensorshipFilter
from telegram_bot.models.filters import AICensorshipConfig

from .fake_message_context import make_fake_message_context


@pytest.mark.asyncio
async def test_dependency_missing(monkeypatch: pytest.MonkeyPatch):
    def fake_get_ai_checker():
        raise ImportError("torch not installed")

    monkeypatch.setattr(
        "telegram_bot.handlers.moderation.filters.censorship.get_ai_checker",
        fake_get_ai_checker,
    )

    ctx = make_fake_message_context("hello")
    config = AICensorshipConfig(enabled=True)

    result = await AICensorshipFilter.check(ctx, config)

    assert not result.triggered
    assert result.status == FilterStatus.SKIPPED
    assert result.error is not None
    assert result.error.code == "ai_censor_dependency_missing"


@pytest.mark.asyncio
async def test_exception(monkeypatch: pytest.MonkeyPatch):
    exc_msg = "exception_message"
    mock_is_toxic = Mock(side_effect=Exception(exc_msg))

    def fake_get_ai_checker():
        return mock_is_toxic

    monkeypatch.setattr(
        "telegram_bot.handlers.moderation.filters.censorship.get_ai_checker",
        fake_get_ai_checker,
    )

    ctx = make_fake_message_context("Some text")
    config = AICensorshipConfig(enabled=True)

    result = await AICensorshipFilter.check(ctx, config)

    mock_is_toxic.assert_called_once_with(ctx.text, config)
    assert not result.triggered
    assert result.status == FilterStatus.FAILED
    assert result.error is not None
    assert result.error.code == "ai_censor_exception"
    assert result.error.message == exc_msg


@pytest.mark.asyncio
async def test_is_toxic_triggered(monkeypatch: pytest.MonkeyPatch):
    mock_is_toxic = AsyncMock(return_value=True)

    def fake_get_ai_checker():
        return mock_is_toxic

    monkeypatch.setattr(
        "telegram_bot.handlers.moderation.filters.censorship.get_ai_checker",
        fake_get_ai_checker,
    )

    ctx = make_fake_message_context("Some text")
    config = AICensorshipConfig(enabled=True)

    result = await AICensorshipFilter.check(ctx, config)

    assert result.triggered
    assert result.reason == AICensorshipFilter.name


@pytest.mark.asyncio
async def test_is_toxic_not_triggered(monkeypatch: pytest.MonkeyPatch):
    mock_is_toxic = AsyncMock(return_value=False)

    def fake_get_ai_checker():
        return mock_is_toxic

    monkeypatch.setattr(
        "telegram_bot.handlers.moderation.filters.censorship.get_ai_checker",
        fake_get_ai_checker,
    )

    ctx = make_fake_message_context("Some text")
    config = AICensorshipConfig(enabled=True)

    result = await AICensorshipFilter.check(ctx, config)

    assert not result.triggered
    assert result.reason == ""
