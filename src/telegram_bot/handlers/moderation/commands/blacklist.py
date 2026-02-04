from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.handlers.moderation.guards import (
    group_only,
    user_is_admin_message,
)
from telegram_bot.i18n import t
from telegram_bot.services.db.blacklist_service import (
    add_blacklist_word,
    get_blacklist_words,
    remove_blacklist_word,
)
from telegram_bot.services.db.chat_settings_service import get_chat_language

router = Router()


async def handle_blacklist_add(message: Message):
    """Handle /blacklist_add: add a word to the chat blacklist."""
    if message.text is None:
        raise AttributeError("Command message text must not be None")

    lang = await get_chat_language(message.chat.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(t("blacklist.add.no_args", lang))
        return

    word = args[1]
    await add_blacklist_word(message.chat.id, word)
    await message.reply(t("blacklist.add.success", lang, word=word))


async def blacklist_add_command_handler(message: Message):
    """Aiogram entrypoint for /blacklist_add."""
    await handle_blacklist_add(message)


async def handle_blacklist_remove(message: Message):
    """Handle /blacklist_remove: remove a word from the chat blacklist."""
    if message.text is None:
        raise AttributeError("Command message text must not be None")

    lang = await get_chat_language(message.chat.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(t("blacklist.remove.no_args", lang))
        return

    word = args[1]
    await remove_blacklist_word(message.chat.id, word)
    await message.reply(t("blacklist.remove.success", lang, word=word))


@router.message(Command("blacklist_remove"))
@group_only
@user_is_admin_message
async def blacklist_remove_command_handler(message: Message):
    """Aiogram entrypoint for /blacklist_remove."""
    await handle_blacklist_remove(message)


async def handle_blacklist_show(message: Message):
    """Handle /blacklist: show all blacklisted words for the current chat."""
    lang = await get_chat_language(message.chat.id)
    words = await get_blacklist_words(message.chat.id)
    if words:
        await message.reply(
            t("blacklist.display", lang) + "\n".join(f"• {word}" for word in words)
        )
    else:
        await message.reply(t("blacklist.empty", lang))


@router.message(Command("blacklist"))
@group_only
async def blacklist_command_hanlder(message: Message):
    """Aiogram entrypoint for /blacklist."""
    await handle_blacklist_show(message)
