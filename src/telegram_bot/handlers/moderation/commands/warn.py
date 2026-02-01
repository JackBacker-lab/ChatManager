from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message, User

from telegram_bot.handlers.moderation.commands.ban import get_unban_button
from telegram_bot.handlers.moderation.guards import (
    bot_has_rights_message,
    group_only,
    require_command_context,
    user_is_admin_message,
)
from telegram_bot.i18n import t
from telegram_bot.models.log import Log
from telegram_bot.services.api.post_service import safe_post_log
from telegram_bot.services.db.chat_settings_service import get_chat_language
from telegram_bot.services.db.warns_service import (
    add_user_warning,
    get_user_warnings,
    reset_user_warnings,
)
from telegram_bot.services.telegram.display import get_display_name
from telegram_bot.services.telegram.processor import get_message_link, process_action

router = Router()


async def _ban_user_and_send_message(
    message: Message,
    text: str,
    bot: Bot,
    chat_id: int,
    lang: str,
    target_user: User,
    link: str | None = None,
) -> None:
    """Ban a user when their warning limit is reached.

    Reset warnings for banned user, log action, and notify the chat.
    """
    log_status = "success"
    log_details = ""
    try:
        await message.reply(
            t(
                "moderation.warn.limit_reached",
                lang,
                display_name=get_display_name(target_user),
            )
        )
        await bot.ban_chat_member(chat_id=chat_id, user_id=target_user.id)

        me = await bot.get_me()
        await message.reply(
            t(
                "moderation.ban.success",
                lang,
                target_names=get_display_name(target_user),
                admin_name=get_display_name(me),
            ),
            reply_markup=get_unban_button(lang, [target_user]),
        )
        await reset_user_warnings(chat_id, target_user.id)
    except Exception as e:
        me = await bot.get_me()
        log_status = "error"
        log_details = str(e)
        await message.reply(t("moderation.ban.error", lang, e=str(e)))

    log = Log(
        chat_id=chat_id,
        status=log_status,
        action="ban",
        action_by_id=me.id,
        target_id=target_user.id,
        text=text,
        link=link,
        reason=t("moderation.warn.limit_reached"),
        details=log_details,
    )
    await safe_post_log(log)


@router.message(Command("warn"))
@bot_has_rights_message
@user_is_admin_message
@group_only
async def warn_user(message: Message):
    """Warn one or more target users in the chat.

    Increment the warning counter for target users, send a summary to the chat,
    and escalate to an automatic ban when the warning limit is reached.
    """
    chat_id = message.chat.id
    text, bot, admin_user = require_command_context(message)

    lang = await get_chat_language(chat_id)
    link = get_message_link(message)

    async def do_warn(bot: Bot, chat_id: int, user_id: int):
        await add_user_warning(chat_id, user_id)

    warned_users = await process_action(
        message,
        text,
        bot,
        admin_user,
        "warn",
        do_warn,
        reply_markup_builder=get_unban_button,
    )

    if warned_users is None:
        raise RuntimeError("Process_action returned None for warn handler.")

    for warned_user in warned_users:
        count = await get_user_warnings(chat_id, warned_user.id)
        if count >= 3:
            await _ban_user_and_send_message(
                message=message,
                text=text,
                bot=bot,
                chat_id=chat_id,
                lang=lang,
                target_user=warned_user,
                link=link,
            )


@router.message(Command("warns_reset"))
@bot_has_rights_message
@user_is_admin_message
@group_only
async def reset_warns(message: Message):
    """Reset warnings for one or more target users."""
    text, bot, admin_user = require_command_context(message)

    async def do_reset_warns(bot: Bot, chat_id: int, user_id: int):
        await reset_user_warnings(chat_id, user_id)

    await process_action(
        message,
        text,
        bot,
        admin_user,
        "reset_warns",
        do_reset_warns,
        reply_markup_builder=get_unban_button,
    )
