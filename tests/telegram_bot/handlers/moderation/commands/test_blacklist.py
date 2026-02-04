from unittest.mock import AsyncMock, Mock, patch

import pytest

from telegram_bot.handlers.moderation.commands.blacklist import (
    handle_blacklist_add,
    handle_blacklist_remove,
    handle_blacklist_show,
)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.add_blacklist_word")
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_add_happy_path(
    mock_get_chat_language: Mock, mock_t: Mock, mock_add_blacklist_word: Mock
):
    word = "someword"
    fake_t_text = "blacklist_add_success"
    fake_lang = "en"

    message = Mock()
    message.text = f"/blacklist_add {word}"
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang

    mock_t.return_value = fake_t_text

    await handle_blacklist_add(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_add_blacklist_word.assert_awaited_once_with(message.chat.id, word)
    message.reply.assert_awaited_once_with(fake_t_text)
    mock_t.assert_called_once_with("blacklist.add.success", fake_lang, word=word)


@pytest.mark.asyncio
async def test_handle_blacklist_add_no_text():
    message = Mock()
    message.text = None

    with pytest.raises(AttributeError):
        await handle_blacklist_add(message)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_add_no_args(mock_get_chat_language: Mock, mock_t: Mock):
    fake_t_text = "blacklist_add_no_args"
    fake_lang = "en"

    message = Mock()
    message.text = "/blacklist_add"
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang

    mock_t.return_value = fake_t_text

    await handle_blacklist_add(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    message.reply.assert_awaited_once_with(fake_t_text)
    mock_t.assert_called_once_with("blacklist.add.no_args", fake_lang)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.remove_blacklist_word")
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_remove_happy_path(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_remove_blacklist_word: Mock,
):
    word = "someword"
    fake_t_text = "blacklist_remove_success"
    fake_lang = "en"

    message = Mock()
    message.text = f"/blacklist_remove {word}"
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_blacklist_remove(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_remove_blacklist_word.assert_awaited_once_with(message.chat.id, word)
    message.reply.assert_awaited_once_with(fake_t_text)
    mock_t.assert_called_once_with("blacklist.remove.success", fake_lang, word=word)


@pytest.mark.asyncio
async def test_handle_blacklist_remove_no_text():
    message = Mock()
    message.text = None

    with pytest.raises(AttributeError):
        await handle_blacklist_remove(message)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_remove_no_args(
    mock_get_chat_language: Mock,
    mock_t: Mock,
):
    fake_t_text = "blacklist_remove_no_args"
    fake_lang = "en"

    message = Mock()
    message.text = "/blacklist_remove"
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    await handle_blacklist_remove(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    message.reply.assert_awaited_once_with(fake_t_text)
    mock_t.assert_called_once_with("blacklist.remove.no_args", fake_lang)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_blacklist_words")
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_show_with_words(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_get_blacklist_words: Mock,
):
    fake_lang = "en"
    words = ["foo", "bar"]

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_get_blacklist_words.return_value = words
    mock_t.return_value = "Blacklisted:\n"

    await handle_blacklist_show(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_get_blacklist_words.assert_awaited_once_with(message.chat.id)

    message.reply.assert_awaited_once_with("Blacklisted:\n" + "• foo\n• bar")


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_blacklist_words")
@patch("telegram_bot.handlers.moderation.commands.blacklist.t")
@patch("telegram_bot.handlers.moderation.commands.blacklist.get_chat_language")
async def test_handle_blacklist_show_empty(
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_get_blacklist_words: Mock,
):
    fake_lang = "en"
    fake_text = "No blacklist"

    message = Mock()
    message.chat.id = -1234567890
    message.reply = AsyncMock()

    mock_get_chat_language.return_value = fake_lang
    mock_get_blacklist_words.return_value = []
    mock_t.return_value = fake_text

    await handle_blacklist_show(message)

    mock_get_chat_language.assert_awaited_once_with(message.chat.id)
    mock_get_blacklist_words.assert_awaited_once_with(message.chat.id)

    message.reply.assert_awaited_once_with(fake_text)
