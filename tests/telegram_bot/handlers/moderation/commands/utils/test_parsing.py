import pytest

from telegram_bot.handlers.moderation.commands.utils.parsing import parse_duration


@pytest.mark.parametrize("sample", ["five minutes", "30sm", "m3h", "-15m"])
def test_invalid_input(sample: str):
    result = parse_duration(sample)
    assert result == 0


@pytest.mark.parametrize(
    "sample, expected_result",
    [["30s", 30], ["20m", 1200], ["2h", 7200], ["1d", 86400]],
)
def test_valid_input(sample: str, expected_result: int):
    result = parse_duration(sample)
    assert result == expected_result
