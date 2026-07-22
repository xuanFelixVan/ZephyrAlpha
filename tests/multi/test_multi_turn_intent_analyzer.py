# [A_test] module_id: MOD-GOV_multi_turn_intent_analyzer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_multi_turn_intent_analyzer

# [INVARIANTS] 测试不可跳过;覆盖实例化+公开方法+边界

# [MODIFY-GUARD] src/zephyr/escalation-engine/multi_turn_intent_analyzer.py

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 测试失败必须包含具体断言信息

# [TESTS] tests/test_multi_turn_intent_analyzer.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.context_governance.multi_turn_intent_analyzer import MultiTurnIntentAnalyzer


class TestMultiTurnIntentAnalyzerInit:
    def test_init_creates_empty_history(self):
        analyzer = MultiTurnIntentAnalyzer()
        assert analyzer._turn_history == []

    def test_init_history_is_list(self):
        analyzer = MultiTurnIntentAnalyzer()
        assert isinstance(analyzer._turn_history, list)

    def test_init_history_length_zero(self):
        analyzer = MultiTurnIntentAnalyzer()
        assert len(analyzer._turn_history) == 0


class TestRecordTurn:
    def test_record_single_turn(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "query", "text": "hello"})
        assert len(analyzer._turn_history) == 1
        assert analyzer._turn_history[0] == {"intent": "query", "text": "hello"}

    def test_record_multiple_turns(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "query"})
        analyzer.record_turn({"intent": "command"})
        analyzer.record_turn({"intent": "override"})
        assert len(analyzer._turn_history) == 3

    def test_record_turn_empty_dict(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({})
        assert len(analyzer._turn_history) == 1
        assert analyzer._turn_history[0] == {}

    def test_record_turn_preserves_all_keys(self):
        analyzer = MultiTurnIntentAnalyzer()
        turn = {"intent": "query", "role": "user", "timestamp": 1234567890}
        analyzer.record_turn(turn)
        assert analyzer._turn_history[0]["role"] == "user"
        assert analyzer._turn_history[0]["timestamp"] == 1234567890

    def test_record_turn_none_value_in_dict(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": None})
        assert analyzer._turn_history[0]["intent"] is None

    def test_record_turn_missing_intent_key(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"text": "no intent field"})
        assert "intent" not in analyzer._turn_history[0]


class TestAccumulatedIntent:
    def test_empty_history_returns_normal(self):
        analyzer = MultiTurnIntentAnalyzer()
        assert analyzer.accumulated_intent() == "normal"

    def test_normal_intents_return_normal(self):
        analyzer = MultiTurnIntentAnalyzer()
        for i in range(5):
            analyzer.record_turn({"intent": "query"})
        assert analyzer.accumulated_intent() == "normal"

    def test_override_keyword_returns_suspicious(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "override security"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_bypass_keyword_returns_suspicious(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "bypass check"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_sudo_keyword_returns_suspicious(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "sudo access"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_force_keyword_returns_suspicious(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "force delete"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_keyword_case_insensitive(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "OVERRIDE"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_keyword_mixed_case(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "Bypass"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_suspicious_outside_window_not_detected(self):
        analyzer = MultiTurnIntentAnalyzer()
        for _ in range(5):
            analyzer.record_turn({"intent": "query"})
        analyzer.record_turn({"intent": "override"})
        for _ in range(5):
            analyzer.record_turn({"intent": "query"})
        assert analyzer.accumulated_intent(window_turns=5) == "normal"

    def test_suspicious_within_window_detected(self):
        analyzer = MultiTurnIntentAnalyzer()
        for _ in range(4):
            analyzer.record_turn({"intent": "query"})
        analyzer.record_turn({"intent": "override"})
        assert analyzer.accumulated_intent(window_turns=5) == "suspicious"

    def test_window_turns_one(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "query"})
        analyzer.record_turn({"intent": "override"})
        assert analyzer.accumulated_intent(window_turns=1) == "suspicious"

    def test_window_turns_one_normal(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "override"})
        analyzer.record_turn({"intent": "query"})
        assert analyzer.accumulated_intent(window_turns=1) == "normal"

    def test_missing_intent_key_treated_as_empty(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({})
        assert analyzer.accumulated_intent() == "normal"

    def test_none_intent_raises_typeerror(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": None})
        with pytest.raises(TypeError):
            analyzer.accumulated_intent()

    def test_keyword_as_substring_detected(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "bypassing the check"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_keyword_embedded_in_word(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "bypassing"})
        assert analyzer.accumulated_intent() == "suspicious"

    def test_default_window_is_five(self):
        analyzer = MultiTurnIntentAnalyzer()
        for _ in range(6):
            analyzer.record_turn({"intent": "query"})
        analyzer.record_turn({"intent": "override"})
        assert analyzer.accumulated_intent() == "suspicious"
        for _ in range(5):
            analyzer.record_turn({"intent": "query"})
        assert analyzer.accumulated_intent() == "normal"


class TestShouldEscalate:
    def test_returns_false_when_normal(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "query"})
        assert analyzer.should_escalate() is False

    def test_returns_true_when_suspicious(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "override"})
        assert analyzer.should_escalate() is True

    def test_returns_false_on_empty_history(self):
        analyzer = MultiTurnIntentAnalyzer()
        assert analyzer.should_escalate() is False

    def test_escalation_changes_with_history(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "query"})
        assert analyzer.should_escalate() is False
        analyzer.record_turn({"intent": "sudo"})
        assert analyzer.should_escalate() is True

    def test_escalation_resets_when_suspicious_exits_window(self):
        analyzer = MultiTurnIntentAnalyzer()
        analyzer.record_turn({"intent": "force"})
        assert analyzer.should_escalate() is True
        for _ in range(5):
            analyzer.record_turn({"intent": "query"})
        assert analyzer.should_escalate() is False
