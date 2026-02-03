import logging
import time

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from telegram_bot.handlers.moderation.commands.utils.parsing import parse_duration
from telegram_bot.handlers.moderation.guards import (
    bot_has_rights_callback,
    bot_has_rights_message,
    group_only,
    require_callback_bot,
    require_callback_context,
    require_command_context,
    supergroup_only_callback,
    supergroup_only_message,
    user_is_admin_callback,
    user_is_admin_message,
)
from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import get_chat_language
from telegram_bot.services.telegram.processor import process_action

router = Router()

UNBAN_CALLBACK_PREFIX = "unban:"


async def ban_user(bot: Bot, chat_id: int, user_id: int, duration_seconds: int) -> None:
    """Ban a user in the chat for the given duration."""
    await bot.ban_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        until_date=int(time.time()) + duration_seconds,
    )


async def ban_logic(message: Message):
    """Core logic for /ban command without decorators."""
    text, bot, admin_user = require_command_context(message)

    duration_seconds = parse_duration(text.split("\n")[0].split()[-1])

    async def do_ban(bot: Bot, chat_id: int, user_id: int):
        await ban_user(bot, chat_id, user_id, duration_seconds)

    await process_action(
        message,
        text,
        bot,
        admin_user,
        "ban",
        do_ban,
        reply_markup_builder=get_unban_button,
    )


@router.message(Command(commands=["ban", "sban"]))
@bot_has_rights_message
@user_is_admin_message
@group_only
async def ban_command_handler(message: Message):
    """Apply a temporary ban to one or more target users."""
    await ban_logic(message)


async def unban_logic(message: Message):
    text, bot, admin_user = require_command_context(message)

    async def do_unban(bot: Bot, chat_id: int, user_id: int):
        await bot.unban_chat_member(chat_id, user_id)

    await process_action(message, text, bot, admin_user, "unban", do_unban)


@router.message(Command(commands=["unban", "sunban"]))
@bot_has_rights_message
@user_is_admin_message
@supergroup_only_message
async def unban_command_handler(message: Message):
    """Lift bans from one or more target users in the chat."""
    await unban_logic(message)


def is_unban_callback(c: CallbackQuery) -> bool:
    return c.data is not None and c.data.startswith(UNBAN_CALLBACK_PREFIX)


async def unban_callback_logic(callback: CallbackQuery):
    msg, data = await require_callback_context(callback)
    bot = await require_callback_bot(callback)

    chat_id = msg.chat.id
    lang = await get_chat_language(msg.chat.id)
    data = data.replace(UNBAN_CALLBACK_PREFIX, "")
    target_members_ids = data.split(",")

    try:
        for target_member_id in target_members_ids:
            await bot.unban_chat_member(chat_id=chat_id, user_id=int(target_member_id))
        await msg.edit_reply_markup(reply_markup=None)
        await msg.edit_text(
            f"<s>{msg.text}</s> {t('moderation.common.canceled', lang)}",
            parse_mode="HTML",
        )
        await callback.answer(
            t(
                "moderation.unban.callback.success",
                lang,
                target_names=", ".join(target_members_ids),
            )
        )
    except Exception as e:
        logging.exception(f"Unban (callback) error: {e}")
        await callback.answer(
            t("moderation.unban.error", lang, e=str(e)), show_alert=True
        )


@router.callback_query(is_unban_callback)
@user_is_admin_callback
@bot_has_rights_callback
@supergroup_only_callback
async def unban_callback_handler(callback: CallbackQuery):
    """Handle unban callback presses and lift bans from selected users."""
    await unban_callback_logic(callback)


def get_unban_button(lang: str, target_users: list[User]) -> InlineKeyboardMarkup:
    """Build an inline keyboard with a bulk unban button for selected users."""
    target_users_ids = ",".join(str(u.id) for u in target_users)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("moderation.buttons.unban", lang),
                    callback_data=f"{UNBAN_CALLBACK_PREFIX}{target_users_ids}",
                )
            ]
        ]
    )
