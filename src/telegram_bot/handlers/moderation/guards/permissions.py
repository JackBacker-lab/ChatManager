"""
Decorators for validating permissions and chat type in moderation handlers.

These helpers ensure that commands are used in the correct chat context and that both
users and the bot have sufficient rights before executing moderation logic.
"""

from collections.abc import Awaitable, Callable
from functools import wraps

from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery, Message

from telegram_bot.i18n import t
from telegram_bot.services.db.chat_settings_service import get_chat_language


def group_only(
    handler: Callable[[Message], Awaitable[None]],
) -> Callable[[Message], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(message: Message) -> None:
        lang = await get_chat_language(message.chat.id)

        if message.chat.type not in ("group", "supergroup"):
            await message.reply(t("decorators.not_group", lang))
            return

        await handler(message)

    return wrapper


def supergroup_only_message(
    handler: Callable[[Message], Awaitable[None]],
) -> Callable[[Message], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(message: Message) -> None:
        lang = await get_chat_language(message.chat.id)
        if message.chat.type != "supergroup":
            await message.reply(t("decorators.not_supergroup", lang))
            return

        return await handler(message)

    return wrapper


def supergroup_only_callback(
    handler: Callable[[CallbackQuery], Awaitable[None]],
) -> Callable[[CallbackQuery], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(callback: CallbackQuery) -> None:
        if callback.message is None:
            return

        lang = await get_chat_language(callback.message.chat.id)
        if callback.message.chat.type != "supergroup":
            await callback.answer(t("decorators.not_supergroup", lang))
            return

        return await handler(callback)

    return wrapper


def user_is_admin_message(
    handler: Callable[[Message], Awaitable[None]],
) -> Callable[[Message], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(message: Message) -> None:
        if message.from_user is None or message.bot is None:
            return

        lang = await get_chat_language(message.chat.id)
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        if member.status not in ("administrator", "creator"):
            await message.reply(t("decorators.user_is_not_admin", lang))
            return

        await handler(message)

    return wrapper


def user_is_admin_callback(
    handler: Callable[[CallbackQuery], Awaitable[None]],
) -> Callable[[CallbackQuery], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(callback: CallbackQuery) -> None:
        if callback.bot is None or callback.message is None:
            return

        lang = await get_chat_language(callback.message.chat.id)
        member = await callback.bot.get_chat_member(
            callback.message.chat.id, callback.from_user.id
        )
        if member.status not in ("administrator", "creator"):
            await callback.answer(
                t("decorators.user_is_not_admin", lang), show_alert=True
            )
            return

        await handler(callback)

    return wrapper


def bot_has_rights_message(
    handler: Callable[[Message], Awaitable[None]],
) -> Callable[[Message], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(message: Message) -> None:
        if message.bot is None:
            return

        lang = await get_chat_language(message.chat.id)
        bot_member = await message.chat.get_member(message.bot.id)
        if not (
            bot_member.status == ChatMemberStatus.ADMINISTRATOR
            and bot_member.can_restrict_members
        ):
            await message.reply(t("decorators.bot_has_not_rights", lang))
            return

        return await handler(message)

    return wrapper


def bot_has_rights_callback(
    handler: Callable[[CallbackQuery], Awaitable[None]],
) -> Callable[[CallbackQuery], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(callback: CallbackQuery):
        if callback.message is None or callback.message.bot is None:
            return

        lang = await get_chat_language(callback.message.chat.id)
        bot_member = await callback.message.chat.get_member(callback.message.bot.id)
        if not (
            bot_member.status == ChatMemberStatus.ADMINISTRATOR
            and bot_member.can_restrict_members
        ):
            await callback.answer(
                t("decorators.bot_has_not_rights", lang), show_alert=True
            )
            return

        return await handler(callback)

    return wrapper
