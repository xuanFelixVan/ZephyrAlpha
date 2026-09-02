# [BLUEPRINT] MOD-RPT-035 | docs/03_modules/_domain_reporting/strategy_explainability_reporter/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RPT-035 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.reporting.test_strategy_explainability_reporter
# [TESTS] src/zephyr/reporting/strategy_explainability_reporter.py
"""MOD-RPT-035 单元测试：strategy_explainability_reporter 策略可解释性报告器。

蓝图验收（B4-06655/CAND-RPT-010，B4 D-REPORTING-14）：
SHAP+LIME 双归因报告（注入解释器，异常降级，双缺规则重要性兜底）+
可解释性门控（覆盖度<阈值→降权/拦截，拦截不发布）+
报告发布对接（注入 publisher）。解释器/publisher/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.reporting.strategy_explainability_reporter",
    reason="strategy_explainability_reporter not importable",
)

from zephyr.reporting.strategy_explainability_reporter import (  # noqa: E402
    AttributionMethod,
    ExplainabilityError,
    ExplanationResult,
    GateDecision,
    StrategyExplainabilityReporter,
)

_T0 = datetime.datetime(2026, 8, 25, 16, 0, 0)

_FEATURES = {"momentum": 1.2, "value": -0.8, "liquidity": 0.5}
_SHAP_RES = ExplanationResult(importances={"momentum": 0.50, "value": -0.30, "liquidity": 0.20}, coverage=0.9)
_LIME_RES = ExplanationResult(importances={"momentum": 0.40, "value": -0.35, "liquidity": 0.25}, coverage=0.7)
_RULE = {"momentum": 0.6, "value": -0.4}


def _reporter(
    *,
    shap=_SHAP_RES,
    lime=_LIME_RES,
    rule: dict | None = None,
    fallback_coverage: float = 0.5,
    publisher=None,
    published: list | None = None,
) -> StrategyExplainabilityReporter:
    def _pub(report):
        if published is not None:
            published.append(report)
        return publisher(report) if publisher is not None else True

    return StrategyExplainabilityReporter(
        shap_explainer=(lambda sid, feat: shap) if shap is not None else None,
        lime_explainer=(lambda sid, feat: lime) if lime is not None else None,
        rule_importance=rule,
        fallback_coverage=fallback_coverage,
        publisher=_pub if (publisher is not None or published is not None) else None,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 初始化（门控阈值/兜底校验）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_inverted_thresholds_raise(self) -> None:
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(pass_threshold=0.4, downweight_threshold=0.8)

    def test_threshold_out_of_range_raises(self) -> None:
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(pass_threshold=1.2)
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(downweight_threshold=-0.1)
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(fallback_coverage=2.0)

    def test_invalid_rule_importance_raises(self) -> None:
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(rule_importance={"": 0.5})
        with pytest.raises(ExplainabilityError):
            StrategyExplainabilityReporter(rule_importance={"f1": float("nan")})


# ──────────────────────────────────────────────────────────────────────────────
# SHAP+LIME 双归因
# ──────────────────────────────────────────────────────────────────────────────


class TestDualAttribution:
    def test_dual_report(self) -> None:
        reporter = _reporter()
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.DUAL
        assert len(report.shap_importances) == 3
        assert len(report.lime_importances) == 3

    def test_coverage_average_of_two(self) -> None:
        reporter = _reporter()
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.coverage == pytest.approx((0.9 + 0.7) / 2)

    def test_importances_sorted_by_abs_weight(self) -> None:
        reporter = _reporter()
        report = reporter.build_report("strat-1", _FEATURES)
        assert [(fi.feature, fi.weight) for fi in report.shap_importances] == [
            ("momentum", 0.50),
            ("value", -0.30),
            ("liquidity", 0.20),
        ]

    def test_single_explainer_only(self) -> None:
        report = _reporter(lime=None).build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.SHAP
        assert report.lime_importances == ()
        assert report.coverage == 0.9
        report = _reporter(shap=None).build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.LIME
        assert report.shap_importances == ()
        assert report.coverage == 0.7

    def test_explainer_exception_degrades_to_other(self) -> None:
        def _bad_shap(_sid, _feat):
            raise RuntimeError("shap exploded")

        reporter = StrategyExplainabilityReporter(
            shap_explainer=_bad_shap,
            lime_explainer=lambda sid, feat: _LIME_RES,
            clock=lambda: _T0,
        )
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.LIME
        assert report.coverage == 0.7

    def test_coverage_out_of_range_raises(self) -> None:
        reporter = _reporter(shap=ExplanationResult(importances={"f": 0.1}, coverage=1.5))
        with pytest.raises(ExplainabilityError):
            reporter.build_report("strat-1", _FEATURES)

    def test_non_finite_importance_raises(self) -> None:
        reporter = _reporter(
            shap=ExplanationResult(importances={"f": float("inf")}, coverage=0.9),
            lime=None,
        )
        with pytest.raises(ExplainabilityError):
            reporter.build_report("strat-1", _FEATURES)


# ──────────────────────────────────────────────────────────────────────────────
# 可解释性门控
# ──────────────────────────────────────────────────────────────────────────────


class TestGate:
    def test_gate_pass_high_coverage(self) -> None:
        reporter = _reporter()  # coverage 0.8 ≥ pass 0.8
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.PASS

    def test_gate_downweight_mid_coverage(self) -> None:
        reporter = _reporter(shap=ExplanationResult(importances={"f": 0.5}, coverage=0.6), lime=None)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.DOWNWEIGHT

    def test_gate_block_low_coverage(self) -> None:
        reporter = _reporter(shap=ExplanationResult(importances={"f": 0.5}, coverage=0.3), lime=None)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.BLOCK

    def test_block_not_published(self) -> None:
        published: list = []
        reporter = _reporter(
            shap=ExplanationResult(importances={"f": 0.5}, coverage=0.3),
            lime=None,
            published=published,
        )
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.BLOCK
        assert report.published is False
        assert published == []  # 拦截不发布

    def test_downweight_still_published(self) -> None:
        published: list = []
        reporter = _reporter(
            shap=ExplanationResult(importances={"f": 0.5}, coverage=0.6),
            lime=None,
            published=published,
        )
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.DOWNWEIGHT
        assert report.published is True
        assert len(published) == 1

    def test_pass_published(self) -> None:
        published: list = []
        reporter = _reporter(published=published)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.gate is GateDecision.PASS
        assert report.published is True
        assert len(published) == 1

    def test_publisher_exception_not_blocking(self) -> None:
        def _bad_pub(_report):
            raise RuntimeError("publish failed")

        reporter = _reporter(publisher=_bad_pub)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.published is False  # 留痕不抛

    def test_publisher_nack_recorded(self) -> None:
        reporter = _reporter(publisher=lambda _r: False)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.published is False


# ──────────────────────────────────────────────────────────────────────────────
# 规则重要性兜底
# ──────────────────────────────────────────────────────────────────────────────


class TestRuleFallback:
    def test_both_missing_rule_fallback(self) -> None:
        reporter = _reporter(shap=None, lime=None, rule=_RULE, fallback_coverage=0.4)
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.RULE_FALLBACK
        assert [(fi.feature, fi.weight) for fi in report.shap_importances] == [
            ("momentum", 0.6),
            ("value", -0.4),
        ]
        assert report.lime_importances == ()
        assert report.coverage == 0.4
        assert report.gate is GateDecision.BLOCK  # 0.4 < downweight 0.5

    def test_both_missing_no_rule_raises(self) -> None:
        reporter = _reporter(shap=None, lime=None)
        with pytest.raises(ExplainabilityError):
            reporter.build_report("strat-1", _FEATURES)

    def test_both_explainers_raise_rule_fallback(self) -> None:
        def _bad(_sid, _feat):
            raise RuntimeError("boom")

        reporter = StrategyExplainabilityReporter(
            shap_explainer=_bad,
            lime_explainer=_bad,
            rule_importance=_RULE,
            fallback_coverage=0.9,
            clock=lambda: _T0,
        )
        report = reporter.build_report("strat-1", _FEATURES)
        assert report.method is AttributionMethod.RULE_FALLBACK
        assert report.coverage == 0.9
        assert report.gate is GateDecision.PASS


# ──────────────────────────────────────────────────────────────────────────────
# 查询 + 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_empty_strategy_id_raises(self) -> None:
        reporter = _reporter()
        with pytest.raises(ExplainabilityError):
            reporter.build_report("", _FEATURES)

    def test_report_of_latest_and_history(self) -> None:
        reporter = _reporter()
        r1 = reporter.build_report("strat-1", _FEATURES)
        r2 = reporter.build_report("strat-1", _FEATURES)
        assert reporter.report_of("strat-1") is r2
        assert reporter.history_of("strat-1") == (r1, r2)

    def test_report_of_unknown_strategy_raises(self) -> None:
        reporter = _reporter()
        with pytest.raises(ExplainabilityError):
            reporter.report_of("ghost")
        with pytest.raises(ExplainabilityError):
            reporter.history_of("ghost")

    def test_deterministic_same_input_same_report(self) -> None:
        reporter = _reporter()
        r1 = reporter.build_report("strat-1", _FEATURES)
        r2 = reporter.build_report("strat-1", _FEATURES)
        assert r1 == r2
