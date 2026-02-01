import re

from telegram_bot.handlers.moderation.filters.base import FilterResult, MessageContext
from telegram_bot.models.filters import (
    CapsConfig,
    GibberishConfig,
    LinksConfig,
    UserMentionsConfig,
)


class ExcessiveCapsFilter:
    """Detect whether a text contains an excessive amount of capital letters."""

    name = "excessive_caps"

    @staticmethod
    def check(ctx: MessageContext, config: CapsConfig) -> FilterResult:
        text = ctx.text
        letters = [c for c in text if c.isalpha()]
        if len(letters) < config.min_length:
            return FilterResult(triggered=False, reason="")

        uppercase = sum(c.isupper() for c in letters)
        ratio = uppercase / len(letters)

        if ratio >= config.ratio:
            return FilterResult(
                triggered=True,
                reason=ExcessiveCapsFilter.name,
                score=ratio,
            )

        return FilterResult(triggered=False, reason="", score=ratio)


class LinkFilter:
    """Detect whether a text contains an external link, except whitelisted domains."""

    name = "external_link"

    @staticmethod
    def check(ctx: MessageContext, config: LinksConfig) -> FilterResult:
        text = ctx.text
        if bool(re.search(r"https?://", text)) and all(
            w not in text for w in config.whitelist
        ):
            return FilterResult(triggered=True, reason=LinkFilter.name)

        return FilterResult(triggered=False, reason="")


class UserMentionsFilter:
    """Detect messages that mention too many users at once."""

    name = "many_users"

    @staticmethod
    def check(ctx: MessageContext, config: UserMentionsConfig) -> FilterResult:
        if ctx.text.count("@") > config.max:
            return FilterResult(triggered=True, reason=UserMentionsFilter.name)

        return FilterResult(triggered=False, reason="")


class GibberishSpamFilter:
    """Detect whether a text message appears to be gibberish or numeric-style spam."""

    name = "gibberish_or_numeric_spam"

    @staticmethod
    def has_low_char_variety(text: str, config: GibberishConfig) -> bool:
        return (
            len(text) >= config.min_length_low_variety
            and len(set(text.lower())) < config.min_unique_chars
        )

    @staticmethod
    def has_repeating_special_chars(text: str, config: GibberishConfig) -> bool:
        special_pattern = (
            rf"[?!@#$%^&*()_+=-]{{{config.max_special_chars_repeat_len + 1},}}"
        )
        return re.search(special_pattern, text) is not None

    @staticmethod
    def has_repeating_any_char(text: str, config: GibberishConfig) -> bool:
        any_char_pattern = rf"(.)\1{{{config.max_any_char_repeat_len},}}"
        return re.search(any_char_pattern, text) is not None

    @staticmethod
    def has_excessive_consonants(text: str, config: GibberishConfig) -> bool:
        cleaned = text.replace(" ", "")
        if len(cleaned) < config.min_length_consonant_check or not cleaned.isalpha():
            return False
        consonants = set("bcdfghjklmnpqrstvwxyz")
        consonant_ratio = sum(c in consonants for c in cleaned.lower()) / len(cleaned)
        return consonant_ratio > config.consonant_ratio_threshold

    @staticmethod
    def has_repeating_phrase(text: str, config: GibberishConfig) -> bool:
        phrase_pattern = (
            rf"(\w+(?:\W+\w+){{{config.phrase_min_words_count - 1},"
            rf"{config.phrase_max_words_count - 1}}})"
            rf"(?:\W+\1){{{config.max_phrase_repeats},}}"
        )
        return re.search(phrase_pattern, text, flags=re.IGNORECASE) is not None

    @staticmethod
    def check(ctx: MessageContext, config: GibberishConfig) -> FilterResult:
        text = ctx.text.strip()

        if GibberishSpamFilter.has_low_char_variety(text, config):
            return FilterResult(
                triggered=True,
                reason=GibberishSpamFilter.has_low_char_variety.__name__,
            )

        if GibberishSpamFilter.has_repeating_special_chars(text, config):
            return FilterResult(
                triggered=True,
                reason=GibberishSpamFilter.has_repeating_special_chars.__name__,
            )

        if GibberishSpamFilter.has_repeating_any_char(text, config):
            return FilterResult(
                triggered=True,
                reason=GibberishSpamFilter.has_repeating_any_char.__name__,
            )

        if GibberishSpamFilter.has_excessive_consonants(text, config):
            return FilterResult(
                triggered=True,
                reason=GibberishSpamFilter.has_excessive_consonants.__name__,
            )

        if GibberishSpamFilter.has_repeating_phrase(text, config):
            return FilterResult(
                triggered=True, reason=GibberishSpamFilter.has_repeating_phrase.__name__
            )

        return FilterResult(triggered=False, reason="")
