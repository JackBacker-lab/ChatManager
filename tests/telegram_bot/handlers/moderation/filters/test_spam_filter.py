import pytest

from telegram_bot.handlers.moderation.filters import (
    ExcessiveCapsFilter,
    GibberishSpamFilter,
    LinkFilter,
    UserMentionsFilter,
)
from telegram_bot.models.filters import GibberishConfig, SpamConfig

from .fake_message_context import make_fake_message_context

GIBBERISH_METHOD_NAMES = [
    "has_low_char_variety",
    "has_repeating_special_chars",
    "has_repeating_any_char",
    "has_excessive_consonants",
    "has_repeating_phrase",
]


@pytest.mark.parametrize(
    "sample, ratio, min_length, expected_trigger",
    [
        pytest.param("70% CAPS IN Text", 0.7, 10, True, id="ratio_at_threshold"),
        pytest.param(
            "ALL CAPS TEXT",
            0.5,
            15,
            False,
            id="too_short",
        ),
        pytest.param(
            "SOME CAPS and some lower",
            0.41,
            5,
            False,
            id="below_threshold",
        ),
    ],
)
def test_caps_filter_threshold_behavior(
    sample: str, ratio: float, min_length: int, expected_trigger: bool
) -> None:
    ctx = make_fake_message_context(sample)
    config = SpamConfig().caps
    config.ratio = ratio
    config.min_length = min_length

    result = ExcessiveCapsFilter.check(ctx, config)

    assert result.triggered == expected_trigger


@pytest.mark.parametrize(
    "text",
    [
        "",
        "😂😂😂😂",
        "!!!???",
        "123456",
    ],
)
def test_caps_filter_ignores_non_alpha(text: str):
    ctx = make_fake_message_context(text)
    config = SpamConfig().caps

    result = ExcessiveCapsFilter.check(ctx, config)

    assert result.triggered is False


@pytest.mark.parametrize(
    "sample, whitelist, expected_trigger",
    [
        pytest.param(
            "https://example.com",
            ["example.com"],
            False,
            id="link_whitelisted_exact_domain",
        ),
        pytest.param(
            "https://example.org",
            [".org"],
            False,
            id="link_whitelisted_tld_fragment",
        ),
        pytest.param(
            "https://example.org",
            ["not-example.org"],
            True,
            id="link_not_whitelisted_domain",
        ),
    ],
)
def test_external_link_filter(
    sample: str, whitelist: list[str], expected_trigger: bool
) -> None:
    ctx = make_fake_message_context(sample)
    config = SpamConfig().links
    config.whitelist = whitelist

    result = LinkFilter.check(ctx, config)

    assert result.triggered == expected_trigger


@pytest.mark.parametrize(
    "sample, max_mentions, expected_trigger",
    [
        # count of user mentions equal to threshold -> no trigger
        pytest.param(
            "@user1 @user2",
            2,
            False,
            id="mentions_equal_to_limit",
        ),
        # count of user mentions greater than threshold -> trigger
        pytest.param(
            "@user1 @user2",
            1,
            True,
            id="mentions_above_limit",
        ),
    ],
)
def test_user_mentions_filter(
    sample: str, max_mentions: int, expected_trigger: bool
) -> None:
    ctx = make_fake_message_context(sample)
    config = SpamConfig().user_mentions
    config.max = max_mentions

    result = UserMentionsFilter.check(ctx, config)

    assert result.triggered == expected_trigger


@pytest.mark.parametrize(
    "sample, min_length_low_variety, min_unique_chars, expected_trigger",
    [
        # length >= min_length and unique chars less than required -> trigger
        pytest.param(
            "aaaaa",
            5,
            2,
            True,
            id="gibberish_low_variety_triggered",
        ),
        # unique chars equal to threshold -> no trigger
        pytest.param(
            "aaabb",
            1,
            2,
            False,
            id="gibberish_unique_chars_at_threshold",
        ),
    ],
)
def test_gibberish_low_char_variety(
    sample: str,
    min_length_low_variety: int,
    min_unique_chars: int,
    expected_trigger: bool,
) -> None:
    text = sample
    config = SpamConfig().gibberish
    config.min_length_low_variety = min_length_low_variety
    config.min_unique_chars = min_unique_chars

    triggered = GibberishSpamFilter.has_low_char_variety(text, config)

    assert triggered == expected_trigger


@pytest.mark.parametrize(
    "sample, max_special_chars_repeat_len, expected_trigger",
    [
        # special chars quantity at threshold -> no trigger
        pytest.param(
            "foo!!!",
            3,
            False,
            id="gibberish_special_chars_at_threshold",
        ),
        # special chars quantity greater than threshold -> trigger
        pytest.param(
            "foo!!!",
            2,
            True,
            id="gibberish_special_chars_triggered",
        ),
    ],
)
def test_gibberish_repeating_special_chars(
    sample: str,
    max_special_chars_repeat_len: int,
    expected_trigger: bool,
) -> None:
    text = sample
    config = SpamConfig().gibberish
    config.max_special_chars_repeat_len = max_special_chars_repeat_len

    triggered = GibberishSpamFilter.has_repeating_special_chars(text, config)

    assert triggered == expected_trigger


