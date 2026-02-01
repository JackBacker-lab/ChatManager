from aiogram.types import Message


def get_message_link(message: Message) -> str | None:
    """Generate a public or private Telegram link for a message.

    Return None for private chats where message links are not available.
    """
    if message.chat.username:
        return f"https://t.me/{message.chat.username}/{message.message_id}"
    elif message.chat.type in ("group", "supergroup"):
        chat_id = str(message.chat.id).replace("-100", "")
        return f"https://t.me/c/{chat_id}/{message.message_id}"
    else:
        return None
