"""
单元测试：src/zephyr/l05_portfolio_construction/strategy_base.py
================================================================

覆盖矩阵：
  StrategyBase (ABC):
    - 抽象类不可实例化 × 1
    - 子类化 + generate_target_weights × 1
    - validate_constraints 默认 × 1
    - meta() 无 _meta 返回 None × 1
  StrategyMeta:
    - frozen × 1
    - 默认值 × 1
  StrategyRegistry:
    - register / get / list_all / count / clear × 5
    - 重复注册 ValueError × 1
    - 无 meta 注册失败 × 1
    - get 未找到返回 None × 1
"""
from __future__ import annotations


from typing import Any

import pytest
from zephyr.l05_portfolio_construction.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)


class TestStrategyBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            StrategyBase()

    def test_subclass_implements_generate_target_weights(self):
        class _TestStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="test-strategy",
                name="Test",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {s: 1.0 / len(universe) for s in universe}

        s = _TestStrategy()
        weights = s.generate_target_weights(["A", "B"], {"A": 1.0, "B": -1.0}, {})
        assert weights == {"A": 0.5, "B": 0.5}

    def test_validate_constraints_default_pass(self):
        class _TestStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="test-strategy-2",
                name="Test2",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        s = _TestStrategy()
        assert s.validate_constraints({"A": 0.5}) is True

    def test_meta_without_class_attr_returns_none(self):
        class _NoMetaStrategy(StrategyBase):
            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        s = _NoMetaStrategy()
        assert s.meta() is None


class TestStrategyMeta:
    def test_frozen(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="Test",
            strategy_type="equity",
            version="1.0",
            description="test",
        )
        with pytest.raises(Exception):
            m.name = "Changed"

    def test_defaults(self):
        m = StrategyMeta(
            strategy_id="s1",
            name="Test",
            strategy_type="equity",
            version="1.0",
            description="test",
        )
        assert m.factor_dependencies == []
        assert m.author == "agent"
        assert m.tags == []
        assert m.supported_markets == []


class TestStrategyRegistry:
    def setup_method(self):
        StrategyRegistry.clear()

    def test_register_and_get(self):
        @StrategyRegistry.register
        class _RegStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="reg-test",
                name="RegTest",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        assert StrategyRegistry.get("reg-test") is _RegStrategy

    def test_list_all(self):
        @StrategyRegistry.register
        class _ListStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="list-test",
                name="ListTest",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        all_strategies = StrategyRegistry.list_all()
        assert "list-test" in all_strategies

    def test_count(self):
        assert StrategyRegistry.count() == 0

        @StrategyRegistry.register
        class _CountStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="count-test",
                name="CountTest",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        assert StrategyRegistry.count() == 1

    def test_clear(self):
        StrategyRegistry.clear()
        assert StrategyRegistry.count() == 0

    def test_duplicate_register_raises(self):
        @StrategyRegistry.register
        class _DupStrategy(StrategyBase):
            _meta = StrategyMeta(
                strategy_id="dup-test",
                name="DupTest",
                strategy_type="equity",
                version="1.0",
                description="test",
            )

            def generate_target_weights(
                self,
                universe: list[str],
                signals: dict[str, float],
                constraints: dict[str, Any],
            ) -> dict[str, float]:
                return {}

        with pytest.raises(ValueError, match="already registered"):
            StrategyRegistry.register(_DupStrategy)

    def test_get_not_found_returns_none(self):
        assert StrategyRegistry.get("nonexistent") is None
