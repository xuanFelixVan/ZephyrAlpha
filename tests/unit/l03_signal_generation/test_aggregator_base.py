"""
单元测试：src/zephyr/l03_signal_generation/aggregator_base.py
=============================================================

覆盖矩阵：
  SignalAggregatorBase (ABC):
    - 抽象类不可实例化 × 1
    - normalize_signal 裁剪 × 2
    - 注册表登记 × 1
  CapitalAllocatorBase (ABC):
    - 抽象类不可实例化 × 1
  DegradationMonitorBase (ABC):
    - 抽象类不可实例化 × 1
"""

import pytest
from zephyr.l03_signal_generation.aggregator_base import (
    CapitalAllocatorBase,
    DegradationMonitorBase,
    SignalAggregatorBase,
)


class TestSignalAggregatorBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            SignalAggregatorBase()

    def test_normalize_signal_clips_upper(self):
        assert SignalAggregatorBase.normalize_signal(5.0) == 3.0

    def test_normalize_signal_clips_lower(self):
        assert SignalAggregatorBase.normalize_signal(-5.0) == -3.0

    def test_normalize_signal_within_range(self):
        assert SignalAggregatorBase.normalize_signal(1.5) == 1.5

    def test_registry_exists(self):
        assert hasattr(SignalAggregatorBase, "_registry")
        assert isinstance(SignalAggregatorBase._registry, dict)


class TestCapitalAllocatorBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            CapitalAllocatorBase()


class TestDegradationMonitorBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            DegradationMonitorBase()
