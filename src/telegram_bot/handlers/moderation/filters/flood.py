import time

from telegram_bot.handlers.moderation.filters.base import FilterResult, MessageContext
from telegram_bot.models.filters import FloodConfig


class FloodFilter:
    """Check whether a user has exceeded the allowed message rate in a chat.

    Track per-user message timestamps and triggers
    when the configured limit is exceeded.
    """

    name = "flood"

    def __init__(self) -> None:
        # {(chat_id, user_id): [timestamp, timestamp, ...]}
        self.user_messages: dict[tuple[int, int], list[float]] = {}

    def check(self, ctx: MessageContext, config: FloodConfig) -> FilterResult:
        key = (ctx.chat_id, ctx.user_id)
        now = time.time()

        timestamps = self.user_messages.get(key, [])
        timestamps = [t for t in timestamps if now - t < config.time_window]
        timestamps.append(now)

        self.user_messages[key] = timestamps

        if len(timestamps) >= config.message_limit:
            self.user_messages[key] = []
            return FilterResult(triggered=True, reason=self.name)

        return FilterResult(triggered=False, reason="")
