from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.handlers.moderation.guards import (
    bot_has_rights_message,
    require_command_context,
    supergroup_only_message,
    user_is_admin_message,
)
from telegram_bot.services.telegram.processor import process_action

router = Router()


async def handle_kick_command(message: Message):
    """Remove one or more target users from the chat."""
    text, bot, admin_user = require_command_context(message)

    async def do_kick(bot: Bot, chat_id: int, user_id: int):
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)

    await process_action(message, text, bot, admin_user, "kick", do_kick)


@router.message(Command(commands=["kick", "skick"]))
@bot_has_rights_message
@user_is_admin_message
@supergroup_only_message
async def kick_command_handler(message: Message):
    """Aiogram entrypoint for /kick."""
    await handle_kick_command(message)
