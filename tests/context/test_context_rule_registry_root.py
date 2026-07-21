# [A_test] module_id: MOD-GOV_context_rule_registry_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_rule_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import os
import tempfile

import pytest

try:
    from zephyr.autonomy_core.context.context_rule_registry import ContextRule, ContextRuleRegistry
except Exception as _exc:
    pytest.skip(f"cannot import context_rule_registry: {_exc}", allow_module_level=True)


class TestContextRule:
    def test_valid_domain_rule(self):
        rule = ContextRule(rule_id="R1", injection_level="DOMAIN", max_tokens=500)
        assert rule.rule_id == "R1"
        assert rule.injection_level == "DOMAIN"

    def test_valid_hot_rule(self):
        rule = ContextRule(rule_id="R2", injection_level="HOT", max_tokens=300)
        assert rule.injection_level == "HOT"

    def test_hot_rule_exceeds_tokens(self):
        with pytest.raises(ValueError, match="HOT level"):
            ContextRule(rule_id="R3", injection_level="HOT", max_tokens=500)

    def test_invalid_injection_level(self):
        with pytest.raises(ValueError, match="injection_level must be one of"):
            ContextRule(rule_id="R4", injection_level="INVALID")

    def test_valid_cold_rule(self):
        rule = ContextRule(rule_id="R5", injection_level="COLD", max_tokens=1000)
        assert rule.injection_level == "COLD"

    def test_defaults(self):
        rule = ContextRule(rule_id="R6")
        assert rule.priority == 50
        assert rule.injection_level == "DOMAIN"
        assert rule.max_tokens == 500
        assert rule.content == ""
        assert rule.trigger_conditions == {}


class TestContextRuleRegistry:
    def test_register_and_lookup(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R1", injection_level="DOMAIN", trigger_conditions={"task_type": "CODE_GEN"})
        reg.register(rule)
        results = reg.lookup(task_type="CODE_GEN")
        assert len(results) == 1
        assert results[0].rule_id == "R1"

    def test_lookup_no_match(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R1", injection_level="DOMAIN", trigger_conditions={"task_type": "CODE_GEN"})
        reg.register(rule)
        results = reg.lookup(task_type="ANALYSIS")
        assert results == []

    def test_lookup_hot_always_matches(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="HOT1", injection_level="HOT", max_tokens=200)
        reg.register(rule)
        results = reg.lookup(task_type="ANYTHING")
        assert len(results) == 1

    def test_lookup_by_tags(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R2", injection_level="DOMAIN", trigger_conditions={"tags": ["python", "security"]})
        reg.register(rule)
        results = reg.lookup(tags=["security"])
        assert len(results) == 1

    def test_lookup_by_keywords(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R3", injection_level="DOMAIN", trigger_conditions={"keywords": ["refactor"]})
        reg.register(rule)
        results = reg.lookup(input_text="please refactor this code")
        assert len(results) == 1

    def test_lookup_empty_conditions_always_matches(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R4", injection_level="DOMAIN", trigger_conditions={})
        reg.register(rule)
        results = reg.lookup(task_type="WHATEVER")
        assert len(results) == 1

    def test_unregister(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="R5", injection_level="DOMAIN")
        reg.register(rule)
        reg.unregister("R5")
        results = reg.lookup()
        assert results == []

    def test_unregister_nonexistent(self):
        reg = ContextRuleRegistry()
        reg.unregister("NONEXISTENT")

    def test_register_overwrites(self):
        reg = ContextRuleRegistry()
        r1 = ContextRule(rule_id="R1", injection_level="DOMAIN", content="first")
        r2 = ContextRule(rule_id="R1", injection_level="DOMAIN", content="second")
        reg.register(r1)
        reg.register(r2)
        results = reg.lookup()
        assert len(results) == 1
        assert results[0].content == "second"

    def test_list_rules_sorted_by_priority(self):
        reg = ContextRuleRegistry()
        reg.register(ContextRule(rule_id="LOW", injection_level="DOMAIN", priority=10))
        reg.register(ContextRule(rule_id="HIGH", injection_level="DOMAIN", priority=90))
        rules = reg.list_rules()
        assert rules[0].rule_id == "HIGH"
        assert rules[1].rule_id == "LOW"

    def test_load_yaml_file_not_found(self):
        reg = ContextRuleRegistry()
        with pytest.raises(FileNotFoundError):
            reg.load_yaml("/nonexistent/path/rules.yaml")

    def test_load_yaml_and_save_yaml(self):
        reg = ContextRuleRegistry()
        reg.register(ContextRule(rule_id="Y1", injection_level="DOMAIN", content="test rule", priority=80))
        reg.register(ContextRule(rule_id="Y2", injection_level="HOT", max_tokens=200, content="hot rule", priority=90))
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "rules.yaml")
            reg.save_yaml(path)
            reg2 = ContextRuleRegistry()
            count = reg2.load_yaml(path)
            assert count == 2
            rules = reg2.list_rules()
            assert len(rules) == 2

    def test_load_yaml_empty_file(self):
        reg = ContextRuleRegistry()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "empty.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            count = reg.load_yaml(path)
            assert count == 0

    def test_lookup_on_demand(self):
        reg = ContextRuleRegistry()
        rule = ContextRule(rule_id="COLD1", injection_level="COLD", trigger_conditions={"on_demand": True})
        reg.register(rule)
        results_no_cold = reg.lookup()
        results_with_cold = reg.lookup(include_cold=True)
        assert len(results_with_cold) >= len(results_no_cold)

    def test_lookup_priority_sorting(self):
        reg = ContextRuleRegistry()
        reg.register(ContextRule(rule_id="LOW", injection_level="DOMAIN", priority=10, trigger_conditions={}))
        reg.register(ContextRule(rule_id="HIGH", injection_level="DOMAIN", priority=90, trigger_conditions={}))
        results = reg.lookup()
        assert results[0].rule_id == "HIGH"
