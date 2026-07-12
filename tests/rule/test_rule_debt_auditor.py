# [A_test] module_id: SRC-TST-1494 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_rule_debt_auditor

# [INVARIANTS] 测试必须覆盖空输入/None/异常边界;不可跳过

# [MODIFY-GUARD] src/zephyr/escalation-engine/rule_debt_auditor.py

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 测试失败必须包含断言消息

# [TESTS] tests/test_rule_debt_auditor.py
# [TTL] task_bound
from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_debt_auditor import RuleDebtAuditor


class TestRuleDebtAuditorInstantiation:
    def test_creates_instance(self):
        auditor = RuleDebtAuditor()
        assert auditor is not None

    def test_instance_has_audit_method(self):
        auditor = RuleDebtAuditor()
        assert callable(getattr(auditor, "audit", None))


class TestAuditMethod:
    def test_empty_rules_list(self):
        auditor = RuleDebtAuditor()
        result = auditor.audit([])
        assert result["total_rules"] == 0
        assert result["unique_levels"] == 0
        assert result["duplicate_patterns"] == 0
        assert result["debt_score"] == 0.0

    def test_single_rule_no_patterns(self):
        auditor = RuleDebtAuditor()
        rules = [{"level": "critical"}]
        result = auditor.audit(rules)
        assert result["total_rules"] == 1
        assert result["unique_levels"] == 1
        assert result["duplicate_patterns"] == 0
        assert result["debt_score"] == 0.0

    def test_multiple_rules_distinct_levels(self):
        auditor = RuleDebtAuditor()
        rules = [
            {"level": "critical"},
            {"level": "warning"},
            {"level": "info"},
        ]
        result = auditor.audit(rules)
        assert result["total_rules"] == 3
        assert result["unique_levels"] == 3
        assert result["duplicate_patterns"] == 0
        assert result["debt_score"] == 0.0

    def test_duplicate_patterns_across_rules(self):
        auditor = RuleDebtAuditor()
        rules = [
            {"level": "critical", "patterns": ["timeout", "retry"]},
            {"level": "warning", "patterns": ["timeout", "retry"]},
        ]
        result = auditor.audit(rules)
        assert result["total_rules"] == 2
        assert result["duplicate_patterns"] == 2
        assert result["debt_score"] == 1.0

    def test_partial_duplicate_patterns(self):
        auditor = RuleDebtAuditor()
        rules = [
            {"level": "critical", "patterns": ["timeout", "retry"]},
            {"level": "warning", "patterns": ["timeout", "fallback"]},
        ]
        result = auditor.audit(rules)
        assert result["total_rules"] == 2
        assert result["duplicate_patterns"] == 1
        assert result["debt_score"] == 0.5

    def test_rule_without_level_defaults_to_unknown(self):
        auditor = RuleDebtAuditor()
        rules = [{"patterns": ["timeout"]}, {"level": "critical"}]
        result = auditor.audit(rules)
        assert result["unique_levels"] == 2

    def test_all_rules_same_level(self):
        auditor = RuleDebtAuditor()
        rules = [{"level": "critical"} for _ in range(5)]
        result = auditor.audit(rules)
        assert result["total_rules"] == 5
        assert result["unique_levels"] == 1

    def test_debt_score_with_no_duplicates(self):
        auditor = RuleDebtAuditor()
        rules = [
            {"level": "critical", "patterns": ["timeout"]},
            {"level": "warning", "patterns": ["retry"]},
        ]
        result = auditor.audit(rules)
        assert result["debt_score"] == 0.0

    def test_none_input_raises_exception(self):
        auditor = RuleDebtAuditor()
        with pytest.raises(TypeError):
            auditor.audit(None)

    def test_non_list_input_raises_exception(self):
        auditor = RuleDebtAuditor()
        with pytest.raises((TypeError, AttributeError)):
            auditor.audit("not a list")

    def test_rule_with_empty_patterns_list(self):
        auditor = RuleDebtAuditor()
        rules = [{"level": "critical", "patterns": []}]
        result = auditor.audit(rules)
        assert result["total_rules"] == 1
        assert result["duplicate_patterns"] == 0

    def test_duplicate_pattern_within_single_rule(self):
        auditor = RuleDebtAuditor()
        rules = [
            {"level": "critical", "patterns": ["timeout", "timeout"]},
        ]
        result = auditor.audit(rules)
        assert result["duplicate_patterns"] == 1
        assert result["debt_score"] == 1.0

    def test_return_dict_has_all_keys(self):
        auditor = RuleDebtAuditor()
        result = auditor.audit([])
        expected_keys = {"total_rules", "unique_levels", "duplicate_patterns", "debt_score"}
        assert set(result.keys()) == expected_keys
