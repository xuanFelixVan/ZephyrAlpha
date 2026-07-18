# [A_test] module_id: SRC-TST-1064 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-389 | docs/03_modules/_domain_governance/blueprint.md | §test
# [MODULE] tests.test_gov_microstructure_defense
# [INVARIANTS] DEFENSE_STRATEGIES覆盖所有DefenseType;FidelityFactor.composite_ff正确
# [MODIFY-GUARD] src/zephyr/governance/microstructure_defense.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_gov_microstructure_defense.py
# [TTL] task_bound

from __future__ import annotations

import pytest

md_mod = pytest.importorskip("zephyr.security.access_control.microstructure_defense")
DefenseType = md_mod.DefenseType
DefenseStrategy = md_mod.DefenseStrategy
DEFENSE_STRATEGIES = md_mod.DEFENSE_STRATEGIES
FidelityFactor = md_mod.FidelityFactor
DEFAULT_FIDELITY = md_mod.DEFAULT_FIDELITY


class TestDefenseType:
    def test_all_values(self):
        assert DefenseType.HFT_FRONT_RUN.value == "HFT_FRONT_RUN"
        assert DefenseType.STOP_HUNTING.value == "STOP_HUNTING"
        assert DefenseType.SPREAD_EXPLOIT.value == "SPREAD_EXPLOIT"
        assert DefenseType.ORDER_BOOK_HOLLOW.value == "ORDER_BOOK_HOLLOW"
        assert DefenseType.GAPPING.value == "GAPPING"

    def test_member_count(self):
        assert len(DefenseType) == 5

    def test_is_str_enum(self):
        assert isinstance(DefenseType.HFT_FRONT_RUN, str)

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            DefenseType("INVALID")


class TestDefenseStrategy:
    def test_create_strategy(self):
        ds = DefenseStrategy(
            defense=DefenseType.HFT_FRONT_RUN,
            threat="test threat",
            countermeasure="test counter",
        )
        assert ds.defense == DefenseType.HFT_FRONT_RUN
        assert ds.threat == "test threat"
        assert ds.countermeasure == "test counter"

    def test_strategy_is_pydantic_model(self):
        ds = DefenseStrategy(
            defense=DefenseType.STOP_HUNTING,
            threat="t",
            countermeasure="c",
        )
        assert hasattr(ds, "model_dump")


class TestDefenseStrategies:
    def test_all_types_have_strategies(self):
        for dt in DefenseType:
            assert dt in DEFENSE_STRATEGIES, f"Missing strategy for {dt}"

    def test_strategy_matches_type(self):
        for dt, strategy in DEFENSE_STRATEGIES.items():
            assert strategy.defense == dt

    def test_strategy_has_threat(self):
        for dt, strategy in DEFENSE_STRATEGIES.items():
            assert len(strategy.threat) > 0, f"Empty threat for {dt}"

    def test_strategy_has_countermeasure(self):
        for dt, strategy in DEFENSE_STRATEGIES.items():
            assert len(strategy.countermeasure) > 0, f"Empty countermeasure for {dt}"


class TestFidelityFactor:
    def test_default_values(self):
        ff = FidelityFactor()
        assert ff.fill_probability == 0.85
        assert ff.slippage == 0.30
        assert ff.order_book_depth == 0.20
        assert ff.partial_fill == 0.60

    def test_composite_ff_calculation(self):
        ff = FidelityFactor(fill_probability=1.0, slippage=1.0, order_book_depth=1.0, partial_fill=1.0)
        expected = 1.0 * 0.30 + 1.0 * 0.35 + 1.0 * 0.20 + 1.0 * 0.15
        assert abs(ff.composite_ff - round(expected, 4)) < 1e-6

    def test_composite_ff_zero(self):
        ff = FidelityFactor(fill_probability=0.0, slippage=0.0, order_book_depth=0.0, partial_fill=0.0)
        assert ff.composite_ff == 0.0

    def test_composite_ff_default(self):
        ff = FidelityFactor()
        assert isinstance(ff.composite_ff, float)
        assert 0.0 <= ff.composite_ff <= 1.0

    def test_description_is_string(self):
        ff = FidelityFactor()
        assert isinstance(ff.description, str)
        assert len(ff.description) > 0

    def test_description_contains_percentage(self):
        ff = FidelityFactor()
        assert "%" in ff.description

    def test_custom_values(self):
        ff = FidelityFactor(fill_probability=0.5, slippage=0.5, order_book_depth=0.5, partial_fill=0.5)
        assert ff.composite_ff > 0.0
        assert ff.composite_ff < 1.0


class TestDefaultFidelity:
    def test_is_fidelity_factor(self):
        assert isinstance(DEFAULT_FIDELITY, FidelityFactor)

    def test_has_composite(self):
        assert DEFAULT_FIDELITY.composite_ff > 0.0
