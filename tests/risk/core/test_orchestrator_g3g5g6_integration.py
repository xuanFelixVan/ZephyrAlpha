# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md | §test
# [MODULE] tests.risk.core.test_orchestrator_g3g5g6_integration
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_risk_manager_orchestrator; zephyr.risk.core.ai_agent_monitor; zephyr.risk.core.model_risk_audit; zephyr.risk.core.operational_risk_monitor; zephyr.risk.core.alert_generator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_orchestrator_g3g5g6_integration.py
# [A_test] module_id: MOD-RK-14 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G3/G5/G6 集成测试: 监控器 → 编排器 → 告警管道（端到端）.

覆盖: 向后兼容(未注入监控器)/正常(无告警)/突破(RED告警)/
best-effort异常不阻断/全流程(G3+G5+G6三路同时触发).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.risk.implementations.default_risk_manager_orchestrator",
    reason="orchestrator not importable",
)

from zephyr.ex_core.audit_journal.auditor import OperationalRiskStats  # noqa: E402
from zephyr.intelligence.model_drift_detector import DriftResult  # noqa: E402
from zephyr.risk.core.ai_agent_monitor import AiAgentMonitor  # noqa: E402
from zephyr.risk.core.alert_generator import AlertGenerator, AlertLevel  # noqa: E402
from zephyr.risk.core.model_risk_audit import ModelRiskAuditor  # noqa: E402
from zephyr.risk.core.operational_risk_monitor import (  # noqa: E402
    OperationalRiskMonitor,
)
from zephyr.risk.implementations.default_risk_manager_orchestrator import (  # noqa: E402
    DefaultRiskManagerOrchestrator,
)

# ── Mock / 辅助 ─────────────────────────────────────────────────────


class _MockDriftDetector:
    """可控 ModelDriftDetector 替身。"""

    def __init__(self, drift_detected: bool, divergence: float):
        self._drift = drift_detected
        self._div = divergence

    def detect_drift(self, outputs):
        return DriftResult(
            drift_detected=self._drift,
            model_name="test",
            divergence_score=self._div,
            threshold=0.15,
            exit_code=34 if self._drift else 0,
            details=["mock"],
        )


def _make_stats(
    failure_rate: float = 0.02,
    latency_p95_ms: float = 80.0,
    submission_count: int = 100,
    rejection_count: int = 2,
) -> OperationalRiskStats:
    now = datetime.now(UTC)
    return OperationalRiskStats(
        period_start=now,
        period_end=now,
        submission_count=submission_count,
        rejection_count=rejection_count,
        filled_count=submission_count - rejection_count,
        failure_rate=failure_rate,
        fill_rate=1.0 - failure_rate,
        latency_count=submission_count - rejection_count,
        latency_p50_ms=50.0,
        latency_p95_ms=latency_p95_ms,
        latency_max_ms=200.0,
        latency_mean_ms=60.0,
        generated_at=now,
    )


# ── 向后兼容 ─────────────────────────────────────────────────────────


class TestBackwardCompatibility:
    """未注入监控器时，check_* 返回 None，不追加检查。"""

    def test_no_ai_agent_monitor_returns_none(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        assert orch.check_ai_agent() is None

    def test_no_model_risk_auditor_returns_none(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        assert orch.check_model_risk() is None

    def test_no_operational_risk_monitor_returns_none(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        assert orch.check_operational_risk(_make_stats()) is None

    def test_no_monitors_no_extra_checks(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        orch.check_ai_agent()
        orch.check_model_risk()
        orch.check_operational_risk(_make_stats())
        report = orch.aggregate_report()
        assert len(report.checks) == 0
        assert orch.last_alerts == []


# ── G3 AI/Agent 风险 ────────────────────────────────────────────────


class TestAiAgentRisk:
    def test_stable_no_alerts(self):
        """STABLE → passed check，无告警。"""
        gen = AlertGenerator()
        mon = AiAgentMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            ai_agent_monitor=mon,
        )
        m = orch.check_ai_agent(
            agent_metrics={"a": 0.5},
            trajectory_anomaly_count=0,
            fingerprint_deviation=0.0,
        )
        assert m is not None
        assert m.is_breached is False
        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_critical_triggers_red_alert(self):
        """CRITICAL → HALT → RED 告警。"""
        gen = AlertGenerator()
        mon = AiAgentMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            ai_agent_monitor=mon,
        )
        # 驱动到 CRITICAL
        for i in range(6):
            m = orch.check_ai_agent(
                agent_metrics={"a": float(i), "b": float(i), "c": float(i), "d": float(i)},
                trajectory_anomaly_count=0,
                fingerprint_deviation=0.0,
            )
        assert m.emergence_state == "CRITICAL"
        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        assert any(a.level == AlertLevel.RED for a in alerts)
        assert any(a.source == "ai_agent_monitor" for a in alerts)


# ── G5 模型风险 ─────────────────────────────────────────────────────


class TestModelRisk:
    def test_low_risk_no_alerts(self):
        gen = AlertGenerator()
        auditor = ModelRiskAuditor(drift_detector=_MockDriftDetector(False, 0.0))
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            model_risk_auditor=auditor,
        )
        r = orch.check_model_risk()
        assert r is not None
        assert r.risk_level == "low"
        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_critical_triggers_red_alert(self):
        """drift + severe ic_decay → critical → HALT → RED 告警。"""
        gen = AlertGenerator()
        auditor = ModelRiskAuditor(drift_detector=_MockDriftDetector(True, 0.20))
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            model_risk_auditor=auditor,
        )
        r = orch.check_model_risk(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.10, 5: 0.02},  # 0.8 decay
        )
        assert r.risk_level == "critical"
        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        assert any(a.level == AlertLevel.RED for a in alerts)
        assert any(a.source == "model_risk_audit" for a in alerts)


