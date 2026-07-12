# [A_test] module_id: SRC-TST-0272 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_adaptive_threshold
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from collections import deque

from zephyr.gov_enforcement.rule_enforcement.adaptive_threshold import AdaptiveThreshold, ThresholdState


class TestThresholdState:
    def test_default_history_is_deque_maxlen_100(self) -> None:
        state = ThresholdState(gate_id="G1", current_threshold=0.8)
        assert isinstance(state.history, deque)
        assert state.history.maxlen == 100

    def test_fields_assigned(self) -> None:
        state = ThresholdState(gate_id="G2", current_threshold=0.5)
        assert state.gate_id == "G2"
        assert state.current_threshold == 0.5
        assert len(state.history) == 0

    def test_explicit_history_preserved(self) -> None:
        h: deque[float] = deque([1.0, 2.0], maxlen=50)
        state = ThresholdState(gate_id="G3", current_threshold=0.9, history=h)
        assert state.history is h
        assert len(state.history) == 2


class TestAdaptiveThresholdInit:
    def test_default_params(self) -> None:
        at = AdaptiveThreshold()
        assert at._window == 50
        assert at._smoothing == 0.2
        assert at._states == {}

    def test_custom_params(self) -> None:
        at = AdaptiveThreshold(window=20, smoothing=0.5)
        assert at._window == 20
        assert at._smoothing == 0.5


class TestGetState:
    def test_creates_new_state_with_default_initial(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("G1")
        assert state.gate_id == "G1"
        assert state.current_threshold == 0.8
        assert len(state.history) == 0

    def test_creates_new_state_with_custom_initial(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("G1", initial=0.3)
        assert state.current_threshold == 0.3

    def test_returns_same_state_for_same_gate_id(self) -> None:
        at = AdaptiveThreshold()
        s1 = at.get_state("G1")
        s2 = at.get_state("G1")
        assert s1 is s2

    def test_different_gate_ids_independent(self) -> None:
        at = AdaptiveThreshold()
        s1 = at.get_state("G1", initial=0.5)
        s2 = at.get_state("G2", initial=0.9)
        assert s1 is not s2
        assert s1.current_threshold == 0.5
        assert s2.current_threshold == 0.9


class TestObserve:
    def test_fail_increases_threshold(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "FAIL")
        assert new_t > initial

    def test_pass_decreases_threshold(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "PASS")
        assert new_t < initial

    def test_invalid_outcome_no_change(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        initial = 0.5
        at.get_state("G1", initial=initial)
        new_t = at.observe("G1", 0.6, "MAYBE")
        assert new_t == initial

    def test_value_appended_to_history(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.7, "PASS")
        state = at.get_state("G1")
        assert 0.7 in state.history

    def test_threshold_clamped_upper(self) -> None:
        at = AdaptiveThreshold(smoothing=0.5)
        at.get_state("G1", initial=0.99)
        new_t = at.observe("G1", 1.0, "FAIL")
        assert new_t <= 0.99

    def test_threshold_clamped_lower(self) -> None:
        at = AdaptiveThreshold(smoothing=0.5)
        at.get_state("G1", initial=0.1)
        new_t = at.observe("G1", 0.0, "PASS")
        assert new_t >= 0.1

    def test_observe_creates_state_if_missing(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("NEW_GATE", 0.5, "PASS")
        assert "NEW_GATE" in at._states
        assert isinstance(new_t, float)

    def test_multiple_observations_accumulate(self) -> None:
        at = AdaptiveThreshold(smoothing=0.2)
        at.get_state("G1", initial=0.5)
        t1 = at.observe("G1", 0.6, "FAIL")
        t2 = at.observe("G1", 0.6, "FAIL")
        assert t2 > t1


class TestEwma:
    def test_empty_history_returns_current_threshold(self) -> None:
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.75)
        assert at.ewma("G1") == 0.75

    def test_single_value_returns_that_value(self) -> None:
        at = AdaptiveThreshold()
        at.observe("G1", 0.6, "PASS")
        result = at.ewma("G1")
        assert result == 0.6

    def test_multiple_values_computes_ewma(self) -> None:
        at = AdaptiveThreshold(window=3)
        at.observe("G1", 1.0, "PASS")
        at.observe("G1", 0.0, "FAIL")
        state = at.get_state("G1")
        history = list(state.history)
        alpha = 2.0 / (min(len(history), 3) + 1)
        expected = history[0]
        for v in history[1:]:
            expected = alpha * v + (1 - alpha) * expected
        result = at.ewma("G1")
        assert abs(result - expected) < 1e-10

    def test_ewma_creates_state_if_missing(self) -> None:
        at = AdaptiveThreshold()
        result = at.ewma("UNKNOWN")
        assert result == 0.8


class TestBoundaryConditions:
    def test_smoothing_zero_no_adjustment(self) -> None:
        at = AdaptiveThreshold(smoothing=0.0)
        at.get_state("G1", initial=0.5)
        new_t = at.observe("G1", 0.6, "FAIL")
        assert new_t == 0.5

    def test_smoothing_zero_pass_no_adjustment(self) -> None:
        at = AdaptiveThreshold(smoothing=0.0)
        at.get_state("G1", initial=0.5)
        new_t = at.observe("G1", 0.6, "PASS")
        assert new_t == 0.5

    def test_history_respects_maxlen(self) -> None:
        at = AdaptiveThreshold()
        at.get_state("G1", initial=0.5)
        for i in range(150):
            at.observe("G1", float(i) / 150.0, "PASS")
        state = at.get_state("G1")
        assert len(state.history) == 100

    def test_empty_string_gate_id(self) -> None:
        at = AdaptiveThreshold()
        state = at.get_state("", initial=0.4)
        assert state.gate_id == ""
        assert state.current_threshold == 0.4

    def test_negative_value_observed(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("G1", -1.0, "PASS")
        assert isinstance(new_t, float)

    def test_large_value_observed(self) -> None:
        at = AdaptiveThreshold()
        new_t = at.observe("G1", 999.0, "FAIL")
        assert isinstance(new_t, float)

    def test_window_one(self) -> None:
        at = AdaptiveThreshold(window=1)
        at.observe("G1", 0.5, "PASS")
        at.observe("G1", 0.8, "FAIL")
        result = at.ewma("G1")
        assert isinstance(result, float)
