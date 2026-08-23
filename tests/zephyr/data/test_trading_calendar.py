# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [A_module] module_id=MOD-GOV-trading_calendar_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-GOV-trading_calendar_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.zephyr.data.test_trading_calendar
# [DOMAIN] D_DATA
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/zephyr/data/test_trading_calendar.py
# [TTL] task_bound
"""trading_calendar 单元测试（15号 §7③ Embargo 真日历切换承载件）。

覆盖：is_trading_day（XSHG 主路径/weekday 回退/异常回退）、
trading_days_in_range（sessions_in_range 主路径/AttributeError 逐日回退/
通用异常回退/weekday 兜底/空区间/去重排序）、
与 PITManager.apply_embargo 的真日历注入链路（节假日不计口径）。

exchange_calendars 全 mock（fake 日历对象），不依赖 pip 包与网络/DB。
"""

from __future__ import annotations

import datetime

import pandas as pd
import pytest

from zephyr.backtest.core.pit_manager import PITConfig, PITManager
from zephyr.data import trading_calendar as tc


class _FakeXshgCalendar:
    """2024 国庆口径 fake XSHG 日历：10-01~10-07 休市，周末休市，其余工作日开市。"""

    _HOLIDAY = {datetime.date(2024, 10, d) for d in range(1, 8)}

    def is_session(self, iso: str) -> bool:
        d = datetime.date.fromisoformat(iso)
        return d.weekday() < 5 and d not in self._HOLIDAY

    def sessions_in_range(self, start_iso: str, end_iso: str) -> list[pd.Timestamp]:
        start = datetime.date.fromisoformat(start_iso)
        end = datetime.date.fromisoformat(end_iso)
        out: list[pd.Timestamp] = []
        cur = start
        while cur <= end:
            if self.is_session(cur.isoformat()):
                out.append(pd.Timestamp(cur))
            cur += datetime.timedelta(days=1)
        return out


@pytest.fixture(autouse=True)
def _reset_calendar_singleton(monkeypatch):
    """每个测试隔离日历单例（防 _xshg_calendar 全局缓存串扰）。"""
    monkeypatch.setattr(tc, "_xshg_calendar", None)
    monkeypatch.setattr(tc, "_xshg_load_failed", False)


def _use_fake(monkeypatch, cal) -> None:
    monkeypatch.setattr(tc, "_get_xshg_calendar", lambda: cal)


def _use_no_calendar(monkeypatch) -> None:
    monkeypatch.setattr(tc, "_get_xshg_calendar", lambda: None)


# ============== is_trading_day ==============


class TestIsTradingDay:
    def test_xshg_primary(self, monkeypatch):
        _use_fake(monkeypatch, _FakeXshgCalendar())
        assert tc.is_trading_day(datetime.date(2024, 9, 30)) is True  # 周一开市
        assert tc.is_trading_day(datetime.date(2024, 10, 1)) is False  # 国庆休市
        assert tc.is_trading_day(datetime.date(2024, 9, 28)) is False  # 周六

    def test_fallback_weekday_when_no_calendar(self, monkeypatch):
        _use_no_calendar(monkeypatch)
        assert tc.is_trading_day(datetime.date(2024, 10, 1)) is True  # 周二（近似：不识节假日）
        assert tc.is_trading_day(datetime.date(2024, 10, 5)) is False  # 周六

    def test_is_session_exception_falls_back(self, monkeypatch):
        class _Broken:
            def is_session(self, iso: str) -> bool:
                raise RuntimeError("boom")

        _use_fake(monkeypatch, _Broken())
        # 异常 → weekday 回退（永不抛异常契约）
        assert tc.is_trading_day(datetime.date(2024, 9, 30)) is True
        assert tc.is_trading_day(datetime.date(2024, 9, 29)) is False


# ============== trading_days_in_range ==============


