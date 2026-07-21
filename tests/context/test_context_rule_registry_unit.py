# [A_test] module_id: MOD-GOV_context_rule_registry_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-XLR-003 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [TTL] task_bound

from __future__ import annotations

import pytest
import yaml

from zephyr.autonomy_core.context.context_rule_registry import ContextRule, ContextRuleRegistry


class TestContextRule:
    def test_valid_rule(self):
        rule = ContextRule(rule_id="R001", content="test")
        assert rule.injection_level == "DOMAIN"
        assert rule.priority == 50

    def test_invalid_injection_level(self):
        with pytest.raises(ValueError, match="injection_level"):
            ContextRule(rule_id="R001", injection_level="INVALID")

    def test_hot_max_tokens_exceeded(self):
        with pytest.raises(ValueError, match="HOT"):
            ContextRule(rule_id="R001", injection_level="HOT", max_tokens=500)


class TestRegisterAndLookup:
    def test_register_and_lookup_basic(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(
            rule_id="TEST-001",
            trigger_conditions={"task_type": "code_gen"},
            content="Use atomic writes",
            priority=70,
        )
        registry.register(rule)
        results = registry.lookup(task_type="code_gen")
        assert len(results) == 1
        assert results[0].rule_id == "TEST-001"

    def test_hot_level_always_matches(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(
            rule_id="HOT-001",
            trigger_conditions={},
            content="Always inject",
            priority=90,
            injection_level="HOT",
            max_tokens=200,
        )
        registry.register(rule)
        results = registry.lookup(task_type="anything", tags=["random"])
        assert len(results) == 1
        assert results[0].rule_id == "HOT-001"

    def test_domain_keyword_trigger(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(
            rule_id="DOMAIN-001",
            trigger_conditions={"keywords": ["dedup", "去重"]},
            content="Dedup rules",
            priority=70,
            injection_level="DOMAIN",
        )
        registry.register(rule)

        results_no_match = registry.lookup(task_type="code_gen", input_text="create new module")
        assert len(results_no_match) == 0

        results_match = registry.lookup(task_type="code_gen", input_text="dedup the code")
        assert len(results_match) == 1

        results_match_zh = registry.lookup(task_type="code_gen", input_text="去重扫描")
        assert len(results_match_zh) == 1

    def test_cold_on_demand(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(
            rule_id="COLD-001",
            trigger_conditions={"on_demand": True},
            content="Full policy tree",
            priority=30,
            injection_level="COLD",
            max_tokens=2000,
        )
        registry.register(rule)

        results_no_cold = registry.lookup(task_type="code_gen")
        assert len(results_no_cold) == 0

        results_with_cold = registry.lookup(task_type="code_gen", include_cold=True)
        assert len(results_with_cold) == 1

    def test_rule_id_conflict_overwrites(self):
        registry = ContextRuleRegistry()
        rule_v1 = ContextRule(rule_id="R001", content="version 1", priority=50)
        rule_v2 = ContextRule(rule_id="R001", content="version 2", priority=80)
        registry.register(rule_v1)
        registry.register(rule_v2)

        results = registry.lookup(task_type="", tags=[])
        assert len(results) == 1
        assert results[0].content == "version 2"
        assert results[0].priority == 80

    def test_unregister(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(rule_id="R001", content="test")
        registry.register(rule)
        assert len(registry.list_rules()) == 1

        registry.unregister("R001")
        assert len(registry.list_rules()) == 0

        registry.unregister("NONEXISTENT")

    def test_empty_registry_lookup(self):
        registry = ContextRuleRegistry()
        results = registry.lookup(task_type="code_gen", tags=["test"])
        assert results == []

    def test_priority_sorting(self):
        registry = ContextRuleRegistry()
        registry.register(ContextRule(rule_id="LOW", content="low", priority=10))
        registry.register(ContextRule(rule_id="HIGH", content="high", priority=90))
        registry.register(ContextRule(rule_id="MID", content="mid", priority=50))

        results = registry.lookup(task_type="", tags=[])
        assert [r.rule_id for r in results] == ["HIGH", "MID", "LOW"]

    def test_tag_matching(self):
        registry = ContextRuleRegistry()
        rule = ContextRule(
            rule_id="TAG-001",
            trigger_conditions={"tags": ["security", "audit"]},
            content="Security rules",
        )
        registry.register(rule)

        results_no = registry.lookup(task_type="code_gen", tags=["refactor"])
        assert len(results_no) == 0

        results_yes = registry.lookup(task_type="code_gen", tags=["security"])
        assert len(results_yes) == 1


class TestLoadYaml:
    def test_load_yaml(self, tmp_path):
        yaml_content = {
            "rules": [
                {
                    "rule_id": "YAML-001",
                    "trigger_conditions": {"keywords": ["test"]},
                    "content": "Test rule from YAML",
                    "priority": 60,
                    "injection_level": "DOMAIN",
                    "max_tokens": 500,
                    "source_module": "MOD-TEST",
                },
                {
                    "rule_id": "YAML-002",
                    "trigger_conditions": {},
                    "content": "Always on rule",
                    "priority": 90,
                    "injection_level": "HOT",
                    "max_tokens": 200,
                    "source_module": "MOD-TEST",
                },
            ]
        }
        yaml_path = tmp_path / "rules.yaml"
        yaml_path.write_text(yaml.dump(yaml_content, allow_unicode=True), encoding="utf-8")

        registry = ContextRuleRegistry()
        count = registry.load_yaml(str(yaml_path))
        assert count == 2

        results = registry.lookup(task_type="", tags=[], input_text="test")
        assert len(results) == 2

    def test_load_yaml_file_not_found(self):
        registry = ContextRuleRegistry()
        with pytest.raises(FileNotFoundError):
            registry.load_yaml("/nonexistent/path/rules.yaml")

    def test_load_yaml_empty(self, tmp_path):
        yaml_path = tmp_path / "empty.yaml"
        yaml_path.write_text("rules: []\n", encoding="utf-8")

        registry = ContextRuleRegistry()
        count = registry.load_yaml(str(yaml_path))
        assert count == 0

    def test_save_and_load_yaml_roundtrip(self, tmp_path):
        registry = ContextRuleRegistry()
        registry.register(
            ContextRule(
                rule_id="SAVE-001",
                trigger_conditions={"keywords": ["save"]},
                content="Save test",
                priority=75,
                injection_level="DOMAIN",
                max_tokens=600,
                source_module="MOD-TEST",
            )
        )

        save_path = str(tmp_path / "saved_rules.yaml")
        registry.save_yaml(save_path)

        registry2 = ContextRuleRegistry()
        count = registry2.load_yaml(save_path)
        assert count == 1

        rules = registry2.list_rules()
        assert rules[0].rule_id == "SAVE-001"
        assert rules[0].content == "Save test"
        assert rules[0].priority == 75