@pytest.mark.parametrize(
    "sample, max_any_char_repeat_len, expected_trigger",
    [
        # repeating chars quantity at threshold -> no trigger
        pytest.param(
            "whaaataaa",
            3,
            False,
            id="gibberish_any_char_at_threshold",
        ),
        # repeating chars quantity greater than threshold -> trigger
        pytest.param(
            "whaaat",
            2,
            True,
            id="gibberish_any_char_triggered",
        ),
    ],
)
def test_gibberish_repeating_any_char(
    sample: str,
    max_any_char_repeat_len: int,
    expected_trigger: bool,
) -> None:
    text = sample
    config = SpamConfig().gibberish
    config.max_any_char_repeat_len = max_any_char_repeat_len

    triggered = GibberishSpamFilter.has_repeating_any_char(text, config)

    assert triggered == expected_trigger


@pytest.mark.parametrize(
    "sample, min_length_consonant_check, consonant_ratio_threshold, expected_trigger",
    [
        # length >= min_length and ratio exactly at threshold -> no trigger
        pytest.param(
            "abcdfghjkl",
            10,
            0.9,
            False,
            id="gibberish_consonants_ratio_at_threshold",
        ),
        # length >= min_length and ratio above threshold -> trigger
        pytest.param(
            "abcdfghjkl",
            10,
            0.85,
            True,
            id="gibberish_consonants_triggered",
        ),
        # ratio above threshold but length < min_length -> no trigger
        pytest.param(
            "bcdfghjkl",
            10,
            0.5,
            False,
            id="gibberish_consonants_below_min_length",
        ),
    ],
)
def test_gibberish_excessive_consonants(
    sample: str,
    min_length_consonant_check: int,
    consonant_ratio_threshold: float,
    expected_trigger: bool,
) -> None:
    text = sample
    config = SpamConfig().gibberish
    config.min_length_consonant_check = min_length_consonant_check
    config.consonant_ratio_threshold = consonant_ratio_threshold

    triggered = GibberishSpamFilter.has_excessive_consonants(text, config)

    assert triggered == expected_trigger


@pytest.mark.parametrize(
    (
        "sample",
        "phrase_min_words_count",
        "phrase_max_words_count",
        "max_phrase_repeats",
        "expected_trigger",
    ),
    [
        # suitable length and max_repeat_times at threshold -> no trigger
        pytest.param(
            "Some phrase? ...Some phrase! ?!)Some phrase.",
            1,
            5,
            3,
            False,
            id="gibberish_repeating_phrase_at_threshold",
        ),
        # suitable length and max_repeat_times above threshold -> trigger
        pytest.param(
            "aSome phrase Some phrase, Some phrase",
            1,
            5,
            2,
            True,
            id="gibberish_repeating_phrase_triggered",
        ),
    ],
)
def test_gibberish_repeating_phrase(
    sample: str,
    phrase_min_words_count: int,
    phrase_max_words_count: int,
    max_phrase_repeats: int,
    expected_trigger: bool,
) -> None:
    config = SpamConfig().gibberish
    config.phrase_min_words_count = phrase_min_words_count
    config.phrase_max_words_count = phrase_max_words_count
    config.max_phrase_repeats = max_phrase_repeats

    text = sample
    triggered = GibberishSpamFilter.has_repeating_phrase(text, config)

    assert triggered == expected_trigger


@pytest.mark.parametrize(
    "fake_method_name",
    GIBBERISH_METHOD_NAMES,
)
def test_gibberish_check_triggered(
    fake_method_name: str, monkeypatch: pytest.MonkeyPatch
):
    def always_false(text: str, config: GibberishConfig):
        return False

    def fake_method(text: str, config: GibberishConfig):
        return True

    for name in GIBBERISH_METHOD_NAMES:
        monkeypatch.setattr(
            GibberishSpamFilter,
            name,
            staticmethod(always_false),
        )

    monkeypatch.setattr(
        GibberishSpamFilter,
        fake_method_name,
        staticmethod(fake_method),
    )

    ctx = make_fake_message_context("Some text")
    config = SpamConfig().gibberish

    result = GibberishSpamFilter.check(ctx, config)

    assert result.triggered
    assert result.reason == "fake_method"


def test_gibberish_check_not_triggered(monkeypatch: pytest.MonkeyPatch):
    def always_false(text: str, config: GibberishConfig):
        return False

    for name in GIBBERISH_METHOD_NAMES:
        monkeypatch.setattr(
            GibberishSpamFilter,
            name,
            staticmethod(always_false),
        )

    ctx = make_fake_message_context("Some text")
    config = SpamConfig().gibberish

    result = GibberishSpamFilter.check(ctx, config)

    assert not result.triggered
    assert result.reason == ""
