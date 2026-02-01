from unittest.mock import AsyncMock, Mock, patch

import pytest

from telegram_bot.handlers.common.commands.help import help_command_handler


@pytest.mark.asyncio
@patch("telegram_bot.handlers.common.commands.help.t")
@patch(
    "telegram_bot.handlers.common.commands.help.get_chat_language",
    return_value="en",
)
async def test_help_command_handler(mock_get_chat_language: Mock, mock_t: Mock):
    fake_chat_id = 1234567890
    fake_text = "help text"

    mock_t.return_value = fake_text

    message = Mock()
    message.chat.id = fake_chat_id
    message.answer = AsyncMock()

    await help_command_handler(message)

    mock_get_chat_language.assert_called_once_with(fake_chat_id)
    mock_t.assert_called_once_with("general.help", "en")
    message.answer.assert_awaited_once_with(fake_text)
