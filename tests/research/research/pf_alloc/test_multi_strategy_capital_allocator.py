# [BLUEPRINT] MOD-PA-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MultiStrategyCapitalAllocator 单元测试 (MOD-PA-003)。"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from zephyr.pf_alloc.core.multi_strategy_capital_allocator import (
    AllocationConfig,
    AllocationResult,
    InvalidAllocationInputError,
    MultiStrategyCapitalAllocator,
    StrategyAllocationRequest,
)

T0 = datetime(2026, 8, 1, 10, 0, tzinfo=timezone.utc)
TODAY = date(2026, 8, 1)


def reqs() -> list[StrategyAllocationRequest]:
    return [
        StrategyAllocationRequest("TREND", 0.6, capacity=0.5),
        StrategyAllocationRequest("MR", 0.4, capacity=0.4),
    ]


# ── 归一化 + 容量 ─────────────────────────────────────────────────────────────


def test_weights_sum_to_one():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), now=T0, today=TODAY)
    assert result.total_weight == pytest.approx(1.0)
    assert result.rebalance_allowed is True


def test_capacity_caps_weight():
    # TREND signal 0.6 but capacity 0.5 → capped to 0.5; MR 0.4 cap 0.4
    # normalized: TREND=0.5/0.9, MR=0.4/0.9
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), now=T0, today=TODAY)
    w = result.weights
    assert w["TREND"] == pytest.approx(0.5 / 0.9)
    assert w["MR"] == pytest.approx(0.4 / 0.9)


def test_capacity_not_exceeded():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), now=T0, today=TODAY)
    # 归一后权重不可超容量 (容量是相对上限, 归一后可能略超, 这里校验 raw 不超)
    for a in result.allocations:
        assert a.raw_weight <= a.capacity + 1e-9


# ── MaxDDLimit ────────────────────────────────────────────────────────────────


def test_max_dd_triggered_reduces():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), max_drawdown=0.20, now=T0, today=TODAY)  # 20% > 15%
    assert result.max_dd_triggered is True
    assert result.reduction_factor == pytest.approx(0.5)


def test_max_dd_not_triggered_below_threshold():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), max_drawdown=0.10, now=T0, today=TODAY)
    assert result.max_dd_triggered is False


# ── 冷启动 ────────────────────────────────────────────────────────────────────


def test_cold_start_active_within_observation_period():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), cold_start_days_elapsed=2, now=T0, today=TODAY)
    assert result.cold_start_active is True
    # reduction = 0.30 (cold_start_factor), 且 ≤ 0.50 cap
    assert result.reduction_factor == pytest.approx(0.30)


def test_cold_start_inactive_after_observation():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), cold_start_days_elapsed=5, now=T0, today=TODAY)
    assert result.cold_start_active is False
    assert result.reduction_factor == pytest.approx(1.0)


def test_cold_start_combined_with_max_dd():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), max_drawdown=0.20, cold_start_days_elapsed=2, now=T0, today=TODAY)
    assert result.max_dd_triggered is True
    assert result.cold_start_active is True
    # 0.5 (MaxDD) × 0.3 (cold) = 0.15, ≤ 0.50 cap
    assert result.reduction_factor == pytest.approx(0.15)


# ── 再平衡频率 ────────────────────────────────────────────────────────────────


def test_rebalance_frequency_blocks_second_same_day():
    alloc = MultiStrategyCapitalAllocator()
    r1 = alloc.allocate(reqs(), now=T0, today=TODAY)
    assert r1.rebalance_allowed is True
    r2 = alloc.allocate(reqs(), now=T0, today=TODAY)  # 同日第二次
    assert r2.rebalance_allowed is False
    assert r2.allocations == []  # 沿用上次 (调用方职责)


def test_rebalance_allowed_next_day():
    alloc = MultiStrategyCapitalAllocator()
    alloc.allocate(reqs(), now=T0, today=TODAY)
    next_day = date(2026, 8, 2)
    r2 = alloc.allocate(reqs(), now=T0, today=next_day)
    assert r2.rebalance_allowed is True


# ── 风险预算 ──────────────────────────────────────────────────────────────────


def test_risk_budget_proportional_to_weight():
    alloc = MultiStrategyCapitalAllocator()
    result = alloc.allocate(reqs(), now=T0, today=TODAY)
    total_rb = sum(a.risk_budget for a in result.allocations)
    assert total_rb == pytest.approx(1.0)  # total_risk_budget default 1.0
    for a in result.allocations:
        assert a.risk_budget == pytest.approx(a.target_weight)


# ── 输入校验 ──────────────────────────────────────────────────────────────────


def test_empty_requests_raises():
    alloc = MultiStrategyCapitalAllocator()
    with pytest.raises(InvalidAllocationInputError):
        alloc.allocate([], now=T0, today=TODAY)


def test_negative_signal_weight_raises():
    alloc = MultiStrategyCapitalAllocator()
    with pytest.raises(InvalidAllocationInputError):
        alloc.allocate([StrategyAllocationRequest("X", -0.5)], now=T0, today=TODAY)


def test_capacity_out_of_range_raises():
    alloc = MultiStrategyCapitalAllocator()
    with pytest.raises(InvalidAllocationInputError):
        alloc.allocate([StrategyAllocationRequest("X", 0.5, capacity=1.5)], now=T0, today=TODAY)


def test_negative_max_drawdown_raises():
    alloc = MultiStrategyCapitalAllocator()
    with pytest.raises(InvalidAllocationInputError):
        alloc.allocate(reqs(), max_drawdown=-0.1, now=T0, today=TODAY)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


def test_config_max_dd_threshold_range():
    with pytest.raises(InvalidAllocationInputError):
        AllocationConfig(max_dd_threshold=1.5)


def test_config_cold_start_factor_range():
    with pytest.raises(InvalidAllocationInputError):
        AllocationConfig(cold_start_factor=1.5)


# ── 可配置 ────────────────────────────────────────────────────────────────────


def test_custom_max_dd_threshold():
    cfg = AllocationConfig(max_dd_threshold=0.10, max_dd_reduction=0.40)
    alloc = MultiStrategyCapitalAllocator(config=cfg)
    # 12% > 自定义 10% → 触发
    result = alloc.allocate(reqs(), max_drawdown=0.12, now=T0, today=TODAY)
    assert result.max_dd_triggered is True
    assert result.reduction_factor == pytest.approx(0.40)
