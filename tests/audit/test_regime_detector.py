# [A_test] module_id: SRC-TST-1438 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] tests.test_regime_detector
# [INVARIANTS] MacroFactor_enum_complete;MacroRegime_enum_complete;MACRO_INDICATORS_covers_all_factors
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_regime_detector.py
# [TTL] task_bound

from zephyr.gov_drift.detector_core.regime_detector import (
    MACRO_INDICATORS,
    REGIME_ALLOCATIONS,
    REGIME_SWITCH_SIGNALS,
    FactorSignal,
    MacroFactor,
    MacroRegime,
)


class TestMacroFactor:
    def test_all_members_exist(self):
        expected = {"ECONOMIC_GROWTH", "MONETARY_POLICY", "INFLATION", "CREDIT_CONDITIONS", "RISK_APPETITE"}
        actual = {m.name for m in MacroFactor}
        assert actual == expected

    def test_str_enum_values(self):
        for member in MacroFactor:
            assert member.value == member.name

    def test_from_value(self):
        assert MacroFactor("INFLATION") is MacroFactor.INFLATION


class TestMacroRegime:
    def test_all_members_exist(self):
        expected = {"EXPANSION", "STAGFLATION", "TIGHTENING", "CRISIS"}
        actual = {m.name for m in MacroRegime}
        assert actual == expected

    def test_str_enum_values(self):
        for member in MacroRegime:
            assert member.value == member.name

    def test_from_value(self):
        assert MacroRegime("CRISIS") is MacroRegime.CRISIS


class TestFactorSignal:
    def test_creation_with_defaults(self):
        sig = FactorSignal(factor=MacroFactor.INFLATION, indicator="CPI")
        assert sig.factor == MacroFactor.INFLATION
        assert sig.indicator == "CPI"
        assert sig.current_value == ""

    def test_creation_with_current_value(self):
        sig = FactorSignal(factor=MacroFactor.RISK_APPETITE, indicator="VIX", current_value="25.3")
        assert sig.current_value == "25.3"

    def test_model_dump(self):
        sig = FactorSignal(factor=MacroFactor.ECONOMIC_GROWTH, indicator="PMI")
        d = sig.model_dump()
        assert d["factor"] == MacroFactor.ECONOMIC_GROWTH
        assert d["indicator"] == "PMI"


class TestMacroIndicators:
    def test_covers_all_factors(self):
        assert set(MACRO_INDICATORS.keys()) == set(MacroFactor)

    def test_each_signal_matches_its_factor(self):
        for factor, signal in MACRO_INDICATORS.items():
            assert signal.factor == factor

    def test_indicators_not_empty(self):
        for factor, signal in MACRO_INDICATORS.items():
            assert len(signal.indicator) > 0


class TestRegimeAllocations:
    def test_covers_all_regimes(self):
        assert set(REGIME_ALLOCATIONS.keys()) == set(MacroRegime)

    def test_allocations_not_empty(self):
        for regime, allocation in REGIME_ALLOCATIONS.items():
            assert len(allocation) > 0


class TestRegimeSwitchSignals:
    def test_signals_not_empty(self):
        assert len(REGIME_SWITCH_SIGNALS) > 0

    def test_each_signal_is_nonempty_string(self):
        for signal in REGIME_SWITCH_SIGNALS:
            assert isinstance(signal, str)
            assert len(signal) > 0
