from telegram_bot.handlers.common.bot_added import router as bot_added_router
from telegram_bot.handlers.common.commands.help import router as help_router
from telegram_bot.handlers.common.commands.start import router as start_router
from telegram_bot.handlers.moderation.commands import (
    ban_router,
    blacklist_router,
    filters_router,
    kick_router,
    mute_router,
    warn_router,
)
from telegram_bot.handlers.moderation.echo import router as echo_router

routers = [
    bot_added_router,
    start_router,
    help_router,
    mute_router,
    ban_router,
    kick_router,
    warn_router,
    blacklist_router,
    filters_router,
    echo_router,
]
