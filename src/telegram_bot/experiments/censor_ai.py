"""
Experimental toxicity detection using Hugging Face transformers.

This module is not used in production because of resource and latency constraints,
but is kept as a prototype for optional AI-based censorship features.
"""

import logging
from typing import TypedDict

from transformers import TextClassificationPipeline, pipeline
from transformers.utils import logging as hf_logging

from telegram_bot.models.filters import AICensorshipConfig

hf_logging.set_verbosity_error()
logging.getLogger("torch").setLevel(logging.ERROR)


class ToxicRecord(TypedDict):
    label: str
    score: float


ToxicResult = list[ToxicRecord]


def _build_ru_classifier() -> TextClassificationPipeline:
    """Create a Russian toxicity classifier pipeline."""
    return pipeline(
        "text-classification",
        model="cointegrated/rubert-tiny-toxicity",
        device=-1,
    )


def _build_en_classifier() -> TextClassificationPipeline:
    """Create an English toxicity classifier pipeline."""
    return pipeline(
        "text-classification",
        model="unitary/toxic-bert",
        device=-1,
    )


TOXIC_LABELS = {
    "toxic",
    "insult",
    "obscenity",
    "threat",
    "dangerous",
    "severe_toxic",
    "obscene",
    "identity_hate",
}


class ToxicityDetector:
    """Lazy-loading wrapper around language-specific toxicity classifiers.

    This class owns the HF pipelines and exposes a single method to check whether
    a given text is likely toxic according to any of the underlying models.
    """

    def __init__(self) -> None:
        self.classifiers: list[TextClassificationPipeline] = []
        self.initialized = False

    def load_classifiers(self) -> None:
        """Synchronously load all classifiers if not loaded yet."""
        try:
            self.classifiers = [_build_en_classifier(), _build_ru_classifier()]
            self.initialized = True
        except Exception as e:
            logging.exception(f"Failed to load toxicity classifiers: {e}")
            self.classifiers = []
            self.initialized = True

    async def is_toxic(self, text: str, config: AICensorshipConfig) -> bool:
        """Return True if any classifier considers the text toxic."""
        if not self.initialized:
            self.load_classifiers()
        if not self.classifiers:
            return False

        results: list[ToxicResult] = []
        for classifier in self.classifiers:
            result_raw = classifier(text)
            result: ToxicResult = [
                {"label": r["label"], "score": float(r["score"])} for r in result_raw
            ]
            results.append(result)
            logging.debug("Toxicity classifier result: %s", result)

        return any(
            any(
                r["label"] in TOXIC_LABELS and r["score"] > config.threshold
                for r in result
            )
            for result in results
        )


_detector = ToxicityDetector()


async def is_toxic(text: str, config: AICensorshipConfig) -> bool:
    """Compatibility wrapper around ToxicityDetector.is_toxic."""
    return await _detector.is_toxic(text, config)
