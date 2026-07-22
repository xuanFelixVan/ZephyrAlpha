# [A_test] module_id: MOD-GOV_utils_time_utils | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_time_utils

# [INVARIANTS] now_utc返回UTC;freeze_time上下文管理器恢复;parse_iso严格

# [MODIFY-GUARD] time_utils.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ValueError on invalid ISO string

# [TESTS] pytest tests/test_utils_time_utils.py -q
# [TTL] task_bound

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.shared.utils.time_utils import (
    format_iso,
    freeze_time,
    now_iso,
    now_utc,
    parse_iso,
    seconds_since,
    seconds_until,
)


class TestNowUtc:
    def test_returns_utc_datetime(self):
        result = now_utc()
        assert isinstance(result, datetime)
        assert result.tzinfo == UTC

    def test_returns_recent_time(self):
        before = datetime.now(UTC)
        result = now_utc()
        after = datetime.now(UTC)
        assert before <= result <= after


class TestNowIso:
    def test_returns_string(self):
        result = now_iso()
        assert isinstance(result, str)
        assert result.endswith("Z")

    def test_parseable_by_parse_iso(self):
        result = now_iso()
        parsed = parse_iso(result)
        assert isinstance(parsed, datetime)


class TestFreezeTime:
    def test_freezes_with_string(self):
        with freeze_time("2026-05-05T12:00:00Z"):
            assert now_utc().year == 2026
            assert now_utc().month == 5
            assert now_utc().day == 5

    def test_freezes_with_datetime(self):
        frozen = datetime(2025, 1, 15, 10, 30, 0, tzinfo=UTC)
        with freeze_time(frozen):
            assert now_utc() == frozen

    def test_restores_after_exit(self):
        before = now_utc()
        with freeze_time("2026-01-01T00:00:00Z"):
            pass
        after = now_utc()
        assert after >= before

    def test_nested_freeze(self):
        with freeze_time("2026-01-01T00:00:00Z"):
            assert now_utc().month == 1
            with freeze_time("2026-06-15T12:00:00Z"):
                assert now_utc().month == 6
            assert now_utc().month == 1

    def test_freeze_naive_datetime_gets_utc(self):
        naive = datetime(2026, 3, 1, 0, 0, 0)
        with freeze_time(naive):
            result = now_utc()
            assert result.tzinfo == UTC
            assert result.month == 3


class TestParseIso:
    def test_valid_z_suffix(self):
        result = parse_iso("2026-05-05T12:00:00Z")
        assert result.year == 2026
        assert result.tzinfo == UTC

    def test_valid_with_offset(self):
        result = parse_iso("2026-05-05T12:00:00+00:00")
        assert result.year == 2026

    def test_naive_gets_utc(self):
        result = parse_iso("2026-05-05T12:00:00")
        assert result.tzinfo == UTC

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_iso("not-a-date")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_iso("")


class TestFormatIso:
    def test_utc_datetime(self):
        dt = datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC)
        result = format_iso(dt)
        assert result.startswith("2026-05-05T12:00:00")
        assert result.endswith("Z")

    def test_naive_datetime_gets_utc(self):
        dt = datetime(2026, 5, 5, 12, 0, 0)
        result = format_iso(dt)
        assert result.endswith("Z")

    def test_roundtrip(self):
        original = datetime(2026, 5, 5, 12, 30, 45, 123456, tzinfo=UTC)
        formatted = format_iso(original)
        parsed = parse_iso(formatted)
        assert abs((parsed - original).total_seconds()) < 1


class TestSecondsSince:
    def test_positive(self):
        past = datetime.now(UTC) - timedelta(seconds=10)
        result = seconds_since(past)
        assert result >= 9

    def test_future_negative(self):
        future = datetime.now(UTC) + timedelta(seconds=10)
        result = seconds_since(future)
        assert result < 0


class TestSecondsUntil:
    def test_positive(self):
        future = datetime.now(UTC) + timedelta(seconds=10)
        result = seconds_until(future)
        assert result >= 9

    def test_past_negative(self):
        past = datetime.now(UTC) - timedelta(seconds=10)
        result = seconds_until(past)
        assert result < 0
