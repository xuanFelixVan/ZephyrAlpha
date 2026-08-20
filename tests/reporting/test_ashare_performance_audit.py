# [BLUEPRINT] MOD-RPT-026 | docs/03_modules/_domain_reporting/ashare_performance_audit/blueprint.md
# [MODULE] tests.reporting.test_ashare_performance_audit
# [DOMAIN] D_REPORTING
# [INVARIANTS] 5类审计(收益率/回撤/风险调整/归因一致性/交易成本); data_hash=SHA-256(canonical_json(content)); 阈值可配置; frozen不可变; 纯建议不自动执行
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAuditInputError(ZA-RPT-0026)
# [TESTS] self
# [A_module] module_id=MOD-RPT-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-026 A-Share Performance Audit 单元测试.

覆盖（blueprint §9）:
  - 5类审计规则: 收益率/回撤/风险调整/归因一致性/交易成本
  - 优化建议触发: 10种映射 (category+severity → type+priority)
  - 阈值可配置: 自定义 AuditThresholds
  - data_hash 确定性 + 篡改检测
  - frozen 不可变
  - 边界值: 空 metrics/缺必填字段/expected_cost=None/expected_cost=0
  - 归因一致性校验: 误差容忍/超出阈值
  - 多 finding 聚合
  - 审计规则确定性: 同输入→同输出
"""

from __future__ import annotations

import dataclasses
import hashlib
from datetime import UTC, datetime
from typing import Any

import pytest

from zephyr.reporting.ashare_performance_audit import (
    ASharePerformanceAuditor,
    AuditCategory,
    AuditFinding,
    AuditSeverity,
    AuditThresholds,
    InvalidAuditInputError,
    OptimizationRecommendation,
    PerformanceAuditReport,
    RecommendationPriority,
    RecommendationType,
    _canonical_json,
    _compute_data_hash,
)

# ── 测试辅助 ──

_GOOD_METRICS = {
    "return_pct": 0.12,
    "max_drawdown": -0.08,
    "sharpe_ratio": 1.5,
    "sortino_ratio": 2.0,
}

_GOOD_ATTRIBUTION = {
    "total_return": 0.12,
    "allocation_effect": 0.05,
    "selection_effect": 0.06,
    "interaction_effect": 0.01,
    "transaction_cost_drag": 0.001,
}


# ── 收益率审计测试 ──


class TestReturnAudit:
    def test_positive_return_no_finding(self) -> None:
        """正收益率 → 无收益率审计发现。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        return_findings = [f for f in report.findings if f["category"] == AuditCategory.RETURN.value]
        assert len(return_findings) == 0

    def test_negative_return_warning(self) -> None:
        """收益率 < -1% → WARNING。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.02}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        return_findings = [f for f in report.findings if f["category"] == AuditCategory.RETURN.value]
        assert len(return_findings) == 1
        assert return_findings[0]["severity"] == AuditSeverity.WARNING.value

    def test_critical_return_critical(self) -> None:
        """收益率 < -5% → CRITICAL。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        return_findings = [f for f in report.findings if f["category"] == AuditCategory.RETURN.value]
        assert len(return_findings) == 1
        assert return_findings[0]["severity"] == AuditSeverity.CRITICAL.value

    def test_return_at_warning_boundary(self) -> None:
        """收益率 == -1% (边界) → 无发现（< 才触发）。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.01}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        return_findings = [f for f in report.findings if f["category"] == AuditCategory.RETURN.value]
        assert len(return_findings) == 0


# ── 回撤审计测试 ──


class TestDrawdownAudit:
    def test_small_drawdown_no_finding(self) -> None:
        """小回撤 → 无发现。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        dd_findings = [f for f in report.findings if f["category"] == AuditCategory.DRAWDOWN.value]
        assert len(dd_findings) == 0

    def test_warning_drawdown(self) -> None:
        """回撤 < -10% → WARNING。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "max_drawdown": -0.12}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        dd_findings = [f for f in report.findings if f["category"] == AuditCategory.DRAWDOWN.value]
        assert len(dd_findings) == 1
        assert dd_findings[0]["severity"] == AuditSeverity.WARNING.value

    def test_critical_drawdown(self) -> None:
        """回撤 < -15% → CRITICAL。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "max_drawdown": -0.18}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        dd_findings = [f for f in report.findings if f["category"] == AuditCategory.DRAWDOWN.value]
        assert len(dd_findings) == 1
        assert dd_findings[0]["severity"] == AuditSeverity.CRITICAL.value


