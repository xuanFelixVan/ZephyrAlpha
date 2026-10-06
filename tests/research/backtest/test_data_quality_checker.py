# [BLUEPRINT] MOD-BT-022 | docs/03_modules/_domain_backtest/data_quality_checker/blueprint.md | §D-BACKTEST BT-22
# [A_module] module_id=MOD-BT-022 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-BT-022 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_data_quality_checker
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""DataQualityChecker (MOD-BT-022) 测试套件。

覆盖: NaN检测(各字段)、交易日gaps、价格异常、零成交量、异常放量、
       负值、OHLC逻辑违背、前复权连续性、多标的、空DataFrame、输入校验、严重度聚合。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.services.data_quality_checker import (
    DataQualityChecker,
    DataQualityConfig,
    DataQualityReport,
    InvalidDataFormatError,
    QualityIssue,
    Severity,
)

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


def _make_clean_df(n: int = 10, start: str = "2026-01-05") -> pd.DataFrame:
    """生成干净的 OHLCV DataFrame (无质量问题)。"""
    dates = pd.bdate_range(start, periods=n)
    base = 100.0
    close = base * np.cumprod(1 + np.random.uniform(-0.01, 0.01, n))
    return pd.DataFrame(
        {
            "open": close * 0.999,
            "high": close * 1.005,
            "low": close * 0.995,
            "close": close,
            "volume": np.full(n, 1_000_000.0),
        },
        index=dates,
    )


@pytest.fixture
def checker() -> DataQualityChecker:
    return DataQualityChecker()


# ──────────────────────────────────────────────────────────────────────────────
# 输入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_non_dataframe_raises(self, checker: DataQualityChecker):
        with pytest.raises(InvalidDataFormatError, match="must be a pandas DataFrame"):
            checker.check([1, 2, 3])

    def test_missing_columns_raises(self, checker: DataQualityChecker):
        df = pd.DataFrame({"open": [1], "high": [2]})
        with pytest.raises(InvalidDataFormatError, match="missing required columns"):
            checker.check(df)

    def test_empty_dataframe_passes(self, checker: DataQualityChecker):
        df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        report = checker.check(df)
        assert report.passed is True
        assert report.total_bars == 0
        assert report.symbols_checked == 0
        assert len(report.issues) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 缺失检测
# ──────────────────────────────────────────────────────────────────────────────


class TestMissingDetection:
    def test_nan_close_is_error(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[2, df.columns.get_loc("close")] = np.nan
        report = checker.check(df)
        assert report.passed is False
        assert report.error_count >= 1
        nan_issues = report.issues_by_rule("nan_value")
        assert any(i.message == "close is NaN" for i in nan_issues)

    def test_nan_open_is_warn(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[1, df.columns.get_loc("open")] = np.nan
        report = checker.check(df)
        # open NaN = WARN, should not fail
        assert report.passed is True
        assert report.warning_count >= 1
        assert any(i.rule == "nan_value" and i.message == "open is NaN" for i in report.issues)

    def test_nan_volume_is_error(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("volume")] = np.nan
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "nan_value" and i.message == "volume is NaN" for i in report.issues)

    def test_trading_day_gap_detected(self, checker: DataQualityChecker):
        """间隔 > max_gap_days (默认10) 应报 WARN。"""
        dates = pd.to_datetime(["2026-01-05", "2026-01-20"])  # 15天间隔
        df = pd.DataFrame(
            {"open": [10, 11], "high": [11, 12], "low": [9, 10], "close": [10, 11], "volume": [100, 200]},
            index=dates,
        )
        report = checker.check(df)
        gap_issues = report.issues_by_rule("trading_day_gap")
        assert len(gap_issues) >= 1
        assert gap_issues[0].severity is Severity.WARN

    def test_no_gap_for_normal_spacing(self, checker: DataQualityChecker):
        """正常工作日间隔 (3天跨周末) 不应报 gap。"""
        dates = pd.bdate_range("2026-01-05", periods=5)
        df = pd.DataFrame(
            {"open": [10] * 5, "high": [11] * 5, "low": [9] * 5, "close": [10] * 5, "volume": [100] * 5},
            index=dates,
        )
        report = checker.check(df)
        assert len(report.issues_by_rule("trading_day_gap")) == 0


# ──────────────────────────────────────────────────────────────────────────────
# 异常检测
# ──────────────────────────────────────────────────────────────────────────────


class TestAnomalyDetection:
    def test_negative_price_is_error(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("close")] = -1.0
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "negative_value" and i.value == -1.0 for i in report.issues)

    def test_negative_volume_is_error(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("volume")] = -500
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "negative_value" and i.message == "volume is negative" for i in report.issues)

    def test_price_anomaly_detected(self, checker: DataQualityChecker):
        """单日涨跌幅 > 20% 应报 WARN。"""
        df = _make_clean_df(5)
        # 让第二天暴涨 30%
        df.iloc[1, df.columns.get_loc("close")] = df.iloc[0]["close"] * 1.30
        df.iloc[1, df.columns.get_loc("high")] = df.iloc[1]["close"] * 1.01
        report = checker.check(df)
        anomaly_issues = report.issues_by_rule("price_anomaly")
        assert len(anomaly_issues) >= 1
        assert all(i.severity is Severity.WARN for i in anomaly_issues)

    def test_zero_volume_detected(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[2, df.columns.get_loc("volume")] = 0
        report = checker.check(df)
        assert any(i.rule == "zero_volume" for i in report.issues)

    def test_volume_spike_detected(self, checker: DataQualityChecker):
        df = _make_clean_df(10)
        # 第5天放量 15倍
        df.iloc[4, df.columns.get_loc("volume")] = df["volume"].mean() * 15
        report = checker.check(df)
        spike_issues = report.issues_by_rule("volume_spike")
        assert len(spike_issues) >= 1
        assert all(i.severity is Severity.WARN for i in spike_issues)

    def test_ohlc_high_lt_low(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("high")] = 5.0
        df.iloc[0, df.columns.get_loc("low")] = 10.0
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "high_lt_low" for i in report.issues)

    def test_ohlc_high_lt_close(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("high")] = 90.0
        df.iloc[0, df.columns.get_loc("close")] = 100.0
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "high_lt_close" for i in report.issues)

    def test_ohlc_low_gt_open(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("low")] = 105.0
        df.iloc[0, df.columns.get_loc("open")] = 100.0
        report = checker.check(df)
        assert report.passed is False
        assert any(i.rule == "low_gt_open" for i in report.issues)


