# [A_test] module_id: SRC-TST-1207 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] zephyr.pf_core
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l05_portfolio_construction.py
# [TTL] task_bound

from __future__ import annotations

import pytest

l05 = pytest.importorskip("zephyr.pf_core", reason="l05-portfolio-construction not importable")

from zephyr.pf_core.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
    autodiscover_strategies,
)


class _ConcreteStrategy(StrategyBase):
    _meta = StrategyMeta(
        strategy_id="test_strat_001",
        name="TestStrategy",
        strategy_type="momentum",
        version="1.0.0",
        description="A test strategy for unit testing",
        factor_dependencies=["alpha_001"],
        author="test",
        tags=["test"],
        supported_markets=["US"],
    )

    def generate_target_weights(self, universe, signals, constraints):
        weights = {}
        for sym in universe:
            sig = signals.get(sym, 0.0)
            weights[sym] = max(0.0, min(1.0, sig))
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        return weights


class _AnotherStrategy(StrategyBase):
    _meta = StrategyMeta(
        strategy_id="test_strat_002",
        name="AnotherStrategy",
        strategy_type="mean_reversion",
        version="1.0.0",
        description="Another test strategy",
    )

    def generate_target_weights(self, universe, signals, constraints):
        return {sym: 1.0 / len(universe) for sym in universe} if universe else {}


class TestStrategyMeta:
    def test_creation_required_fields(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="Strategy1",
            strategy_type="momentum",
            version="2.0",
            description="desc",
        )
        assert m.strategy_id == "s1"
        assert m.name == "Strategy1"
        assert m.strategy_type == "momentum"
        assert m.version == "2.0"

    def test_defaults(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="S1",
            strategy_type="t",
            version="1.0",
            description="d",
        )
        assert m.factor_dependencies == []
        assert m.author == "agent"
        assert m.tags == []
        assert m.supported_markets == []

    def test_frozen(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="S1",
            strategy_type="t",
            version="1.0",
            description="d",
        )
        with pytest.raises(AttributeError):
            m.strategy_id = "other"

    def test_custom_fields(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="S1",
            strategy_type="t",
            version="1.0",
            description="d",
            factor_dependencies=["f1", "f2"],
            author="human",
            tags=["alpha"],
            supported_markets=["US", "HK"],
        )
        assert len(m.factor_dependencies) == 2
        assert m.author == "human"
        assert "US" in m.supported_markets


class TestStrategyBase:
    def test_generate_target_weights(self):
        s = _ConcreteStrategy()
        weights = s.generate_target_weights(
            ["AAPL", "GOOG"],
            {"AAPL": 0.6, "GOOG": 0.4},
            {},
        )
        assert "AAPL" in weights
        assert "GOOG" in weights
        assert abs(sum(weights.values()) - 1.0) < 1e-9

    def test_validate_constraints_default(self):
        s = _ConcreteStrategy()
        assert s.validate_constraints({}) is True

    def test_meta_classmethod(self):
        m = _ConcreteStrategy.meta()
        assert m is not None
        assert m.strategy_id == "test_strat_001"

    def test_on_fill_noop(self):
        s = _ConcreteStrategy()
        s.on_fill(None)

    def test_on_risk_alert_noop(self):
        s = _ConcreteStrategy()
        s.on_risk_alert(None)

    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            StrategyBase()

    def test_empty_universe(self):
        s = _ConcreteStrategy()
        weights = s.generate_target_weights([], {}, {})
        assert weights == {}

    def test_zero_signals(self):
        s = _ConcreteStrategy()
        weights = s.generate_target_weights(["AAPL"], {"AAPL": 0.0}, {})
        assert weights == {"AAPL": 0.0}

    def test_negative_signal_clamped(self):
        s = _ConcreteStrategy()
        weights = s.generate_target_weights(["AAPL"], {"AAPL": -0.5}, {})
        assert weights["AAPL"] == 0.0


class TestStrategyRegistry:
    def setup_method(self):
        StrategyRegistry.clear()

    def test_register_and_get(self):
        StrategyRegistry.register(_ConcreteStrategy)
        result = StrategyRegistry.get("test_strat_001")
        assert result is _ConcreteStrategy

    def test_get_nonexistent(self):
        assert StrategyRegistry.get("nonexistent") is None

    def test_list_all_empty(self):
        assert StrategyRegistry.list_all() == {}

    def test_list_all_with_entries(self):
        StrategyRegistry.register(_ConcreteStrategy)
        StrategyRegistry.register(_AnotherStrategy)
        all_strats = StrategyRegistry.list_all()
        assert len(all_strats) == 2
        assert "test_strat_001" in all_strats
        assert "test_strat_002" in all_strats

    def test_count(self):
        assert StrategyRegistry.count() == 0
        StrategyRegistry.register(_ConcreteStrategy)
        assert StrategyRegistry.count() == 1
        StrategyRegistry.register(_AnotherStrategy)
        assert StrategyRegistry.count() == 2

    def test_clear(self):
        StrategyRegistry.register(_ConcreteStrategy)
        StrategyRegistry.clear()
        assert StrategyRegistry.count() == 0

    def test_duplicate_registration_raises(self):
        StrategyRegistry.register(_ConcreteStrategy)
        with pytest.raises(ValueError, match="already registered"):
            StrategyRegistry.register(_ConcreteStrategy)


class TestAutodiscoverStrategies:
    def test_nonexistent_package(self):
        result = autodiscover_strategies("zephyr.nonexistent.package")
        assert result == 0

    def test_default_package_no_error(self):
        result = autodiscover_strategies()
        assert isinstance(result, int)
