from unittest.mock import AsyncMock, Mock, patch

import pytest

from telegram_bot.handlers.common.commands.start import (
    is_set_lang_callback,
    set_language_callback_handler,
    start_command_handler,
)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.common.commands.start.t")
@patch("telegram_bot.handlers.common.commands.start.get_chat_language")
@patch("telegram_bot.handlers.common.commands.start.InlineKeyboardMarkup")
async def test_start_command_handler(
    mock_inline_keyboard_markup: Mock, mock_get_chat_language: Mock, mock_t: Mock
):
    fake_chat_id = 1234567890
    fake_text = "start text"
    lang = "en"

    mock_t.return_value = fake_text
    mock_get_chat_language.return_value = lang

    message = Mock()
    message.chat.id = fake_chat_id
    message.answer = AsyncMock()

    await start_command_handler(message)

    mock_get_chat_language.assert_called_once_with(fake_chat_id)
    mock_t.assert_called_once_with("general.start", lang)
    message.answer.assert_awaited_once_with(
        fake_text, reply_markup=mock_inline_keyboard_markup()
    )


@pytest.mark.parametrize(
    "data, expected_result",
    [
        ["set_lang:en", True],
        ["set_langen", False],
        ["notset_lang:en", False],
    ],
)
def test_is_set_lang_callback(data: str, expected_result: bool):
    callback = Mock()
    callback.data = data

    assert is_set_lang_callback(callback) == expected_result


@pytest.mark.asyncio
@patch("telegram_bot.handlers.common.commands.start.t")
@patch("telegram_bot.handlers.common.commands.start.set_chat_language")
@patch("telegram_bot.handlers.common.commands.start.require_callback_context")
async def test_set_language_callback_handler(
    mock_require_callback_context: Mock, mock_set_chat_language: Mock, mock_t: Mock
):
    fake_chat_id = 1234567890
    fake_lang = "en"
    fake_data = f"set_lang:{fake_lang}"
    fake_text = "lang set"

    message = Mock()
    message.chat.id = fake_chat_id
    message.edit_text = AsyncMock()
    mock_require_callback_context.return_value = (message, fake_data)

    mock_t.return_value = fake_text

    callback = Mock()
    callback.answer = AsyncMock()

    await set_language_callback_handler(callback)

    mock_require_callback_context.assert_called_once_with(callback)
    mock_set_chat_language.assert_called_once_with(fake_chat_id, fake_lang)

    assert mock_t.call_count == 2
    key, called_lang = mock_t.call_args.args
    assert called_lang == "en"
    assert key.endswith("lang_set")

    callback.answer.assert_awaited_once_with(fake_text, show_alert=True)
    message.edit_text.assert_awaited_once_with(fake_text)
