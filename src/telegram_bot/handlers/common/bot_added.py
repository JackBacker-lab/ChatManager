import logging

from aiogram import Router
from aiogram.types import ChatMemberUpdated

from telegram_bot.models.user import UserDTO
from telegram_bot.services.api.post_service import safe_post_groups
from telegram_bot.services.db.chat_service import add_chat
from telegram_bot.services.db.users_service import register_user

router = Router()


@router.my_chat_member()
async def bot_added(update: ChatMemberUpdated):
    """Register the chat and its administrators in the system."""
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        chat = update.chat
        logging.info(f"Bot added to chat: {chat.title} ({chat.id})")
        await add_chat(chat.id, chat.title, chat.type)
        admins = await chat.get_administrators()
        for admin in admins:
            user = admin.user
            await register_user(
                UserDTO(id=user.id, full_name=user.full_name, username=user.username)
            )
            await safe_post_groups(chat.id, admin.user.id)