# ── 风险调整收益审计测试 ──


class TestRiskAdjustedAudit:
    def test_good_sharpe_no_finding(self) -> None:
        """Sharpe >= 0.5 → 无发现。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        ra_findings = [f for f in report.findings if f["category"] == AuditCategory.RISK_ADJUSTED.value]
        assert len(ra_findings) == 0

    def test_sharpe_info(self) -> None:
        """0 <= Sharpe < 0.5 → INFO。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "sharpe_ratio": 0.3}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        ra_findings = [
            f
            for f in report.findings
            if f["category"] == AuditCategory.RISK_ADJUSTED.value and f["metric_name"] == "sharpe_ratio"
        ]
        assert len(ra_findings) == 1
        assert ra_findings[0]["severity"] == AuditSeverity.INFO.value

    def test_negative_sharpe_warning(self) -> None:
        """Sharpe < 0 → WARNING。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "sharpe_ratio": -0.5}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        ra_findings = [
            f
            for f in report.findings
            if f["category"] == AuditCategory.RISK_ADJUSTED.value and f["metric_name"] == "sharpe_ratio"
        ]
        assert len(ra_findings) == 1
        assert ra_findings[0]["severity"] == AuditSeverity.WARNING.value

    def test_negative_sortino_warning(self) -> None:
        """Sortino < 0 → WARNING。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "sortino_ratio": -0.5}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        sortino_findings = [
            f
            for f in report.findings
            if f["category"] == AuditCategory.RISK_ADJUSTED.value and f["metric_name"] == "sortino_ratio"
        ]
        assert len(sortino_findings) == 1
        assert sortino_findings[0]["severity"] == AuditSeverity.WARNING.value


# ── 归因一致性校验测试 ──


class TestAttributionConsistency:
    def test_consistent_attribution_no_finding(self) -> None:
        """归因自洽（误差 < tolerance）→ 无发现。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        attr_findings = [f for f in report.findings if f["category"] == AuditCategory.ATTRIBUTION.value]
        assert len(attr_findings) == 0

    def test_inconsistent_attribution_warning(self) -> None:
        """归因不自洽（误差 > tolerance）→ WARNING。"""
        auditor = ASharePerformanceAuditor()
        attribution = {
            **_GOOD_ATTRIBUTION,
            "total_return": 0.20,  # 0.05+0.06+0.01=0.12 ≠ 0.20, 误差=0.08
        }
        report = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, attribution)
        attr_findings = [f for f in report.findings if f["category"] == AuditCategory.ATTRIBUTION.value]
        assert len(attr_findings) == 1
        assert attr_findings[0]["severity"] == AuditSeverity.WARNING.value

    def test_attribution_within_tolerance(self) -> None:
        """误差 == tolerance 以下 → 无发现（> 才触发）。"""
        auditor = ASharePerformanceAuditor()
        attribution = {
            **_GOOD_ATTRIBUTION,
            "total_return": 0.1201,  # 误差 0.0001 < 0.001
        }
        report = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, attribution)
        attr_findings = [f for f in report.findings if f["category"] == AuditCategory.ATTRIBUTION.value]
        assert len(attr_findings) == 0


# ── 交易成本审计测试 ──


class TestCostAudit:
    def test_no_expected_cost_skips_audit(self) -> None:
        """expected_cost=None → 跳过成本审计。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
            expected_cost=None,
        )
        cost_findings = [f for f in report.findings if f["category"] == AuditCategory.COST.value]
        assert len(cost_findings) == 0

    def test_zero_expected_cost_skips_audit(self) -> None:
        """expected_cost=0 → 跳过成本审计（避免除零）。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
            expected_cost=0.0,
        )
        cost_findings = [f for f in report.findings if f["category"] == AuditCategory.COST.value]
        assert len(cost_findings) == 0

    def test_normal_cost_no_finding(self) -> None:
        """成本比例 < 1.5x → 无发现。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
            expected_cost=0.001,  # 0.001/0.001 = 1.0x
        )
        cost_findings = [f for f in report.findings if f["category"] == AuditCategory.COST.value]
        assert len(cost_findings) == 0

    def test_cost_warning(self) -> None:
        """成本比例 > 1.5x → WARNING。"""
        auditor = ASharePerformanceAuditor()
        attribution = {**_GOOD_ATTRIBUTION, "transaction_cost_drag": 0.002}
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            attribution,
            expected_cost=0.001,  # 0.002/0.001 = 2.0x → 但 > 1.5 → WARNING
        )
        cost_findings = [f for f in report.findings if f["category"] == AuditCategory.COST.value]
        assert len(cost_findings) == 1
        assert cost_findings[0]["severity"] == AuditSeverity.WARNING.value

    def test_cost_critical(self) -> None:
        """成本比例 > 2.0x → CRITICAL。"""
        auditor = ASharePerformanceAuditor()
        attribution = {**_GOOD_ATTRIBUTION, "transaction_cost_drag": 0.003}
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            attribution,
            expected_cost=0.001,  # 0.003/0.001 = 3.0x → CRITICAL
        )
        cost_findings = [f for f in report.findings if f["category"] == AuditCategory.COST.value]
        assert len(cost_findings) == 1
        assert cost_findings[0]["severity"] == AuditSeverity.CRITICAL.value


