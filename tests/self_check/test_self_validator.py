# [A_test] module_id: MOD-GOV_self_validator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_self_validator
# [INVARIANTS] Shadow Parallel Run必须通过;自验证不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_self_validator.py
# [TTL] task_bound

from zephyr.governance.intelligence_governance.self_validator import SelfValidator


class TestSelfValidatorInit:
    def test_instantiation(self):
        sv = SelfValidator()
        assert sv is not None


class TestValidateRules:
    def test_valid_rules(self):
        sv = SelfValidator()
        rules = [
            {"rule_id": "R001", "level": "high", "patterns": ["pattern_a"]},
            {"rule_id": "R002", "level": "low", "patterns": ["pattern_b"]},
        ]
        result = sv.validate_rules(rules)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_rule_id(self):
        sv = SelfValidator()
        rules = [{"level": "high", "patterns": ["pattern_a"]}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert any("Missing rule_id" in e for e in result["errors"])

    def test_missing_level(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R001", "patterns": ["pattern_a"]}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert any("missing level" in e for e in result["errors"])

    def test_no_patterns(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R001", "level": "high"}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert any("no patterns" in e for e in result["errors"])

    def test_empty_patterns_list(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R001", "level": "high", "patterns": []}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False

    def test_multiple_errors_in_single_rule(self):
        sv = SelfValidator()
        rules = [{}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert len(result["errors"]) >= 2

    def test_empty_rules_list(self):
        sv = SelfValidator()
        result = sv.validate_rules([])
        assert result["valid"] is True
        assert result["errors"] == []

    def test_error_includes_rule_id_when_available(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R001", "level": "high"}]
        result = sv.validate_rules(rules)
        assert any("R001" in e for e in result["errors"])

    def test_missing_rule_id_shows_question_mark(self):
        sv = SelfValidator()
        rules = [{"level": "high"}]
        result = sv.validate_rules(rules)
        assert any("?" in e for e in result["errors"])


class TestSelfCheck:
    def test_self_check_returns_true(self):
        sv = SelfValidator()
        assert sv.self_check() is True

    def test_self_check_consistent(self):
        sv = SelfValidator()
        assert sv.self_check() is True
        assert sv.self_check() is True
