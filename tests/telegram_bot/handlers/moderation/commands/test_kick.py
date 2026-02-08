from unittest.mock import Mock, patch

import pytest

from telegram_bot.handlers.moderation.commands.kick import handle_kick_command


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.kick.process_action")
@patch("telegram_bot.handlers.moderation.commands.kick.require_command_context")
async def test_handle_kick_command(
    mock_require_command_context: Mock,
    mock_process_action: Mock,
):
    # Arrange
    fake_text = "/kick"
    fake_bot = Mock()
    fake_admin_user = Mock()

    message = Mock()
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)

    # Act
    await handle_kick_command(message)

    # Assert
    mock_require_command_context.assert_called_once_with(message)

    mock_process_action.assert_called_once()
    args, _ = mock_process_action.call_args

    (
        called_message,
        called_text,
        called_bot,
        called_admin_user,
        action_name,
        do_kick,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "kick"
    assert callable(do_kick)
