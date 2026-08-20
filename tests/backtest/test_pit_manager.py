# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_pit_manager
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_pit_manager.py
# [TTL] task_bound
"""PITManager 单元测试(52号 §7 新发现1 测试债清偿).

覆盖: AS OF JOIN(泄漏防护/版本对齐/缺列报错)、Embargo 隔离(边界/排序)、
pit_consistency_test(一致/超阈值违规/无共同样本)、check_survivorship_bias
(含退市/遗漏退市/覆盖率)、配置 frozen。
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from zephyr.backtest.core.pit_manager import (
    PITConfig,
    PITError,
    PITManager,
)


def _df(dates: list[str], values: list[float], **extra) -> pd.DataFrame:
    data = {"date": pd.to_datetime(dates), "value": values}
    data.update(extra)
    return pd.DataFrame(data)


# ============== AS OF JOIN ==============


class TestAsOfJoin:
    def test_leakage_guard(self):
        mgr = PITManager()
        df = _df(["2024-01-01", "2024-06-01", "2024-12-31"], [1.0, 2.0, 3.0])
        visible = mgr.as_of_join(df, pd.Timestamp("2024-06-01"))
        # query_time(含)之前可见, 未来数据被屏蔽
        assert len(visible) == 2
        assert visible["value"].tolist() == [1.0, 2.0]

    def test_empty_data_raises(self):
        mgr = PITManager()
        with pytest.raises(PITError):
            mgr.as_of_join(pd.DataFrame(), pd.Timestamp("2024-01-01"))

    def test_missing_event_col_raises(self):
        mgr = PITManager()
        df = pd.DataFrame({"other": [1]})
        with pytest.raises(PITError):
            mgr.as_of_join(df, pd.Timestamp("2024-01-01"))

    def test_missing_available_col_raises(self):
        mgr = PITManager()
        df = _df(["2024-01-01"], [1.0])
        with pytest.raises(PITError):
            mgr.as_of_join(df, pd.Timestamp("2024-01-01"), available_time_col="avail")

    def test_version_alignment_latest_available(self):
        mgr = PITManager()
        # 同一(event_time, symbol)两个版本: v1发布于1/2, v2(修正)发布于1/5
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-01-01"]),
            "symbol": ["A", "A"],
            "avail": pd.to_datetime(["2024-01-02", "2024-01-05"]),
            "value": [1.0, 1.5],
        })
        # 1/3 查询: 仅v1可见
        v1 = mgr.as_of_join(df, pd.Timestamp("2024-01-03"), available_time_col="avail")
        assert v1["value"].tolist() == [1.0]
        # 1/6 查询: 版本对齐取最新可用v2
        v2 = mgr.as_of_join(df, pd.Timestamp("2024-01-06"), available_time_col="avail")
        assert v2["value"].tolist() == [1.5]

    def test_event_time_beyond_query_excluded(self):
        mgr = PITManager()
        # 已发布(avail<=T)但事件时间在未来(event>T)的数据仍须屏蔽
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-06-01"]),
            "avail": pd.to_datetime(["2024-01-01"]),
            "value": [9.9],
        })
        visible = mgr.as_of_join(
            df, pd.Timestamp("2024-03-01"), available_time_col="avail"
        )
        assert len(visible) == 0

    def test_sorted_by_event_time(self):
        mgr = PITManager()
        df = _df(["2024-03-01", "2024-01-01", "2024-02-01"], [3.0, 1.0, 2.0])
        visible = mgr.as_of_join(df, pd.Timestamp("2024-04-01"))
        assert visible["value"].tolist() == [1.0, 2.0, 3.0]

    def test_string_dates_compatible(self):
        mgr = PITManager()
        df = pd.DataFrame({"date": ["2024-01-01", "2024-02-01"], "value": [1.0, 2.0]})
        visible = mgr.as_of_join(df, pd.Timestamp("2024-01-15"))
        assert visible["value"].tolist() == [1.0]


# ============== Embargo ==============


class TestEmbargo:
    def test_embargo_excludes_recent(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        df = _df(
            ["2024-01-01", "2024-01-08", "2024-01-09", "2024-01-10"],
            [1.0, 2.0, 3.0, 4.0],
        )
        safe = mgr.apply_embargo(df, pd.Timestamp("2024-01-10"))
        # cutoff = 2024-01-10 - 5 BDay = 2024-01-03 → 仅 1/1 保留
        assert safe["value"].tolist() == [1.0]

    def test_old_data_all_pass(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        df = _df(["2023-01-02", "2023-02-01"], [1.0, 2.0])
        safe = mgr.apply_embargo(df, pd.Timestamp("2024-01-10"))
        assert len(safe) == 2

    def test_empty_data_raises(self):
        mgr = PITManager()
        with pytest.raises(PITError):
            mgr.apply_embargo(pd.DataFrame(), pd.Timestamp("2024-01-01"))

    def test_missing_col_raises(self):
        mgr = PITManager()
        with pytest.raises(PITError):
            mgr.apply_embargo(pd.DataFrame({"x": [1]}), pd.Timestamp("2024-01-01"))

    def test_output_sorted(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        df = _df(["2023-02-01", "2023-01-02"], [2.0, 1.0])
        safe = mgr.apply_embargo(df, pd.Timestamp("2024-01-10"))
        assert safe["value"].tolist() == [1.0, 2.0]


# ============== 一致性校验 ==============


class TestConsistency:
    def test_consistent(self):
        mgr = PITManager()
        idx = pd.date_range("2024-01-01", periods=3)
        train = pd.DataFrame({"f": [1.0, 2.0, 3.0]}, index=idx)
        bt = pd.DataFrame({"f": [1.0, 2.0, 3.0]}, index=idx)
        r = mgr.pit_consistency_test(train, bt, "f")
        assert r["consistent"] is True
        assert r["max_deviation"] == 0.0
        assert r["violations"] == []

    def test_violation_detected(self):
        mgr = PITManager(PITConfig(consistency_threshold=0.01))
        idx = pd.date_range("2024-01-01", periods=2)
        train = pd.DataFrame({"f": [1.0, 1.0]}, index=idx)
        bt = pd.DataFrame({"f": [1.0, 1.05]}, index=idx)  # 5% > 1%
        r = mgr.pit_consistency_test(train, bt, "f")
        assert r["consistent"] is False
        assert len(r["violations"]) == 1
        assert r["violations"][0]["deviation"] == pytest.approx(0.05, abs=1e-9)

    def test_no_common_index_consistent(self):
        mgr = PITManager()
        train = pd.DataFrame({"f": [1.0]}, index=pd.date_range("2024-01-01", periods=1))
        bt = pd.DataFrame({"f": [9.9]}, index=pd.date_range("2025-01-01", periods=1))
        r = mgr.pit_consistency_test(train, bt, "f")
        assert r["consistent"] is True
        assert r["max_deviation"] == 0.0

    def test_nan_dropped(self):
        mgr = PITManager()
        idx = pd.date_range("2024-01-01", periods=2)
        train = pd.DataFrame({"f": [1.0, float("nan")]}, index=idx)
        bt = pd.DataFrame({"f": [1.0, 9.9]}, index=idx)
        r = mgr.pit_consistency_test(train, bt, "f")
        assert r["consistent"] is True  # NaN样本剔除后仅1点且一致

    def test_empty_raises(self):
        mgr = PITManager()
        with pytest.raises(PITError):
            mgr.pit_consistency_test(pd.DataFrame(), pd.DataFrame({"f": [1]}), "f")
        with pytest.raises(PITError):
            mgr.pit_consistency_test(pd.DataFrame({"f": [1]}), pd.DataFrame(), "f")

    def test_missing_factor_col_raises(self):
        mgr = PITManager()
        with pytest.raises(PITError):
            mgr.pit_consistency_test(
                pd.DataFrame({"g": [1]}), pd.DataFrame({"f": [1]}), "f"
            )

    def test_zero_train_value_epsilon_guard(self):
        mgr = PITManager(PITConfig(consistency_threshold=0.01))
        idx = pd.date_range("2024-01-01", periods=1)
        train = pd.DataFrame({"f": [0.0]}, index=idx)
        bt = pd.DataFrame({"f": [0.0]}, index=idx)
        r = mgr.pit_consistency_test(train, bt, "f")
        assert r["consistent"] is True  # 分母epsilon保护不除零


# ============== 幸存者偏差检测 ==============


class TestSurvivorshipBias:
    def test_contains_delisted(self):
        mgr = PITManager()
        r = mgr.check_survivorship_bias(
            backtest_symbols=["A", "B", "D"],
            all_symbols=["A", "B", "C", "D"],
            delisted_symbols=["D"],
        )
        assert r["has_delisted"] is True
        assert r["delisted_count"] == 1
        assert r["missing_delisted"] == []

    def test_missing_delisted_flagged(self):
        mgr = PITManager()
        r = mgr.check_survivorship_bias(
            backtest_symbols=["A", "B"],
            all_symbols=["A", "B", "D"],
            delisted_symbols=["D"],
        )
        assert r["has_delisted"] is False
        assert r["missing_delisted"] == ["D"]
        assert r["coverage_ratio"] == pytest.approx(2 / 3)

    def test_empty_inputs(self):
        mgr = PITManager()
        r = mgr.check_survivorship_bias([], [], [])
        assert r["has_delisted"] is False
        assert r["coverage_ratio"] == 0.0


# ============== 配置 ==============


class TestPITConfig:
    def test_defaults(self):
        cfg = PITConfig()
        assert cfg.embargo_days == 5
        assert cfg.consistency_threshold == pytest.approx(0.01)

    def test_frozen(self):
        cfg = PITConfig()
        with pytest.raises(FrozenInstanceError):
            cfg.embargo_days = 10  # type: ignore[misc]


# ============== Embargo 真交易日历（15 号 §7③：BDay 近似→真日历，日历数据注入式）==============

# 2024 国庆前后真交易日历（10-01~10-07 休市；09-28/29 为周末）
_TRADING_DAYS = [
    "2024-09-23", "2024-09-24", "2024-09-25", "2024-09-26", "2024-09-27",
    "2024-09-30",
    "2024-10-08", "2024-10-09", "2024-10-10", "2024-10-11",
]


def _daily_labels(start: str, end: str) -> pd.DataFrame:
    """按自然日连续的标签数据（含周末/节假日，便于区分 BDay 与真日历口径）。"""
    return pd.DataFrame({"date": pd.date_range(start, end, freq="D"), "value": 1.0})


class TestApplyEmbargoTradingCalendar:
    """apply_embargo 注入 trading_calendar 后按真交易日回数（节假日不计）。"""

    def test_default_bday_behavior_unchanged(self):
        """无日历注入时 BDay 近似行为锁定（向后兼容）。"""
        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-09-20", "2024-10-09")
        safe = mgr.apply_embargo(data, pd.Timestamp("2024-10-09"))
        # BDay(5)：10-09 回数 5 个工作日 = 10-02 → 保留 <= 10-02
        assert safe["date"].max() == pd.Timestamp("2024-10-02")

    def test_holiday_not_counted_with_calendar(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-09-20", "2024-10-09")
        safe = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"), trading_calendar=_TRADING_DAYS
        )
        # 真日历：10-09 回数 5 个交易日（10-08/09-30/09-27/09-26/09-25）→ 保留 <= 09-25
        assert safe["date"].max() == pd.Timestamp("2024-09-25")

    def test_calendar_stricter_than_bday_across_holiday(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-09-20", "2024-10-09")
        safe_cal = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"), trading_calendar=_TRADING_DAYS
        )
        safe_bday = mgr.apply_embargo(data, pd.Timestamp("2024-10-09"))
        # 09-30（国庆前最后交易日）：BDay 放行、真日历拦截
        assert pd.Timestamp("2024-09-30") in set(safe_bday["date"])
        assert pd.Timestamp("2024-09-30") not in set(safe_cal["date"])

    def test_current_on_non_trading_day_anchors_last_session(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-09-20", "2024-10-12")
        # 10-12 周六 → 锚定 10-11（周五），回数 5 个交易日 = 09-27
        safe = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-12"), trading_calendar=_TRADING_DAYS
        )
        assert safe["date"].max() == pd.Timestamp("2024-09-27")

    def test_short_calendar_conservative_cutoff(self):
        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-10-01", "2024-10-09")
        # 日历仅 2 个交易日，回数越界 → cutoff=首交易日前一日（10-07），近端全拦
        safe = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"),
            trading_calendar=["2024-10-08", "2024-10-09"],
        )
        assert safe["date"].max() == pd.Timestamp("2024-10-07")
        assert pd.Timestamp("2024-10-08") not in set(safe["date"])

    def test_calendar_input_forms_equivalent(self):
        import datetime as dt

        mgr = PITManager(PITConfig(embargo_days=5))
        data = _daily_labels("2024-09-20", "2024-10-09")
        by_str = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"), trading_calendar=_TRADING_DAYS
        )
        by_idx = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"),
            trading_calendar=pd.DatetimeIndex(_TRADING_DAYS),
        )
        by_date = mgr.apply_embargo(
            data, pd.Timestamp("2024-10-09"),
            trading_calendar=[dt.date.fromisoformat(d) for d in _TRADING_DAYS],
        )
        assert by_str["date"].equals(by_idx["date"])
        assert by_str["date"].equals(by_date["date"])

    def test_current_before_calendar_start_blocks_all(self):
        mgr = PITManager(PITConfig(embargo_days=1))
        data = _daily_labels("2024-09-20", "2024-09-25")
        # current_time 早于日历首日 → 无法锚定 → 保守全拦
        safe = mgr.apply_embargo(
            data, pd.Timestamp("2024-09-01"), trading_calendar=_TRADING_DAYS
        )
        assert safe.empty
