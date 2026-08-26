# [BLUEPRINT] MOD-FE-010 | docs/03_modules/_domain_frontend/compliance_dashboard/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-010 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_compliance_dashboard
# [TESTS] src/zephyr/frontend/compliance_dashboard.py
"""MOD-FE-010 单元测试：compliance_dashboard 合规仪表盘数据器。

蓝图验收（B14-04672/CAND-FE-011，A9 M36-S07）：规则命中率/审查异常清单/
证据链完整度/整改任务看板四卡数据聚合（数据源注入）+ 日窗口趋势序列
（指标词表闭合，缺值=0.0）。数据源/时钟全内存替身，不触库不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.compliance_dashboard",
    reason="compliance_dashboard not importable",
)

from zephyr.frontend.compliance_dashboard import (  # noqa: E402
    AnomalyRecord,
    AnomalySeverity,
    ComplianceDashboard,
    ComplianceDashboardError,
    EvidenceRecord,
    RemediationStatus,
    RemediationTask,
    RuleCheckRecord,
    TrendMetric,
)

_NOW = datetime.datetime(2026, 8, 26, 15, 0, 0)
_TODAY = _NOW.date()


def _dashboard(
    rule_checks=(),
    anomalies=(),
    evidences=(),
    tasks=(),
    trend=None,
) -> ComplianceDashboard:
    return ComplianceDashboard(
        rule_checks_provider=lambda: rule_checks,
        anomalies_provider=lambda: anomalies,
        evidence_provider=lambda: evidences,
        remediation_provider=lambda: tasks,
        trend_providers=trend,
        clock=lambda: _NOW,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造配置（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_missing_provider_raises(self) -> None:
        with pytest.raises(ComplianceDashboardError):
            ComplianceDashboard(
                rule_checks_provider=None,
                anomalies_provider=list,
                evidence_provider=list,
                remediation_provider=list,
            )

    def test_trend_metric_illegal_raises(self) -> None:
        with pytest.raises(ComplianceDashboardError):
            _dashboard(trend={"hit_rate": lambda d: 0.0})


# ──────────────────────────────────────────────────────────────────────────────
# 规则命中率卡
# ──────────────────────────────────────────────────────────────────────────────


class TestRuleHitCard:
    def test_hit_rate(self) -> None:
        dash = _dashboard(rule_checks=(
            RuleCheckRecord("r1", True),
            RuleCheckRecord("r2", True),
            RuleCheckRecord("r3", False),
            RuleCheckRecord("r4", True),
        ))
        card = dash.rule_hit_card()
        assert card.total_checks == 4
        assert card.hits == 3
        assert card.hit_rate == pytest.approx(0.75)

    def test_empty_rate_zero(self) -> None:
        card = _dashboard().rule_hit_card()
        assert card.total_checks == 0
        assert card.hit_rate == 0.0

    def test_wrong_record_type_raises(self) -> None:
        dash = _dashboard(rule_checks=(("r1", True),))
        with pytest.raises(ComplianceDashboardError):
            dash.rule_hit_card()

    def test_non_bool_hit_raises(self) -> None:
        dash = _dashboard(rule_checks=(RuleCheckRecord("r1", 1),))
        with pytest.raises(ComplianceDashboardError):
            dash.rule_hit_card()


# ──────────────────────────────────────────────────────────────────────────────
# 审查异常清单卡
# ──────────────────────────────────────────────────────────────────────────────


class TestAnomalyCard:
    def test_counts_and_by_severity(self) -> None:
        dash = _dashboard(anomalies=(
            AnomalyRecord("a1", AnomalySeverity.HIGH, "越权下单", True),
            AnomalyRecord("a2", AnomalySeverity.LOW, "备注缺失", True),
            AnomalyRecord("a3", AnomalySeverity.HIGH, "重复报单", False),
        ))
        card = dash.anomaly_card()
        assert card.total == 3
        assert card.open_count == 2
        assert card.by_severity[AnomalySeverity.HIGH] == 1
        assert card.by_severity[AnomalySeverity.MEDIUM] == 0
        assert card.by_severity[AnomalySeverity.LOW] == 1

    def test_open_items_sorted_high_first_then_id(self) -> None:
        dash = _dashboard(anomalies=(
            AnomalyRecord("a9", AnomalySeverity.LOW, "", True),
            AnomalyRecord("a2", AnomalySeverity.HIGH, "", True),
            AnomalyRecord("a1", AnomalySeverity.HIGH, "", True),
            AnomalyRecord("a5", AnomalySeverity.MEDIUM, "", True),
        ))
        ids = [r.anomaly_id for r in dash.anomaly_card().open_items]
        assert ids == ["a1", "a2", "a5", "a9"]

    def test_invalid_severity_raises(self) -> None:
        dash = _dashboard(anomalies=(AnomalyRecord("a1", "P0", "", True),))
        with pytest.raises(ComplianceDashboardError):
            dash.anomaly_card()


# ──────────────────────────────────────────────────────────────────────────────
# 证据链完整度卡
# ──────────────────────────────────────────────────────────────────────────────


class TestEvidenceCard:
    def test_completeness_and_incomplete_ids(self) -> None:
        dash = _dashboard(evidences=(
            EvidenceRecord("e2", False, ("signature",)),
            EvidenceRecord("e1", True),
            EvidenceRecord("e3", False),
        ))
        card = dash.evidence_card()
        assert card.total == 3
        assert card.complete_count == 1
        assert card.completeness == pytest.approx(round(1 / 3, 6))
        assert card.incomplete_ids == ("e2", "e3")

    def test_empty_completeness_zero(self) -> None:
        assert _dashboard().evidence_card().completeness == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# 整改任务看板卡
# ──────────────────────────────────────────────────────────────────────────────


class TestRemediationCard:
    def test_by_status_full_vocab(self) -> None:
        dash = _dashboard(tasks=(
            RemediationTask("t1", RemediationStatus.OPEN),
            RemediationTask("t2", RemediationStatus.IN_PROGRESS),
            RemediationTask("t3", RemediationStatus.OVERDUE),
            RemediationTask("t4", RemediationStatus.DONE),
            RemediationTask("t5", RemediationStatus.OVERDUE),
        ))
        card = dash.remediation_card()
        assert card.total == 5
        assert card.by_status == {
            RemediationStatus.OPEN: 1,
            RemediationStatus.IN_PROGRESS: 1,
            RemediationStatus.DONE: 1,
            RemediationStatus.OVERDUE: 2,
        }
        assert card.overdue_ids == ("t3", "t5")

    def test_invalid_status_raises(self) -> None:
        dash = _dashboard(tasks=(RemediationTask("t1", "doing"),))
        with pytest.raises(ComplianceDashboardError):
            dash.remediation_card()


# ──────────────────────────────────────────────────────────────────────────────
# 快照
# ──────────────────────────────────────────────────────────────────────────────


class TestSnapshot:
    def test_snapshot_aggregates_four_cards(self) -> None:
        dash = _dashboard(
            rule_checks=(RuleCheckRecord("r1", True),),
            anomalies=(AnomalyRecord("a1", AnomalySeverity.HIGH, "", True),),
            evidences=(EvidenceRecord("e1", True),),
            tasks=(RemediationTask("t1", RemediationStatus.OPEN),),
        )
        snap = dash.snapshot()
        assert snap.generated_at == _NOW
        assert snap.rule_hit.hits == 1
        assert snap.anomalies.open_count == 1
        assert snap.evidence.completeness == 1.0
        assert snap.remediation.total == 1


# ──────────────────────────────────────────────────────────────────────────────
# 趋势序列
# ──────────────────────────────────────────────────────────────────────────────


class TestTrend:
    def test_trend_ascending_with_none_filled(self) -> None:
        data = {_TODAY - datetime.timedelta(days=2): 0.5, _TODAY: 0.8}
        dash = _dashboard(trend={TrendMetric.RULE_HIT_RATE: lambda d: data.get(d)})
        points = dash.trend(TrendMetric.RULE_HIT_RATE, 3, end_date=_TODAY)
        assert [p.day for p in points] == [
            _TODAY - datetime.timedelta(days=2),
            _TODAY - datetime.timedelta(days=1),
            _TODAY,
        ]
        assert [p.value for p in points] == [0.5, 0.0, 0.8]

    def test_missing_metric_provider_raises(self) -> None:
        with pytest.raises(ComplianceDashboardError):
            _dashboard().trend(TrendMetric.ANOMALY_COUNT, 3, end_date=_TODAY)

    def test_invalid_metric_raises(self) -> None:
        with pytest.raises(ComplianceDashboardError):
            _dashboard().trend("hit_rate", 3, end_date=_TODAY)

    def test_days_out_of_range_raises(self) -> None:
        dash = _dashboard(trend={TrendMetric.RULE_HIT_RATE: lambda d: 0.0})
        with pytest.raises(ComplianceDashboardError):
            dash.trend(TrendMetric.RULE_HIT_RATE, 0, end_date=_TODAY)
        with pytest.raises(ComplianceDashboardError):
            dash.trend(TrendMetric.RULE_HIT_RATE, 367, end_date=_TODAY)

    def test_non_numeric_value_raises(self) -> None:
        dash = _dashboard(trend={TrendMetric.RULE_HIT_RATE: lambda d: "high"})
        with pytest.raises(ComplianceDashboardError):
            dash.trend(TrendMetric.RULE_HIT_RATE, 2, end_date=_TODAY)

    def test_default_end_uses_clock(self) -> None:
        dash = _dashboard(trend={TrendMetric.OPEN_REMEDIATION: lambda d: 1})
        points = dash.trend(TrendMetric.OPEN_REMEDIATION, 2)
        assert points[-1].day == _TODAY
        assert all(p.value == 1.0 for p in points)


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_snapshot(self) -> None:
        kwargs = dict(
            rule_checks=(RuleCheckRecord("r1", True), RuleCheckRecord("r2", False)),
            anomalies=(AnomalyRecord("a1", AnomalySeverity.HIGH, "", True),),
            evidences=(EvidenceRecord("e1", False, ("x",)),),
            tasks=(RemediationTask("t1", RemediationStatus.OVERDUE),),
        )
        assert _dashboard(**kwargs).snapshot() == _dashboard(**kwargs).snapshot()
