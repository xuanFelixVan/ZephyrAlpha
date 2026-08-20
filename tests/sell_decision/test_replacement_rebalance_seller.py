"""MOD-SELL-006 置换与再平衡卖出 单元测试。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.replacement_rebalance_seller import (
    InvalidRebalanceInputError,
    ReplacementRebalanceOrder,
    ReplacementRebalanceSeller,
    SellOrderType,
)
from zephyr.sell_decision.core.sell_signal_collector import SellDirection

T0 = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


# ── 再平衡评估 ──


def test_rebalance_overweight_triggers_sell():
    """超配(current>target+阈值) → 触发再平衡卖出。"""
    seller = ReplacementRebalanceSeller()
    order = seller.evaluate_rebalance("000001.SZ", 0.12, 0.05, now=T0)
    assert order is not None
    assert order.order_type is SellOrderType.REBALANCE
    assert order.direction is SellDirection.REDUCE
    assert order.metadata["drift"] == pytest.approx(0.07)


def test_rebalance_within_threshold_no_sell():
    """偏离 ≤ 阈值 → 不触发。"""
    seller = ReplacementRebalanceSeller(rebalance_threshold=0.05)
    order = seller.evaluate_rebalance("000001.SZ", 0.08, 0.05, now=T0)  # drift=0.03 < 0.05
    assert order is None


def test_rebalance_equal_threshold_no_sell():
    """偏离 == 阈值 → 不触发(严格大于)。"""
    seller = ReplacementRebalanceSeller(rebalance_threshold=0.05)
    order = seller.evaluate_rebalance("000001.SZ", 0.10, 0.05, now=T0)  # drift=0.05 == 阈值
    assert order is None


def test_rebalance_underweight_no_sell():
    """低配(current<target) → 不触发卖出(需买入, 非本模块职责)。"""
    seller = ReplacementRebalanceSeller()
    order = seller.evaluate_rebalance("000001.SZ", 0.03, 0.08, now=T0)  # drift=-0.05
    assert order is None


def test_rebalance_confidence_increases_with_drift():
    """偏离越大置信度越高。"""
    seller = ReplacementRebalanceSeller()
    o1 = seller.evaluate_rebalance("A", 0.11, 0.05, now=T0)  # drift=0.06 > 0.05
    o2 = seller.evaluate_rebalance("B", 0.20, 0.05, now=T0)  # drift=0.15
    assert o1 is not None and o2 is not None
    assert o1.confidence < o2.confidence


def test_rebalance_confidence_capped_at_09():
    """置信度上限 0.9。"""
    seller = ReplacementRebalanceSeller()
    order = seller.evaluate_rebalance("A", 0.90, 0.05, now=T0)  # drift=0.85
    assert order is not None
    assert order.confidence == pytest.approx(0.9)


# ── 置换评估 ──


def test_replacement_candidate_better_triggers_replace():
    """候选评分高出当前 > 阈值 → 置换卖出。"""
    seller = ReplacementRebalanceSeller()
    order = seller.evaluate_replacement("000001.SZ", 0.60, "600000.SH", 0.85, now=T0)
    assert order is not None
    assert order.order_type is SellOrderType.REPLACEMENT
    assert order.direction is SellDirection.REPLACE
    assert order.replace_with == "600000.SH"


def test_replacement_candidate_not_better_no_replace():
    """候选评分不够优 → 不置换。"""
    seller = ReplacementRebalanceSeller(replacement_score_threshold=0.20)
    order = seller.evaluate_replacement("A", 0.70, "B", 0.85, now=T0)  # diff=0.15 < 0.20
    assert order is None


def test_replacement_confidence_increases_with_score_diff():
    """评分差越大置信度越高。"""
    seller = ReplacementRebalanceSeller()
    o1 = seller.evaluate_replacement("A", 0.60, "B", 0.85, now=T0)  # diff=0.25
    o2 = seller.evaluate_replacement("C", 0.50, "D", 0.90, now=T0)  # diff=0.40
    assert o1 is not None and o2 is not None
    assert o1.confidence < o2.confidence


def test_replacement_confidence_capped_at_09():
    """置换置信度上限 0.9。"""
    seller = ReplacementRebalanceSeller()
    order = seller.evaluate_replacement("A", 0.10, "B", 0.95, now=T0)  # diff=0.85
    assert order is not None
    assert order.confidence == pytest.approx(0.9)


# ── 输入校验 ──


def test_rebalance_invalid_empty_symbol():
    with pytest.raises(InvalidRebalanceInputError, match="symbol"):
        ReplacementRebalanceSeller().evaluate_rebalance("", 0.1, 0.05)


def test_rebalance_invalid_weight_overflow():
    with pytest.raises(InvalidRebalanceInputError, match="current_weight"):
        ReplacementRebalanceSeller().evaluate_rebalance("A", 1.5, 0.05)


def test_replacement_invalid_empty_replace_with():
    with pytest.raises(InvalidRebalanceInputError, match="replace_with"):
        ReplacementRebalanceSeller().evaluate_replacement("A", 0.6, "", 0.8)


def test_replacement_invalid_score_overflow():
    with pytest.raises(InvalidRebalanceInputError, match="candidate_score"):
        ReplacementRebalanceSeller().evaluate_replacement("A", 0.6, "B", 1.5)


# ── 构造器校验 ──


def test_seller_invalid_threshold_zero():
    with pytest.raises(InvalidRebalanceInputError, match="rebalance_threshold"):
        ReplacementRebalanceSeller(rebalance_threshold=0)


def test_seller_invalid_score_threshold_negative():
    with pytest.raises(InvalidRebalanceInputError, match="replacement_score_threshold"):
        ReplacementRebalanceSeller(replacement_score_threshold=-0.1)


# ── ReplacementRebalanceOrder 校验 ──


def test_order_replacement_requires_replace_with():
    """REPLACEMENT 类型必须设置 replace_with。"""
    with pytest.raises(InvalidRebalanceInputError, match="replace_with"):
        ReplacementRebalanceOrder(
            symbol="A",
            order_type=SellOrderType.REPLACEMENT,
            current_weight=0.6,
            target_weight=0.8,
            direction=SellDirection.REPLACE,
            confidence=0.7,
            replace_with="",  # 空 → 报错
        )


def test_order_invalid_weight():
    with pytest.raises(InvalidRebalanceInputError, match="current_weight"):
        ReplacementRebalanceOrder(
            symbol="A",
            order_type=SellOrderType.REBALANCE,
            current_weight=1.5,
            target_weight=0.05,
            direction=SellDirection.REDUCE,
            confidence=0.7,
        )


def test_order_invalid_confidence():
    with pytest.raises(InvalidRebalanceInputError, match="confidence"):
        ReplacementRebalanceOrder(
            symbol="A",
            order_type=SellOrderType.REBALANCE,
            current_weight=0.1,
            target_weight=0.05,
            direction=SellDirection.REDUCE,
            confidence=1.5,
        )


# ── 事件回调 ──


def test_on_order_callback_invoked():
    """卖出指令生成触发回调。"""
    received: list[ReplacementRebalanceOrder] = []
    seller = ReplacementRebalanceSeller()
    seller.on_order(received.append)
    seller.evaluate_rebalance("A", 0.12, 0.05, now=T0)
    assert len(received) == 1
    assert received[0].order_type is SellOrderType.REBALANCE


def test_on_order_callback_failure_isolated():
    """回调异常不阻断。"""

    def bad_cb(_):
        raise RuntimeError("boom")

    seller = ReplacementRebalanceSeller()
    seller.on_order(bad_cb)
    order = seller.evaluate_rebalance("A", 0.12, 0.05, now=T0)
    assert order is not None  # 回调异常不影响返回


# ── 时钟注入 ──


def test_custom_clock_injection():
    fixed = datetime(2025, 1, 1, tzinfo=timezone.utc)
    seller = ReplacementRebalanceSeller(clock=lambda: fixed)
    order = seller.evaluate_rebalance("A", 0.12, 0.05)
    assert order is not None
    assert order.timestamp == fixed


# ── 自定义阈值 ──


def test_custom_rebalance_threshold():
    """自定义阈值 10% → drift=7% 不触发。"""
    seller = ReplacementRebalanceSeller(rebalance_threshold=0.10)
    order = seller.evaluate_rebalance("A", 0.12, 0.05, now=T0)  # drift=0.07 < 0.10
    assert order is None


def test_custom_replacement_threshold():
    """自定义置换阈值 30% → diff=25% 不触发。"""
    seller = ReplacementRebalanceSeller(replacement_score_threshold=0.30)
    order = seller.evaluate_replacement("A", 0.60, "B", 0.85, now=T0)  # diff=0.25 < 0.30
    assert order is None