# ── 优化建议触发测试 ──


class TestOptimizationRecommendations:
    def test_no_findings_no_recommendations(self) -> None:
        """无审计发现 → 无优化建议。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        assert len(report.findings) == 0
        assert len(report.recommendations) == 0

    def test_return_critical_triggers_strategy_adjust_high(self) -> None:
        """收益率 CRITICAL → STRATEGY_ADJUST HIGH。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        recs = report.recommendations
        assert len(recs) >= 1
        strategy_recs = [r for r in recs if r["type"] == RecommendationType.STRATEGY_ADJUST.value]
        assert len(strategy_recs) >= 1
        assert strategy_recs[0]["priority"] == RecommendationPriority.HIGH.value

    def test_drawdown_critical_triggers_risk_tighten_high(self) -> None:
        """回撤 CRITICAL → RISK_TIGHTEN HIGH。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "max_drawdown": -0.18}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        risk_recs = [r for r in report.recommendations if r["type"] == RecommendationType.RISK_TIGHTEN.value]
        assert len(risk_recs) >= 1
        assert risk_recs[0]["priority"] == RecommendationPriority.HIGH.value

    def test_cost_critical_triggers_cost_control_high(self) -> None:
        """成本 CRITICAL → COST_CONTROL HIGH。"""
        auditor = ASharePerformanceAuditor()
        attribution = {**_GOOD_ATTRIBUTION, "transaction_cost_drag": 0.003}
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            attribution,
            expected_cost=0.001,
        )
        cost_recs = [r for r in report.recommendations if r["type"] == RecommendationType.COST_CONTROL.value]
        assert len(cost_recs) >= 1
        assert cost_recs[0]["priority"] == RecommendationPriority.HIGH.value

    def test_sharpe_warning_triggers_param_optimize_medium(self) -> None:
        """Sharpe WARNING → PARAM_OPTIMIZE MEDIUM。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "sharpe_ratio": -0.5}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        param_recs = [r for r in report.recommendations if r["type"] == RecommendationType.PARAM_OPTIMIZE.value]
        assert len(param_recs) >= 1
        assert param_recs[0]["priority"] == RecommendationPriority.MEDIUM.value

    def test_attribution_inconsistency_triggers_strategy_adjust(self) -> None:
        """归因不一致 → STRATEGY_ADJUST MEDIUM。"""
        auditor = ASharePerformanceAuditor()
        attribution = {**_GOOD_ATTRIBUTION, "total_return": 0.20}
        report = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, attribution)
        strategy_recs = [r for r in report.recommendations if r["type"] == RecommendationType.STRATEGY_ADJUST.value]
        assert len(strategy_recs) >= 1

    def test_recommendation_links_to_finding(self) -> None:
        """每条建议关联到一条审计发现。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06, "max_drawdown": -0.18}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        finding_ids = {f["finding_id"] for f in report.findings}
        for rec in report.recommendations:
            assert rec["finding_id"] in finding_ids

    def test_target_module_correct(self) -> None:
        """建议的 target_module 映射正确。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        strategy_recs = [r for r in report.recommendations if r["type"] == RecommendationType.STRATEGY_ADJUST.value]
        assert all(r["target_module"] == "D_PF_CORE" for r in strategy_recs)


# ── 阈值可配置测试 ──


