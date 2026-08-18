# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §
# [MODULE] tests.backtest.test_shrinkage_provider
# [DOMAIN] D_BACKTEST
# [A_module] module_id=MOD-TEST-BT-PROV | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #B2-shrinkage-provider
"""ShrinkageProvider 系列 (B2) 单元测试——mock 生成器 + ShrinkageAdapter。

覆盖:
  - clamp_shrinkage 工具函数
  - ConstShrinkageProvider 恒定值 + NaN 拒绝
  - ScheduleShrinkageProvider PIT as-of join
  - MockShrinkageProvider 波动率 4 档映射
  - build_schedule_from_results（ShrinkageResult / float）
  - build_schedule_from_detector（fake detector）
  - RegimeDetectorShrinkageAdapter on-demand + 缓存
"""
from __future__ import annotations

import math
from datetime import datetime

import pytest

from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
    MockShrinkageProvider,
    RegimeDetectorShrinkageAdapter,
    ScheduleShrinkageProvider,
    ShrinkageProviderError,
    build_schedule_from_detector,
    build_schedule_from_results,
    clamp_shrinkage,
)

# ── clamp_shrinkage ───────────────────────────────────────────────────

class TestClamp:
    def test_normal_value(self):
        assert clamp_shrinkage(0.6) == 0.6

    def test_above_one_clamps_to_one(self):
        assert clamp_shrinkage(1.5) == 1.0

    def test_negative_clamps_to_zero(self):
        assert clamp_shrinkage(-0.2) == 0.0

    def test_nan_returns_one(self):
        assert clamp_shrinkage(float("nan")) == 1.0

    def test_boundary_zero_and_one(self):
        assert clamp_shrinkage(0.0) == 0.0
        assert clamp_shrinkage(1.0) == 1.0


# ── ConstShrinkageProvider ────────────────────────────────────────────

class TestConstProvider:
    def test_returns_constant(self):
        p = ConstShrinkageProvider(0.7)
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 0.7

    def test_default_is_full_deploy(self):
        p = ConstShrinkageProvider()
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_clamps_above_one(self):
        p = ConstShrinkageProvider(1.5)
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_clamps_negative(self):
        p = ConstShrinkageProvider(-0.1)
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 0.0

    def test_nan_rejected(self):
        with pytest.raises(ShrinkageProviderError):
            ConstShrinkageProvider(float("nan"))


# ── ScheduleShrinkageProvider ─────────────────────────────────────────

class TestScheduleProvider:
    def _sched(self):
        return {
            datetime(2026, 1, 5): 0.8,
            datetime(2026, 1, 10): 0.5,
            datetime(2026, 1, 15): 0.3,
        }

    def test_exact_match(self):
        p = ScheduleShrinkageProvider(self._sched())
        assert p.get_shrinkage(datetime(2026, 1, 10)) == 0.5

    def test_before_first_returns_one(self):
        """查询日期早于 schedule 首条 → 1.0（regime 未启动）。"""
        p = ScheduleShrinkageProvider(self._sched())
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_as_of_join_picks_most_recent(self):
        """PIT as-of join：取 ≤ 查询日期的最近一条。"""
        p = ScheduleShrinkageProvider(self._sched())
        # 1/7 在 1/5 和 1/10 之间 → 取 1/5 的 0.8
        assert p.get_shrinkage(datetime(2026, 1, 7)) == 0.8
        # 1/12 在 1/10 和 1/15 之间 → 取 1/10 的 0.5
        assert p.get_shrinkage(datetime(2026, 1, 12)) == 0.5

    def test_no_future_lookup(self):
        """PIT 铁律：查询日期之前的 schedule 不影响。"""
        p = ScheduleShrinkageProvider(self._sched())
        # 1/3 查询，1/5 的记录尚未发生 → 1.0
        assert p.get_shrinkage(datetime(2026, 1, 3)) == 1.0

    def test_empty_schedule_returns_one(self):
        p = ScheduleShrinkageProvider({})
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_none_schedule_returns_one(self):
        p = ScheduleShrinkageProvider(None)
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_values_clamped(self):
        p = ScheduleShrinkageProvider({datetime(2026, 1, 1): 1.5, datetime(2026, 1, 2): -0.1})
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0
        assert p.get_shrinkage(datetime(2026, 1, 2)) == 0.0


