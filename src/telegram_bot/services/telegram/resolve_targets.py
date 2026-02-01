import logging

from aiogram import Bot
from aiogram.types import ChatMember, Message

from telegram_bot.services.db.users_service import get_user


async def fetch_member(bot: Bot, chat_id: int, identifier: str) -> ChatMember | str:
    """Return ChatMember by username or ID if resolved, else original identifier."""
    try:
        member = identifier
        if identifier.startswith("@"):
            if user := await get_user(username=identifier[1:]):
                user_id = user.id
                member = await bot.get_chat_member(chat_id, user_id)
        elif identifier.isdigit() or (
            identifier.startswith("-") and identifier[1:].isdigit()
        ):
            user_id = int(identifier)
            member = await bot.get_chat_member(chat_id, user_id)

        return member

    except Exception as e:
        logging.warning(f"Failed to fetch member {identifier}: {e}")
        return identifier


async def get_target_members(
    message: Message, text: str, bot: Bot
) -> list[ChatMember | str]:
    """Retrieve and return a list of chat members targeted by a moderation command."""
    chat_id = message.chat.id
    parts = text.split()[1:]
    members: list[ChatMember | str] = []

    if message.reply_to_message and message.reply_to_message.from_user:
        try:
            cm = await bot.get_chat_member(
                chat_id, message.reply_to_message.from_user.id
            )
            members.append(cm)
        except Exception as e:
            logging.warning(f"Failed to fetch reply member: {e}")

    for part in parts:
        member = await fetch_member(bot, chat_id, part)
        members.append(member)

    return members
