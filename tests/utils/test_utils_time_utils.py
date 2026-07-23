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
    now_utc_str,
    parse_iso,
    register_sqlite_datetime_str_adapter,
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


class TestNowUtcStr:
    """now_utc_str() 返回空格分隔 str 时间戳（与 sqlite3 存储格式一致）。"""

    def test_returns_str(self):
        result = now_utc_str()
        assert isinstance(result, str)

    def test_space_separated_not_iso(self):
        # 空格分隔（如 '2026-07-23 17:42:13.539162+00:00'），非 ISO 'T' 分隔
        result = now_utc_str()
        assert " " in result
        # 日期与时间之间是空格而非 T
        date_part = result.split(" ")[0]
        assert "T" not in date_part

    def test_consistent_with_now_utc_via_adapter(self):
        # now_utc() 经 adapter 存入 sqlite3 == now_utc_str() 格式
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE t (ts TEXT)")
        conn.execute("INSERT INTO t VALUES (?)", (now_utc(),))
        stored = conn.execute("SELECT ts FROM t").fetchone()[0]
        conn.close()
        assert isinstance(stored, str)
        assert " " in stored  # 空格分隔


class TestSqliteDatetimeStrAdapter:
    """#SQLITE-DATETIME-ADAPTER: datetime/date→sqlite3 str 适配器（Python 3.12 deprecation 治本）。"""

    def test_datetime_no_deprecation_warning(self):
        """datetime 传给 sqlite3 不触发 DeprecationWarning。"""
        import sqlite3
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE t (ts TEXT)")
            conn.execute("INSERT INTO t VALUES (?)", (datetime.now(UTC),))
            conn.close()
            dep = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert dep == [], f"不应有 DeprecationWarning: {dep}"

    def test_datetime_stored_as_space_separated_str(self):
        """datetime 经 adapter 存储为空格分隔 str（与默认 adapter isoformat(' ') 一致）。"""
        import sqlite3

        dt = datetime(2026, 7, 23, 10, 30, 0, tzinfo=UTC)
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE t (ts TEXT)")
        conn.execute("INSERT INTO t VALUES (?)", (dt,))
        stored = conn.execute("SELECT ts FROM t").fetchone()[0]
        conn.close()
        assert stored == str(dt)
        assert " " in stored  # 空格分隔，非 'T'

    def test_date_no_deprecation_warning(self):
        """date 传给 sqlite3 不触发 DeprecationWarning。"""
        import sqlite3
        import warnings
        from datetime import date

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE t (d TEXT)")
            conn.execute("INSERT INTO t VALUES (?)", (date(2026, 7, 23),))
            conn.close()
            dep = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert dep == [], f"不应有 DeprecationWarning: {dep}"

    def test_register_idempotent(self):
        """重复注册 adapter 安全（幂等）。"""
        # 多次调用不应抛异常
        register_sqlite_datetime_str_adapter()
        register_sqlite_datetime_str_adapter()
        # 验证仍正常工作
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE t (ts TEXT)")
        conn.execute("INSERT INTO t VALUES (?)", (datetime.now(UTC),))
        stored = conn.execute("SELECT ts FROM t").fetchone()[0]
        conn.close()
        assert isinstance(stored, str)