# ── MockShrinkageProvider ─────────────────────────────────────────────

class TestMockProvider:
    def test_low_vol_full_deploy(self):
        """vol < 15% → 1.0（满部署）。"""
        p = MockShrinkageProvider(
            volatility_schedule={datetime(2026, 1, 1): 0.10}
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_mid_vol_light_throttle(self):
        """vol 15-25% → 0.85。"""
        p = MockShrinkageProvider(
            volatility_schedule={datetime(2026, 1, 1): 0.20}
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 0.85

    def test_high_vol_mid_throttle(self):
        """vol 25-40% → 0.60。"""
        p = MockShrinkageProvider(
            volatility_schedule={datetime(2026, 1, 1): 0.35}
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 0.60

    def test_crisis_vol_strong_throttle(self):
        """vol ≥ 40% → 0.30（crisis-like）。"""
        p = MockShrinkageProvider(
            volatility_schedule={datetime(2026, 1, 1): 0.50}
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 0.30

    def test_vol_fn_mode(self):
        """vol_fn 在线计算模式。"""
        p = MockShrinkageProvider(vol_fn=lambda d: 0.30 if d.day > 15 else 0.10)
        assert p.get_shrinkage(datetime(2026, 1, 5)) == 1.0
        assert p.get_shrinkage(datetime(2026, 1, 20)) == 0.60

    def test_vol_fn_exception_fallback(self):
        """vol_fn 异常 → 1.0。"""
        p = MockShrinkageProvider(vol_fn=lambda d: (_ for _ in ()).throw(RuntimeError()))
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_nan_vol_returns_one(self):
        p = MockShrinkageProvider(
            volatility_schedule={datetime(2026, 1, 1): float("nan")}
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_requires_schedule_or_fn(self):
        with pytest.raises(ShrinkageProviderError):
            MockShrinkageProvider()

    def test_schedule_uses_as_of_join(self):
        """schedule 模式复用 ScheduleShrinkageProvider 的 as-of join。"""
        p = MockShrinkageProvider(
            volatility_schedule={
                datetime(2026, 1, 5): 0.20,  # → 0.85
                datetime(2026, 1, 10): 0.45,  # → 0.30
            }
        )
        assert p.get_shrinkage(datetime(2026, 1, 1)) == 1.0  # 未启动
        assert p.get_shrinkage(datetime(2026, 1, 7)) == 0.85
        assert p.get_shrinkage(datetime(2026, 1, 12)) == 0.30


# ── build_schedule_from_results ───────────────────────────────────────

class TestBuildScheduleFromResults:
    def test_from_shrinkage_result_objects(self):
        """从含 .value 字段的 ShrinkageResult-like 对象构建。"""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class _FakeShrinkageResult:
            value: float

        results = [
            (datetime(2026, 1, 1), _FakeShrinkageResult(0.8)),
            (datetime(2026, 1, 2), _FakeShrinkageResult(0.5)),
        ]
        sched = build_schedule_from_results(results)
        assert sched == {datetime(2026, 1, 1): 0.8, datetime(2026, 1, 2): 0.5}

    def test_from_floats(self):
        results = [
            (datetime(2026, 1, 1), 0.8),
            (datetime(2026, 1, 2), 0.5),
        ]
        sched = build_schedule_from_results(results)
        assert sched[datetime(2026, 1, 1)] == 0.8
        assert sched[datetime(2026, 1, 2)] == 0.5

    def test_clamps_values(self):
        results = [(datetime(2026, 1, 1), 1.5), (datetime(2026, 1, 2), -0.2)]
        sched = build_schedule_from_results(results)
        assert sched[datetime(2026, 1, 1)] == 1.0
        assert sched[datetime(2026, 1, 2)] == 0.0

    def test_invalid_payload_raises(self):
        with pytest.raises(ShrinkageProviderError):
            build_schedule_from_results([(datetime(2026, 1, 1), "not-a-number")])

    def test_invalid_entry_shape_raises(self):
        with pytest.raises(ShrinkageProviderError):
            build_schedule_from_results([(datetime(2026, 1, 1),)])  # 一元组

    def test_non_datetime_date_raises(self):
        with pytest.raises(ShrinkageProviderError):
            build_schedule_from_results([("2026-01-01", 0.5)])


# ── build_schedule_from_detector ──────────────────────────────────────

class TestBuildScheduleFromDetector:
    def test_uses_detector_detect_output(self):
        """fake detector 的 detect 返回 value=0.6 → schedule 记 0.6。"""

        class _FakeShrinkageResult:
            def __init__(self, v):
                self.value = v

        class _FakeDetector:
            def __init__(self):
                self.calls = 0

            def detect(self, feats, overlay, risk):
                self.calls += 1
                return (None, _FakeShrinkageResult(0.6))

        detector = _FakeDetector()
        dated_inputs = {
            datetime(2026, 1, 1): ({}, {}, {}),
            datetime(2026, 1, 2): ({}, {}, {}),
        }
        sched = build_schedule_from_detector(detector, dated_inputs)
        assert sched == {datetime(2026, 1, 1): 0.6, datetime(2026, 1, 2): 0.6}
        assert detector.calls == 2

    def test_detect_exception_falls_back_to_one(self):
        class _FakeDetector:
            def detect(self, *args, **kwargs):
                raise RuntimeError("hmm")

        sched = build_schedule_from_detector(
            _FakeDetector(), {datetime(2026, 1, 1): ({}, {}, {})}
        )
        assert sched[datetime(2026, 1, 1)] == 1.0


# ── RegimeDetectorShrinkageAdapter ────────────────────────────────────

class TestRegimeDetectorAdapter:
    def test_on_demand_and_cache(self):
        class _FakeShrinkageResult:
            def __init__(self, v):
                self.value = v

        class _FakeDetector:
            def __init__(self):
                self.calls = 0

            def detect(self, feats, overlay, risk):
                self.calls += 1
                return (None, _FakeShrinkageResult(0.7))

        detector = _FakeDetector()
        adapter = RegimeDetectorShrinkageAdapter(
            detector=detector,
            inputs_provider=lambda d: ({}, {}, {}),
        )

        v1 = adapter.get_shrinkage(datetime(2026, 1, 1))
        assert v1 == 0.7
        assert detector.calls == 1

        # 第二次同日期 → 走缓存，不重复 detect
        v2 = adapter.get_shrinkage(datetime(2026, 1, 1))
        assert v2 == 0.7
        assert detector.calls == 1
        assert datetime(2026, 1, 1) in adapter.cache

    def test_detect_exception_falls_back_to_one(self):
        class _FakeDetector:
            def detect(self, *args, **kwargs):
                raise RuntimeError("boom")

        adapter = RegimeDetectorShrinkageAdapter(
            detector=_FakeDetector(),
            inputs_provider=lambda d: ({}, {}, {}),
        )
        assert adapter.get_shrinkage(datetime(2026, 1, 1)) == 1.0

    def test_respects_detector_shrinkage_disabled(self):
        """detector.shrinkage_enabled=False → detector 返回 1.0，adapter 透传。"""

        class _FakeShrinkageResult:
            def __init__(self, v):
                self.value = v

        class _FakeDetector:
            shrinkage_enabled = False

            def detect(self, feats, overlay, risk):
                # 真实 detector 关时返回 value=1.0
                return (None, _FakeShrinkageResult(1.0))

        adapter = RegimeDetectorShrinkageAdapter(
            detector=_FakeDetector(),
            inputs_provider=lambda d: ({}, {}, {}),
        )
        assert adapter.get_shrinkage(datetime(2026, 1, 1)) == 1.0
