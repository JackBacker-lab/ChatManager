"""
Provide guard helpers for moderation handler.

These functions ensure that required bot, user, message, and callback data are available
before processing commands, echo messages, or callback queries.
"""

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User

from telegram_bot.i18n import t


def require_command_context(message: Message) -> tuple[str, Bot, User]:
    if message.text is None:
        raise AttributeError("Message.text must not be None")
    if message.bot is None:
        raise AttributeError("Message.bot must not be None")
    if message.from_user is None:
        raise AttributeError("Message.from_user must not be None")
    return message.text, message.bot, message.from_user


def require_echo_context(message: Message) -> tuple[Bot, User]:
    if message.bot is None:
        raise AttributeError("Message.bot must not be None")
    if message.from_user is None:
        raise AttributeError("Message.from_user must not be None")
    return message.bot, message.from_user


async def require_callback_context(callback: CallbackQuery) -> tuple[Message, str]:
    if callback.message is None or not isinstance(callback.message, Message):
        await callback.answer(t("moderation.common.message_not_found"))
        raise AttributeError("Callback.message must not be None")
    if callback.data is None:
        raise AttributeError("Callback.data must not be None")
    return callback.message, callback.data


async def require_callback_bot(callback: CallbackQuery) -> Bot:
    if callback.bot is None:
        raise AttributeError("Callback.bot must not be None")
    return callback.bot