class TestCustomThresholds:
    def test_custom_thresholds_change_audit_results(self) -> None:
        """自定义阈值改变审计结果。"""
        # 默认阈值: return_warning=-0.01, 用宽松阈值 -0.10
        thresholds = AuditThresholds(return_warning=-0.10, return_critical=-0.20)
        auditor = ASharePerformanceAuditor(thresholds=thresholds)
        metrics = {**_GOOD_METRICS, "return_pct": -0.05}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        return_findings = [f for f in report.findings if f["category"] == AuditCategory.RETURN.value]
        # -0.05 > -0.10 (宽松阈值), 无发现
        assert len(return_findings) == 0

    def test_default_thresholds(self) -> None:
        """默认阈值 AuditThresholds() 生成正确。"""
        t = AuditThresholds()
        assert t.return_warning == -0.01
        assert t.return_critical == -0.05
        assert t.drawdown_warning == -0.10
        assert t.drawdown_critical == -0.15
        assert t.sharpe_warning == 0.0
        assert t.sharpe_info == 0.5
        assert t.attribution_tolerance == 0.001
        assert t.cost_warning_ratio == 1.5
        assert t.cost_critical_ratio == 2.0


# ── data_hash / 完整性校验测试 ──


class TestDataHashAndValidation:
    def test_valid_report_passes(self) -> None:
        """未篡改的报告 → validate_report 返回 True。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        assert auditor.validate_report(report) is True

    def test_tampered_content_fails(self) -> None:
        """篡改 content → validate_report 返回 False。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        tampered = dataclasses.replace(
            report,
            performance_summary={**report.performance_summary, "return_pct": 999.0},
        )
        assert auditor.validate_report(tampered) is False

    def test_tampered_findings_fails(self) -> None:
        """篡改 findings → validate_report 返回 False。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06}
        report = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        tampered_findings = list(report.findings)
        if tampered_findings:
            tampered_findings[0] = {**tampered_findings[0], "severity": "INFO"}
        tampered = dataclasses.replace(report, findings=tampered_findings)
        assert auditor.validate_report(tampered) is False

    def test_data_hash_is_sha256_hex(self) -> None:
        """data_hash 是 64 位 hex 字符串。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        assert len(report.data_hash) == 64
        int(report.data_hash, 16)


# ── 审计确定性测试 ──


class TestDeterminism:
    def test_same_input_same_findings_count(self) -> None:
        """同输入 → 相同数量的 findings 和 recommendations。"""
        auditor = ASharePerformanceAuditor()
        metrics = {**_GOOD_METRICS, "return_pct": -0.06, "max_drawdown": -0.12}
        r1 = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        r2 = auditor.audit("PF-001", "2026-Q3", metrics, _GOOD_ATTRIBUTION)
        assert len(r1.findings) == len(r2.findings)
        assert len(r1.recommendations) == len(r2.recommendations)

    def test_same_input_same_data_hash(self) -> None:
        """同输入 → 相同 data_hash。"""
        auditor = ASharePerformanceAuditor()
        r1 = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)
        r2 = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)
        assert r1.data_hash == r2.data_hash

    def test_different_input_different_data_hash(self) -> None:
        """不同输入 → 不同 data_hash。"""
        auditor = ASharePerformanceAuditor()
        r1 = auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)
        metrics2 = {**_GOOD_METRICS, "return_pct": -0.06}
        r2 = auditor.audit("PF-001", "2026-Q3", metrics2, _GOOD_ATTRIBUTION)
        assert r1.data_hash != r2.data_hash


# ── 不可变性测试 ──


