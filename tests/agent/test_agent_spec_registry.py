# [A_test] module_id: MOD-GOV_agent_spec_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_agent_spec_registry
# [INVARIANTS] SpecRegistry entries keyed by agent_id; register overwrites existing
# [MODIFY-GUARD] Changes must sync with agent-spec/registry.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_agent_spec_registry.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.autonomy_core.skill_rbac_registry import (
    AgentCapability,
    SpecRegistry,
)


class TestAgentCapability:
    def test_creation_defaults(self):
        cap = AgentCapability(agent_id="test-agent")
        assert cap.agent_id == "test-agent"
        assert cap.capabilities == []
        assert cap.version == "1.0.0"
        assert cap.spec_hash == ""

    def test_creation_with_values(self):
        cap = AgentCapability(
            agent_id="my-agent",
            capabilities=["read", "write"],
            version="2.0.0",
            spec_hash="abc123",
        )
        assert cap.capabilities == ["read", "write"]
        assert cap.version == "2.0.0"
        assert cap.spec_hash == "abc123"

    def test_empty_capabilities_list(self):
        cap = AgentCapability(agent_id="empty")
        assert len(cap.capabilities) == 0


class TestSpecRegistry:
    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_register_and_get(self):
        reg = SpecRegistry()
        cap = AgentCapability(agent_id="agent-1", capabilities=["skill-a"])
        reg.register(cap)
        result = reg.get("agent-1")
        assert result is not None
        assert result.agent_id == "agent-1"

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_get_nonexistent_returns_none(self):
        reg = SpecRegistry()
        assert reg.get("no-such-agent") is None

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_register_overwrites(self):
        reg = SpecRegistry()
        cap1 = AgentCapability(agent_id="a", version="1.0.0")
        cap2 = AgentCapability(agent_id="a", version="2.0.0")
        reg.register(cap1)
        reg.register(cap2)
        assert reg.get("a").version == "2.0.0"

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_all_empty(self):
        reg = SpecRegistry()
        assert reg.list_all() == []

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_all_with_entries(self):
        reg = SpecRegistry()
        reg.register(AgentCapability(agent_id="x", capabilities=["name-x", "domain"]))
        reg.register(AgentCapability(agent_id="y", capabilities=["name-y", "role"]))
        result = reg.list_all()
        assert len(result) == 2
        ids = {r["skill_id"] for r in result}
        assert ids == {"x", "y"}

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_by_category(self):
        reg = SpecRegistry()
        reg.register(AgentCapability(agent_id="d1", capabilities=["name", "domain"]))
        reg.register(AgentCapability(agent_id="r1", capabilities=["name", "role"]))
        domain_entries = reg.list_by_category("domain")
        role_entries = reg.list_by_category("role")
        assert len(domain_entries) == 1
        assert len(role_entries) == 1

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_all_entry_structure(self):
        reg = SpecRegistry()
        reg.register(AgentCapability(agent_id="z", capabilities=["z-name", "domain", "extra"], version="3.0.0"))
        entries = reg.list_all()
        entry = entries[0]
        assert entry["skill_id"] == "z"
        assert entry["name"] == "z-name"
        assert entry["category"] == "domain"
        assert entry["version"] == "3.0.0"

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_all_empty_capabilities_uses_agent_id_as_name(self):
        reg = SpecRegistry()
        reg.register(AgentCapability(agent_id="bare", capabilities=[]))
        entries = reg.list_all()
        assert entries[0]["name"] == "bare"
        assert entries[0]["category"] == "unknown"

    @patch.object(SpecRegistry, "_load_via_skill_router", lambda self: None)
    def test_list_by_category_no_match(self):
        reg = SpecRegistry()
        reg.register(AgentCapability(agent_id="a", capabilities=["n", "domain"]))
        result = reg.list_by_category("nonexistent")
        assert result == []
