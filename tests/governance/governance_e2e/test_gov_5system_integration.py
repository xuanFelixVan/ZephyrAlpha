# [A_test] module_id: MOD-GOV_gov_integration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-291 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gov_5system_integration
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-291 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
G-CT-009: Five-System Governance Discovery Integration Test — MOD-INF-021~025

Verifies all 5 foundational governance modules are discoverable and functional
through the governance namespace. Ensures no system is orphaned.

Systems tested:
  - escalation-protocol (MOD-INF-022, v0.14.0)
  - budget-enforcer      (MOD-INF-024, v0.7.0)
  - drift-detector       (MOD-INF-023, v1.0.0)
  - rollback-system      (MOD-INF-021, v0.10.0)
  - a2a-protocol         (MOD-INF-025, HOLD)

Usage:
    python -m pytest tests/governance/test_gov_5system_integration.py -v
"""

import pytest

MODULE_VERSIONS = {
    "escalation_protocol": "0.14.0",
    "budget_enforcer_mod": "0.8.0",
    "drift_detector_mod": "1.0.0",
    "rollback_mod": "0.10.0",
}


class TestFiveSystemDiscovery:
    def test_all_modules_importable(self):
        from zephyr.governance import (
            a2a_protocol,
            budget_enforcer_mod,
            drift_detector_mod,
            escalation_protocol,
            rollback_mod,
        )

        assert escalation_protocol is not None
        assert budget_enforcer_mod is not None
        assert drift_detector_mod is not None
        assert rollback_mod is not None
        assert a2a_protocol is not None

    @pytest.mark.parametrize(
        "mod_name,expected_version",
        [
            ("escalation_protocol", "0.14.0"),
            ("budget_enforcer_mod", "0.8.0"),
            ("drift_detector_mod", "1.0.0"),
            ("rollback_mod", "0.10.0"),
        ],
    )
    def test_versions_match_blueprint(self, mod_name, expected_version):
        from zephyr.governance import (
            budget_enforcer_mod,
            drift_detector_mod,
            escalation_protocol,
            rollback_mod,
        )

        mods = {
            "escalation_protocol": escalation_protocol,
            "budget_enforcer_mod": budget_enforcer_mod,
            "drift_detector_mod": drift_detector_mod,
            "rollback_mod": rollback_mod,
        }
        assert mods[mod_name].__version__ == expected_version, (
            f"{mod_name}: expected {expected_version}, got {mods[mod_name].__version__}"
        )

    def test_escalation_engine_functional(self):
        from zephyr.governance.escalation.escalation_engine import EscalationEngine, RuleCategory

        e = EscalationEngine("gct009-test")
        ev = e.evaluate(RuleCategory.AUTO_GUARD_FAILURE, "test guard failure")
        assert ev.level.value <= 4
        assert e.circuit_breaker.state.name == "CLOSED"
        assert len(e.rules) >= 9

    def test_budget_engine_functional(self):
        from zephyr.governance.ops_governance.budget_engine import BudgetEngine

        be = BudgetEngine()
        r = be.pre_flight_check("gct009-req", 1000, 0.1)
        assert r.decision.name == "ALLOW"
        assert r.budget_level.name == "L0_NORMAL"

    def test_cross_system_escalation_chain(self):
        from zephyr.governance.escalation.escalation_engine import EscalationEngine, RuleCategory
        from zephyr.governance.ops_governance.budget_engine import BudgetEngine

        e = EscalationEngine("chain-test")
        be = BudgetEngine()
        r = be.pre_flight_check("chain-req", 1000, 0.1)
        assert r.decision.name == "ALLOW"
        ev = e.evaluate(RuleCategory.BUDGET_EXCEEDED, "test budget escalation", "agent-1")
        result = e.escalate(ev)
        assert result.escalated

    def test_a2a_hold_status(self):
        import zephyr.infrastructure.a2a_protocol as a2a

        assert a2a is not None
