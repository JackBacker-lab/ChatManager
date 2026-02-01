from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from telegram_bot.handlers.moderation.guards import require_callback_context
from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import (
    get_chat_language,
    set_chat_language,
)

router = Router()

SET_LANG_CALLBACK_PREFIX = "set_lang:"


@router.message(CommandStart())
async def start_command_handler(message: Message):
    """Show the language selection keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
            [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang:ua")],
        ]
    )
    lang = await get_chat_language(message.chat.id)
    await message.answer(t("general.start", lang), reply_markup=keyboard)


def is_set_lang_callback(c: CallbackQuery) -> bool:
    return c.data is not None and c.data.startswith(SET_LANG_CALLBACK_PREFIX)


@router.callback_query(is_set_lang_callback)
async def set_language_callback_handler(callback: CallbackQuery):
    """Update the chat language."""
    message, data = await require_callback_context(callback)
    chat_id = message.chat.id
    lang = data.split(":")[1]

    await set_chat_language(chat_id, lang)

    await callback.answer(t("general.lang_set", lang), show_alert=True)
    await message.edit_text(t("general.lang_set", lang))
