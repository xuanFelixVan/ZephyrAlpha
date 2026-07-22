# [A_test] module_id: MOD-GOV_phase_hold | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_phase_hold
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

ph = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.phase_hold",
    reason="phase_hold module not available",
)


class TestPhase4Hold:
    def test_instantiation(self):
        obj = ph.Phase4Hold()
        assert obj is not None
        assert obj.hold_active is True

    def test_check_returns_dict(self):
        obj = ph.Phase4Hold()
        result = obj.check()
        assert isinstance(result, dict)
        assert "hold_active" in result
        assert "reason" in result
        assert "hold_since" in result
        assert result["hold_active"] is True

    def test_can_proceed_phase4(self):
        obj = ph.Phase4Hold()
        assert obj.can_proceed("Phase4") is True
        assert obj.can_proceed("phase4") is True
        assert obj.can_proceed("4") is True

    def test_can_proceed_other_phases(self):
        obj = ph.Phase4Hold()
        assert obj.can_proceed("Phase3") is False
        assert obj.can_proceed("phase2") is False
        assert obj.can_proceed("1") is False

    def test_can_proceed_empty_string(self):
        obj = ph.Phase4Hold()
        assert obj.can_proceed("") is False

    def test_hold_since_is_iso_format(self):
        obj = ph.Phase4Hold()
        result = obj.check()
        assert "T" in result["hold_since"] or "-" in result["hold_since"]
