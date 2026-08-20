# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md | §test
# [MODULE] tests.risk.core.test_orchestrator_alert_integration
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_risk_manager_orchestrator; zephyr.risk.core.alert_generator
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_orchestrator_alert_integration.py
# [A_test] module_id: MOD-RK-06 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G1-S6 集成测试: DefaultRiskManagerOrchestrator ↔ AlertGenerator.

覆盖: 向后兼容(无 alert_generator)/正常派发/kill_switch 场景/
best-effort 异常不阻断/last_alerts 属性/全流程.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.implementations.default_risk_manager_orchestrator",
    reason="orchestrator not importable",
)

from zephyr.risk.core.alert_generator import Alert, AlertGenerator, AlertLevel  # noqa: E402
from zephyr.risk.implementations.default_risk_manager_orchestrator import (  # noqa: E402
    DefaultRiskManagerOrchestrator,
)
from zephyr.risk.risk_manager_base import RiskCheckResult  # noqa: E402


class TestBackwardCompatibility:
    """无 alert_generator 时，编排器行为与修改前完全一致。"""

    def test_no_alert_generator_no_alerts(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_no_alert_generator_returns_report_normally(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="p1")
        # 模拟一个失败的检查
        orch._check_results.append(
            RiskCheckResult(
                check_id="c1",
                rule_name="position_limit",
                passed=False,
                limit_value=Decimal("0.10"),
                actual_value=Decimal("0.25"),
                severity="HALT",
            )
        )
        report = orch.aggregate_report()
        assert report.overall_pass is False
        assert orch.last_alerts == []  # 无 alert_generator → 不派发


class TestAlertDispatch:
    """有 alert_generator 时，aggregate_report 自动派发告警。"""

    def test_clean_report_no_alerts(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )
        report = orch.aggregate_report()
        assert report.overall_pass is True
        assert orch.last_alerts == []

    def test_halt_violation_dispatches_red_alert(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )
        orch._check_results.append(
            RiskCheckResult(
                check_id="c1",
                rule_name="position_limit",
                passed=False,
                limit_value=Decimal("0.10"),
                actual_value=Decimal("0.25"),
                severity="HALT",
                message="position limit breached",
            )
        )
        report = orch.aggregate_report()
        assert report.overall_pass is False
        alerts = orch.last_alerts
        assert len(alerts) >= 1
        assert any(a.level == AlertLevel.RED for a in alerts)

    def test_warning_dispatches_orange_alert(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )
        orch._check_results.append(
            RiskCheckResult(
                check_id="c1",
                rule_name="drawdown",
                passed=False,
                limit_value=Decimal("0.05"),
                actual_value=Decimal("0.08"),
                severity="WARNING",
                message="drawdown approaching limit",
            )
        )
        report = orch.aggregate_report()
        assert report.overall_pass is False  # failed check → overall_pass=False (regardless of severity)
        alerts = orch.last_alerts
        assert len(alerts) >= 1
        assert any(a.level == AlertLevel.ORANGE for a in alerts)

    def test_kill_switch_dispatches_red_alert(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )
        # 模拟 kill switch 触发
        orch._validator.trigger_kill_switch()
        orch._check_results.append(
            RiskCheckResult(
                check_id="c1",
                rule_name="daily_pnl_check",
                passed=False,
                limit_value=Decimal("-50000"),
                actual_value=Decimal("-60000"),
                severity="HALT",
                message="daily loss limit breached",
            )
        )
        report = orch.aggregate_report()
        assert report.kill_switch_active is True
        alerts = orch.last_alerts
        assert any(a.level == AlertLevel.RED for a in alerts)
        assert any(a.source == "kill_switch" for a in alerts)

    def test_mixed_scenario_multiple_alerts(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )
        orch._check_results.extend(
            [
                RiskCheckResult(
                    check_id="c1",
                    rule_name="position_limit",
                    passed=False,
                    limit_value=Decimal("0.10"),
                    actual_value=Decimal("0.25"),
                    severity="HALT",
                    message="position limit breached",
                ),
                RiskCheckResult(
                    check_id="c2",
                    rule_name="drawdown",
                    passed=False,
                    limit_value=Decimal("0.05"),
                    actual_value=Decimal("0.08"),
                    severity="WARNING",
                    message="drawdown approaching limit",
                ),
                RiskCheckResult(
                    check_id="c3",
                    rule_name="leverage",
                    passed=True,
                    limit_value=Decimal("1.5"),
                    actual_value=Decimal("1.2"),
                    severity="info",
                ),
            ]
        )
        report = orch.aggregate_report()
        alerts = orch.last_alerts
        levels = {a.level for a in alerts}
        assert AlertLevel.RED in levels
        assert AlertLevel.ORANGE in levels


class TestBestEffort:
    """告警派发异常不阻断 aggregate_report。"""

    def test_alert_generator_exception_does_not_block(self):
        class _FailingGenerator(AlertGenerator):
            def process(self, report):
                raise RuntimeError("generator broken")

        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=_FailingGenerator(),
        )
        orch._check_results.append(
            RiskCheckResult(
                check_id="c1",
                rule_name="position_limit",
                passed=False,
                limit_value=Decimal("0.10"),
                actual_value=Decimal("0.25"),
                severity="HALT",
            )
        )
        # Should NOT raise
        report = orch.aggregate_report()
        assert report is not None
        assert report.overall_pass is False
        assert orch.last_alerts == []  # failed → empty


class TestFullPipeline:
    """完整流程: 事前检查 → 事后检查 → 日终检查 → 汇总报告 → 告警派发。"""

    def test_full_pipeline_with_alerts(self):
        gen = AlertGenerator()
        orch = DefaultRiskManagerOrchestrator(
            portfolio_id="p1",
            alert_generator=gen,
        )

        # 1. 事前检查通过
        from zephyr.shared.contracts.risk_limits import RiskLimits

        limits = RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="ik-test",
            max_single_position=0.10,
            max_gross_leverage=1.5,
        )

        class _MockOrder:
            symbol = "600000.SH"
            quantity = 0.05

        orch.pre_trade_check(_MockOrder(), limits, [])
        assert orch.aggregate_report().overall_pass is True
        assert orch.last_alerts == []  # clean

        # 2. 日终检查失败（触发 kill switch）
        orch.daily_pnl_check(
            daily_pnl=Decimal("-60000"),
            loss_limit=Decimal("50000"),
        )

        # 3. 汇总报告应自动派发 RED 告警
        report = orch.aggregate_report()
        assert report.overall_pass is False
        assert report.kill_switch_active is True

        alerts = orch.last_alerts
        assert len(alerts) > 0
        assert any(a.level == AlertLevel.RED for a in alerts)
