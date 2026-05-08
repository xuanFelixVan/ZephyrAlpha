"""
单元测试：src/zephyr/l02_alpha_factor/factors/momentum_factor.py + value_factor.py
==================================================================================

覆盖矩阵：
  Momentum20d:
    - compute 默认窗口 × 1
    - compute 自定义窗口 × 1
    - validate 数据不足 × 1
    - validate 缺少 close 列 × 1
    - 注册表已注册 × 1
  ValueFactor:
    - compute 默认 × 1
    - validate 数据不足 × 1
    - 注册表已注册 × 1
"""

import numpy as np
import pandas as pd
import pytest
from zephyr.l02_alpha_factor.factor_base import FactorRegistry
from zephyr.l02_alpha_factor.factors.momentum_factor import Momentum20d
from zephyr.l02_alpha_factor.factors.value_factor import ValueFactor


@pytest.fixture(autouse=True)
def _ensure_factors_registered():
    if "momentum_20d" not in FactorRegistry._registry:
        FactorRegistry.register(Momentum20d)
    if "value_factor" not in FactorRegistry._registry:
        FactorRegistry.register(ValueFactor)


class TestMomentum20d:
    def test_compute_default_window(self):
        data = pd.DataFrame({"close": np.random.randn(30).cumsum() + 100})
        factor = Momentum20d()
        result = factor.compute(data)
        assert len(result) == len(data)
        assert result.iloc[20] != 0

    def test_compute_custom_window(self):
        data = pd.DataFrame({"close": np.random.randn(30).cumsum() + 100})
        factor = Momentum20d()
        result = factor.compute(data, window=10)
        assert len(result) == len(data)

    def test_validate_insufficient_data(self):
        data = pd.DataFrame({"close": [1.0, 2.0]})
        factor = Momentum20d()
        assert factor.validate(data) is False

    def test_validate_missing_close(self):
        data = pd.DataFrame({"open": np.random.randn(30)})
        factor = Momentum20d()
        assert factor.validate(data) is False

    def test_registered_in_registry(self):
        assert "momentum_20d" in FactorRegistry._registry


class TestValueFactor:
    def test_compute_default(self):
        data = pd.DataFrame({"close": np.random.randn(70).cumsum() + 100})
        factor = ValueFactor()
        result = factor.compute(data)
        assert len(result) == len(data)

    def test_validate_insufficient_data(self):
        data = pd.DataFrame({"close": np.random.randn(10)})
        factor = ValueFactor()
        assert factor.validate(data) is False

    def test_registered_in_registry(self):
        assert "value_factor" in FactorRegistry._registry
