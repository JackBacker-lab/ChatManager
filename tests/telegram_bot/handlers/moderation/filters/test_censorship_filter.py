import pytest

from telegram_bot.handlers.moderation.filters import CensorshipFilter
from telegram_bot.models.filters import CensorshipConfig

from .data.offensive_samples import bad_samples, norm_samples
from .fake_message_context import make_fake_message_context


@pytest.mark.parametrize(
    ("bad_word", "sample"),
    [
        (bad_word, sample)
        for bad_word, samples in bad_samples.items()
        for sample in samples
    ],
)
def test_bad_samples_triggered(bad_word: str, sample: str) -> None:
    ctx = make_fake_message_context(sample)
    config = CensorshipConfig()
    result = CensorshipFilter.check(ctx, [bad_word], config)
    assert result.triggered


@pytest.mark.parametrize(
    ("norm_word", "sample"),
    [
        (norm_word, sample)
        for norm_word, samples in norm_samples.items()
        for sample in samples
    ],
)
def test_norm_samples_not_triggered(norm_word: str, sample: str) -> None:
    ctx = make_fake_message_context(sample)
    config = CensorshipConfig()
    result = CensorshipFilter.check(ctx, [norm_word], config)
    assert not result.triggered
