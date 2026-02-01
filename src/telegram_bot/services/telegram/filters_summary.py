from telegram_bot.i18n import t
from telegram_bot.models.filters import FiltersConfig


def _on_off(value: bool, lang: str) -> str:
    return (
        t("moderation.filters.state.on", lang)
        if value
        else t("moderation.filters.state.off", lang)
    )


def build_filters_summary(filters: FiltersConfig, lang: str) -> str:
    """Build a summary message of all moderation filters for a chat."""
    censor = filters.censorship
    censorship_block: list[str] = [
        t(
            "moderation.filters.censorship.header",
            lang,
            state=_on_off(censor.enabled, lang),
        ),
        t(
            "moderation.filters.censorship.similarity",
            lang,
            similarity=str(censor.similarity),
        ),
        t(
            "moderation.filters.censorship.languages",
            lang,
            languages=", ".join(censor.languages),
        ),
        t(
            "moderation.filters.censorship.ai",
            lang,
            state=_on_off(censor.ai.enabled, lang),
            threshold=str(censor.ai.threshold),
        ),
    ]

    flood = filters.flood
    flood_block: list[str] = [
        t(
            "moderation.filters.flood.header",
            lang,
            state=_on_off(flood.enabled, lang),
        ),
        t(
            "moderation.filters.flood.limit",
            lang,
            limit=str(flood.message_limit),
            window=str(flood.time_window),
        ),
        t(
            "moderation.filters.flood.mute",
            lang,
            mute=str(flood.mute_time),
        ),
    ]

    spam = filters.spam
    spam_block: list[str] = [
        t(
            "moderation.filters.spam.header",
            lang,
            state=_on_off(spam.enabled, lang),
        ),
        t(
            "moderation.filters.spam.links",
            lang,
            state=_on_off(spam.links.enabled, lang),
        ),
        t(
            "moderation.filters.spam.caps",
            lang,
            state=_on_off(spam.caps.enabled, lang),
            ratio=str(spam.caps.ratio),
            min_length=str(spam.caps.min_length),
        ),
        t(
            "moderation.filters.spam.user_mentions",
            lang,
            state=_on_off(spam.user_mentions.enabled, lang),
            max=str(spam.user_mentions.max),
        ),
        t(
            "moderation.filters.spam.gibberish",
            lang,
            state=_on_off(spam.gibberish.enabled, lang),
        ),
    ]

    return "\n\n".join(
        "\n".join(block) for block in (censorship_block, flood_block, spam_block)
    )
