# [BLUEPRINT] MOD-RPT-034 | docs/03_modules/_domain_reporting/trading_review_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RPT-034 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.reporting.test_trading_review_engine
# [TESTS] src/zephyr/reporting/trading_review_engine.py
"""MOD-RPT-034 单元测试：trading_review_engine A股交易审查引擎。

蓝图验收（B14-04662/CAND-RPT-009，A9 D-REPORTING-15）：
日终撤单率/申报速率/自成交/拉抬打压四模式扫描（阈值表注入）→
审查报告（异常标的+证据+处置建议三要素）+ 联动检测数据注入 +
报告版本化。检测数据/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.reporting.trading_review_engine",
    reason="trading_review_engine not importable",
)

from zephyr.reporting.trading_review_engine import (  # noqa: E402
    PatternMetric,
    ReviewPattern,
    TradingReviewEngine,
    TradingReviewError,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 30, 0)
_D0 = datetime.date(2026, 8, 25)

_THRESHOLDS = {
    ReviewPattern.CANCEL_RATE: 0.30,
    ReviewPattern.ORDER_RATE: 300.0,
    ReviewPattern.SELF_TRADE: 0.0,
    ReviewPattern.PUMP_DUMP: 0.05,
}


def _engine(metrics: list | None = None) -> TradingReviewEngine:
    return TradingReviewEngine(
        thresholds=_THRESHOLDS,
        detector_metrics=(lambda d: list(metrics)) if metrics is not None else None,
        clock=lambda: _T0,
    )


def _metric(
    pattern: ReviewPattern = ReviewPattern.CANCEL_RATE,
    symbol: str = "600000.SH",
    value: float = 0.5,
) -> PatternMetric:
    return PatternMetric(
        symbol=symbol,
        pattern=pattern,
        value=value,
        evidence={"window": "eod", "pattern": getattr(pattern, "value", pattern)},
    )


# ──────────────────────────────────────────────────────────────────────────────
# 初始化（阈值表注入校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_thresholds_raises(self) -> None:
        with pytest.raises(TradingReviewError):
            TradingReviewEngine(thresholds={})

    def test_missing_pattern_raises(self) -> None:
        partial = dict(_THRESHOLDS)
        del partial[ReviewPattern.PUMP_DUMP]
        with pytest.raises(TradingReviewError):
            TradingReviewEngine(thresholds=partial)

    def test_negative_threshold_raises(self) -> None:
        bad = dict(_THRESHOLDS)
        bad[ReviewPattern.CANCEL_RATE] = -0.1
        with pytest.raises(TradingReviewError):
            TradingReviewEngine(thresholds=bad)

    def test_non_finite_threshold_raises(self) -> None:
        bad = dict(_THRESHOLDS)
        bad[ReviewPattern.ORDER_RATE] = float("inf")
        with pytest.raises(TradingReviewError):
            TradingReviewEngine(thresholds=bad)


# ──────────────────────────────────────────────────────────────────────────────
# 日终四模式扫描
# ──────────────────────────────────────────────────────────────────────────────


class TestDailyReview:
    def test_clean_day_no_findings(self) -> None:
        engine = _engine(
            [
                _metric(ReviewPattern.CANCEL_RATE, value=0.10),
                _metric(ReviewPattern.ORDER_RATE, value=100.0),
            ]
        )
        report = engine.run_daily_review(_D0)
        assert report.findings == ()
        assert report.version == 1
        assert report.report_date == _D0

    def test_cancel_rate_anomaly(self) -> None:
        engine = _engine([_metric(ReviewPattern.CANCEL_RATE, value=0.45)])
        report = engine.run_daily_review(_D0)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.pattern is ReviewPattern.CANCEL_RATE
        assert finding.symbol == "600000.SH"
        assert finding.value == 0.45
        assert finding.threshold == 0.30
        assert "撤单率" in finding.suggestion

    def test_order_rate_anomaly(self) -> None:
        engine = _engine([_metric(ReviewPattern.ORDER_RATE, value=500.0)])
        report = engine.run_daily_review(_D0)
        assert report.findings[0].pattern is ReviewPattern.ORDER_RATE
        assert "申报速率" in report.findings[0].suggestion

    def test_self_trade_anomaly(self) -> None:
        engine = _engine([_metric(ReviewPattern.SELF_TRADE, value=2.0)])
        report = engine.run_daily_review(_D0)
        assert report.findings[0].pattern is ReviewPattern.SELF_TRADE
        assert "自成交" in report.findings[0].suggestion

    def test_pump_dump_anomaly(self) -> None:
        engine = _engine([_metric(ReviewPattern.PUMP_DUMP, value=0.09)])
        report = engine.run_daily_review(_D0)
        assert report.findings[0].pattern is ReviewPattern.PUMP_DUMP
        assert "拉抬打压" in report.findings[0].suggestion

    def test_all_four_patterns_sorted_by_pattern_rank(self) -> None:
        engine = _engine(
            [
                _metric(ReviewPattern.PUMP_DUMP, value=0.09),
                _metric(ReviewPattern.SELF_TRADE, value=3.0),
                _metric(ReviewPattern.ORDER_RATE, value=800.0),
                _metric(ReviewPattern.CANCEL_RATE, value=0.60),
            ]
        )
        report = engine.run_daily_review(_D0)
        assert [f.pattern for f in report.findings] == [
            ReviewPattern.CANCEL_RATE,
            ReviewPattern.ORDER_RATE,
            ReviewPattern.SELF_TRADE,
            ReviewPattern.PUMP_DUMP,
        ]

    def test_threshold_boundary_equal_not_flagged(self) -> None:
        engine = _engine([_metric(ReviewPattern.CANCEL_RATE, value=0.30)])
        report = engine.run_daily_review(_D0)
        assert report.findings == ()

    def test_findings_sorted_by_symbol_within_pattern(self) -> None:
        engine = _engine(
            [
                _metric(ReviewPattern.CANCEL_RATE, symbol="600519.SH", value=0.50),
                _metric(ReviewPattern.CANCEL_RATE, symbol="000001.SZ", value=0.55),
            ]
        )
        report = engine.run_daily_review(_D0)
        assert [f.symbol for f in report.findings] == ["000001.SZ", "600519.SH"]

    def test_evidence_carried_into_finding(self) -> None:
        engine = _engine([_metric(ReviewPattern.CANCEL_RATE, value=0.45)])
        report = engine.run_daily_review(_D0)
        assert report.findings[0].evidence == {"window": "eod", "pattern": "cancel_rate"}

    def test_detector_not_injected_raises(self) -> None:
        engine = TradingReviewEngine(thresholds=_THRESHOLDS, clock=lambda: _T0)
        with pytest.raises(TradingReviewError):
            engine.run_daily_review(_D0)

    def test_invalid_metric_raises(self) -> None:
        with pytest.raises(TradingReviewError):
            _engine([_metric(symbol="")]).run_daily_review(_D0)
        with pytest.raises(TradingReviewError):
            _engine([_metric(pattern="bogus")]).run_daily_review(_D0)
        with pytest.raises(TradingReviewError):
            _engine([_metric(value=float("nan"))]).run_daily_review(_D0)

    def test_generated_at_uses_injected_clock(self) -> None:
        engine = _engine([])
        report = engine.run_daily_review(_D0)
        assert report.generated_at == _T0


# ──────────────────────────────────────────────────────────────────────────────
# 报告版本化
# ──────────────────────────────────────────────────────────────────────────────


class TestVersioning:
    def test_rerun_same_day_version_increments(self) -> None:
        engine = _engine([_metric(value=0.45)])
        r1 = engine.run_daily_review(_D0)
        r2 = engine.run_daily_review(_D0)
        assert (r1.version, r2.version) == (1, 2)
        assert engine.report_of(_D0) is r2  # 默认最新版

    def test_report_of_specific_version(self) -> None:
        engine = _engine([_metric(value=0.45)])
        r1 = engine.run_daily_review(_D0)
        engine.run_daily_review(_D0)
        assert engine.report_of(_D0, version=1) is r1

    def test_report_of_unknown_date_raises(self) -> None:
        engine = _engine([])
        with pytest.raises(TradingReviewError):
            engine.report_of(_D0)

    def test_report_of_unknown_version_raises(self) -> None:
        engine = _engine([])
        engine.run_daily_review(_D0)
        with pytest.raises(TradingReviewError):
            engine.report_of(_D0, version=2)
        with pytest.raises(TradingReviewError):
            engine.report_of(_D0, version=0)

    def test_versions_of(self) -> None:
        engine = _engine([])
        engine.run_daily_review(_D0)
        engine.run_daily_review(_D0)
        assert engine.versions_of(_D0) == (1, 2)
        with pytest.raises(TradingReviewError):
            engine.versions_of(datetime.date(2026, 8, 26))

    def test_deterministic_same_input_same_findings(self) -> None:
        metrics = [
            _metric(ReviewPattern.PUMP_DUMP, "600519.SH", 0.09),
            _metric(ReviewPattern.CANCEL_RATE, "000001.SZ", 0.55),
        ]
        engine = _engine(metrics)
        r1 = engine.run_daily_review(_D0)
        r2 = engine.run_daily_review(_D0)
        assert r1.findings == r2.findings
