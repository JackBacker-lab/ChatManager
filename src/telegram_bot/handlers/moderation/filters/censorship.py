import re
from difflib import SequenceMatcher

from telegram_bot.handlers.moderation.filters.base import (
    FilterError,
    FilterResult,
    FilterStatus,
    MessageContext,
)
from telegram_bot.models.filters import AICensorshipConfig, CensorshipConfig


class CensorshipFilter:
    """Check whether the text approximately contains any blacklisted word.

    The text and blacklist entries are normalized
    and then compared using fuzzy substring matching.
    """

    name = "blacklist"

    @staticmethod
    def _normalize_text(text: str, lang: str, config: CensorshipConfig) -> str:
        from .replacements import REPLACEMENTS

        text = text.lower()
        for base, variants in REPLACEMENTS[lang].items():
            for v in variants:
                text = text.replace(v, base)

        normalized = re.sub(r"[^а-яa-z0-9]", "", text)
        return normalized[: config.max_norm_text_len]

    @staticmethod
    def _is_similar(s1: str, s2: str, threshold: float = 0.85) -> bool:
        return SequenceMatcher(None, s1, s2).ratio() >= threshold

    @staticmethod
    def check(
        ctx: MessageContext,
        blacklist: list[str],
        config: CensorshipConfig,
    ) -> FilterResult:
        for lang in config.languages:
            norm_text = CensorshipFilter._normalize_text(ctx.text, lang, config)
            for bad_word in blacklist:
                norm_bad = CensorshipFilter._normalize_text(bad_word, lang, config)

                length = len(norm_bad)
                window_len_margin = config.window_len_margin
                window_range = range(
                    max(length - window_len_margin, 1),
                    length + window_len_margin + 1,
                )

                for window_len in window_range:
                    for i in range(len(norm_text) - window_len + 1):
                        fragment = norm_text[i : i + window_len]
                        if CensorshipFilter._is_similar(
                            fragment,
                            norm_bad,
                            threshold=config.similarity,
                        ):
                            return FilterResult(
                                triggered=True,
                                reason=CensorshipFilter.name,
                            )

        return FilterResult(triggered=False, reason="")


def get_ai_checker():
    from telegram_bot.experiments.censor_ai import is_toxic

    return is_toxic


class AICensorshipFilter:
    """Detect toxic content using AI classifiers.

    Delegate detection to the experimental censor_ai module when available.
    Silent return if AI censorship is turned off or dependencies are missing.
    """

    name = "ai_censor"

    @staticmethod
    async def check(ctx: MessageContext, config: AICensorshipConfig) -> FilterResult:
        try:
            is_toxic = get_ai_checker()
        except ImportError as e:
            return FilterResult(
                triggered=False,
                reason="",
                status=FilterStatus.SKIPPED,
                error=FilterError(code="ai_censor_dependency_missing", message=str(e)),
            )

        try:
            toxic = await is_toxic(ctx.text, config)
        except Exception as e:
            return FilterResult(
                triggered=False,
                reason="",
                status=FilterStatus.FAILED,
                error=FilterError(code="ai_censor_exception", message=str(e)),
            )

        if toxic:
            return FilterResult(triggered=True, reason=AICensorshipFilter.name)

        return FilterResult(triggered=False, reason="")
