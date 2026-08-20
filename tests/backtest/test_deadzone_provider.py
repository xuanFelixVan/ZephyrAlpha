# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_deadzone_provider
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-TEST-BT-DEADZONE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-C1-RUNNER-001 #deadzone-optimization
"""DeadzoneShrinkageProvider 单元测试——死区装饰器（Turnover 优化）。

覆盖:
  - 微抖过滤（变化 < deadzone 保持上次）
  - 大幅调整保留（变化 >= deadzone 更新）
  - deadzone=0 透传（退化为 inner 行为）
  - 首次调用直接返回 raw
  - reset() 清状态
  - 负 deadzone 抛错
  - 满足 ShrinkageProvider 协议
  - 包装 ScheduleShrinkageProvider 端到端
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from zephyr.backtest.implementations.shrinkage_engine import ShrinkageProvider
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
    DeadzoneShrinkageProvider,
    ScheduleShrinkageProvider,
    ShrinkageProviderError,
)


def _dt(i: int) -> datetime:
    return datetime(2024, 1, 1) + timedelta(days=i)


class TestDeadzoneCore:
    """死区核心逻辑。"""

    def test_first_call_returns_raw(self):
        """首次调用无 last_effective → 直接返回 raw（不过滤）。"""
        inner = ConstShrinkageProvider(0.8)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        assert dz.get_shrinkage(_dt(0)) == pytest.approx(0.8)

    def test_small_change_filtered(self):
        """变化 < deadzone → 保持上次（过滤微抖）。"""
        schedule = {_dt(0): 0.80, _dt(1): 0.805}  # Δ=0.005 < 0.02
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        first = dz.get_shrinkage(_dt(0))  # 0.80
        second = dz.get_shrinkage(_dt(1))  # raw=0.805, Δ=0.005<0.02 → 保持 0.80
        assert first == pytest.approx(0.80)
        assert second == pytest.approx(0.80)  # 被过滤

    def test_large_change_passed(self):
        """变化 >= deadzone → 更新（保留有效调整）。"""
        schedule = {_dt(0): 0.80, _dt(1): 0.60}  # Δ=0.20 >= 0.02
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        first = dz.get_shrinkage(_dt(0))  # 0.80
        second = dz.get_shrinkage(_dt(1))  # raw=0.60, Δ=0.20>=0.02 → 更新
        assert first == pytest.approx(0.80)
        assert second == pytest.approx(0.60)

    def test_boundary_just_above_deadzone_passed(self):
        """变化略大于 deadzone → 更新（用 0.025 避开 0.82-0.80 浮点陷阱）。"""
        schedule = {_dt(0): 0.80, _dt(1): 0.825}  # Δ=0.025 > 0.02
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        dz.get_shrinkage(_dt(0))
        assert dz.get_shrinkage(_dt(1)) == pytest.approx(0.825)  # 略大于阈值 → 更新

    def test_deadzone_zero_passthrough(self):
        """deadzone=0 → 退化为透传（与 inner 行为一致）。"""
        schedule = {_dt(0): 0.80, _dt(1): 0.801, _dt(2): 0.802}
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.0)
        assert dz.get_shrinkage(_dt(0)) == pytest.approx(0.80)
        assert dz.get_shrinkage(_dt(1)) == pytest.approx(0.801)
        assert dz.get_shrinkage(_dt(2)) == pytest.approx(0.802)

    def test_accumulated_filtering(self):
        """连续微抖：多次小变化被过滤，直到大幅变化触发更新（基于 last_effective）。"""
        # 0.80→0.81(Δ0.01<0.02 过滤,保持0.80)→0.84(Δ0.04 vs last=0.80 更新)
        schedule = {_dt(0): 0.80, _dt(1): 0.81, _dt(2): 0.84}
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        assert dz.get_shrinkage(_dt(0)) == pytest.approx(0.80)
        assert dz.get_shrinkage(_dt(1)) == pytest.approx(0.80)  # Δ0.01 过滤
        assert dz.get_shrinkage(_dt(2)) == pytest.approx(0.84)  # Δ0.04 vs 0.80 更新


class TestDeadzoneState:
    """状态管理。"""

    def test_reset_clears_state(self):
        """reset() 后首次调用重新返回 raw。"""
        inner = ConstShrinkageProvider(0.8)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        dz.get_shrinkage(_dt(0))  # 设置 last_effective=0.8
        dz.reset()
        assert dz._last_effective is None
        # reset 后首次调用返回 raw
        assert dz.get_shrinkage(_dt(1)) == pytest.approx(0.8)

    def test_negative_deadzone_raises(self):
        """负 deadzone → ShrinkageProviderError。"""
        with pytest.raises(ShrinkageProviderError, match="deadzone"):
            DeadzoneShrinkageProvider(ConstShrinkageProvider(1.0), deadzone=-0.01)


class TestDeadzoneProtocol:
    """协议与集成。"""

    def test_satisfies_shrinkage_provider_protocol(self):
        """DeadzoneShrinkageProvider 满足 ShrinkageProvider 协议（runtime_checkable）。"""
        dz = DeadzoneShrinkageProvider(ConstShrinkageProvider(1.0), deadzone=0.02)
        assert isinstance(dz, ShrinkageProvider)

    def test_wraps_schedule_end_to_end(self):
        """包装 ScheduleShrinkageProvider 端到端：危机期调整保留，平稳期微抖过滤。"""
        # 模拟真实序列：平稳期微抖 + 危机期大跌
        schedule = {
            _dt(0): 0.95,  # 平稳
            _dt(1): 0.948,  # 微抖 Δ0.002 → 过滤
            _dt(2): 0.951,  # 微抖 Δ0.003 → 过滤
            _dt(3): 0.60,  # 危机 Δ0.35 → 更新
            _dt(4): 0.59,  # 危机微抖 Δ0.01 → 过滤
            _dt(5): 0.90,  # 回升 Δ0.31 → 更新
        }
        inner = ScheduleShrinkageProvider(schedule)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.02)
        results = [dz.get_shrinkage(_dt(i)) for i in range(6)]
        assert results[0] == pytest.approx(0.95)
        assert results[1] == pytest.approx(0.95)  # 微抖过滤
        assert results[2] == pytest.approx(0.95)  # 微抖过滤
        assert results[3] == pytest.approx(0.60)  # 危机更新
        assert results[4] == pytest.approx(0.60)  # 危机微抖过滤
        assert results[5] == pytest.approx(0.90)  # 回升更新

    def test_properties(self):
        """deadzone / inner 属性可读。"""
        inner = ConstShrinkageProvider(0.8)
        dz = DeadzoneShrinkageProvider(inner, deadzone=0.05)
        assert dz.deadzone == pytest.approx(0.05)
        assert dz.inner is inner
