from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import get_chat_language

router = Router()


@router.message(Command("help"))
async def help_command_handler(message: Message):
    """Show a summary of available bot features."""
    lang = await get_chat_language(message.chat.id)
    await message.answer(t("general.help", lang))