# ── G6 操作风险 ─────────────────────────────────────────────────────


class TestOperationalRisk:
    def test_healthy_no_alerts(self):
        gen = AlertGenerator()
        mon = OperationalRiskMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            operational_risk_monitor=mon,
        )
        a = orch.check_operational_risk(_make_stats(failure_rate=0.02, latency_p95_ms=80.0))
        assert a is not None
        assert a.overall_severity == "info"
        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_severe_failure_triggers_red_alert(self):
        """failure_rate severe → HALT → RED 告警。"""
        gen = AlertGenerator()
        mon = OperationalRiskMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            operational_risk_monitor=mon,
        )
        a = orch.check_operational_risk(_make_stats(failure_rate=0.15, rejection_count=15))
        assert a.overall_severity == "HALT"
        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        assert any(a.level == AlertLevel.RED for a in alerts)
        assert any(a.source == "operational_risk_monitor" for a in alerts)


# ── best-effort ─────────────────────────────────────────────────────


class TestBestEffort:
    def test_ai_agent_exception_returns_none(self):
        """监控器内部异常 → None，编排器不崩溃。"""

        class _FailingMonitor(AiAgentMonitor):
            def assess(self, *args, **kwargs):
                raise RuntimeError("broken")

        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            ai_agent_monitor=_FailingMonitor(),
        )
        assert orch.check_ai_agent() is None
        report = orch.aggregate_report()
        assert report is not None
        assert len(report.checks) == 0

    def test_model_risk_exception_returns_none(self):

        class _FailingAuditor(ModelRiskAuditor):
            def audit(self, *args, **kwargs):
                raise RuntimeError("broken")

        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            model_risk_auditor=_FailingAuditor(),
        )
        assert orch.check_model_risk() is None
        assert orch.aggregate_report() is not None

    def test_operational_risk_exception_returns_none(self):

        class _FailingOp(OperationalRiskMonitor):
            def assess(self, stats):
                raise RuntimeError("broken")

        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            operational_risk_monitor=_FailingOp(),
        )
        assert orch.check_operational_risk(_make_stats()) is None
        assert orch.aggregate_report() is not None


# ── 全流程：G3 + G5 + G6 三路同时触发 ───────────────────────────────


class TestFullPipeline:
    def test_all_three_trigger_alerts(self):
        """G3(CRITICAL) + G5(critical) + G6(HALT) 同时触发 → 多条 RED 告警。"""
        gen = AlertGenerator()
        ai_mon = AiAgentMonitor()
        model_auditor = ModelRiskAuditor(drift_detector=_MockDriftDetector(True, 0.20))
        op_mon = OperationalRiskMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            ai_agent_monitor=ai_mon,
            model_risk_auditor=model_auditor,
            operational_risk_monitor=op_mon,
        )

        # G3: 驱动到 CRITICAL
        for i in range(6):
            orch.check_ai_agent(
                agent_metrics={"a": float(i), "b": float(i), "c": float(i), "d": float(i)},
            )
        # G5: critical
        orch.check_model_risk(
            model_outputs=[{"pred": 1}],
            ic_data={1: 0.10, 5: 0.02},
        )
        # G6: HALT
        orch.check_operational_risk(_make_stats(failure_rate=0.15, rejection_count=15))

        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        sources = {a.source for a in alerts}
        # 三个监控器都应产生告警
        assert "ai_agent_monitor" in sources
        assert "model_risk_audit" in sources
        assert "operational_risk_monitor" in sources
        # 至少 3 条 RED 告警
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) >= 3

    def test_mixed_healthy_and_breach(self):
        """G3 健康 + G6 突破 → overall_pass=False，仅 G6 告警。"""
        gen = AlertGenerator()
        ai_mon = AiAgentMonitor()
        op_mon = OperationalRiskMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            ai_agent_monitor=ai_mon,
            operational_risk_monitor=op_mon,
        )

        # G3: STABLE（健康）
        orch.check_ai_agent(agent_metrics={"a": 0.5})
        # G6: severe failure
        orch.check_operational_risk(_make_stats(failure_rate=0.15, rejection_count=15))

        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        sources = {a.source for a in alerts}
        assert "operational_risk_monitor" in sources
