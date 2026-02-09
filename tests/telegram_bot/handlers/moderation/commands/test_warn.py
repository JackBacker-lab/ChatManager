from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram import Bot
from aiogram.types import Message, User

from telegram_bot.handlers.moderation.commands.warn import (
    ban_user_and_send_message,
    handle_warn_command,
    handle_warns_reset_command,
)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.register_log")
@patch("telegram_bot.handlers.moderation.commands.warn.reset_user_warnings")
@patch(
    "telegram_bot.handlers.moderation.commands.warn.get_unban_button",
    return_value="mock_button",
)
@patch(
    "telegram_bot.handlers.moderation.commands.warn.get_display_name",
    return_value="[user's name]",
)
@patch("telegram_bot.handlers.moderation.commands.warn.t", return_value="fake_t_text")
async def test_ban_user_and_send_message_happy_path(
    mock_t: Mock,
    mock_get_display_name: Mock,
    mock_get_unban_button: Mock,
    mock_reset_user_warnings: Mock,
    mock_register_log: Mock,
):
    fake_text = "/ban @user1 @user2 40s"
    fake_chat_id = -1234509876
    fake_lang = "en"
    fake_link = "https://example.com/telegram/1"
    fake_bot_user = Mock()
    fake_bot_user.id = 345710894

    mock_message = Mock(spec=Message)
    mock_message.reply = AsyncMock()
    mock_bot = Mock(spec=Bot)
    mock_bot.ban_chat_member = AsyncMock()
    mock_bot.get_me.return_value = fake_bot_user
    mock_target_user = Mock(spec=User)
    mock_target_user.id = 1234567890

    await ban_user_and_send_message(
        mock_message,
        fake_text,
        mock_bot,
        fake_chat_id,
        fake_lang,
        mock_target_user,
        fake_link,
    )

    assert mock_message.reply.await_count == 2
    msg_reply_first_call = mock_message.reply.await_args_list[0]
    msg_reply_second_call = mock_message.reply.await_args_list[1]

    msg_reply_args1, msg_reply_kwargs1 = msg_reply_first_call
    assert msg_reply_args1[0] == mock_t.return_value
    assert msg_reply_kwargs1 == {}

    msg_reply_args2, msg_reply_kwargs2 = msg_reply_second_call
    assert msg_reply_args2[0] == mock_t.return_value
    assert "reply_markup" in msg_reply_kwargs2
    assert msg_reply_kwargs2["reply_markup"] == mock_get_unban_button.return_value

    mock_bot.ban_chat_member.assert_awaited_once_with(
        chat_id=fake_chat_id, user_id=mock_target_user.id
    )

    mock_reset_user_warnings.assert_awaited_once_with(fake_chat_id, mock_target_user.id)

    assert mock_register_log.await_count == 1
    (log_arg,), _ = mock_register_log.await_args
    assert log_arg.chat_id == fake_chat_id
    assert log_arg.status.value == "success"
    assert log_arg.action_name == "ban"
    assert log_arg.called_by_id == mock_bot.get_me.return_value.id
    assert log_arg.target_id == mock_target_user.id
    assert log_arg.msg_text == fake_text
    assert log_arg.msg_link == fake_link
    assert log_arg.details == ""


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.register_log")
@patch("telegram_bot.handlers.moderation.commands.warn.reset_user_warnings")
@patch(
    "telegram_bot.handlers.moderation.commands.warn.get_unban_button",
    return_value="mock_button",
)
@patch(
    "telegram_bot.handlers.moderation.commands.warn.get_display_name",
    return_value="[user's name]",
)
@patch("telegram_bot.handlers.moderation.commands.warn.t", return_value="fake_t_text")
async def test_ban_user_and_send_message_exception(
    mock_t: Mock,
    mock_get_display_name: Mock,
    mock_get_unban_button: Mock,
    mock_reset_user_warnings: Mock,
    mock_register_log: Mock,
):
    mock_message = Mock(spec=Message)
    mock_message.reply = AsyncMock()
    mock_bot = Mock(spec=Bot)
    fake_exception_message = "exception_message"
    mock_bot.ban_chat_member = AsyncMock(side_effect=Exception(fake_exception_message))
    mock_target_user = Mock(spec=User)
    mock_target_user.id = 1234567890
    fake_text = "/ban @user1 @user2 40s"
    fake_chat_id = -1234509876
    fake_lang = "en"
    fake_link = "https://example.com/telegram/1"

    await ban_user_and_send_message(
        mock_message,
        fake_text,
        mock_bot,
        fake_chat_id,
        fake_lang,
        mock_target_user,
        fake_link,
    )

    mock_bot.ban_chat_member.assert_awaited_once_with(
        chat_id=fake_chat_id, user_id=mock_target_user.id
    )

    last_reply_call = mock_message.reply.await_args_list[-1]
    args, _ = last_reply_call
    assert args[0] == mock_t.return_value

    last_t_call = mock_t.call_args_list[-1]
    args, kwargs = last_t_call
    assert args[0] == "moderation.ban.error"
    assert args[1] == fake_lang
    assert "e" in kwargs
    assert kwargs["e"] == fake_exception_message

    (log_arg,), _ = mock_register_log.await_args
    assert log_arg.status.value == "error"
    assert fake_exception_message in (log_arg.details or "")


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.process_action")
@patch("telegram_bot.handlers.moderation.commands.warn.get_message_link")
@patch("telegram_bot.handlers.moderation.commands.warn.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.warn.require_command_context")
async def test_handle_warn_command_warned_users_is_none(
    mock_require_command_context: Mock,
    mock_get_chat_language: Mock,
    mock_get_message_link: Mock,
    mock_process_action: Mock,
):
    # Arrange
    fake_chat_id = -1932523008
    fake_text = "/ban 30s"
    fake_lang = "en"
    fake_link = "https://example.com/telegram/1"
    fake_bot = Mock()
    fake_admin_user = Mock()
    fake_target_user = Mock()
    fake_target_user.id = 1234567890

    message = Mock()
    message.chat.id = fake_chat_id
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)
    mock_get_chat_language.return_value = fake_lang
    mock_get_message_link.return_value = fake_link
    mock_process_action.return_value = None

    # Act
    with pytest.raises(RuntimeError):
        await handle_warn_command(message)

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
        do_warn,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "warn"
    assert callable(do_warn)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.ban_user_and_send_message")
