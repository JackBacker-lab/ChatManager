import logging
import time

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from telegram_bot.handlers.moderation.commands.utils.parsing import parse_duration
from telegram_bot.handlers.moderation.guards import (
    bot_has_rights_callback,
    bot_has_rights_message,
    require_callback_bot,
    require_callback_context,
    require_command_context,
    supergroup_only_message,
    user_is_admin_callback,
    user_is_admin_message,
)
from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import get_chat_language
from telegram_bot.services.telegram.processor import process_action

router = Router()

UNMUTE_CALLBACK_PREFIX = "unmute:"


async def mute_user(
    bot: Bot, chat_id: int, user_id: int, duration_seconds: int
) -> None:
    """Mute a user in the chat for the give duration."""
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=int(time.time()) + duration_seconds,
    )


async def handle_mute_command(message: Message):
    """Handle /mute: parse duration and schedule temporary mutes for target users."""
    text, bot, admin_user = require_command_context(message)

    duration_seconds = parse_duration(text.split("\n")[0].split()[-1])

    async def do_mute(bot: Bot, chat_id: int, user_id: int):
        await mute_user(bot, chat_id, user_id, duration_seconds)

    await process_action(
        message,
        text,
        bot,
        admin_user,
        "mute",
        do_mute,
        reply_markup_builder=get_unmute_button,
    )


@router.message(Command(commands=["mute", "smute"]))
@user_is_admin_message
@bot_has_rights_message
@supergroup_only_message
async def mute_command_handler(message: Message):
    """Aiogram entrypoint for /mute."""
    await handle_mute_command(message)


async def handle_unmute_command(message: Message):
    """Handle /unmute: lift mute from one or more target users in the chat."""
    text, bot, admin_user = require_command_context(message)

    async def do_unmute(bot: Bot, chat_id: int, user_id: int):
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=0,
        )

    await process_action(message, text, bot, admin_user, "unmute", do_unmute)


@router.message(Command(commands=["unmute", "sunmute"]))
@user_is_admin_message
@bot_has_rights_message
@supergroup_only_message
async def unmute_command_handler(message: Message):
    """Aiogram entrypoint for /unmute."""
    await handle_unmute_command(message)


def is_unmute_callback(c: CallbackQuery) -> bool:
    return c.data is not None and c.data.startswith(UNMUTE_CALLBACK_PREFIX)


async def handle_unmute_callback(callback: CallbackQuery):
    """Handle unmute callback presses and lift mute from selected users."""
    msg, data = await require_callback_context(callback)
    bot = await require_callback_bot(callback)

    chat_id = msg.chat.id
    lang = await get_chat_language(msg.chat.id)
    data = data.replace(UNMUTE_CALLBACK_PREFIX, "")
    target_members_ids = data.split(",")

    try:
        for target_member_id in target_members_ids:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=int(target_member_id),
                permissions=ChatPermissions(can_send_messages=True),
                until_date=0,
            )

        await msg.edit_reply_markup(reply_markup=None)
        await msg.edit_text(
            f"<s>{msg.text}</s> {t('moderation.common.canceled', lang)}",
            parse_mode="HTML",
        )
        await callback.answer(
            t(
                "moderation.unmute.callback.success",
                lang,
                target_names=", ".join(target_members_ids),
            )
        )
    except Exception as e:
        logging.exception(f"Unmute (callback) error: {e}")
        await callback.answer(
            t("moderation.unmute.error", lang, e=str(e)), show_alert=True
        )


@router.callback_query(is_unmute_callback)
@user_is_admin_callback
@bot_has_rights_callback
async def unmute_callback_handler(callback: CallbackQuery):
    """Aiogram entrypoint for unmute callback."""
    await handle_unmute_callback(callback)


def get_unmute_button(lang: str, target_users: list[User]) -> InlineKeyboardMarkup:
    """Build an inline keyboard with a bulk unmute button for selected users."""
    target_users_ids = ",".join(str(u.id) for u in target_users)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("moderation.buttons.unmute", lang),
                    callback_data=f"{UNMUTE_CALLBACK_PREFIX}{target_users_ids}",
                )
            ]
        ]
    )
