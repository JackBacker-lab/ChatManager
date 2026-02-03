from typing import Any
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram_bot.handlers.moderation.commands.ban import (
    ban_logic,
    ban_user,
    get_unban_button,
    is_unban_callback,
    unban_callback_logic,
    unban_logic,
)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.time.time")
async def test_ban_user(mock_time: Mock):
    fake_chat_id = -1234567890
    fake_user_id = 1234509876
    fake_duration = 30
    fake_time = 100

    bot = Mock()
    bot.ban_chat_member = AsyncMock()
    mock_time.return_value = fake_time

    await ban_user(bot, fake_chat_id, fake_user_id, fake_duration)

    bot.ban_chat_member.assert_awaited_once_with(
        chat_id=fake_chat_id, user_id=fake_user_id, until_date=fake_time + fake_duration
    )


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.get_unban_button")
@patch("telegram_bot.handlers.moderation.commands.ban.process_action")
@patch("telegram_bot.handlers.moderation.commands.ban.require_command_context")
async def test_ban_logic(
    mock_require_command_context: Mock,
    mock_process_action: Mock,
    mock_get_unban_button: Mock,
):
    # Arrange
    fake_text = "/ban 30s"
    fake_bot = Mock()
    fake_admin_user = Mock()

    message = Mock()
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)

    # Act
    await ban_logic(message)

    # Assert
    mock_require_command_context.assert_called_once_with(message)

    mock_process_action.assert_called_once()
    args, kwargs = mock_process_action.call_args

    (
        called_message,
        called_text,
        called_bot,
        called_admin_user,
        action_name,
        do_ban,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "ban"
    assert callable(do_ban)
    assert kwargs["reply_markup_builder"] == mock_get_unban_button


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.process_action")
@patch("telegram_bot.handlers.moderation.commands.ban.require_command_context")
async def test_unban_logic(
    mock_require_command_context: Mock,
    mock_process_action: Mock,
):
    # Arrange
    fake_text = "/unban"
    fake_bot = Mock()
    fake_admin_user = Mock()

    message = Mock()
    mock_require_command_context.return_value = (fake_text, fake_bot, fake_admin_user)

    # Act
    await unban_logic(message)

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
        do_unban,
    ) = args[:7]

    assert called_message is message
    assert called_text == fake_text
    assert called_bot is fake_bot
    assert called_admin_user is fake_admin_user
    assert action_name == "unban"
    assert callable(do_unban)


def _setup_unban_callback_test(
    mock_require_callback_context: Mock,
    mock_require_callback_bot: Mock,
    mock_get_chat_language: Mock,
    mock_t: Mock,
    data_suffix: str,
) -> dict[str, Any]:
    fake_chat_id = -1234567890
    fake_t_text = "fake_t_text"
    fake_lang = "en"

    fake_bot = Mock()
    fake_bot.unban_chat_member = AsyncMock()

    message = AsyncMock()
    message.chat.id = fake_chat_id
    message.edit_reply_markup = AsyncMock()
    message.edit_text = AsyncMock()
    message.text = "hello"

    mock_require_callback_context.return_value = (message, f"unban:{data_suffix}")
    mock_require_callback_bot.return_value = fake_bot
    mock_get_chat_language.return_value = fake_lang
    mock_t.return_value = fake_t_text

    callback = AsyncMock()

    return {
        "fake_chat_id": fake_chat_id,
        "fake_t_text": fake_t_text,
        "fake_lang": fake_lang,
        "fake_bot": fake_bot,
        "message": message,
        "callback": callback,
    }


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.t")
@patch("telegram_bot.handlers.moderation.commands.ban.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_bot")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_context")
async def test_unban_callback_logic_happy_path_single(
    mock_require_callback_context: Mock,
    mock_require_callback_bot: Mock,
    mock_get_chat_language: Mock,
    mock_t: Mock,
):
    # Arrange
    fake_user_id = 1234567890
    ctx = _setup_unban_callback_test(
        mock_require_callback_context,
        mock_require_callback_bot,
        mock_get_chat_language,
        mock_t,
        str(fake_user_id),
    )
    fake_chat_id = ctx["fake_chat_id"]
    fake_t_text = ctx["fake_t_text"]
    fake_lang = ctx["fake_lang"]
    fake_bot = ctx["fake_bot"]
    message = ctx["message"]
    callback = ctx["callback"]

    # Act
    await unban_callback_logic(callback)

    # Assert
    mock_require_callback_context.assert_called_once_with(callback)
    mock_require_callback_bot.assert_called_once_with(callback)
    mock_get_chat_language.assert_called_once_with(fake_chat_id)

    fake_bot.unban_chat_member.assert_awaited_once_with(
        chat_id=fake_chat_id, user_id=fake_user_id
    )
    message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)

    message.edit_text.assert_awaited_once()
    args, kwargs = message.edit_text.call_args
    assert args[0] == f"<s>{message.text}</s> {fake_t_text}"
    assert kwargs["parse_mode"] == "HTML"

    assert mock_t.call_count == 2

    first_call = mock_t.call_args_list[0]
    second_call = mock_t.call_args_list[1]

    args1, kwargs1 = first_call
    assert args1[0] == "moderation.common.canceled"
    assert args1[1] == fake_lang
    assert kwargs1 == {}

    args2, kwargs2 = second_call
    assert args2[0] == "moderation.unban.callback.success"
    assert args2[1] == fake_lang
    assert "target_names" in kwargs2
    assert str(fake_user_id) in kwargs2["target_names"]

    callback.answer.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.t")
