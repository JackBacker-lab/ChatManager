from pytest_mock import MockerFixture

from telegram_bot.handlers.moderation.filters import FloodFilter
from telegram_bot.models.filters import FloodConfig

from .fake_message_context import make_fake_message_context


def test_flood_filter_init():
    flood_filter = FloodFilter()
    assert not flood_filter.user_messages


def test_flood_filter_triggers_on_message_limit(mocker: MockerFixture):
    ctx = make_fake_message_context("")
    config = FloodConfig(message_limit=3, time_window=10)

    flood_filter = FloodFilter()

    fake_time = 1_000_000.0
    mocker.patch("time.time", return_value=fake_time)

    # First messages → no trigger
    assert not flood_filter.check(ctx, config).triggered
    assert not flood_filter.check(ctx, config).triggered

    # Third message → trigger
    result = flood_filter.check(ctx, config)
    assert result.triggered

    # State should be cleared
    assert flood_filter.user_messages[(ctx.chat_id, ctx.user_id)] == []


def test_flood_filter_respects_time_window(mocker: MockerFixture):
    ctx = make_fake_message_context("")
    config = FloodConfig(message_limit=3, time_window=10)

    flood_filter = FloodFilter()

    times = iter([1, 2, 11])  # third message outside window
    mocker.patch("time.time", side_effect=lambda: next(times))

    assert not flood_filter.check(ctx, config).triggered
    assert not flood_filter.check(ctx, config).triggered
    assert not flood_filter.check(ctx, config).triggered


def test_flood_filter_edge_case_triggers(mocker: MockerFixture):
    ctx = make_fake_message_context("")
    config = FloodConfig(message_limit=3, time_window=10)

    flood_filter = FloodFilter()

    times = iter([1, 2, 10])  # third message on the threshold of the window
    mocker.patch("time.time", side_effect=lambda: next(times))

    assert not flood_filter.check(ctx, config).triggered
    assert not flood_filter.check(ctx, config).triggered
    assert flood_filter.check(ctx, config).triggered
