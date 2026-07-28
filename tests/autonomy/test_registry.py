# [A_test] module_id: MOD-GOV_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §3
# [MODULE] tests.test_registry
# [INVARIANTS] register must be atomic; get returns None for unknown; list_all returns list of dicts
# [MODIFY-GUARD] skill-registry.yaml; engine.py; __init__.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] registry load failure returns empty dict; missing registry file skips load
# [TESTS] tests/test_registry.py
# [TTL] task_bound


import pytest
import yaml

from zephyr.autonomy_core.skill_rbac_registry import GOVERNANCE_SKILL_TYPES, AgentCapability, SpecRegistry


class TestAgentCapabilityModel:
    def test_default_values(self):
        cap = AgentCapability(agent_id="test-agent")
        assert cap.agent_id == "test-agent"
        assert cap.capabilities == []
        assert cap.version == "1.0.0"
        assert cap.spec_hash == ""

    def test_full_creation(self):
        cap = AgentCapability(
            agent_id="my-agent",
            capabilities=["governor-specialist", "domain"],
            version="2.0.0",
            spec_hash="abc123",
        )
        assert cap.agent_id == "my-agent"
        assert len(cap.capabilities) == 2
        assert cap.version == "2.0.0"
        assert cap.spec_hash == "abc123"

    def test_pydantic_model_validation(self):
        with pytest.raises(Exception):
            AgentCapability()

    def test_capabilities_mutable_list(self):
        cap = AgentCapability(agent_id="x")
        cap.capabilities.append("new-cap")
        assert "new-cap" in cap.capabilities


class TestGovernanceSkillTypes:
    def test_domain_types(self):
        assert "domain" in GOVERNANCE_SKILL_TYPES
        assert len(GOVERNANCE_SKILL_TYPES["domain"]) >= 10

    def test_role_types(self):
        assert "role" in GOVERNANCE_SKILL_TYPES
        assert "architect" in GOVERNANCE_SKILL_TYPES["role"]
        assert "implementer" in GOVERNANCE_SKILL_TYPES["role"]
        assert "governor" in GOVERNANCE_SKILL_TYPES["role"]


class TestSpecRegistryInit:
    def test_init_with_missing_registry_file(self, tmp_path):
        missing = tmp_path / "nonexistent.yaml"
        reg = SpecRegistry(registry_path=missing)
        assert len(reg.entries) == 0

    def test_init_with_valid_registry(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {
                    "gov-spec": {
                        "name": "Governance Specialist",
                        "description": "Handles governance tasks",
                        "version": "1.0.0",
                    }
                },
                "role": {
                    "arch": {
                        "name": "Architect",
                        "description": "Designs architecture",
                        "version": "0.5.0",
                    }
                },
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert "gov-spec" in reg.entries
        assert "arch" in reg.entries

    def test_init_with_empty_registry(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert len(reg.entries) == 0

    def test_init_with_null_yaml(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("null", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert len(reg.entries) == 0


class TestSpecRegistryRegister:
    def test_register_new_capability(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        cap = AgentCapability(agent_id="new-skill", capabilities=["New Skill", "domain"])
        reg.register(cap)
        assert reg.get("new-skill") is not None

    def test_register_overwrites_existing(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        cap1 = AgentCapability(agent_id="skill-1", capabilities=["Old Name", "domain"], version="1.0.0")
        reg.register(cap1)
        cap2 = AgentCapability(agent_id="skill-1", capabilities=["New Name", "domain"], version="2.0.0")
        reg.register(cap2)
        result = reg.get("skill-1")
        assert result.version == "2.0.0"
        assert result.capabilities[0] == "New Name"


class TestSpecRegistryGet:
    def test_get_existing(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {"my-skill": {"name": "My Skill", "description": "desc", "version": "1.0.0"}},
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        result = reg.get("my-skill")
        assert result is not None
        assert result.agent_id == "my-skill"

    def test_get_nonexistent_returns_none(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert reg.get("no-such-skill") is None

    def test_get_after_register(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        cap = AgentCapability(agent_id="x", capabilities=["X", "role"])
        reg.register(cap)
        assert reg.get("x") is not None
        assert reg.get("x").agent_id == "x"


class TestSpecRegistryListAll:
    def test_list_all_empty(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("", encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert reg.list_all() == []

    def test_list_all_with_entries(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {
                    "skill-a": {"name": "Skill A", "description": "d", "version": "1.0.0"},
                    "skill-b": {"name": "Skill B", "description": "d2", "version": "0.1.0"},
                },
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        result = reg.list_all()
        assert len(result) == 2
        ids = [e["skill_id"] for e in result]
        assert "skill-a" in ids
        assert "skill-b" in ids

    def test_list_all_dict_structure(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {"s1": {"name": "S1", "description": "d", "version": "1.0.0"}},
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        result = reg.list_all()
        entry = result[0]
        assert "skill_id" in entry
        assert "name" in entry
        assert "category" in entry
        assert "version" in entry


class TestSpecRegistryListByCategory:
    def test_filter_by_domain(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {"s1": {"name": "S1", "description": "d", "version": "1.0.0"}},
                "role": {"s2": {"name": "S2", "description": "d", "version": "1.0.0"}},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        domain_entries = reg.list_by_category("domain")
        assert len(domain_entries) == 1
        assert domain_entries[0]["category"] == "domain"

    def test_filter_by_role(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {},
                "role": {"arch": {"name": "Architect", "description": "d", "version": "1.0.0"}},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        role_entries = reg.list_by_category("role")
        assert len(role_entries) == 1

    def test_filter_nonexistent_category(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {"skills": {"domain": {"s1": {"name": "S1", "description": "d", "version": "1.0.0"}}, "role": {}}}
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert reg.list_by_category("nonexistent") == []


class TestSpecRegistryReload:
    def test_reload_clears_and_reloads(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {"s1": {"name": "S1", "description": "d", "version": "1.0.0"}},
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert len(reg.entries) == 1
        reg.register(AgentCapability(agent_id="manual", capabilities=["M", "domain"]))
        assert len(reg.entries) == 2
        reg.reload()
        assert len(reg.entries) == 1
        assert reg.get("manual") is None

    def test_reload_with_updated_file(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data_v1 = {
            "skills": {
                "domain": {"s1": {"name": "S1", "description": "d", "version": "1.0.0"}},
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data_v1, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert reg.get("s1") is not None
        data_v2 = {
            "skills": {
                "domain": {
                    "s1": {"name": "S1", "description": "d", "version": "1.0.0"},
                    "s2": {"name": "S2", "description": "d2", "version": "2.0.0"},
                },
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data_v2, allow_unicode=True), encoding="utf-8")
        reg.reload()
        assert reg.get("s1") is not None
        assert reg.get("s2") is not None


class TestSpecRegistryBoundary:
    def test_corrupt_yaml_file(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text("{{invalid::yaml", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            SpecRegistry(registry_path=reg_file)

    def test_registry_with_missing_skills_key(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text(yaml.dump({"other_key": "value"}, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert len(reg.entries) == 0

    def test_registry_with_missing_category_keys(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        reg_file.write_text(yaml.dump({"skills": {}}, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        assert len(reg.entries) == 0

    def test_skill_with_missing_name_uses_id(self, tmp_path):
        reg_file = tmp_path / "skill-registry.yaml"
        data = {
            "skills": {
                "domain": {"my-id": {"description": "no name field", "version": "1.0.0"}},
                "role": {},
            }
        }
        reg_file.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        reg = SpecRegistry(registry_path=reg_file)
        result = reg.get("my-id")
        assert result is not None
        assert result.capabilities[0] == "my-id"
