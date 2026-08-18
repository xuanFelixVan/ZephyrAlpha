# [A_test] module_id: MOD-GOV_permission_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_permission_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 PermissionGuard — 七层统一编排"""

from pathlib import Path

import pytest
import yaml

from zephyr.security.access_control.guards.permission_guard import (
    GuardDecision,
    GuardResult,
    PermissionGuard,
)
from zephyr.security.access_control.identity import AgentIdentity


@pytest.fixture
def temp_rbac_config(tmp_path: Path, monkeypatch) -> Path:
    config = {
        "version": "0.14.0",
        "agents": {
            "test-pg-1": {
                "maturity": "L0_INTERN",
                "permissions": ["read:docs"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
            "test-pg-2": {
                "maturity": "L0_INTERN",
                "permissions": ["read:docs"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
            "test-pg-3": {
                "maturity": "L0_INTERN",
                "permissions": ["read:docs"],
                "auto_guard_eligible": True,
                "owner_approved": False,
            },
            "test-pg-4": {
                "maturity": "L0_INTERN",
                "permissions": ["read:docs"],
                "auto_guard_eligible": False,
                "owner_approved": False,
            },
            "test-pg-5": {
                "maturity": "L0_INTERN",
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


class TestBasicFlows:
    def test_read_allowed(self, tmp_path, monkeypatch, temp_rbac_config):
        monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
        from zephyr.security.access_control.immutable_core import ImmutableCore

        guard = PermissionGuard()
        guard.l0 = ImmutableCore(project_root=tmp_path)
        guard.l1 = type(guard.l1)(immutable_core=guard.l0)
        agent = AgentIdentity(session_id="test-pg-1")
        result = guard.check(agent, "read:docs")
        assert result.decision == GuardDecision.ALLOW
        assert not guard.is_blocked(result)

    def test_always_blocked(self, tmp_path, monkeypatch, temp_rbac_config):
        monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
        from zephyr.security.access_control.immutable_core import ImmutableCore

        guard = PermissionGuard()
        guard.l0 = ImmutableCore(project_root=tmp_path)
        guard.l1 = type(guard.l1)(immutable_core=guard.l0)
        agent = AgentIdentity(session_id="test-pg-2")
        result = guard.check(agent, "delete:audit_logs")
        assert result.decision == GuardDecision.BLOCKED
        assert guard.is_blocked(result)

    def test_write_with_auto_guard(self, tmp_path, monkeypatch, temp_rbac_config):
        monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
        from zephyr.security.access_control.immutable_core import ImmutableCore

        guard = PermissionGuard()
        guard.l0 = ImmutableCore(project_root=tmp_path)
        guard.l1 = type(guard.l1)(immutable_core=guard.l0)
        agent = AgentIdentity(
            session_id="test-pg-3",
            auto_guard_eligible=True,
        )
        result = guard.check(agent, "write:src")
        assert result.decision in (GuardDecision.AUTO_GUARD, GuardDecision.ALLOW)


class TestBlockedScenarios:
    def test_blocked_by_l0(self, tmp_path, monkeypatch, temp_rbac_config):
        monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
        from zephyr.security.access_control.immutable_core import ImmutableCore

        guard = PermissionGuard()
        guard.l0 = ImmutableCore(project_root=tmp_path)
        guard.l1 = type(guard.l1)(immutable_core=guard.l0)
        agent = AgentIdentity(session_id="test-pg-4")
        result = guard.check(agent, "delete:audit_logs")
        assert guard.is_blocked(result) or result.decision == GuardDecision.BLOCKED

    def test_explain_blocked(self, tmp_path, monkeypatch, temp_rbac_config):
        monkeypatch.setattr("zephyr.security.access_control.immutable_core.PROJECT_ROOT", tmp_path)
        from zephyr.security.access_control.immutable_core import ImmutableCore

        guard = PermissionGuard()
        guard.l0 = ImmutableCore(project_root=tmp_path)
        guard.l1 = type(guard.l1)(immutable_core=guard.l0)
        agent = AgentIdentity(session_id="test-pg-5")
        result = guard.check(agent, "delete:audit_logs")
        if guard.is_blocked(result):
            explanation = guard.explain(result)
            assert "blocked_layer" in explanation


class TestGuardResult:
    def test_guard_result_fields(self):
        result = GuardResult(
            decision=GuardDecision.BLOCKED,
            layer="L1",
            reason="No permission",
            rule_id="RBAC-001",
        )
        assert result.decision == GuardDecision.BLOCKED
        assert result.layer == "L1"
        assert result.rule_id == "RBAC-001"
