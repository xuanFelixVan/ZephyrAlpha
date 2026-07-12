# [A_test] module_id: SRC-TST-0538 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_code_review_ai
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_code_review_ai.py -q
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.behavioral_admission.code_review_ai import (
    REVIEW_RULES,
    REVIEW_TIMEOUTS,
    ReviewLevel,
)


class TestReviewLevel:
    def test_enum_values(self):
        assert ReviewLevel.L0_RUFF.value == "L0_ruff"
        assert ReviewLevel.L1_SECURITY.value == "L1_security"
        assert ReviewLevel.L2_LOGIC.value == "L2_logic"
        assert ReviewLevel.L3_ARCH.value == "L3_arch"
        assert ReviewLevel.L4_STRATEGY.value == "L4_strategy"
        assert ReviewLevel.L5_DUAL_AI.value == "L5_dual_ai"

    def test_enum_count(self):
        assert len(ReviewLevel) == 6

    def test_enum_is_str(self):
        for level in ReviewLevel:
            assert isinstance(level.value, str)

    def test_instantiation_from_value(self):
        level = ReviewLevel("L0_ruff")
        assert level == ReviewLevel.L0_RUFF

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ReviewLevel("L99_nonexistent")


class TestReviewTimeouts:
    def test_all_levels_have_timeout(self):
        for level in ReviewLevel:
            assert level in REVIEW_TIMEOUTS

    def test_timeouts_are_positive_integers(self):
        for level, timeout in REVIEW_TIMEOUTS.items():
            assert isinstance(timeout, int)
            assert timeout > 0

    def test_timeout_ordering(self):
        assert REVIEW_TIMEOUTS[ReviewLevel.L0_RUFF] <= REVIEW_TIMEOUTS[ReviewLevel.L1_SECURITY]
        assert REVIEW_TIMEOUTS[ReviewLevel.L1_SECURITY] <= REVIEW_TIMEOUTS[ReviewLevel.L2_LOGIC]
        assert REVIEW_TIMEOUTS[ReviewLevel.L2_LOGIC] <= REVIEW_TIMEOUTS[ReviewLevel.L3_ARCH]
        assert REVIEW_TIMEOUTS[ReviewLevel.L3_ARCH] <= REVIEW_TIMEOUTS[ReviewLevel.L4_STRATEGY]
        assert REVIEW_TIMEOUTS[ReviewLevel.L4_STRATEGY] <= REVIEW_TIMEOUTS[ReviewLevel.L5_DUAL_AI]

    def test_l0_is_fastest(self):
        assert REVIEW_TIMEOUTS[ReviewLevel.L0_RUFF] == 1

    def test_l5_is_slowest(self):
        assert REVIEW_TIMEOUTS[ReviewLevel.L5_DUAL_AI] == 120


class TestReviewRules:
    def test_rules_is_list(self):
        assert isinstance(REVIEW_RULES, list)

    def test_rules_non_empty(self):
        assert len(REVIEW_RULES) > 0

    def test_rules_contain_L3_requirement(self):
        l3_rules = [r for r in REVIEW_RULES if "L3" in r]
        assert len(l3_rules) > 0

    def test_rules_contain_L4_requirement(self):
        l4_rules = [r for r in REVIEW_RULES if "L4" in r]
        assert len(l4_rules) > 0

    def test_rules_are_strings(self):
        for rule in REVIEW_RULES:
            assert isinstance(rule, str)
            assert len(rule) > 0
