# [BLUEPRINT] MOD-PF-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""Strategy Engine 单元测试 (MOD-PF-001)。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.governance.strategies.strategy_base import StrategyBase, StrategyMeta
from zephyr.pf_core.core.strategy_engine import (
    ColdStartViolationError,
    DecisionDimension,
    StrategyDecision,
    StrategyEngine,
    StrategyEngineConfig,
    StrategyLifecycleError,
    StrategyNotFoundError,
    StrategyStatus,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)


def _meta(sid="s1", version="1.0.0"):
    return StrategyMeta(
        strategy_id=sid,
        name=f"Test {sid}",
        strategy_type="momentum",
        version=version,
        description="test strategy",
    )


class _StubStrategy(StrategyBase):
    """简单测试策略: 按 signal strength 比例分配权重。"""

    _meta = _meta()

    def __init__(self, weights=None):
        self._weights = weights

    def generate_target_weights(self, universe, signals, constraints):
        if self._weights is not None:
            return {s: self._weights.get(s, 0.0) for s in universe}
        total = sum(abs(v) for v in signals.values()) or 1.0
        return {s: max(0.0, signals.get(s, 0.0)) / total for s in universe}


class _FixedClock:
    def __init__(self, start=T0):
        self.t = start

    def __call__(self):
        return self.t

    def advance(self, **kwargs):
        self.t = self.t + timedelta(**kwargs)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_invalid_cold_start_factor_zero():
    with pytest.raises(ColdStartViolationError):
        StrategyEngineConfig(cold_start_factor=0)


def test_config_invalid_cold_start_factor_over_one():
    with pytest.raises(ColdStartViolationError):
        StrategyEngineConfig(cold_start_factor=1.5)


def test_config_invalid_max_strategies():
    with pytest.raises(StrategyLifecycleError):
        StrategyEngineConfig(max_strategies=0)


def test_config_invalid_ic_decay_threshold():
    with pytest.raises(StrategyLifecycleError):
        StrategyEngineConfig(ic_decay_threshold=0)


# ── 注册 ──────────────────────────────────────────────────────────────────────


def test_register_returns_event():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    event = engine.register(_StubStrategy())
    assert event.new_status == "registered"
    assert event.previous_status == "(none)"
    assert event.strategy_id == "s1"
    assert event.idempotency_key  # 非空


def test_register_duplicate_same_version_raises():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    with pytest.raises(StrategyLifecycleError):
        engine.register(_StubStrategy())


def test_register_version_bump_archives_old():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy(weights={"A": 0.5, "B": 0.5}))
    # 推进到 ACTIVE
    clock.advance(days=1)
    engine.transition("s1", StrategyStatus.TESTING)
    clock.advance(days=8)
    engine.transition("s1", StrategyStatus.ACTIVE)

    # 版本变更: 注册 v2.0.0
    new_strat = _StubStrategy(weights={"A": 0.3, "B": 0.7})
    new_strat._meta = _meta(version="2.0.0")
    engine.register(new_strat)

    record = engine.get_record("s1")
    assert record.version == "2.0.0"
    assert record.status == StrategyStatus.REGISTERED
    # 旧版本被归档为 DEPRECATED (在生命周期日志中)
    deprecate_events = [e for e in engine.lifecycle_log if e.new_status == "deprecated" and e.reason == "version_bump"]
    assert len(deprecate_events) == 1


def test_register_missing_meta_raises():
    class _NoMeta(StrategyBase):
        def generate_target_weights(self, universe, signals, constraints):
            return {}

    engine = StrategyEngine(clock=_FixedClock())
    with pytest.raises(StrategyLifecycleError):
        engine.register(_NoMeta())


def test_register_exceeds_max_strategies():
    cfg = StrategyEngineConfig(max_strategies=2)
    engine = StrategyEngine(config=cfg, clock=_FixedClock())
    for i in range(2):
        s = _StubStrategy()
        s._meta = _meta(sid=f"s{i}")
        engine.register(s)
    s = _StubStrategy()
    s._meta = _meta(sid="sX")
    with pytest.raises(StrategyLifecycleError):
        engine.register(s)


# ── 生命周期状态机 ────────────────────────────────────────────────────────────


def test_valid_transition_registered_to_testing():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    event = engine.transition("s1", StrategyStatus.TESTING)
    assert event.new_status == "testing"
    assert engine.get_record("s1").status == StrategyStatus.TESTING


def test_transition_to_active_requires_testing_period():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=7)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    clock.advance(days=3)  # 未满 7 天
    with pytest.raises(StrategyLifecycleError):
        engine.transition("s1", StrategyStatus.ACTIVE)


def test_transition_to_active_after_testing_period():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=7)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    clock.advance(days=8)
    event = engine.transition("s1", StrategyStatus.ACTIVE)
    assert event.new_status == "active"
    assert engine.get_record("s1").activated_at is not None


