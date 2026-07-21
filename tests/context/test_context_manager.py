# [A_test] module_id: MOD-GOV_context_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_context_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_context_manager.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.context_governance.context_manager import (
    MAX_HISTORY_DAYS,
    TIER_TOKENS,
    TRIM_DUPLICATE_THRESHOLD,
    HallucinationLevel,
    TokenTier,
)


class TestTokenTier:
    def test_enum_members_exist(self):
        assert TokenTier.T0.value == "T0_500"
        assert TokenTier.T1.value == "T1_2K"
        assert TokenTier.T2.value == "T2_5K"
        assert TokenTier.T3.value == "T3_18K"
        assert TokenTier.T4.value == "T4_40K"

    def test_all_tiers_in_tier_tokens(self):
        for tier in TokenTier:
            assert tier in TIER_TOKENS

    def test_tier_tokens_values_positive(self):
        for tier, tokens in TIER_TOKENS.items():
            assert tokens > 0
            assert isinstance(tokens, int)

    def test_tier_ordering(self):
        values = [
            TIER_TOKENS[TokenTier.T0],
            TIER_TOKENS[TokenTier.T1],
            TIER_TOKENS[TokenTier.T2],
            TIER_TOKENS[TokenTier.T3],
            TIER_TOKENS[TokenTier.T4],
        ]
        assert values == sorted(values)

    def test_enum_is_str_subclass(self):
        for member in TokenTier:
            assert isinstance(member, str)


class TestHallucinationLevel:
    def test_enum_members_exist(self):
        assert HallucinationLevel.L1_FACT.value == "L1_fact_inconsistency"
        assert HallucinationLevel.L2_BLUEPRINT.value == "L2_blueprint_conflict"
        assert HallucinationLevel.L3_SELF_REF.value == "L3_self_refuting"

    def test_enum_is_str_subclass(self):
        for member in HallucinationLevel:
            assert isinstance(member, str)

    def test_three_levels(self):
        assert len(HallucinationLevel) == 3


class TestConstants:
    def test_trim_duplicate_threshold_range(self):
        assert 0.0 < TRIM_DUPLICATE_THRESHOLD < 1.0

    def test_max_history_days_positive(self):
        assert MAX_HISTORY_DAYS > 0
        assert isinstance(MAX_HISTORY_DAYS, int)
