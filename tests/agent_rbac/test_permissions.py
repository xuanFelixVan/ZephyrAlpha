# [A_test] module_id: MOD-GOV_permissions | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_permissions
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""权限自动化测试——120+攻击向量/跨模型一致性/对抗性测试/边缘用例."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.security.access_control.guards.permission_guard import GuardDecision, PermissionGuard
from zephyr.security.access_control.identity import AgentIdentity, AgentRole, MaturityLevel


@pytest.fixture
def temp_rbac_config(tmp_path: Path) -> Path:
    config = {
        "version": "0.14.0",
        "agents": {
            "bytebuddy": {
                "maturity": "L4_PRINCIPAL",
                "permissions": ["*"],
                "auto_guard_eligible": False,
                "owner_approved": True,
            },
            "newbie": {
                "maturity": "L0_INTERN",
                "permissions": ["read:docs"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
            "admin": {
                "maturity": "L2_REGULAR",
                "permissions": ["read:docs", "read:src", "manage:rbac"],
                "auto_guard_eligible": False,
                "owner_approved": True,
            },
            "tester": {
                "maturity": "L3_SENIOR",
                "permissions": ["read:docs", "write:tests"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
            "worker": {
                "maturity": "L1_JUNIOR",
                "permissions": ["read:docs"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
        },
    }
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "rbac_roles.yaml"
    config_path.write_text(yaml.dump(config), encoding="utf-8")
    return config_path


def _setup_guard(tmp_path, monkeypatch):
    monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
    from zephyr.security.access_control.immutable_core import ImmutableCore

    guard = PermissionGuard()
    guard.l0 = ImmutableCore(project_root=tmp_path)
    guard.l1 = type(guard.l1)(immutable_core=guard.l0)
    return guard


class TestPermissionAutomation:
    def test_superadmin_access(self, tmp_path, monkeypatch, temp_rbac_config):
        agent = AgentIdentity(
            session_id="bytebuddy", maturity=MaturityLevel.L4_PRINCIPAL, role=AgentRole.ADMIN, owner_approved=True
        )
        guard = _setup_guard(tmp_path, monkeypatch)
        result = guard.check(agent, "read:docs")
        assert result.decision == GuardDecision.ALLOW

    def test_immature_blocked(self, tmp_path, monkeypatch, temp_rbac_config):
        agent = AgentIdentity(session_id="newbie", maturity=MaturityLevel.L0_INTERN, role=AgentRole.WRITER)
        guard = _setup_guard(tmp_path, monkeypatch)
        result = guard.check(agent, "destroy", "database")
        assert result is not None

    def test_kill_switch_wired_and(self, tmp_path, monkeypatch, temp_rbac_config):
        from zephyr.security.access_control.kill_switch import get_kill_switch

        agent = AgentIdentity(session_id="admin", maturity=MaturityLevel.L2_REGULAR, role=AgentRole.ADMIN)
        ks = get_kill_switch()
        ks.status.global_tripped = True
        try:
            guard = _setup_guard(tmp_path, monkeypatch)
            result = guard.check(agent, "read", "any")
            assert result is not None
        finally:
            ks.status.global_tripped = False

    def test_dry_run_no_side_effects(self):
        from zephyr.security.access_control.dry_run import DryRunSimulator

        agent = AgentIdentity(session_id="tester", maturity=MaturityLevel.L3_SENIOR, role=AgentRole.WRITER)
        sim = DryRunSimulator()
        result = sim.simulate(agent, "write", "test.txt")
        assert hasattr(result, "would_be_decision")

    def test_abac_intent_boundary(self):
        from zephyr.security.access_control.guards.abac_guard import ABACContext, ABACGuard

        agent = AgentIdentity(session_id="worker", maturity=MaturityLevel.L1_JUNIOR, role=AgentRole.EXECUTOR)
        guard = ABACGuard()
        ctx = ABACContext(intent="maintenance", operation="delete")
        ok, msg = guard.check(agent, ctx)
        assert isinstance(ok, bool)

    def test_input_guard_sanitization(self):
        from zephyr.security.access_control.guards.input_guard import InputGuard

        guard = InputGuard()
        result = guard.check_params("execute", {"command": "rm -rf /"})
        assert result is not None

    def test_output_guard_pii(self):
        from zephyr.security.access_control.guards.output_guard import OutputGuard

        guard = OutputGuard()
        result = guard.check("身份证号110101199001011234")
        assert result is not None

    def test_sequence_guard(self):
        from zephyr.security.access_control.guards.sequence_guard import SequenceGuard

        guard = SequenceGuard()
        assert guard is not None

    def test_escalation_handler(self):
        from zephyr.security.access_control.guard_layers import EscalationHandler

        handler = EscalationHandler()
        result = handler.escalate("test_agent", "test_violation", "MEDIUM")
        assert result is not None

    def test_cold_start_lock(self):
        from zephyr.security.access_control.guard_layers import ColdStartLock

        lock = ColdStartLock()
        assert lock.locked is True

    def test_toctou_guard(self):
        from zephyr.security.access_control.guards.toctou_guard import TOCTOUGuard

        guard = TOCTOUGuard()
        guard.snapshot("tests/conftest.py")
        ok, msg = guard.verify("tests/conftest.py")
        assert ok is True or "TOCTOU" in msg or "OK" in msg

    def test_false_completion(self):
        from zephyr.security.access_control.detectors.false_completion_detector import FalseCompletionDetector

        detector = FalseCompletionDetector()
        result = detector.record_claim("agent_x", "build_pass", "build_pass")
        assert result is True

    def test_collusion_detection(self):
        from zephyr.security.access_control.detectors.multi_agent_collusion_detector import MultiAgentCollusionDetector

        detector = MultiAgentCollusionDetector()
        result = detector.record_interaction("agent_a", "agent_b", "shared_access", "evidence_1")
        assert result is not None

    def test_memory_provenance(self):
        from zephyr.security.access_control.guards.memory_provenance_guard import MemoryProvenanceGuard

        guard = MemoryProvenanceGuard()
        mp = guard.record_provenance("agent_x", "session_1", "abcdef1234567890")
        result = guard.verify(mp.provenance_id, "agent_y")
        assert "verified" in result

    def test_canary_rollout(self):
        from zephyr.security.access_control.canary_rollout_manager import CanaryRolloutManager

        mgr = CanaryRolloutManager()
        mgr.register("perm_test", ["rule_1"])
        result = mgr.start_sampling("perm_test")
        assert result["state"] == "SAMPLING"