def test_deprecated_is_terminal_cannot_resurrect():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.DEPRECATED)
    with pytest.raises(StrategyLifecycleError):
        engine.transition("s1", StrategyStatus.ACTIVE)


def test_skip_transition_registered_to_active_raises():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    with pytest.raises(StrategyLifecycleError):
        engine.transition("s1", StrategyStatus.ACTIVE)  # 跳过 TESTING


def test_transition_unknown_strategy_raises():
    engine = StrategyEngine(clock=_FixedClock())
    with pytest.raises(StrategyNotFoundError):
        engine.transition("nope", StrategyStatus.TESTING)


def test_idempotent_same_status_transition():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    # 重复同状态转换: 不报错, 记录事件
    event = engine.transition("s1", StrategyStatus.TESTING)
    assert event.new_status == "testing"


def test_demote_active_to_testing():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    event = engine.transition("s1", StrategyStatus.TESTING, reason="performance_drop")
    assert event.new_status == "testing"


# ── 冷启动协议 ────────────────────────────────────────────────────────────────


def test_cold_start_active_right_after_activation():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0, cold_start_days=7, cold_start_factor=0.3)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy(weights={"A": 0.6, "B": 0.4}))
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.6, "B": 0.4})
    assert decision.cold_start_active is True
    # 权重被 ×0.3 后归一化, 比例不变
    assert decision.target_weights["A"] == pytest.approx(0.6, rel=1e-6)
    assert decision.target_weights["B"] == pytest.approx(0.4, rel=1e-6)


def test_cold_start_expires_after_period():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0, cold_start_days=7)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy(weights={"A": 0.5, "B": 0.5}))
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    clock.advance(days=8)  # 超过冷启动期
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.5, "B": 0.5})
    assert decision.cold_start_active is False


def test_cold_start_not_active_for_testing_strategy():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy(weights={"A": 1.0}))
    engine.transition("s1", StrategyStatus.TESTING)
    decision = engine.evaluate("s1", ["A"], {"A": 1.0})
    assert decision.cold_start_active is False


def test_cold_start_zero_days_disables():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0, cold_start_days=0)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy(weights={"A": 1.0}))
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    decision = engine.evaluate("s1", ["A"], {"A": 1.0})
    assert decision.cold_start_active is False


# ── 决策聚合 ──────────────────────────────────────────────────────────────────


def test_evaluate_splits_buy_sell_signals():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    universe = ["A", "B", "C"]
    signals = {"A": 0.6, "B": -0.3, "C": 0.1}
    decision = engine.evaluate("s1", universe, signals)
    assert len(decision.buy_signals) == 2  # A, C
    assert len(decision.sell_signals) == 1  # B
    assert all(s.dimension == DecisionDimension.BUY for s in decision.buy_signals)
    assert all(s.dimension == DecisionDimension.SELL for s in decision.sell_signals)


def test_evaluate_normalizes_weights():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.3, "B": 0.7})
    total = sum(decision.target_weights.values())
    assert total == pytest.approx(1.0, rel=1e-6)


def test_evaluate_filters_universe_outside_symbols():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy(weights={"A": 0.5, "B": 0.5, "X": 0.9}))
    engine.transition("s1", StrategyStatus.TESTING)
    # universe 不含 X
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.5, "B": 0.5})
    assert "X" not in decision.target_weights
    assert set(decision.target_weights.keys()) == {"A", "B"}


def test_evaluate_zero_weights_returns_empty():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    strat = _StubStrategy(weights={"A": 0.0, "B": 0.0})
    engine.register(strat)
    engine.transition("s1", StrategyStatus.TESTING)
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.0, "B": 0.0})
    assert decision.target_weights == {}


def test_evaluate_registered_strategy_not_runnable():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    with pytest.raises(StrategyLifecycleError):
        engine.evaluate("s1", ["A"], {"A": 1.0})


def test_evaluate_deprecated_strategy_not_runnable():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.DEPRECATED)
    with pytest.raises(StrategyLifecycleError):
        engine.evaluate("s1", ["A"], {"A": 1.0})


def test_evaluate_has_idempotency_key():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    d1 = engine.evaluate("s1", ["A"], {"A": 1.0})
    d2 = engine.evaluate("s1", ["A"], {"A": 1.0})
    assert d1.idempotency_key != d2.idempotency_key


def test_decision_to_dict():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.6, "B": -0.4})
    d = decision.to_dict()
    assert d["strategy_id"] == "s1"
    assert d["buy_signals"] == 1
    assert d["sell_signals"] == 1
    assert d["cold_start_active"] is False


# ── 退化检测 ──────────────────────────────────────────────────────────────────


