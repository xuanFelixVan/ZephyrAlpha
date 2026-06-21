# [A_test] module_id: SRC-TST-0599 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md | §
# [MODULE] tests.test_context_optimizer
# [INVARIANTS] ONBOARDING_MAX_ROUNDS=3; should_load_onboarding returns True for rounds < 3; increment_round increments per session
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_context_optimizer.py

import pytest
from zephyr.autonomy_core.context_optimizer import ContextOptimizer


class TestContextOptimizerInstantiation:
    def test_has_onboarding_max_rounds(self):
        assert hasattr(ContextOptimizer, "ONBOARDING_MAX_ROUNDS")

    def test_onboarding_max_rounds_value(self):
        assert ContextOptimizer.ONBOARDING_MAX_ROUNDS == 3

    def test_has_conversation_round_dict(self):
        assert isinstance(ContextOptimizer._conversation_round, dict)


class TestShouldLoadOnboarding:
    def setup_method(self):
        ContextOptimizer._conversation_round.clear()

    def test_returns_true_for_new_session(self):
        assert ContextOptimizer.should_load_onboarding("session-new") is True

    def test_returns_true_for_round_below_max(self):
        ContextOptimizer._conversation_round["session-a"] = 0
        assert ContextOptimizer.should_load_onboarding("session-a") is True

    def test_returns_true_for_round_just_below_max(self):
        ContextOptimizer._conversation_round["session-b"] = 2
        assert ContextOptimizer.should_load_onboarding("session-b") is True

    def test_returns_false_at_max_round(self):
        ContextOptimizer._conversation_round["session-c"] = 3
        assert ContextOptimizer.should_load_onboarding("session-c") is False

    def test_returns_false_above_max_round(self):
        ContextOptimizer._conversation_round["session-d"] = 10
        assert ContextOptimizer.should_load_onboarding("session-d") is False

    def test_different_sessions_independent(self):
        ContextOptimizer._conversation_round["session-x"] = 5
        assert ContextOptimizer.should_load_onboarding("session-y") is True

    def test_empty_string_session_id(self):
        assert ContextOptimizer.should_load_onboarding("") is True


class TestIncrementRound:
    def setup_method(self):
        ContextOptimizer._conversation_round.clear()

    def test_increment_returns_1_for_new_session(self):
        result = ContextOptimizer.increment_round("session-new")
        assert result == 1

    def test_increment_increments_existing(self):
        ContextOptimizer._conversation_round["session-a"] = 2
        result = ContextOptimizer.increment_round("session-a")
        assert result == 3

    def test_increment_updates_internal_state(self):
        ContextOptimizer.increment_round("session-z")
        assert ContextOptimizer._conversation_round["session-z"] == 1
        ContextOptimizer.increment_round("session-z")
        assert ContextOptimizer._conversation_round["session-z"] == 2

    def test_increment_different_sessions_independent(self):
        ContextOptimizer.increment_round("session-1")
        ContextOptimizer.increment_round("session-2")
        ContextOptimizer.increment_round("session-1")
        assert ContextOptimizer._conversation_round["session-1"] == 2
        assert ContextOptimizer._conversation_round["session-2"] == 1

    def test_increment_then_should_load_onboarding(self):
        ContextOptimizer._conversation_round.clear()
        sid = "session-integration"
        for i in range(3):
            assert ContextOptimizer.should_load_onboarding(sid) is True
            ContextOptimizer.increment_round(sid)
        assert ContextOptimizer.should_load_onboarding(sid) is False
