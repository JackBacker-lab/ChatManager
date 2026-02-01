import logging

from aiogram import Bot, Router
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, Message, User

from telegram_bot.handlers.moderation.commands.mute import mute_user
from telegram_bot.handlers.moderation.filters import (
    AICensorshipFilter,
    CensorshipFilter,
    ExcessiveCapsFilter,
    FilterResult,
    FloodFilter,
    GibberishSpamFilter,
    LinkFilter,
    MessageContext,
    UserMentionsFilter,
)
from telegram_bot.handlers.moderation.guards import (
    group_only,
    require_echo_context,
)
from telegram_bot.i18n import t
from telegram_bot.models.filters import (
    AICensorshipConfig,
    CensorshipConfig,
    FloodConfig,
    SpamConfig,
)
from telegram_bot.models.user import UserDTO
from telegram_bot.services.api.post_service import safe_post_groups
from telegram_bot.services.db.blacklist_service import get_blacklist_words
from telegram_bot.services.db.chat_settings_service import (
    get_chat_filters,
    get_chat_language,
)
from telegram_bot.services.db.users_service import register_user
from telegram_bot.services.telegram.display import get_display_name
from telegram_bot.services.telegram.resolve_targets import fetch_member

router = Router()

flood_filter = FloodFilter()


@group_only
@router.message()
async def echo_handler(message: Message) -> None:
    """Process incoming group messages and orchestrate moderation workflows.

    Register users, handle new member joins, and delegate flood,
    censorship, and spam checks to dedicated helper functions.
    """
    chat_id = message.chat.id
    text = message.text

    bot, user = require_echo_context(message)

    lang = await get_chat_language(chat_id)
    filter_configs = await get_chat_filters(chat_id)

    if await handle_new_chat_members(message, chat_id):
        return

    await handle_user_registration(chat_id, user)

    if await handle_antiflood(message, bot, chat_id, user, lang, filter_configs.flood):
        return

    if not text:
        return

    message_context = MessageContext(
        chat_id=chat_id,
        user_id=user.id,
        text=text,
    )

    if await handle_censorship(
        message, bot, chat_id, lang, message_context, filter_configs.censorship
    ):
        return

    await handle_antispam(message, bot, lang, message_context, filter_configs.spam)


async def handle_new_chat_members(message: Message, chat_id: int) -> bool:
    """Register each newly joined user in the database."""
    if message.new_chat_members:
        for user in message.new_chat_members:
            await register_user(
                UserDTO(
                    id=user.id,
                    full_name=user.full_name,
                    username=user.username,
                )
            )
            await safe_post_groups(chat_id, user.id)
            logging.info(f"New user in group: {get_display_name(user)} ({user.id})")
        return True
    return False


async def handle_user_registration(chat_id: int, user: User) -> None:
    """Store or refresh the user's profile information in the database."""
    await register_user(
        UserDTO(id=user.id, full_name=user.full_name, username=user.username)
    )
    await safe_post_groups(chat_id, user.id)
    logging.info(f"Received message from {get_display_name(user)} ({user.id})")


async def _mute_user_and_send_message(
    message: Message,
    bot: Bot,
    chat_id: int,
    lang: str,
    target_user: User,
    mute_time: int,
    reason: str,
) -> bool:
    """Apply a temporary mute to a user and send a notification to the chat.

    Skip administrators, perform the mute, and report the action to the chat.
    """
    try:
        target_member = await fetch_member(bot, chat_id, str(target_user.id))

        if isinstance(target_member, (ChatMemberAdministrator, ChatMemberOwner)):
            return False

        await mute_user(bot, chat_id, target_user.id, mute_time)

        me = await bot.get_me()
        await message.reply(
            t(
                "moderation.mute.success",
                lang,
                admin_name=get_display_name(me),
                target_names=get_display_name(target_user),
            )
            + "\n"
            + t("moderation.common.duration", duration=f"{mute_time}s")
            + "\n"
            + t("moderation.common.reason", lang, reason=reason)
        )
    except Exception as e:
        logging.exception("Mute error")
        await message.reply(t("moderation.mute.error", lang, e=str(e)))
        return False

    return True


async def handle_antiflood(
    message: Message, bot: Bot, chat_id: int, user: User, lang: str, config: FloodConfig
) -> bool:
    """Check whether the user has exceeded the allowed message rate in the chat.

    If flood is detected, apply a temporary mute and notify the chat about the
    moderation action.
    """
    if not config.enabled:
        return False

    ctx = MessageContext(chat_id=chat_id, user_id=user.id, text=message.text or "")
    flood_result = flood_filter.check(ctx, config)

    if flood_result.triggered:
        return await _mute_user_and_send_message(
            message, bot, chat_id, lang, user, config.mute_time, flood_result.reason
        )

    return False


