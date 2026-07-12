# [A_test] module_id: SRC-TST-1439 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_regime_gain_scheduling
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.regime_gain_scheduling
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_regime_gain_scheduling.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.regime_gain_scheduling import (
    MarketRegime,
    RegimeGainScheduling,
)


class TestMarketRegimeEnum:
    def test_all_regimes_exist(self):
        assert MarketRegime.CALM.value == "CALM"
        assert MarketRegime.NORMAL.value == "NORMAL"
        assert MarketRegime.VOLATILE.value == "VOLATILE"
        assert MarketRegime.CRISIS.value == "CRISIS"

    def test_regime_from_string(self):
        assert MarketRegime("CALM") is MarketRegime.CALM


class TestRegimeGainSchedulingInstantiation:
    def test_default_instantiation(self):
        rgs = RegimeGainScheduling()
        assert rgs.current_regime == MarketRegime.NORMAL
        assert rgs.current_gain == 1.0
        assert rgs.regime_transition_count == 0

    def test_custom_gain_map(self):
        custom_map = {"CALM": 2.0, "NORMAL": 1.0, "VOLATILE": 0.5, "CRISIS": 0.1}
        rgs = RegimeGainScheduling(gain_map=custom_map)
        assert rgs.gain_map["CALM"] == 2.0


class TestSetRegime:
    def test_set_same_regime_no_transition(self):
        rgs = RegimeGainScheduling()
        rgs.set_regime(MarketRegime.NORMAL)
        assert rgs.regime_transition_count == 0

    def test_set_different_regime_increments_transition(self):
        rgs = RegimeGainScheduling()
        rgs.set_regime(MarketRegime.CALM)
        assert rgs.regime_transition_count == 1
        assert rgs.current_regime == MarketRegime.CALM

    def test_set_regime_updates_gain(self):
        rgs = RegimeGainScheduling()
        gain = rgs.set_regime(MarketRegime.CRISIS)
        assert gain == 0.3
        assert rgs.current_gain == 0.3

    def test_set_regime_calm_high_sensitivity(self):
        rgs = RegimeGainScheduling()
        gain = rgs.set_regime(MarketRegime.CALM)
        assert gain == 1.5


class TestApplyGain:
    def test_apply_normal_gain(self):
        rgs = RegimeGainScheduling()
        assert rgs.apply_gain(10.0) == pytest.approx(10.0)

    def test_apply_crisis_gain(self):
        rgs = RegimeGainScheduling()
        rgs.set_regime(MarketRegime.CRISIS)
        assert rgs.apply_gain(10.0) == pytest.approx(3.0)

    def test_apply_zero_score(self):
        rgs = RegimeGainScheduling()
        assert rgs.apply_gain(0.0) == 0.0

    def test_apply_negative_score(self):
        rgs = RegimeGainScheduling()
        rgs.set_regime(MarketRegime.CALM)
        assert rgs.apply_gain(-10.0) == pytest.approx(-15.0)


class TestDetectRegimeFromVolatility:
    def test_crisis_regime(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.95) == MarketRegime.CRISIS

    def test_volatile_regime(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.75) == MarketRegime.VOLATILE

    def test_calm_regime(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.1) == MarketRegime.CALM

    def test_normal_regime(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.5) == MarketRegime.NORMAL

    def test_boundary_crisis(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.91) == MarketRegime.CRISIS

    def test_boundary_volatile(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.71) == MarketRegime.VOLATILE

    def test_boundary_calm(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.19) == MarketRegime.CALM


class TestRegimeGainSchedulingBoundaries:
    def test_unknown_regime_gain_defaults_to_one(self):
        rgs = RegimeGainScheduling(gain_map={"CALM": 1.5})
        gain = rgs.set_regime(MarketRegime.NORMAL)
        assert gain == 1.0

    def test_zero_volatility(self):
        rgs = RegimeGainScheduling()
        assert rgs.detect_regime_from_volatility(0.0) == MarketRegime.CALM
