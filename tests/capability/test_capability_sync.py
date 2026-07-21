# [A_test] module_id: MOD-GOV_capability_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_capability_sync
# [INVARIANTS] sync_a2a and sync_skills are idempotent; existing cap_ids are skipped
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import yaml

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.capability_sync import CapabilitySync


class _FakeA2ACard:
    def __init__(self, agent_id: str, name: str, description: str, capabilities: list | None = None) -> None:
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities or []


class _FakeA2ARegistry:
    def __init__(self, cards: dict[str, _FakeA2ACard] | None = None) -> None:
        self._cards = cards or {}


class TestCapabilitySyncInit:
    def test_init_with_registry(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        assert sync._registry is registry

    def test_init_with_empty_registry(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        assert registry.count() == 0


class TestSyncA2A:
    def test_sync_a2a_none_registry(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        result = sync.sync_a2a(None)
        assert result == 0

    def test_sync_a2a_registers_new_agents(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        fake_card = _FakeA2ACard("agent-1", "TestAgent", "A test agent")
        a2a = _FakeA2ARegistry({"a1": fake_card})
        result = sync.sync_a2a(a2a)
        assert result == 1
        cap = registry.get("a2a-agent-agent-1")
        assert cap is not None
        assert cap.name == "A2A Agent: TestAgent"

    def test_sync_a2a_skips_existing(self) -> None:
        registry = CapabilityRegistry()
        existing = CapabilityCard(
            capability_id="a2a-agent-agent-1",
            name="A2A Agent: TestAgent",
            category=CapabilityCategory.SEARCH,
            description="existing",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        registry.register(existing)
        sync = CapabilitySync(registry)
        fake_card = _FakeA2ACard("agent-1", "TestAgent", "A test agent")
        a2a = _FakeA2ARegistry({"a1": fake_card})
        result = sync.sync_a2a(a2a)
        assert result == 0

    def test_sync_a2a_multiple_agents(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        cards = {
            "a1": _FakeA2ACard("agent-1", "Agent1", "First"),
            "a2": _FakeA2ACard("agent-2", "Agent2", "Second"),
        }
        a2a = _FakeA2ARegistry(cards)
        result = sync.sync_a2a(a2a)
        assert result == 2

    def test_sync_a2a_empty_registry(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        a2a = _FakeA2ARegistry({})
        result = sync.sync_a2a(a2a)
        assert result == 0

    def test_sync_a2a_exception_returns_zero(self) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)

        class BadRegistry:
            _cards = property(lambda self: (_ for _ in ()).throw(RuntimeError("boom")))

        result = sync.sync_a2a(BadRegistry())
        assert result == 0


class TestSyncSkills:
    def test_sync_skills_nonexistent_path(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        result = sync.sync_skills(tmp_path / "nonexistent.yaml")
        assert result == 0

    def test_sync_skills_registers_new_skills(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        skill_data = {
            "skills": {
                "domain": {
                    "DATABASE_SPECIALIST": {
                        "name": "database-specialist",
                        "description": "Database expert skill",
                        "tier": "L1",
                    }
                }
            }
        }
        path = tmp_path / "skills.yaml"
        path.write_text(yaml.dump(skill_data), encoding="utf-8")
        result = sync.sync_skills(path)
        assert result == 1
        cap = registry.get("database-specialist")
        assert cap is not None
        assert cap.name == "Skill: database-specialist"

    def test_sync_skills_skips_existing(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        existing = CapabilityCard(
            capability_id="database-specialist",
            name="Skill: database-specialist",
            category=CapabilityCategory.DATA,
            description="already registered",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        registry.register(existing)
        sync = CapabilitySync(registry)
        skill_data = {
            "skills": {
                "domain": {
                    "DATABASE_SPECIALIST": {
                        "name": "database-specialist",
                        "description": "Database expert skill",
                    }
                }
            }
        }
        path = tmp_path / "skills.yaml"
        path.write_text(yaml.dump(skill_data), encoding="utf-8")
        result = sync.sync_skills(path)
        assert result == 0

    def test_sync_skills_empty_yaml(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        path = tmp_path / "skills.yaml"
        path.write_text("", encoding="utf-8")
        result = sync.sync_skills(path)
        assert result == 0

    def test_sync_skills_role_category(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        skill_data = {
            "skills": {
                "role": {
                    "FEEDBACK_SPECIALIST": {
                        "name": "feedback-specialist",
                        "description": "Feedback skill",
                        "tier": "L2",
                    }
                }
            }
        }
        path = tmp_path / "skills.yaml"
        path.write_text(yaml.dump(skill_data), encoding="utf-8")
        result = sync.sync_skills(path)
        assert result == 1
        cap = registry.get("feedback-specialist")
        assert cap is not None
        assert cap.runtime_plane == "cold"
        assert cap.priority == "P2"

    def test_sync_skills_idempotent(self, tmp_path: Path) -> None:
        registry = CapabilityRegistry()
        sync = CapabilitySync(registry)
        skill_data = {
            "skills": {
                "domain": {
                    "GATE_SPECIALIST": {
                        "name": "gate-specialist",
                        "description": "Gate skill",
                    }
                }
            }
        }
        path = tmp_path / "skills.yaml"
        path.write_text(yaml.dump(skill_data), encoding="utf-8")
        first = sync.sync_skills(path)
        second = sync.sync_skills(path)
        assert first == 1
        assert second == 0
