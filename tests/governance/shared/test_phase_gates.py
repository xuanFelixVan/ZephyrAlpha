# [A_test] module_id: SRC-TST-0142 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-299 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_phase_gates
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Phase Gates + 依赖审计隔离 + A2A Phase 4 Hold 测试."""

from __future__ import annotations

import pytest

from zephyr.infrastructure.a2a_protocol.phase_hold import Phase4Hold
from zephyr.security.access_control.bootstrap_superadmin import BootstrapSuperadmin


class TestPhase1GateCheck:
    def test_bootstrap_superadmin(self):
        admin = BootstrapSuperadmin()
        result = admin.bootstrap()
        assert result["bootstrapped"] is True
        assert result["account"] == "bytebuddy"

    def test_superadmin_check_granted(self):
        admin = BootstrapSuperadmin()
        result = admin.check("read", "config.yml")
        assert result["granted"] is True

    def test_superadmin_check_denied(self):
        admin = BootstrapSuperadmin()
        result = admin.check("unknown_permission", "secret.yml")
        assert result["granted"] is False


class TestPhase2GateCheck:
    def test_superadmin_has_all_roles(self):
        admin = BootstrapSuperadmin()
        assert len(admin.roles) == 4
        assert "superadmin" in admin.roles
        assert "auditor" in admin.roles


class TestPhase3GateCheck:
    def test_superadmin_capabilities(self):
        admin = BootstrapSuperadmin()
        assert len(admin.capabilities) == 7
        assert "escalate" in admin.capabilities
        assert "rollback" in admin.capabilities


class TestCycleDependencyAuditIsolation:
    def test_no_cycle_in_imports(self):
        try:
            from zephyr.governance.escalation.contracts import EscalationContracts

            contracts = EscalationContracts()
            assert contracts is not None
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")


class TestA2APhase4Hold:
    def test_phase4_hold_active(self):
        hold = Phase4Hold()
        status = hold.check()
        assert status["hold_active"] is True

    def test_can_proceed_phase4(self):
        hold = Phase4Hold()
        assert hold.can_proceed("Phase4") is True

    def test_cannot_proceed_phase3(self):
        hold = Phase4Hold()
        assert hold.can_proceed("Phase3") is False


class TestP0ContractSmoke:
    def test_rollback_result_types_smoke(self):
        from zephyr.governance.escalation.result_types import RollbackResult as RR

        rr = RR(rollback_id="SMOKE-1", target="test")
        assert rr.rollback_id == "SMOKE-1"

    def test_budget_alert_smoke(self):
        from zephyr.governance.bridges.alerts import BudgetAlert

        alert = BudgetAlert(alert_id="SMOKE-1", burn_rate=0.5)
        assert alert.burn_rate == 0.5

    def test_a2a_comm_smoke(self):
        from zephyr.infrastructure.a2a_protocol import A2ACommunication

        comm = A2ACommunication(a2a_id="SMOKE", from_agent_id="a", to_agent_id="b")
        assert comm.a2a_id == "SMOKE"

    def test_registry_smoke(self):
        from zephyr.autonomy_core.skill_rbac_registry import AgentCapability

        cap = AgentCapability(agent_id="test", claimed_capabilities=["read"])
        assert cap.agent_id == "test"


class TestP0InputValidation:
    def test_rollback_result_status_enum(self):
        from zephyr.governance.escalation.result_types import RollbackStatus

        assert RollbackStatus.SUCCESS.value == "SUCCESS"
        assert RollbackStatus.FAILED.value == "FAILED"

    def test_drift_type_enum(self):
        from zephyr.gov_drift.events import DriftType

        assert DriftType.CODE_DIVERGENCE.value == "CODE_DIVERGENCE"

    def test_budget_alert_from_burn_rate_validation(self):
        from zephyr.governance.bridges.alerts import BudgetAlert, BudgetSeverity

        alert = BudgetAlert.from_burn_rate("B-1", burn_rate=1.5, threshold=0.8, remaining=-100)
        assert alert.severity == BudgetSeverity.CRITICAL
