from aiogram.types import User

from telegram_bot.i18n import t
from telegram_bot.services.telegram.display import get_display_name
from telegram_bot.services.telegram.types import ActionLiteral


def build_action_messages(
    acted_users: list[User],
    skipped_members_names: list[str],
    unknown_members_names: list[str],
    admin_user: User,
    action_name: ActionLiteral,
    lang: str,
    reason: str | None = None,
    duration: str | None = None,
) -> list[str]:
    """Build summary messages for a moderation action."""
    messages: list[str] = []

    if acted_users:
        # Use string concatenation instead of f-strings so static i18n key checks
        # can detect the base key prefix and verify that all action-specific keys exist.
        messages.append(
            t(
                "moderation." + action_name + ".success",
                lang,
                target_names=", ".join(get_display_name(u) for u in acted_users),
                admin_name=get_display_name(admin_user),
            )
        )
    if duration:
        messages.append(t("moderation.common.duration", lang, duration=duration))
    if skipped_members_names:
        messages.append(
            t(
                "moderation.common.skipped_members",
                lang,
                target_names=", ".join(skipped_members_names),
            )
        )
    if unknown_members_names:
        messages.append(
            t(
                "moderation.common.unidentified_members",
                lang,
                target_names=", ".join(unknown_members_names),
            )
        )
    if reason:
        messages.append(t("moderation.common.reason", lang, reason=reason))

    return messages
