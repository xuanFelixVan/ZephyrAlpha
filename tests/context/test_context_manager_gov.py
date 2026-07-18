# [A_test] module_id: SRC-TST-0597 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-369 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_context_manager_gov
# [INVARIANTS] TIER_TOKENS keys must match TokenTier; TRIM_DUPLICATE_THRESHOLD in (0,1)
# [MODIFY-GUARD] Changes must sync with context_manager.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_context_manager_gov.py
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
    def test_enum_values(self):
        assert TokenTier.T0.value == "T0_500"
        assert TokenTier.T4.value == "T4_40K"

    def test_enum_count(self):
        assert len(TokenTier) == 5

    def test_all_values_unique(self):
        values = [t.value for t in TokenTier]
        assert len(values) == len(set(values))


class TestTierTokens:
    def test_keys_match_token_tier(self):
        assert set(TIER_TOKENS.keys()) == set(TokenTier)

    def test_all_values_positive(self):
        for tier, tokens in TIER_TOKENS.items():
            assert tokens > 0, f"Non-positive tokens for {tier}"

    def test_tokens_increase_with_tier(self):
        tiers = list(TokenTier)
        for i in range(len(tiers) - 1):
            assert TIER_TOKENS[tiers[i]] < TIER_TOKENS[tiers[i + 1]]

    def test_t0_is_500(self):
        assert TIER_TOKENS[TokenTier.T0] == 500

    def test_t4_is_40000(self):
        assert TIER_TOKENS[TokenTier.T4] == 40000


class TestHallucinationLevel:
    def test_enum_values(self):
        assert HallucinationLevel.L1_FACT.value == "L1_fact_inconsistency"
        assert HallucinationLevel.L2_BLUEPRINT.value == "L2_blueprint_conflict"
        assert HallucinationLevel.L3_SELF_REF.value == "L3_self_refuting"

    def test_enum_count(self):
        assert len(HallucinationLevel) == 3


class TestTrimDuplicateThreshold:
    def test_in_range(self):
        assert 0.0 < TRIM_DUPLICATE_THRESHOLD < 1.0

    def test_is_float(self):
        assert isinstance(TRIM_DUPLICATE_THRESHOLD, float)


class TestMaxHistoryDays:
    def test_is_positive(self):
        assert MAX_HISTORY_DAYS > 0

    def test_is_integer(self):
        assert isinstance(MAX_HISTORY_DAYS, int)
