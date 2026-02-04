from unittest.mock import Mock

import pytest

from telegram_bot.experiments.censor_ai import ToxicityDetector
from telegram_bot.models.filters import AICensorshipConfig

from .data.offensive_samples import norm_samples, toxic_samples


def test_toxicity_detector_init():
    detector = ToxicityDetector()

    assert not detector.classifiers
    assert not detector.initialized


@pytest.mark.slow
def test_toxicity_detector_real_models():
    detector = ToxicityDetector()

    # Should not throw any exceptions
    detector.load_classifiers()

    assert detector.classifiers
    assert detector.initialized


def test_toxicity_detector_load_classifiers_happy_path(monkeypatch: pytest.MonkeyPatch):
    detector = ToxicityDetector()

    fake_classifier_ru = Mock(name="ru_classifier")
    fake_classifier_en = Mock(name="en_classifier")

    monkeypatch.setattr(
        "telegram_bot.experiments.censor_ai._build_ru_classifier",
        Mock(return_value=fake_classifier_ru),
    )
    monkeypatch.setattr(
        "telegram_bot.experiments.censor_ai._build_en_classifier",
        Mock(return_value=fake_classifier_en),
    )

    # Should not throw any exceptions and should use fake classifiers
    detector.load_classifiers()

    assert detector.initialized
    assert detector.classifiers == [
        fake_classifier_en,
        fake_classifier_ru,
    ]


def test_toxicity_detector_load_classifiers_exception(monkeypatch: pytest.MonkeyPatch):
    detector = ToxicityDetector()

    fake_classifier_en = Mock(name="en_classifier")
    monkeypatch.setattr(
        "telegram_bot.experiments.censor_ai._build_en_classifier",
        Mock(return_value=fake_classifier_en),
    )
    monkeypatch.setattr(
        "telegram_bot.experiments.censor_ai._build_ru_classifier",
        Mock(side_effect=Exception("exception_message")),
    )

    # Exception must be handled inside load_classifiers
    detector.load_classifiers()

    assert not detector.classifiers
    assert detector.initialized


@pytest.mark.slow
@pytest.mark.asyncio
@pytest.mark.parametrize("sample", toxic_samples)
async def test_toxicity_detector_toxic_samples(sample: str):
    detector = ToxicityDetector()
    config = AICensorshipConfig(enabled=True)

    assert await detector.is_toxic(sample, config)


@pytest.mark.slow
@pytest.mark.asyncio
@pytest.mark.parametrize("sample", norm_samples)
async def test_toxicity_detector_norm_samples(sample: str):
    detector = ToxicityDetector()
    config = AICensorshipConfig(enabled=True)

    assert not await detector.is_toxic(sample, config)