@patch("telegram_bot.handlers.moderation.commands.ban.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_bot")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_context")
async def test_unban_callback_logic_happy_path_multiple(
    mock_require_callback_context: Mock,
    mock_require_callback_bot: Mock,
    mock_get_chat_language: Mock,
    mock_t: Mock,
):
    # Arrange
    fake_user_ids = [1, 2, 3]
    fake_ids_str = ",".join(str(i) for i in fake_user_ids)

    ctx = _setup_unban_callback_test(
        mock_require_callback_context,
        mock_require_callback_bot,
        mock_get_chat_language,
        mock_t,
        fake_ids_str,
    )
    fake_chat_id = ctx["fake_chat_id"]
    fake_t_text = ctx["fake_t_text"]
    fake_lang = ctx["fake_lang"]
    fake_bot = ctx["fake_bot"]
    message = ctx["message"]
    callback = ctx["callback"]

    # Act
    await unban_callback_logic(callback)

    # Assert
    mock_require_callback_context.assert_called_once_with(callback)
    mock_require_callback_bot.assert_called_once_with(callback)
    mock_get_chat_language.assert_called_once_with(fake_chat_id)

    assert fake_bot.unban_chat_member.await_count == len(fake_user_ids)
    fake_bot.unban_chat_member.assert_has_awaits(
        [call(chat_id=fake_chat_id, user_id=user_id) for user_id in fake_user_ids],
        any_order=False,
    )

    message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)

    message.edit_text.assert_awaited_once()
    args, kwargs = message.edit_text.call_args
    assert args[0] == f"<s>{message.text}</s> {fake_t_text}"
    assert kwargs["parse_mode"] == "HTML"

    assert mock_t.call_count == 2
    (args1, kwargs1), (args2, kwargs2) = list(
        map(lambda c: (c.args, c.kwargs), mock_t.call_args_list)
    )

    assert args1[0] == "moderation.common.canceled"
    assert args1[1] == fake_lang
    assert kwargs1 == {}

    assert args2[0] == "moderation.unban.callback.success"
    assert args2[1] == fake_lang
    assert kwargs2["target_names"] == ", ".join(str(i) for i in fake_user_ids)

    callback.answer.assert_awaited_once_with(fake_t_text)


@pytest.mark.asyncio
@patch("telegram_bot.handlers.moderation.commands.ban.logging.exception")
@patch("telegram_bot.handlers.moderation.commands.ban.t")
@patch("telegram_bot.handlers.moderation.commands.ban.get_chat_language")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_bot")
@patch("telegram_bot.handlers.moderation.commands.ban.require_callback_context")
async def test_unban_callback_logic_exception(
    mock_require_callback_context: Mock,
    mock_require_callback_bot: Mock,
    mock_get_chat_language: Mock,
    mock_t: Mock,
    mock_logging_exception: Mock,
):
    # Arrange
    fake_user_id = 1234567890
    fake_exception_message = "exception_message"

    ctx = _setup_unban_callback_test(
        mock_require_callback_context,
        mock_require_callback_bot,
        mock_get_chat_language,
        mock_t,
        str(fake_user_id),
    )
    fake_chat_id = ctx["fake_chat_id"]
    fake_t_text = ctx["fake_t_text"]
    fake_lang = ctx["fake_lang"]
    fake_bot = ctx["fake_bot"]
    callback = ctx["callback"]

    fake_bot.unban_chat_member = AsyncMock(
        side_effect=Exception(fake_exception_message)
    )

    # Act
    await unban_callback_logic(callback)

    # Assert
    mock_require_callback_context.assert_called_once_with(callback)
    mock_require_callback_bot.assert_called_once_with(callback)

    mock_get_chat_language.assert_called_once_with(fake_chat_id)

    # Should throw an exception
    fake_bot.unban_chat_member.assert_called_once_with(
        chat_id=fake_chat_id, user_id=fake_user_id
    )

    mock_logging_exception.assert_called_once()
    callback.answer.assert_called_once_with(fake_t_text, show_alert=True)

    mock_t.assert_called_once()
    args, kwargs = mock_t.call_args
    assert args[0] == "moderation.unban.error"
    assert args[1] == fake_lang
    assert "e" in kwargs
    assert fake_exception_message in kwargs["e"]


@pytest.mark.parametrize(
    "data, expected_result",
    [
        ["unban:1234567890", True],
        ["unban1234567890", False],
        ["ban:1234567890", False],
        [None, False],
    ],
)
def test_is_unban_callback(data: str, expected_result: bool):
    callback = Mock()
    callback.data = data

    assert is_unban_callback(callback) == expected_result


@patch("telegram_bot.handlers.moderation.commands.ban.t")
def test_get_unban_button_single_user(mock_t: Mock):
    lang = "en"
    fake_text = "Unban"
    mock_t.return_value = fake_text

    user = Mock()
    user.id = 42

    markup = get_unban_button(lang, [user])

    mock_t.assert_called_once_with("moderation.buttons.unban", lang)

    assert isinstance(markup, InlineKeyboardMarkup)
    assert len(markup.inline_keyboard) == 1
    assert len(markup.inline_keyboard[0]) == 1

    button = markup.inline_keyboard[0][0]
    assert isinstance(button, InlineKeyboardButton)
    assert button.text == fake_text
    assert button.callback_data == "unban:42"


@patch("telegram_bot.handlers.moderation.commands.ban.t")
def test_get_unban_button_multiple_users(mock_t: Mock):
    lang = "en"
    fake_text = "Unban all"
    mock_t.return_value = fake_text

    user1 = Mock()
    user1.id = 1
    user2 = Mock()
    user2.id = 2
    user3 = Mock()
    user3.id = 3

    markup = get_unban_button(lang, [user1, user2, user3])

    mock_t.assert_called_once_with("moderation.buttons.unban", lang)

    button = markup.inline_keyboard[0][0]
    assert button.text == fake_text
    assert button.callback_data == "unban:1,2,3"
