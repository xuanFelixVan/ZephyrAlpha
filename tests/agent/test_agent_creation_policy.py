# [A_test] module_id: MOD-GOV_agent_creation_policy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.test_agent_creation_policy
# [INVARIANTS] test_coverage>=2_public_methods;boundary_tests_included
# [MODIFY-GUARD] sync_with_source_on_refactor
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0_on_pass
# [TESTS] tests/test_agent_creation_policy.py
# [TTL] task_bound

from __future__ import annotations

import time
from typing import Any

from zephyr.security.access_control.agent_creation_policy import AgentCreationPolicy, CreationPolicy


class TestCreationPolicyModel:
    def test_default_fields(self):
        p = CreationPolicy(
            parent_agent_id="a1",
            parent_maturity="MATURE",
            parent_capability_count=5,
        )
        assert p.max_children == 10
        assert p.spawn_window_seconds == 300
        assert p.decay_factor == 0.7

    def test_custom_fields(self):
        p = CreationPolicy(
            parent_agent_id="a2",
            parent_maturity="PROVEN",
            parent_capability_count=3,
            max_children=2,
            spawn_window_seconds=60,
            decay_factor=0.5,
        )
        assert p.max_children == 2
        assert p.spawn_window_seconds == 60


class TestAgentCreationPolicy:
    def setup_method(self):
        self.policy_engine = AgentCreationPolicy()

    def _make_policy(self, **overrides: Any) -> CreationPolicy:
        defaults = dict(
            parent_agent_id="agent-1",
            parent_maturity="MATURE",
            parent_capability_count=5,
        )
        defaults.update(overrides)
        return CreationPolicy(**defaults)

    def test_can_create_allowed_initially(self):
        p = self._make_policy()
        result = self.policy_engine.can_create(p)
        assert result["allowed"] is True
        assert result["parent_agent_id"] == "agent-1"

    def test_can_create_blocked_after_max_children(self):
        p = self._make_policy(max_children=2, spawn_window_seconds=600)
        self.policy_engine.record_spawn("agent-1")
        self.policy_engine.record_spawn("agent-1")
        result = self.policy_engine.can_create(p)
        assert result["allowed"] is False
        assert result["reason"] == "spawn_storm_detected"
        assert result["recent_spawns"] == 2

    def test_can_create_resets_after_window(self):
        p = self._make_policy(max_children=1, spawn_window_seconds=1)
        self.policy_engine.record_spawn("agent-1")
        time.sleep(1.1)
        result = self.policy_engine.can_create(p)
        assert result["allowed"] is True

    def test_get_child_maturity_decay(self):
        assert self.policy_engine.get_child_maturity("MATURE") == "ADOLESCENT"
        assert self.policy_engine.get_child_maturity("ADOLESCENT") == "IMMATURE"
        assert self.policy_engine.get_child_maturity("PROVEN") == "MATURE"
        assert self.policy_engine.get_child_maturity("SUPERADMIN") == "PROVEN"

    def test_get_child_maturity_immature_floor(self):
        assert self.policy_engine.get_child_maturity("IMMATURE") == "IMMATURE"

    def test_get_child_maturity_unknown(self):
        assert self.policy_engine.get_child_maturity("UNKNOWN_LEVEL") == "IMMATURE"

    def test_get_child_maturity_none_like(self):
        assert self.policy_engine.get_child_maturity("") == "IMMATURE"

    def test_get_child_capabilities_decay(self):
        caps = ["read", "write", "delete", "admin", "super"]
        result = self.policy_engine.get_child_capabilities(caps)
        assert len(result) == 3
        assert result == ["read", "write", "delete"]

    def test_get_child_capabilities_single(self):
        result = self.policy_engine.get_child_capabilities(["only_one"])
        assert result == ["only_one"]

    def test_get_child_capabilities_empty(self):
        result = self.policy_engine.get_child_capabilities([])
        assert result == []

    def test_record_spawn_creates_entry(self):
        self.policy_engine.record_spawn("new-agent")
        assert "new-agent" in self.policy_engine._child_counts
        assert len(self.policy_engine._child_counts["new-agent"]) == 1

    def test_record_spawn_appends(self):
        self.policy_engine.record_spawn("agent-x")
        self.policy_engine.record_spawn("agent-x")
        assert len(self.policy_engine._child_counts["agent-x"]) == 2

    def test_can_create_different_agents_independent(self):
        p1 = self._make_policy(parent_agent_id="a1", max_children=1)
        p2 = self._make_policy(parent_agent_id="a2", max_children=1)
        self.policy_engine.record_spawn("a1")
        r1 = self.policy_engine.can_create(p1)
        r2 = self.policy_engine.can_create(p2)
        assert r1["allowed"] is False
        assert r2["allowed"] is True
