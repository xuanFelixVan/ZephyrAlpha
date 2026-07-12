# [A_test] module_id: SRC-TST-1791 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-441 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_vibe_coding_enforcer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_enforcement.behavioral_admission.vibe_coding_enforcer import (
    VIBE_CODING_RULES,
    VibeRuleLevel,
    enforce,
    enforce_all,
    list_rules_by_level,
    must,
    should,
)


class TestVibeRuleLevel:
    def test_enum_values(self):
        assert VibeRuleLevel.MUST == "MUST"
        assert VibeRuleLevel.SHOULD == "SHOULD"
        assert VibeRuleLevel.MAY == "MAY"

    def test_enum_members_count(self):
        assert len(VibeRuleLevel) == 3


class TestVibeCodingRules:
    def test_rules_not_empty(self):
        assert len(VIBE_CODING_RULES) > 0

    def test_all_rules_have_level_and_desc(self):
        for name, (level, desc) in VIBE_CODING_RULES.items():
            assert isinstance(level, VibeRuleLevel)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_must_rules_exist(self):
        must_rules = [n for n, (l, _) in VIBE_CODING_RULES.items() if l == VibeRuleLevel.MUST]
        assert len(must_rules) > 0

    def test_should_rules_exist(self):
        should_rules = [n for n, (l, _) in VIBE_CODING_RULES.items() if l == VibeRuleLevel.SHOULD]
        assert len(should_rules) > 0

    def test_may_rules_exist(self):
        may_rules = [n for n, (l, _) in VIBE_CODING_RULES.items() if l == VibeRuleLevel.MAY]
        assert len(may_rules) > 0


class TestEnforce:
    def test_must_rule_without_level_returns_false(self):
        result = enforce("lock_before_write")
        assert result is False

    def test_should_rule_without_level_returns_true(self):
        result = enforce("dual_ai_review")
        assert result is True

    def test_may_rule_without_level_returns_true(self):
        result = enforce("exploratory_first")
        assert result is True

    def test_unknown_rule_returns_true(self):
        result = enforce("nonexistent_rule")
        assert result is True

    def test_must_rule_with_must_level(self):
        result = enforce("lock_before_write", level=VibeRuleLevel.MUST)
        assert result is True

    def test_must_rule_with_should_level(self):
        result = enforce("lock_before_write", level=VibeRuleLevel.SHOULD)
        assert result is True

    def test_must_rule_with_may_level(self):
        result = enforce("lock_before_write", level=VibeRuleLevel.MAY)
        assert result is True

    def test_should_rule_with_must_level(self):
        result = enforce("dual_ai_review", level=VibeRuleLevel.MUST)
        assert result is False

    def test_should_rule_with_should_level(self):
        result = enforce("dual_ai_review", level=VibeRuleLevel.SHOULD)
        assert result is True


class TestEnforceAll:
    def test_all_pass(self):
        checks = {
            "lock_before_write": VibeRuleLevel.MUST,
            "dual_ai_review": VibeRuleLevel.SHOULD,
        }
        result = enforce_all(checks)
        assert result["lock_before_write"] is True
        assert result["dual_ai_review"] is True

    def test_mixed_results(self):
        checks = {
            "dual_ai_review": VibeRuleLevel.MUST,
            "lock_before_write": None,
        }
        result = enforce_all(checks)
        assert result["dual_ai_review"] is False
        assert result["lock_before_write"] is False


class TestListRulesByLevel:
    def test_must_rules(self):
        rules = list_rules_by_level(VibeRuleLevel.MUST)
        assert len(rules) > 0
        for name, desc in rules.items():
            assert len(desc) > 0

    def test_should_rules(self):
        rules = list_rules_by_level(VibeRuleLevel.SHOULD)
        assert len(rules) > 0

    def test_may_rules(self):
        rules = list_rules_by_level(VibeRuleLevel.MAY)
        assert len(rules) > 0


class TestMustDecorator:
    def test_decorated_function_runs(self):
        @must("lock_before_write")
        def my_func():
            return 42

        result = my_func()
        assert result == 42

    def test_decorated_function_has_vibe_attrs(self):
        @must("lock_before_write")
        def my_func():
            return 42

        assert hasattr(my_func, "_vibe_rule")
        assert my_func._vibe_rule == "lock_before_write"
        assert my_func._vibe_level == VibeRuleLevel.MUST


class TestShouldDecorator:
    def test_decorated_function_runs(self):
        @should("dual_ai_review")
        def my_func():
            return "ok"

        result = my_func()
        assert result == "ok"

    def test_decorated_function_has_vibe_attrs(self):
        @should("dual_ai_review")
        def my_func():
            return "ok"

        assert hasattr(my_func, "_vibe_rule")
        assert my_func._vibe_level == VibeRuleLevel.SHOULD
