import logging
from collections.abc import Awaitable, Callable

from aiogram import Bot
from aiogram.types import (
    ChatMember,
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
    InlineKeyboardMarkup,
    Message,
    User,
)

from telegram_bot.handlers.moderation.commands.utils.parsing import parse_duration
from telegram_bot.i18n import t
from telegram_bot.models.log import Log
from telegram_bot.services.api.post_service import safe_post_log
from telegram_bot.services.db.chat_settings_service import get_chat_language
from telegram_bot.services.telegram.build_messages import build_action_messages
from telegram_bot.services.telegram.display import get_display_name
from telegram_bot.services.telegram.message_links import get_message_link
from telegram_bot.services.telegram.resolve_targets import get_target_members
from telegram_bot.services.telegram.types import ActionLiteral

CHAT_MEMBER_TYPES = (
    ChatMemberOwner
    | ChatMemberAdministrator
    | ChatMemberMember
    | ChatMemberRestricted
    | ChatMemberLeft
    | ChatMemberBanned
)


def _split_text_and_parse_reason(text: str) -> tuple[str, str | None]:
    """Split command text into body and optional reason (last line)."""
    lines = text.split("\n")
    if len(lines) >= 2:
        reason = lines[-1].strip() or None
        cleaned_text = "\n".join(lines[:-1])
        return cleaned_text, reason
    return text, None


def _get_silent_mode(text: str, action_name: ActionLiteral) -> bool:
    silent_mode_prefix = f"/s{action_name}"
    return text.startswith(silent_mode_prefix)


def _split_text_and_parse_duration(text: str) -> tuple[str, str | None]:
    """Split command text into body and optional duration (last word in first line).

    If the last word of the first line is a valid duration (e.g. '10m'),
    it is removed from the text and returned as a string for display.
    """
    first_line, *rest_lines = text.split("\n", 1)
    parts = first_line.split()

    if not parts:
        return text, None

    candidate = parts[-1]

    duration_seconds = parse_duration(candidate)
    if duration_seconds == 0:
        return text, "forever"

    parts_without_duration = parts[:-1]
    cleaned_first_line = " ".join(parts_without_duration)

    if rest_lines:
        cleaned_text = cleaned_first_line + "\n" + rest_lines[0]
    else:
        cleaned_text = cleaned_first_line

    return cleaned_text, candidate


async def process_action(
    message: Message,
    text: str,
    bot: Bot,
    admin_user: User,
    action_name: ActionLiteral,
    action_func: Callable[[Bot, int, int], Awaitable[None]],  # bot, chat_id, user_id
    reply_markup_builder: (
        Callable[[str, list[User]], InlineKeyboardMarkup] | None
    ) = None,  # lang, target_members
) -> list[User] | None:
    """Process a moderation action command in a chat.

    Determine the target users, apply the specified action,
    and send a summary message to the chat.

    Return:
        List of acted users only for warn action
    """
    chat_id = message.chat.id
    lang = await get_chat_language(chat_id)

    text, reason = _split_text_and_parse_reason(text)
    text, duration = _split_text_and_parse_duration(text)
    silent_mode = _get_silent_mode(text, action_name)
    link = get_message_link(message)

    target_members = await get_target_members(message, text, bot)

    if not target_members:
        await message.reply(t("moderation.common.no_target_members", lang))
        return

    acted_users, skipped_members_names, unknown_members_names = await process_targets(
        bot,
        chat_id,
        admin_user,
        text,
        target_members,
        action_name,
        action_func,
        link,
        reason,
    )

    if silent_mode:
        await message.delete()
        return

    messages = build_action_messages(
        acted_users,
        skipped_members_names,
        unknown_members_names,
        admin_user,
        action_name,
        lang,
        reason,
        duration,
    )

    reply_markup = (
        reply_markup_builder(lang, acted_users)
        if reply_markup_builder and acted_users
        else None
    )
    await message.reply("\n".join(messages), reply_markup=reply_markup)

    if action_name == "warn":
        return acted_users


async def process_targets(
    bot: Bot,
    chat_id: int,
    admin_user: User,
    text: str,
    target_members: list[ChatMember | str],
    action_name: ActionLiteral,
    action_func: Callable[[Bot, int, int], Awaitable[None]],
    link: str | None = None,
    reason: str | None = None,
) -> tuple[list[User], list[str], list[str]]:
    """Process a list of target members for a moderation action.

    Apply the specified action to each valid target member.

    Return:
        A tuple containing lists of acted users,
        skipped member names, and unknown member names.
    """
    acted_users: list[User] = []
    skipped_members_names: list[str] = []
    unknown_members_names: list[str] = []

    for target_member in target_members:
        if isinstance(target_member, str):
            unknown_members_names.append(target_member)
            continue

        if not isinstance(target_member, CHAT_MEMBER_TYPES):
            raise RuntimeError(
                f"Unexpected ChatMember type: {type(target_member).__name__}. \
                Expected one of: {CHAT_MEMBER_TYPES}"
            )

        if _can_user_be_restricted(target_member, bot.id, admin_user.id):
            skipped_members_names.append(get_display_name(target_member.user))
            continue

        try:
            acted_users.append(target_member.user)
            await action_func(bot, chat_id, target_member.user.id)
            log_status = "success"
            log_details = ""

        except Exception as e:
            logging.info(f"Error while {action_name}: {e}")
            log_status = "error"
            log_details = str(e)

        log = Log(
            chat_id=chat_id,
            status=log_status,
            action=action_name,
            action_by_id=admin_user.id,
            target_id=target_member.user.id,
            text=text,
            link=link,
            reason=reason,
            details=log_details,
        )
        await safe_post_log(log)

    return acted_users, skipped_members_names, unknown_members_names


def _can_user_be_restricted(
    member: CHAT_MEMBER_TYPES,
    bot_id: int,
    admin_user_id: int,
) -> bool:
    """Return True if the target should be skipped (admin, self, or not in chat)."""
    is_user_admin = isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))
    is_user_self = member.user.id in (bot_id, admin_user_id)
    is_user_not_participant = isinstance(member, (ChatMemberLeft, ChatMemberBanned))
    return is_user_admin or is_user_self or is_user_not_participant
