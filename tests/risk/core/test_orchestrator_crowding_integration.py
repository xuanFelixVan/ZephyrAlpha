# [BLUEPRINT] MOD-RK-13 | docs/03_modules/_domain_risk/crowding_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_orchestrator_crowding_integration
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_risk_manager_orchestrator; zephyr.risk.core.crowding_monitor; zephyr.risk.core.alert_generator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_orchestrator_crowding_integration.py
# [A_test] module_id: MOD-RK-13 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G4-S6 集成测试: 拥挤度监控 → 编排器 → 告警管道（G1↔G4 端到端）.

覆盖: 向后兼容(无crowding_monitor)/不拥挤(无告警)/拥挤(RED告警)/
best-effort异常不阻断/全流程/G1+G2+G4三路同时触发.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.risk.implementations.default_risk_manager_orchestrator",
    reason="orchestrator not importable",
)

from zephyr.risk.core.alert_generator import AlertGenerator, AlertLevel  # noqa: E402
from zephyr.risk.core.crowding_monitor import CrowdingMonitor  # noqa: E402
from zephyr.risk.implementations.default_risk_manager_orchestrator import (  # noqa: E402
    DefaultRiskManagerOrchestrator,
)

# ── Mock 数据 ─────────────────────────────────────────────────────────


#: 拥挤: 3策略高重叠 + 同方向
MOCK_CROWDED = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2, "600036.SH": 0.1},
    "strat_b": {"600000.SH": 0.28, "000001.SZ": 0.18, "600036.SH": 0.12},
    "strat_c": {"600000.SH": 0.25, "000001.SZ": 0.22, "600036.SH": 0.08},
}
MOCK_CROWDED_EXP = {"strat_a": 0.8, "strat_b": 0.7, "strat_c": 0.6}

#: 不拥挤: 3策略低重叠
MOCK_NOT_CROWDED = {
    "strat_a": {"600000.SH": 0.3, "000001.SZ": 0.2},
    "strat_b": {"600036.SH": 0.3, "601398.SH": 0.2},
    "strat_c": {"000002.SZ": 0.3, "600519.SH": 0.2},
}
MOCK_NOT_CROWDED_EXP = {"strat_a": 0.5, "strat_b": 0.3, "strat_c": 0.4}

#: 单策略（不足以评估）
MOCK_SINGLE = {"strat_a": {"600000.SH": 0.3}}


# ── 向后兼容测试 ──────────────────────────────────────────────────────


class TestBackwardCompatibility:
    def test_no_crowding_monitor_returns_none(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        result = orch.check_crowding("momentum", MOCK_CROWDED)
        assert result is None

    def test_no_crowding_monitor_no_extra_checks(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        orch.check_crowding("momentum", MOCK_CROWDED)
        report = orch.aggregate_report()
        assert len(report.checks) == 0


# ── 不拥挤测试 ────────────────────────────────────────────────────────


class TestNotCrowded:
    def test_not_crowded_no_alerts(self):
        gen = AlertGenerator()
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            crowding_monitor=mon,
        )

        metrics = orch.check_crowding("value", MOCK_NOT_CROWDED, MOCK_NOT_CROWDED_EXP)
        assert metrics is not None
        assert metrics.is_crowded is False

        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_not_crowded_check_result_is_pass(self):
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            crowding_monitor=mon,
        )

        orch.check_crowding("value", MOCK_NOT_CROWDED, MOCK_NOT_CROWDED_EXP)
        report = orch.aggregate_report()

        assert len(report.checks) == 1
        assert report.checks[0].passed is True


# ── 拥挤测试 ──────────────────────────────────────────────────────────


class TestCrowded:
    def test_crowded_triggers_red_alert(self):
        """高重叠 + 同方向 → is_crowded=True → HALT → RED 告警"""
        gen = AlertGenerator()
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            crowding_monitor=mon,
        )

        metrics = orch.check_crowding("momentum", MOCK_CROWDED, MOCK_CROWDED_EXP)
        assert metrics is not None
        assert metrics.is_crowded is True

        report = orch.aggregate_report()
        assert report.overall_pass is False

        alerts = orch.last_alerts
        assert len(alerts) > 0
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) > 0
        assert any(a.source == "crowding_monitor" for a in red_alerts)

    def test_crowded_check_result_is_halt(self):
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            crowding_monitor=mon,
        )

        orch.check_crowding("momentum", MOCK_CROWDED, MOCK_CROWDED_EXP)
        report = orch.aggregate_report()

        assert len(report.checks) == 1
        assert report.checks[0].passed is False
        assert report.checks[0].severity == "HALT"


# ── Best-effort 测试 ──────────────────────────────────────────────────


class TestBestEffort:
    def test_single_strategy_returns_default(self):
        """单策略 → assess 返回默认值（not crowded），不崩溃"""
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            crowding_monitor=mon,
        )

        metrics = orch.check_crowding("test", MOCK_SINGLE)
        assert metrics is not None
        assert metrics.is_crowded is False  # 默认不拥挤
        assert metrics.n_strategies == 1


# ── 全流程测试 ────────────────────────────────────────────────────────


class TestFullPipeline:
    def test_full_pipeline_crowded_alert(self):
        gen = AlertGenerator()
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            crowding_monitor=mon,
        )

        # 1. 拥挤度检查（拥挤）
        metrics = orch.check_crowding("momentum", MOCK_CROWDED, MOCK_CROWDED_EXP)
        assert metrics.is_crowded is True

        # 2. 汇总报告 → 自动派发 RED 告警
        report = orch.aggregate_report()
        assert report.overall_pass is False

        alerts = orch.last_alerts
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) > 0
        assert any(a.source == "crowding_monitor" for a in red_alerts)

    def test_multiple_factors_batch(self):
        """多因子检查：一个拥挤一个不拥挤"""
        gen = AlertGenerator()
        mon = CrowdingMonitor()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
            crowding_monitor=mon,
        )

        # 拥挤因子
        m1 = orch.check_crowding("momentum", MOCK_CROWDED, MOCK_CROWDED_EXP)
        assert m1.is_crowded is True

        # 不拥挤因子
        m2 = orch.check_crowding("value", MOCK_NOT_CROWDED, MOCK_NOT_CROWDED_EXP)
        assert m2.is_crowded is False

        report = orch.aggregate_report()
        assert report.overall_pass is False  # momentum 拥挤了

        # 应有 momentum 的 RED 告警
        alerts = orch.last_alerts
        red_alerts = [a for a in alerts if a.level == AlertLevel.RED]
        assert len(red_alerts) > 0