@patch("telegram_bot.handlers.moderation.commands.warn.get_user_warnings")
@patch("telegram_bot.handlers.moderation.commands.warn.process_action")
@patch("telegram_bot.handlers.moderation.commands.warn.get_message_link")
@patch("telegram_bot.handlers.moderation.commands.warn.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.warn.require_command_context")
async def test_handle_warn_command_user_must_be_banned(
    mock_require_command_context: Mock,
    mock_get_chat_language: Mock,
    mock_get_message_link: Mock,
    mock_process_action: Mock,
    mock_get_user_warnings: Mock,
    mock_ban_user_and_send_message: Mock,
):
    # Arrange
    fake_chat_id = -1932523008
    fake_text = "/ban 30s"
    fake_lang = "en"
    fake_link = "https://example.com/telegram/1"
    fake_bot = Mock()
    fake_admin_user = Mock()
    fake_target_user = Mock()
    fake_target_user.id = 1234567890

    message = Mock()
    message.chat.id = fake_chat_id
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)
    mock_get_chat_language.return_value = fake_lang
    mock_get_message_link.return_value = fake_link
    mock_process_action.return_value = [fake_target_user]
    mock_get_user_warnings.return_value = 3  # at the threshold

    # Act
    await handle_warn_command(message)

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
        do_warn,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "warn"
    assert callable(do_warn)

    mock_get_user_warnings.assert_awaited_once_with(fake_chat_id, fake_target_user.id)

    mock_ban_user_and_send_message.assert_awaited_once()
    args, kwargs = mock_ban_user_and_send_message.await_args
    assert kwargs["message"] is message
    assert kwargs["text"] == fake_text
    assert kwargs["bot"] is fake_bot
    assert kwargs["chat_id"] == fake_chat_id
    assert kwargs["lang"] == fake_lang
    assert kwargs["target_user"] is fake_target_user
    assert kwargs["link"] == fake_link


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.ban_user_and_send_message")
@patch("telegram_bot.handlers.moderation.commands.warn.get_user_warnings")
@patch("telegram_bot.handlers.moderation.commands.warn.process_action")
@patch("telegram_bot.handlers.moderation.commands.warn.get_message_link")
@patch("telegram_bot.handlers.moderation.commands.warn.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.warn.require_command_context")
async def test_handle_warn_command_user_not_banned_when_below_limit(
    mock_require_command_context: Mock,
    mock_get_chat_language: Mock,
    mock_get_message_link: Mock,
    mock_process_action: Mock,
    mock_get_user_warnings: Mock,
    mock_ban_user_and_send_message: Mock,
):
    fake_chat_id = -1932523008
    fake_text = "/warn"
    fake_lang = "en"
    fake_link = "https://example.com/telegram/1"
    fake_bot = Mock()
    fake_admin_user = Mock()
    fake_target_user = Mock()
    fake_target_user.id = 1234567890

    message = Mock()
    message.chat.id = fake_chat_id
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)
    mock_get_chat_language.return_value = fake_lang
    mock_get_message_link.return_value = fake_link
    mock_process_action.return_value = [fake_target_user]
    mock_get_user_warnings.return_value = 2  # below the threshold

    await handle_warn_command(message)

    mock_get_user_warnings.assert_awaited_once_with(fake_chat_id, fake_target_user.id)
    mock_ban_user_and_send_message.assert_not_awaited()


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.warn.process_action")
@patch("telegram_bot.handlers.moderation.commands.warn.require_command_context")
async def test_handle_warns_reset_command(
    mock_require_command_context: Mock,
    mock_process_action: Mock,
):
    fake_text = "/warns_reset"
    fake_bot = Mock()
    fake_admin_user = Mock()
    message = Mock()

    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)

    await handle_warns_reset_command(message)

    mock_require_command_context.assert_called_once_with(message)
    mock_process_action.assert_called_once()
    args, _ = mock_process_action.call_args

    (
        called_message,
        called_text,
        called_bot,
        called_admin_user,
        action_name,
        do_reset_warns,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "reset_warns"
    assert callable(do_reset_warns)
