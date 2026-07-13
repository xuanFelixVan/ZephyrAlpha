# [A_test] module_id: SRC-TST-1312 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_nonstationary_effectiveness
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.nonstationary_effectiveness
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_nonstationary_effectiveness.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.nonstationary_effectiveness import (
    EffectivenessState,
    NonstationaryEffectiveness,
)


class TestEffectivenessState:
    def test_nominal_value(self):
        assert EffectivenessState.NOMINAL.value == "NOMINAL"

    def test_degrading_value(self):
        assert EffectivenessState.DEGRADING.value == "DEGRADING"

    def test_ineffective_value(self):
        assert EffectivenessState.INEFFECTIVE.value == "INEFFECTIVE"

    def test_all_states_count(self):
        assert len(EffectivenessState) == 3


class TestNonstationaryEffectivenessInstantiation:
    def test_default_instantiation(self):
        ne = NonstationaryEffectiveness()
        assert ne.window_size == 50
        assert ne.degradation_threshold == 0.3
        assert ne.state == EffectivenessState.NOMINAL
        assert ne.baseline_score == 0.8
        assert ne.current_score == 0.8
        assert ne.rolling_window == []
        assert ne.degradation_started_at == 0.0

    def test_custom_instantiation(self):
        ne = NonstationaryEffectiveness(window_size=100, degradation_threshold=0.5)
        assert ne.window_size == 100
        assert ne.degradation_threshold == 0.5


class TestRecordOutcome:
    def test_record_success(self):
        ne = NonstationaryEffectiveness()
        state = ne.record_outcome(True)
        assert len(ne.rolling_window) == 1
        assert ne.rolling_window[0] == 1.0

    def test_record_failure(self):
        ne = NonstationaryEffectiveness()
        state = ne.record_outcome(False)
        assert ne.rolling_window[0] == 0.0

    def test_record_returns_state(self):
        ne = NonstationaryEffectiveness()
        state = ne.record_outcome(True)
        assert isinstance(state, EffectivenessState)

    def test_window_trims_to_size(self):
        ne = NonstationaryEffectiveness(window_size=5)
        for _ in range(10):
            ne.record_outcome(True)
        assert len(ne.rolling_window) == 5

    def test_nominal_with_high_success_rate(self):
        ne = NonstationaryEffectiveness(window_size=20, baseline_score=0.8)
        for _ in range(20):
            ne.record_outcome(True)
        assert ne.state == EffectivenessState.NOMINAL

    def test_ineffective_with_high_failure_rate(self):
        ne = NonstationaryEffectiveness(window_size=50, baseline_score=0.8, degradation_threshold=0.3)
        for _ in range(50):
            ne.record_outcome(False)
        assert ne.state == EffectivenessState.INEFFECTIVE

    def test_degrading_intermediate(self):
        ne = NonstationaryEffectiveness(window_size=50, baseline_score=0.9, degradation_threshold=0.3)
        for _ in range(35):
            ne.record_outcome(True)
        for _ in range(15):
            ne.record_outcome(False)
        assert ne.state in (EffectivenessState.DEGRADING, EffectivenessState.INEFFECTIVE, EffectivenessState.NOMINAL)


class TestNeedsRecalibration:
    def test_nominal_does_not_need_recalibration(self):
        ne = NonstationaryEffectiveness()
        ne.state = EffectivenessState.NOMINAL
        assert ne.needs_recalibration() is False

    def test_ineffective_needs_recalibration(self):
        ne = NonstationaryEffectiveness()
        ne.state = EffectivenessState.INEFFECTIVE
        assert ne.needs_recalibration() is True

    def test_degrading_does_not_need_recalibration(self):
        ne = NonstationaryEffectiveness()
        ne.state = EffectivenessState.DEGRADING
        assert ne.needs_recalibration() is False
