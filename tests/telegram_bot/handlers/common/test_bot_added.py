from unittest.mock import AsyncMock, Mock, patch

import pytest

from telegram_bot.handlers.common.bot_added import bot_added
from telegram_bot.models.user import UserDTO


@pytest.mark.asyncio
@patch("telegram_bot.handlers.common.bot_added.register_user")
@patch("telegram_bot.handlers.common.bot_added.add_chat")
async def test_bot_added(mock_add_chat: Mock, mock_register_user: Mock):
    # Arrange
    fake_old_chat_member_status = "kicked"
    fake_new_chat_member_status = "member"
    fake_chat_title = "SomeChat"
    fake_chat_id = 1234567890
    fake_chat_type = "group"
    fake_admin_user_id = 1234509876
    fake_admin_full_name = "John Doe"
    fake_admin_username = "@johndoe"

    fake_user = Mock()
    fake_user.id = fake_admin_user_id
    fake_user.full_name = fake_admin_full_name
    fake_user.username = fake_admin_username

    fake_admin = Mock()
    fake_admin.user = fake_user
    fake_admins = [fake_admin]

    update = Mock()
    update.old_chat_member.status = fake_old_chat_member_status
    update.new_chat_member.status = fake_new_chat_member_status
    update.chat.title = fake_chat_title
    update.chat.id = fake_chat_id
    update.chat.type = fake_chat_type
    update.chat.get_administrators = AsyncMock(return_value=fake_admins)

    # Act
    await bot_added(update)

    # Assert
    mock_add_chat.assert_called_once_with(fake_chat_id, fake_chat_title, fake_chat_type)

    mock_register_user.assert_called_once()
    (user_dto,), _ = mock_register_user.call_args
    assert isinstance(user_dto, UserDTO)
    assert user_dto.id == fake_admin_user_id
    assert user_dto.full_name == fake_admin_full_name
    assert user_dto.username == fake_admin_username
