from telegram_bot.handlers.moderation.filters import MessageContext


def make_fake_message_context(text: str) -> MessageContext:
    return MessageContext(
        chat_id=1234567890,
        user_id=9876543210,
        text=text,
    )