class TestTradingDaysInRange:
    def test_sessions_in_range_primary(self, monkeypatch):
        _use_fake(monkeypatch, _FakeXshgCalendar())
        days = tc.trading_days_in_range(datetime.date(2024, 9, 27), datetime.date(2024, 10, 11))
        # 9-27(五)/9-30(一)开市；10-01~07 国庆+周末休；10-08~11 开市
        assert days == [
            datetime.date(2024, 9, 27),
            datetime.date(2024, 9, 30),
            datetime.date(2024, 10, 8),
            datetime.date(2024, 10, 9),
            datetime.date(2024, 10, 10),
            datetime.date(2024, 10, 11),
        ]
        assert all(isinstance(d, datetime.date) for d in days)

    def test_sessions_dedup_sorted(self, monkeypatch):
        class _Dup(_FakeXshgCalendar):
            def sessions_in_range(self, start_iso, end_iso):
                return [pd.Timestamp("2024-09-30"), pd.Timestamp("2024-09-27"), pd.Timestamp("2024-09-30")]

        _use_fake(monkeypatch, _Dup())
        days = tc.trading_days_in_range(datetime.date(2024, 9, 27), datetime.date(2024, 9, 30))
        assert days == [datetime.date(2024, 9, 27), datetime.date(2024, 9, 30)]

    def test_attribute_error_falls_back_to_daily_is_session(self, monkeypatch):
        class _Legacy:
            """无 sessions_in_range 属性 → AttributeError 回退逐日 is_session。"""

            _fake = _FakeXshgCalendar()

            def is_session(self, iso: str) -> bool:
                return self._fake.is_session(iso)

        _use_fake(monkeypatch, _Legacy())
        days = tc.trading_days_in_range(datetime.date(2024, 9, 30), datetime.date(2024, 10, 9))
        assert days == [datetime.date(2024, 9, 30), datetime.date(2024, 10, 8), datetime.date(2024, 10, 9)]

    def test_generic_error_falls_back_to_daily_is_session(self, monkeypatch):
        class _Flaky(_FakeXshgCalendar):
            def sessions_in_range(self, start_iso, end_iso):
                raise RuntimeError("xcal quirk")

        _use_fake(monkeypatch, _Flaky())
        days = tc.trading_days_in_range(datetime.date(2024, 9, 30), datetime.date(2024, 10, 9))
        assert days == [datetime.date(2024, 9, 30), datetime.date(2024, 10, 8), datetime.date(2024, 10, 9)]

    def test_no_calendar_weekday_fallback(self, monkeypatch):
        _use_no_calendar(monkeypatch)
        days = tc.trading_days_in_range(datetime.date(2024, 10, 4), datetime.date(2024, 10, 8))
        # 兜底不识节假日：10-04(五)/10-07(一)/10-08(二)
        assert days == [datetime.date(2024, 10, 4), datetime.date(2024, 10, 7), datetime.date(2024, 10, 8)]

    def test_empty_range(self, monkeypatch):
        _use_fake(monkeypatch, _FakeXshgCalendar())
        assert tc.trading_days_in_range(datetime.date(2024, 10, 8), datetime.date(2024, 10, 1)) == []


# ============== 与 apply_embargo 真日历注入链路（15号 §7③）==============


class TestEmbargoChainWithRealSource:
    def test_trading_days_feed_apply_embargo(self, monkeypatch):
        """trading_days_in_range 产出直接注入 apply_embargo——国庆长假不计入隔离回数。"""
        _use_fake(monkeypatch, _FakeXshgCalendar())
        cal = tc.trading_days_in_range(datetime.date(2024, 9, 20), datetime.date(2024, 10, 9))
        mgr = PITManager(PITConfig(embargo_days=5))
        data = pd.DataFrame({"date": pd.date_range("2024-09-20", "2024-10-09", freq="D"), "value": 1.0})
        safe = mgr.apply_embargo(data, pd.Timestamp("2024-10-09"), trading_calendar=cal)
        # 真日历回数 5 个交易日（10-08/09-30/09-27/09-26/09-25）→ 保留 <= 09-25
        assert safe["date"].max() == pd.Timestamp("2024-09-25")
