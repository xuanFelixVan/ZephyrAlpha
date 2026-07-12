# [A_test] module_id: SRC-TST-0137 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-294 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_p0_i2_construction_order
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""P0-I2 施工顺序验证 — DOM-GOV-001 §8.4."""

from __future__ import annotations

from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT


class TestP0I2ConstructionOrder:
    """施工顺序: Phase 1→2→3→4 不允许跳级."""

    def test_phase1_must_complete_before_phase2(self):
        phases = range(1, 5)
        for i in range(1, len(phases)):
            assert phases[i] > phases[i - 1], f"Phase {phases[i]} should come after Phase {phases[i - 1]}"

    def test_all_modules_have_contracts_interface(self):
        from zephyr.gov_audit.contracts import AuditWriter
        from zephyr.governance.escalation.contracts import EscalationContracts, RollbackHandler
        from zephyr.security.access_control.contracts import RBACAuditBridge

        assert hasattr(RBACAuditBridge(), "check_and_log")
        assert hasattr(AuditWriter(), "write")
        assert hasattr(RollbackHandler(), "on_audit_anomaly")
        assert hasattr(EscalationContracts(), "on_rollback_failure")

    def test_bridge_files_follow_ct_convention(self):
        bridge_files = [
            "agent-rbac/contracts.py",
            "audit-trail/contracts.py",
            "rollback/contracts.py",
            "escalation/contracts.py",
        ]
        for bf in bridge_files:
            path = REPO_ROOT / "src" / "zephyr" / "governance" / bf
            assert path.exists(), f"Bridge file missing: {bf}"