async def _check_blacklist(
    chat_id: int, ctx: MessageContext, config: CensorshipConfig
) -> FilterResult:
    blacklist = await get_blacklist_words(chat_id)
    return CensorshipFilter.check(ctx, blacklist, config)


async def _check_ai(ctx: MessageContext, config: AICensorshipConfig) -> FilterResult:
    if config.enabled:
        return await AICensorshipFilter.check(ctx, config)

    return FilterResult(triggered=False, reason="")


async def handle_censorship(
    message: Message,
    bot: Bot,
    chat_id: int,
    lang: str,
    ctx: MessageContext,
    config: CensorshipConfig,
) -> bool:
    """Determine whether the message violates blacklist or AI-based censorship rules.

    If a violation is detected, remove the offending message and send a separate
    notification to the chat explaining that moderation was applied.
    """
    if not config.enabled:
        return False

    try:
        blacklist_result = await _check_blacklist(chat_id, ctx, config)
        ai_result = await _check_ai(ctx, config.ai)

        if blacklist_result.triggered or ai_result.triggered:
            reason = blacklist_result.reason or ai_result.reason
            try:
                await message.delete()
            except Exception as e:
                logging.exception("Failed to delete spam message.")
                await message.answer(
                    t("moderation.delete_message.error", lang, e=str(e))
                )
            try:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=(
                        t("moderation.delete_message.success", lang)
                        + "\n"
                        + t("moderation.common.reason", reason=reason)
                    ),
                )
            except Exception as e:
                logging.exception(f"Failed to send antispam notification: {e}")

            return True

    except Exception as e:
        logging.exception(f"Error while applying censorship filters: {e}")
        await message.answer(t("moderation.censor.error", lang, e=str(e)))

    return False


async def handle_antispam(
    message: Message,
    bot: Bot,
    lang: str,
    ctx: MessageContext,
    config: SpamConfig,
) -> None:
    """Run anti-spam filters for a message, delete it if any filter is triggered.

    Determine the primary reason for triggering
    and notify the user when their message is removed.
    """
    if not any(
        (
            config.links.enabled,
            config.caps.enabled,
            config.user_mentions.enabled,
            config.gibberish.enabled,
        )
    ):
        return

    (
        link_result,
        caps_result,
        user_mentions_result,
        gibberish_result,
    ) = _run_spam_filters(ctx, config)

    triggered_reason = _get_first_triggered_reason(
        link_result,
        caps_result,
        user_mentions_result,
        gibberish_result,
    )

    if triggered_reason is not None:
        try:
            await message.delete()
        except Exception as e:
            logging.exception(f"Failed to delete spam message: {e}")

        try:
            await bot.send_message(
                chat_id=message.chat.id,
                text=(
                    t("moderation.delete_message.success", lang)
                    + "\n"
                    + t("moderation.common.reason", lang, reason=triggered_reason)
                ),
            )
        except Exception as e:
            logging.exception(f"Error while applying censorship filters: {e}")
            await message.answer(t("moderation.delete_message.error", lang, e=str(e)))


def _run_spam_filters(
    ctx: MessageContext, config: SpamConfig
) -> tuple[FilterResult, FilterResult, FilterResult, FilterResult]:
    link_result = (
        LinkFilter.check(ctx, config.links)
        if getattr(config.links, "enabled", False)
        else FilterResult(triggered=False, reason="")
    )
    caps_result = (
        ExcessiveCapsFilter.check(ctx, config.caps)
        if getattr(config.caps, "enabled", False)
        else FilterResult(triggered=False, reason="")
    )
    user_mentions_result = (
        UserMentionsFilter.check(ctx, config.user_mentions)
        if getattr(config.user_mentions, "enabled", False)
        else FilterResult(triggered=False, reason="")
    )
    gibberish_result = (
        GibberishSpamFilter.check(ctx, config.gibberish)
        if getattr(config.gibberish, "enabled", False)
        else FilterResult(triggered=False, reason="")
    )
    return link_result, caps_result, user_mentions_result, gibberish_result


def _get_first_triggered_reason(*results: FilterResult) -> str | None:
    return next(
        (result.reason for result in results if result.triggered),
        None,
    )