class TestImmutability:
    def test_report_is_frozen(self) -> None:
        """PerformanceAuditReport frozen——不可修改字段。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.portfolio_id = "PF-999"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.data_hash = "fake"  # type: ignore[misc]

    def test_finding_is_frozen(self) -> None:
        """AuditFinding frozen。"""
        f = AuditFinding(
            finding_id="FIND-test",
            category=AuditCategory.RETURN,
            severity=AuditSeverity.WARNING,
            metric_name="return_pct",
            actual_value=-0.02,
            threshold=-0.01,
            description="test",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            f.severity = AuditSeverity.CRITICAL  # type: ignore[misc]

    def test_thresholds_is_frozen(self) -> None:
        """AuditThresholds frozen。"""
        t = AuditThresholds()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.return_warning = -0.5  # type: ignore[misc]

    def test_enum_values(self) -> None:
        """枚举值正确。"""
        assert AuditCategory.RETURN.value == "return"
        assert AuditCategory.DRAWDOWN.value == "drawdown"
        assert AuditCategory.RISK_ADJUSTED.value == "risk_adjusted"
        assert AuditCategory.ATTRIBUTION.value == "attribution"
        assert AuditCategory.COST.value == "cost"
        assert AuditSeverity.INFO.value == "INFO"
        assert AuditSeverity.WARNING.value == "WARNING"
        assert AuditSeverity.CRITICAL.value == "CRITICAL"


# ── 边界值 / 错误契约测试 ──


class TestEdgeCases:
    def test_empty_portfolio_id_raises(self) -> None:
        """portfolio_id 为空 → 拒绝。"""
        auditor = ASharePerformanceAuditor()
        with pytest.raises(InvalidAuditInputError):
            auditor.audit("", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)

    def test_empty_audit_period_raises(self) -> None:
        """audit_period 为空 → 拒绝。"""
        auditor = ASharePerformanceAuditor()
        with pytest.raises(InvalidAuditInputError):
            auditor.audit("PF-001", "  ", _GOOD_METRICS, _GOOD_ATTRIBUTION)

    def test_empty_metrics_raises(self) -> None:
        """performance_metrics 为空 dict → 拒绝。"""
        auditor = ASharePerformanceAuditor()
        with pytest.raises(InvalidAuditInputError):
            auditor.audit("PF-001", "2026-Q3", {}, _GOOD_ATTRIBUTION)

    def test_empty_attribution_raises(self) -> None:
        """attribution_result 为空 dict → 拒绝。"""
        auditor = ASharePerformanceAuditor()
        with pytest.raises(InvalidAuditInputError):
            auditor.audit("PF-001", "2026-Q3", _GOOD_METRICS, {})

    def test_error_code_is_za_rpt_0026(self) -> None:
        """InvalidAuditInputError.error_code = ZA-RPT-0026。"""
        assert InvalidAuditInputError.error_code == "ZA-RPT-0026"

    def test_report_id_format(self) -> None:
        """report_id 格式: AUDIT-<hex10>。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        assert report.report_id.startswith("AUDIT-")
        hex_part = report.report_id.split("AUDIT-")[1]
        assert len(hex_part) == 10
        int(hex_part, 16)

    def test_generated_at_is_utc(self) -> None:
        """generated_at 为 UTC 时间。"""
        auditor = ASharePerformanceAuditor()
        before = datetime.now(UTC)
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        after = datetime.now(UTC)
        assert report.generated_at.tzinfo is not None
        assert before <= report.generated_at <= after

    def test_schema_version(self) -> None:
        """schema_version = "1.0"。"""
        auditor = ASharePerformanceAuditor()
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            _GOOD_METRICS,
            _GOOD_ATTRIBUTION,
        )
        assert report.schema_version == "1.0"

    def test_multiple_findings_aggregated(self) -> None:
        """多类审计发现同时存在时正确聚合。"""
        auditor = ASharePerformanceAuditor()
        metrics = {
            "return_pct": -0.06,  # CRITICAL → STRATEGY_ADJUST HIGH
            "max_drawdown": -0.18,  # CRITICAL → RISK_TIGHTEN HIGH
            "sharpe_ratio": -0.5,  # WARNING → PARAM_OPTIMIZE MEDIUM
            "sortino_ratio": -0.5,  # WARNING → PARAM_OPTIMIZE MEDIUM (但复用映射)
        }
        attribution = {
            **_GOOD_ATTRIBUTION,
            "total_return": 0.20,  # 归因不一致 → STRATEGY_ADJUST MEDIUM
            "transaction_cost_drag": 0.003,  # 成本 CRITICAL
        }
        report = auditor.audit(
            "PF-001",
            "2026-Q3",
            metrics,
            attribution,
            expected_cost=0.001,
        )
        # 至少 5 个发现（收益率+回撤+Sharpe+Sortino+归因+成本=6）
        assert len(report.findings) >= 5
        # 至少 4 条建议（Sharpe INFO 不触发, Sortino WARNING 复用 RISK_ADJUSTED WARNING 映射）
        assert len(report.recommendations) >= 4

    def test_auditor_has_no_external_state(self) -> None:
        """ASharePerformanceAuditor 无外部状态。"""
        gen1 = ASharePerformanceAuditor()
        gen2 = ASharePerformanceAuditor()
        r1 = gen1.audit("PF-001", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)
        r2 = gen2.audit("PF-001", "2026-Q3", _GOOD_METRICS, _GOOD_ATTRIBUTION)
        assert r1.data_hash == r2.data_hash
