from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.handlers.moderation.guards import (
    group_only,
    user_is_admin_message,
)
from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import (
    get_chat_filters,
    get_chat_language,
    set_chat_ai_censorship,
    set_chat_antispam,
    set_chat_censorship,
)
from telegram_bot.services.telegram.filters_summary import build_filters_summary

router = Router()


@router.message(Command("filters"))
@group_only
@user_is_admin_message
async def filters_command_filters(message: Message):
    """Show a summary of all moderation filters configured for this chat."""
    lang = await get_chat_language(message.chat.id)
    filters = await get_chat_filters(message.chat.id)
    summary = build_filters_summary(filters, lang)
    await message.reply(t("moderation.filters.display", lang, summary=summary))


@router.message(Command("censor_on"))
@group_only
@user_is_admin_message
async def censor_on_command_handler(message: Message):
    """Enable blacklist-based censorship in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_censorship(message.chat.id, True)
    await message.reply(t("moderation.modes.censorship.on", lang))


@router.message(Command("censor_off"))
@group_only
@user_is_admin_message
async def censor_off_command_handler(message: Message):
    """Disable blacklist-based censorship in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_censorship(message.chat.id, False)
    await message.reply(t("moderation.modes.censorship.off", lang))


@router.message(Command("ai_censor_on"))
@group_only
@user_is_admin_message
async def ai_censor_on_command_handler(message: Message):
    """Enable AI-based censorship in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_ai_censorship(message.chat.id, True)
    await message.reply(t("moderation.modes.censorship.on", lang))


@router.message(Command("ai_censor_off"))
@group_only
@user_is_admin_message
async def ai_censor_off_command_handler(message: Message):
    """Disable AI-based censorship in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_ai_censorship(message.chat.id, False)
    await message.reply(t("moderation.modes.censorship.off", lang))


@router.message(Command("antispam_on"))
@group_only
@user_is_admin_message
async def antispam_on_command_handler(message: Message):
    """Enable anti-spam filters in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_antispam(message.chat.id, True)
    await message.reply(t("moderation.modes.antispam.on", lang))


@router.message(Command("antispam_off"))
@group_only
@user_is_admin_message
async def antispam_off_command_handler(message: Message):
    """Disable anti-spam filters in the current chat."""
    lang = await get_chat_language(message.chat.id)
    await set_chat_antispam(message.chat.id, False)
    await message.reply(t("moderation.modes.antispam.off", lang))
