# [A_test] module_id: MOD-GOV_e_self_validator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_self_validator
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.self_validator import SelfValidator


class TestSelfValidator:
    def test_validate_rules_all_valid(self):
        sv = SelfValidator()
        rules = [
            {"rule_id": "R1", "level": "P0", "patterns": ["x"]},
            {"rule_id": "R2", "level": "P1", "patterns": ["y"]},
        ]
        result = sv.validate_rules(rules)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_rules_missing_rule_id(self):
        sv = SelfValidator()
        rules = [{"level": "P0", "patterns": ["x"]}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert any("Missing rule_id" in e for e in result["errors"])

    def test_validate_rules_missing_level(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R1", "patterns": ["x"]}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False
        assert any("missing level" in e for e in result["errors"])

    def test_validate_rules_no_patterns(self):
        sv = SelfValidator()
        rules = [{"rule_id": "R1", "level": "P0", "patterns": []}]
        result = sv.validate_rules(rules)
        assert result["valid"] is False

    def test_validate_rules_empty(self):
        sv = SelfValidator()
        result = sv.validate_rules([])
        assert result["valid"] is True
        assert result["errors"] == []

    def test_self_check(self):
        sv = SelfValidator()
        assert sv.self_check() is True