# ──────────────────────────────────────────────────────────────────────────────
# 一致性检查
# ──────────────────────────────────────────────────────────────────────────────


class TestConsistencyCheck:
    def test_adj_discontinuity_detected(self, checker: DataQualityChecker):
        """前复权跳变 > 30% 应报 WARN。"""
        df = _make_clean_df(5)
        # 让第二天跳变 40%
        df.iloc[1, df.columns.get_loc("close")] = df.iloc[0]["close"] * 0.60
        df.iloc[1, df.columns.get_loc("high")] = df.iloc[1]["close"] * 1.01
        df.iloc[1, df.columns.get_loc("low")] = df.iloc[1]["close"] * 0.99
        df.iloc[1, df.columns.get_loc("open")] = df.iloc[1]["close"] * 0.999
        report = checker.check(df)
        adj_issues = report.issues_by_rule("adj_continuity")
        assert len(adj_issues) >= 1


# ──────────────────────────────────────────────────────────────────────────────
# 多标的
# ──────────────────────────────────────────────────────────────────────────────


class TestMultiSymbol:
    def test_multiindex_multi_symbol(self, checker: DataQualityChecker):
        """MultiIndex [symbol, date] 多标的检查。"""
        dates = pd.bdate_range("2026-01-05", periods=5)
        sym_a = pd.DataFrame(
            {"open": [10] * 5, "high": [11] * 5, "low": [9] * 5, "close": [10] * 5, "volume": [100] * 5},
            index=dates,
        )
        sym_b = pd.DataFrame(
            {"open": [20] * 5, "high": [21] * 5, "low": [19] * 5, "close": [20] * 5, "volume": [200] * 5},
            index=dates,
        )
        # sym_b 引入负值
        sym_b.iloc[0, sym_b.columns.get_loc("close")] = -1.0

        data = pd.concat(
            {"AAA": sym_a, "BBB": sym_b},
            names=["symbol", "date"],
        )
        report = checker.check(data)
        assert report.symbols_checked == 2
        assert report.total_bars == 10
        assert report.passed is False  # BBB 有负值
        assert any(i.rule == "negative_value" and i.symbol == "BBB" for i in report.issues)

    def test_single_symbol_uses_default(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        report = checker.check(df)
        assert report.symbols_checked == 1
        assert all(i.symbol == "_default" for i in report.issues)


# ──────────────────────────────────────────────────────────────────────────────
# 严重度聚合与报告
# ──────────────────────────────────────────────────────────────────────────────


class TestReportAggregation:
    def test_clean_data_passes(self, checker: DataQualityChecker):
        df = _make_clean_df(20)
        report = checker.check(df)
        assert report.passed is True
        assert report.error_count == 0

    def test_error_makes_report_fail(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("close")] = -1.0
        report = checker.check(df)
        assert report.passed is False
        assert report.error_count >= 1

    def test_warn_only_does_not_fail(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[2, df.columns.get_loc("open")] = np.nan  # open NaN = WARN
        report = checker.check(df)
        assert report.passed is True
        assert report.warning_count >= 1

    def test_issues_by_severity(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("close")] = -1.0  # ERROR
        df.iloc[1, df.columns.get_loc("open")] = np.nan  # WARN
        report = checker.check(df)
        errors = report.issues_by_severity(Severity.ERROR)
        warns = report.issues_by_severity(Severity.WARN)
        assert len(errors) >= 1
        assert len(warns) >= 1

    def test_issues_by_rule(self, checker: DataQualityChecker):
        df = _make_clean_df(5)
        df.iloc[0, df.columns.get_loc("close")] = -1.0
        df.iloc[1, df.columns.get_loc("high")] = -1.0
        report = checker.check(df)
        neg_issues = report.issues_by_rule("negative_value")
        assert len(neg_issues) >= 2


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_custom_anomaly_threshold(self):
        cfg = DataQualityConfig(price_anomaly_threshold=0.05)
        checker = DataQualityChecker(cfg)
        df = _make_clean_df(5)
        # 6% 涨幅 — 默认阈值 20% 不报, 自定义 5% 报
        df.iloc[1, df.columns.get_loc("close")] = df.iloc[0]["close"] * 1.06
        df.iloc[1, df.columns.get_loc("high")] = df.iloc[1]["close"] * 1.01
        report = checker.check(df)
        assert any(i.rule == "price_anomaly" for i in report.issues)

    def test_invalid_threshold_raises(self):
        with pytest.raises(InvalidDataFormatError):
            DataQualityConfig(price_anomaly_threshold=1.5)

    def test_invalid_multiplier_raises(self):
        with pytest.raises(InvalidDataFormatError):
            DataQualityConfig(volume_spike_multiplier=-1)

    def test_does_not_modify_input(self, checker: DataQualityChecker):
        df = _make_clean_df(10)
        df_copy = df.copy()
        checker.check(df)
        pd.testing.assert_frame_equal(df, df_copy)
