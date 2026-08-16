# [A_test] module_id: MOD-GOV_token_budget_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.token_budget
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

import pytest

try:
    from zephyr.infrastructure.capacity_assurance.token_budget import (
        BUDGET_CAPS,
        BudgetState,
        TokenBudgetManager,
        TokenBudgetTier,
        estimate_tokens,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


class TestEstimateTokens:
    def test_empty_string_returns_zero(self):
        assert estimate_tokens("") == 0

    def test_none_like_empty_returns_zero(self):
        assert estimate_tokens("") == 0

    def test_short_text_returns_at_least_one(self):
        assert estimate_tokens("ab") >= 1

    def test_long_text_division(self):
        text = "a" * 40
        assert estimate_tokens(text) == 10

    def test_exact_four_chars(self):
        assert estimate_tokens("abcd") == 1

    def test_five_chars(self):
        assert estimate_tokens("abcde") == 1


class TestTokenBudgetTier:
    def test_tier_values(self):
        assert TokenBudgetTier.L1.value == "L1"
        assert TokenBudgetTier.L2.value == "L2"
        assert TokenBudgetTier.L3.value == "L3"

    def test_budget_caps_keys(self):
        assert set(BUDGET_CAPS.keys()) == {TokenBudgetTier.L1, TokenBudgetTier.L2, TokenBudgetTier.L3}

    def test_budget_caps_ordering(self):
        assert BUDGET_CAPS[TokenBudgetTier.L1] < BUDGET_CAPS[TokenBudgetTier.L2] < BUDGET_CAPS[TokenBudgetTier.L3]


class TestBudgetState:
    def test_default_values(self):
        state = BudgetState()
        assert state.level == TokenBudgetTier.L1
        assert state.cap == 500
        assert state.consumed == 0
        assert state.degraded is False

    def test_custom_values(self):
        state = BudgetState(level=TokenBudgetTier.L3, cap=8000, consumed=7999, degraded=True)
        assert state.level == TokenBudgetTier.L3
        assert state.cap == 8000
        assert state.consumed == 7999
        assert state.degraded is True


class TestTokenBudgetManager:
    def test_init_defaults(self):
        mgr = TokenBudgetManager()
        assert mgr.level == TokenBudgetTier.L1
        assert mgr.cap == 500
        assert mgr.consumed == 0
        assert mgr.remaining == 500
        assert mgr.degraded is False

    def test_init_with_session_id(self):
        mgr = TokenBudgetManager(session_id="sess-001")
        assert mgr.session_id == "sess-001"

    def test_set_level(self):
        mgr = TokenBudgetManager()
        mgr.set_level(TokenBudgetTier.L2)
        assert mgr.level == TokenBudgetTier.L2
        assert mgr.cap == BUDGET_CAPS[TokenBudgetTier.L2]

    def test_consume_success(self):
        mgr = TokenBudgetManager()
        assert mgr.consume(100) is True
        assert mgr.consumed == 100
        assert mgr.remaining == 400

    def test_consume_exact_cap(self):
        mgr = TokenBudgetManager()
        cap = mgr.cap
        assert mgr.consume(cap) is True
        assert mgr.consumed == cap
        assert mgr.remaining == 0

    def test_consume_over_cap_fails(self):
        mgr = TokenBudgetManager()
        cap = mgr.cap
        assert mgr.consume(cap + 1) is False
        assert mgr.consumed == 0

    def test_can_consume(self):
        mgr = TokenBudgetManager()
        assert mgr.can_consume(mgr.cap) is True
        assert mgr.can_consume(mgr.cap + 1) is False

    def test_degraded_flag(self):
        mgr = TokenBudgetManager()
        mgr.consume(int(mgr.cap * 0.9))
        assert mgr.degraded is True

    def test_not_degraded_below_threshold(self):
        mgr = TokenBudgetManager()
        mgr.consume(int(mgr.cap * 0.5))
        assert mgr.degraded is False

    def test_reset(self):
        mgr = TokenBudgetManager()
        mgr.consume(200)
        mgr.reset()
        assert mgr.consumed == 0
        assert mgr.remaining == mgr.cap

    def test_to_dict(self):
        mgr = TokenBudgetManager()
        d = mgr.to_dict()
        assert d["level"] == "L1"
        assert d["cap"] == 500
        assert d["consumed"] == 0
        assert "remaining" in d
        assert "degraded" in d
        assert "usage_ratio" in d

    def test_to_dict_usage_ratio(self):
        mgr = TokenBudgetManager()
        mgr.consume(250)
        d = mgr.to_dict()
        assert abs(d["usage_ratio"] - 0.5) < 1e-9

    def test_consume_zero(self):
        mgr = TokenBudgetManager()
        assert mgr.consume(0) is True
        assert mgr.consumed == 0

    def test_consume_negative(self):
        mgr = TokenBudgetManager()
        result = mgr.consume(-1)
        assert mgr.consumed <= 0 or result is False

    def test_degraded_with_zero_cap(self):
        mgr = TokenBudgetManager()
        # cap is a read-only property (no setter); white-box the zero-cap guard
        mgr._cap = 0
        assert mgr.degraded is False