def test_detect_degradation_ic_decay_over_threshold():
    engine = StrategyEngine(config=StrategyEngineConfig(ic_decay_threshold=0.5), clock=_FixedClock())
    engine.register(_StubStrategy())
    # 基线 IC=0.10, 最近 IC=0.03 → 衰减 70% > 50%
    ic_history = [0.10, 0.09, 0.08, 0.05, 0.03]
    assert engine.detect_degradation("s1", ic_history) is True


def test_detect_degradation_no_decay():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    ic_history = [0.05, 0.06, 0.07, 0.08]
    assert engine.detect_degradation("s1", ic_history) is False


def test_detect_degradation_insufficient_history():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    assert engine.detect_degradation("s1", [0.05]) is False
    assert engine.detect_degradation("s1", []) is False


def test_auto_degrade_transitions_active_to_deprecated():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0, ic_decay_threshold=0.5)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    ic_history = [0.10, 0.09, 0.08, 0.05, 0.03]
    event = engine.auto_degrade("s1", ic_history)
    assert event is not None
    assert event.new_status == "deprecated"
    assert engine.get_record("s1").status == StrategyStatus.DEPRECATED


def test_auto_degrade_no_action_when_not_degraded():
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    event = engine.auto_degrade("s1", [0.05, 0.06, 0.07])
    assert event is None
    assert engine.get_record("s1").status == StrategyStatus.ACTIVE


# ── 选择 / 查询 ──────────────────────────────────────────────────────────────


def test_select_active_returns_only_active():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    s1 = _StubStrategy()
    s1._meta = _meta(sid="s1")
    s2 = _StubStrategy()
    s2._meta = _meta(sid="s2")
    engine.register(s1)
    engine.register(s2)
    engine.transition("s1", StrategyStatus.TESTING)
    assert len(engine.select_active()) == 0
    assert len(engine.select_runnable()) == 1  # s1 TESTING


def test_count_and_list_all():
    engine = StrategyEngine(clock=_FixedClock())
    s1 = _StubStrategy()
    s1._meta = _meta(sid="s1")
    s2 = _StubStrategy()
    s2._meta = _meta(sid="s2")
    engine.register(s1)
    engine.register(s2)
    assert engine.count() == 2
    assert len(engine.list_all()) == 2


def test_get_record_unknown_returns_none():
    engine = StrategyEngine(clock=_FixedClock())
    assert engine.get_record("nope") is None


# ── 生命周期日志 ──────────────────────────────────────────────────────────────


def test_lifecycle_log_records_all_events():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    # 至少 2 个事件 (register + testing)
    assert len(engine.lifecycle_log) >= 2
    statuses = [e.new_status for e in engine.lifecycle_log]
    assert "registered" in statuses
    assert "testing" in statuses


def test_lifecycle_event_has_idempotency_key():
    engine = StrategyEngine(clock=_FixedClock())
    event = engine.register(_StubStrategy())
    assert event.idempotency_key
    # 每个事件的幂等键唯一
    e2 = engine.transition("s1", StrategyStatus.TESTING)
    assert event.idempotency_key != e2.idempotency_key


# ── 不变量 ────────────────────────────────────────────────────────────────────


def test_invariant_weights_sum_to_one_when_nonzero():
    clock = _FixedClock()
    engine = StrategyEngine(clock=clock)
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    for _ in range(5):
        decision = engine.evaluate("s1", ["A", "B", "C"], {"A": 0.3, "B": 0.5, "C": 0.2})
        if decision.target_weights:
            assert sum(decision.target_weights.values()) == pytest.approx(1.0, rel=1e-6)


def test_invariant_no_resurrection_from_deprecated():
    engine = StrategyEngine(clock=_FixedClock())
    engine.register(_StubStrategy())
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.DEPRECATED)
    for target in (StrategyStatus.ACTIVE, StrategyStatus.TESTING, StrategyStatus.REGISTERED):
        with pytest.raises(StrategyLifecycleError):
            engine.transition("s1", target)


def test_invariant_cold_start_scales_weights():
    """冷启动期: 权重比例不变但绝对值受 factor 约束 (归一化后比例守恒)。"""
    clock = _FixedClock()
    cfg = StrategyEngineConfig(min_testing_days=0, cold_start_days=7, cold_start_factor=0.3)
    engine = StrategyEngine(config=cfg, clock=clock)
    engine.register(_StubStrategy(weights={"A": 0.75, "B": 0.25}))
    engine.transition("s1", StrategyStatus.TESTING)
    engine.transition("s1", StrategyStatus.ACTIVE)
    decision = engine.evaluate("s1", ["A", "B"], {"A": 0.75, "B": 0.25})
    # 归一化后比例仍为 3:1
    assert decision.target_weights["A"] == pytest.approx(0.75, rel=1e-6)
    assert decision.target_weights["B"] == pytest.approx(0.25, rel=1e-6)
    assert decision.cold_start_active is True
