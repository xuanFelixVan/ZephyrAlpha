# [A_test] module_id: MOD-GOV_formal_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_formal_verifier
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_formal_verifier.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.architecture_governance.formal_verifier import FormalVerifier


class TestFormalVerifierInstantiation:
    def test_init_creates_instance(self):
        fv = FormalVerifier()
        assert fv is not None

    def test_instance_has_verify_rule_completeness(self):
        fv = FormalVerifier()
        assert callable(getattr(fv, "verify_rule_completeness", None))

    def test_instance_has_verify_rule_consistency(self):
        fv = FormalVerifier()
        assert callable(getattr(fv, "verify_rule_consistency", None))


class TestFormalVerifierCompleteness:
    def test_complete_coverage_returns_complete(self):
        fv = FormalVerifier()
        rules = [{"rule_id": "R1", "patterns": ["read", "write"]}]
        result = fv.verify_rule_completeness(rules, ["read", "write"])
        assert result["complete"] is True
        assert result["gaps"] == []
        assert result["coverage"] == 1.0

    def test_partial_coverage_returns_gaps(self):
        fv = FormalVerifier()
        rules = [{"rule_id": "R1", "patterns": ["read"]}]
        result = fv.verify_rule_completeness(rules, ["read", "write", "delete"])
        assert result["complete"] is False
        assert set(result["gaps"]) == {"write", "delete"}
        assert result["coverage"] == pytest.approx(1 / 3)

    def test_no_rules_all_gaps(self):
        fv = FormalVerifier()
        result = fv.verify_rule_completeness([], ["read", "write"])
        assert result["complete"] is False
        assert set(result["gaps"]) == {"read", "write"}
        assert result["coverage"] == 0.0

    def test_empty_operation_space_is_complete(self):
        fv = FormalVerifier()
        result = fv.verify_rule_completeness([], [])
        assert result["complete"] is True
        assert result["gaps"] == []
        assert result["coverage"] == 0.0

    def test_rules_with_no_patterns_contribute_nothing(self):
        fv = FormalVerifier()
        rules = [{"rule_id": "R1"}]
        result = fv.verify_rule_completeness(rules, ["read"])
        assert result["complete"] is False
        assert result["gaps"] == ["read"]

    def test_coverage_ratio_calculation(self):
        fv = FormalVerifier()
        rules = [{"rule_id": "R1", "patterns": ["a", "b"]}]
        result = fv.verify_rule_completeness(rules, ["a", "b", "c", "d"])
        assert result["coverage"] == 0.5

    def test_overlapping_patterns_across_rules(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read", "write"]},
            {"rule_id": "R2", "patterns": ["write", "delete"]},
        ]
        result = fv.verify_rule_completeness(rules, ["read", "write", "delete"])
        assert result["complete"] is True
        assert result["coverage"] == 1.0


class TestFormalVerifierConsistency:
    def test_no_conflicts_returns_empty(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read"], "level": "high"},
            {"rule_id": "R2", "patterns": ["write"], "level": "high"},
        ]
        result = fv.verify_rule_consistency(rules)
        assert result == []

    def test_same_level_no_conflict(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read", "write"], "level": "high"},
            {"rule_id": "R2", "patterns": ["write", "delete"], "level": "high"},
        ]
        result = fv.verify_rule_consistency(rules)
        assert result == []

    def test_different_levels_with_overlap_produces_conflict(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read", "write"], "level": "high"},
            {"rule_id": "R2", "patterns": ["write", "delete"], "level": "low"},
        ]
        result = fv.verify_rule_consistency(rules)
        assert len(result) == 1
        assert "R1" in result[0]
        assert "R2" in result[0]
        assert "write" in result[0]

    def test_empty_rules_returns_empty(self):
        fv = FormalVerifier()
        result = fv.verify_rule_consistency([])
        assert result == []

    def test_single_rule_no_conflict(self):
        fv = FormalVerifier()
        rules = [{"rule_id": "R1", "patterns": ["read"], "level": "high"}]
        result = fv.verify_rule_consistency(rules)
        assert result == []

    def test_multiple_conflicts_detected(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read"], "level": "high"},
            {"rule_id": "R2", "patterns": ["read"], "level": "low"},
            {"rule_id": "R3", "patterns": ["read"], "level": "medium"},
        ]
        result = fv.verify_rule_consistency(rules)
        assert len(result) == 3

    def test_rules_without_patterns_no_conflict(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "level": "high"},
            {"rule_id": "R2", "level": "low"},
        ]
        result = fv.verify_rule_consistency(rules)
        assert result == []

    def test_rules_without_level_no_conflict_even_with_overlap(self):
        fv = FormalVerifier()
        rules = [
            {"rule_id": "R1", "patterns": ["read"]},
            {"rule_id": "R2", "patterns": ["read"]},
        ]
        result = fv.verify_rule_consistency(rules)
        assert result == []
