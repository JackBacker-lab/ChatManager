import logging

from aiogram import Bot
from aiogram.types import ChatMember, Message

from telegram_bot.services.db.users_service import get_user
from telegram_bot.services.telegram.types import ChatMemberTypes


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
    """Retrieve and return a list of chat members targeted by a moderation command.

    Ensure each concrete user appears only once (by user.id).
    """
    chat_id = message.chat.id
    parts = text.split()[1:]
    members: list[ChatMember | str] = []
    seen_ids: set[int] = set()

    # 1) target from reply
    if message.reply_to_message and message.reply_to_message.from_user:
        try:
            user_id = message.reply_to_message.from_user.id
            cm = await bot.get_chat_member(chat_id, user_id)
            members.append(cm)
            seen_ids.add(user_id)
        except Exception as e:
            logging.warning(f"Failed to fetch reply member: {e}")

    # 2) targets from command text
    for part in parts:
        member = await fetch_member(bot, chat_id, part)

        if isinstance(member, ChatMemberTypes):
            user_id = member.user.id
            if user_id in seen_ids:
                continue
            seen_ids.add(user_id)

        members.append(member)

    return members
