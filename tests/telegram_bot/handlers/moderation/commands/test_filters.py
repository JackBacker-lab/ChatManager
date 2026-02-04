from unittest.mock import AsyncMock, Mock, patch

import pytest

from telegram_bot.handlers.moderation.commands.filters import (
    handle_ai_censor_off,
    handle_ai_censor_on,
    handle_antispam_off,
    handle_antispam_on,
    handle_censor_off,
    handle_censor_on,
    handle_filters_overview,
)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.build_filters_summary")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_filters")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_filters_overview(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_get_chat_filters: Mock,
    mock_build_filters_summary: Mock,
):
    fake_lang = "en"
    fake_filters = {"dummy": True}
    fake_summary = "summary text"
    fake_t_text = "filters text"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_get_chat_filters.return_value = fake_filters
    mock_build_filters_summary.return_value = fake_summary
    mock_t.return_value = fake_t_text

    await handle_filters_overview(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_get_chat_filters.assert_awaited_once_with(message.chat.id)
    mock_build_filters_summary.assert_called_once_with(fake_filters, fake_lang)
    mock_t.assert_called_once_with(
        "moderation.filters.display", fake_lang, summary=fake_summary
    )
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_censorship")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_censor_on(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_censorship: Mock,
):
    fake_lang = "en"
    fake_t_text = "censor on"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_censor_on(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_censorship.assert_awaited_once_with(message.chat.id, True)
    mock_t.assert_called_once_with("moderation.modes.censorship.on", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_censorship")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_censor_off(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_censorship: Mock,
):
    fake_lang = "en"
    fake_t_text = "censor off"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_censor_off(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_censorship.assert_awaited_once_with(message.chat.id, False)
    mock_t.assert_called_once_with("moderation.modes.censorship.off", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_ai_censorship")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_ai_censor_on(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_ai_censorship: Mock,
):
    fake_lang = "en"
    fake_t_text = "ai censor on"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_ai_censor_on(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_ai_censorship.assert_awaited_once_with(message.chat.id, True)
    mock_t.assert_called_once_with("moderation.modes.censorship.on", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_ai_censorship")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_ai_censor_off(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_ai_censorship: Mock,
):
    fake_lang = "en"
    fake_t_text = "ai censor off"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_ai_censor_off(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_ai_censorship.assert_awaited_once_with(message.chat.id, False)
    mock_t.assert_called_once_with("moderation.modes.censorship.off", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_antispam")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_antispam_on(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_antispam: Mock,
):
    fake_lang = "en"
    fake_t_text = "antispam on"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_antispam_on(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_antispam.assert_awaited_once_with(message.chat.id, True)
    mock_t.assert_called_once_with("moderation.modes.antispam.on", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.filters.set_chat_antispam")
@patch("telegram_bot.handlers.moderation.commands.filters.t")
@patch("telegram_bot.handlers.moderation.commands.filters.get_chat_language")
async def test_handle_antispam_off(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_set_chat_antispam: Mock,
):
    fake_lang = "en"
    fake_t_text = "antispam off"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_antispam_off(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_set_chat_antispam.assert_awaited_once_with(message.chat.id, False)
    mock_t.assert_called_once_with("moderation.modes.antispam.off", fake_lang)
    message.reply.assert_awaited_once_with(fake_t_text)
