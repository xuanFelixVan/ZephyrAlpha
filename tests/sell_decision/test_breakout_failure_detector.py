# [BLUEPRINT] MOD-SELL-017 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SELL-003 突破成败检测器 单元测试。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.sell_decision.core.breakout_failure_detector import (
    BreakoutFailureDetector,
    BreakoutResult,
    BreakoutStatus,
    InvalidBreakoutInputError,
)
from zephyr.sell_decision.core.sell_signal_collector import SellDirection

T0 = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


# ── 辅助构造 ──


def detect(
    symbol: str = "000001.SZ",
    resistance: float = 10.50,
    price: float = 10.30,
    challenge: int = 0,
    detector: BreakoutFailureDetector | None = None,
):
    det = detector or BreakoutFailureDetector()
    return det.detect(symbol, resistance, price, challenge, now=T0)


# ── 突破成功 ──


def test_breakout_success_price_above_resistance():
    """价格 > 压力位 → 突破成功, 持有(不卖出)。"""
    r = detect(resistance=10.50, price=10.80, challenge=0)
    assert r.status is BreakoutStatus.SUCCESS
    assert r.direction is SellDirection.REPLACE  # 占位=持有
    assert r.challenge_count == 0  # 成功不累计
    assert r.confidence == pytest.approx(0.8)


def test_breakout_success_records_breakout_pct():
    """突破成功记录突破幅度。"""
    r = detect(resistance=10.00, price=10.50, challenge=0)
    assert r.metadata["breakout_pct"] == pytest.approx(0.05)


# ── 突破失败 ──


def test_breakout_failure_price_below_resistance():
    """价格 < 压力位 → 突破失败, 减仓。"""
    r = detect(resistance=10.50, price=10.30, challenge=0)
    assert r.status is BreakoutStatus.FAILURE
    assert r.direction is SellDirection.REDUCE
    assert r.challenge_count == 1  # 累计+1


def test_breakout_failure_confidence_increases_with_challenges():
    """突破失败置信度随挑战次数递增。"""
    r1 = detect(resistance=10.50, price=10.30, challenge=0)
    r2 = detect(resistance=10.50, price=10.30, challenge=1)
    assert r1.confidence < r2.confidence
    assert r1.confidence == pytest.approx(0.5)  # base + 0*boost
    assert r2.confidence == pytest.approx(0.6)  # base + 1*boost


def test_breakout_failure_confidence_capped_at_09():
    """突破失败置信度上限 0.9(不超强制清仓)。"""
    r = detect(resistance=10.50, price=10.30, challenge=10)
    # challenge=10 → new=11, 但 11>=3 → FORCED_CLEAR, 不走 FAILURE 路径
    assert r.status is BreakoutStatus.FORCED_CLEAR


def test_breakout_failure_equal_price_treated_as_failure():
    """价格 == 压力位 → 视为突破失败(未确认突破)。"""
    r = detect(resistance=10.50, price=10.50, challenge=0)
    assert r.status is BreakoutStatus.FAILURE


# ── 强制清仓 ──


def test_forced_clear_on_third_failure():
    """第3次挑战失败(K≥3) → 强制清仓, confidence=1.0。"""
    r = detect(resistance=10.50, price=10.30, challenge=2)  # 第3次
    assert r.status is BreakoutStatus.FORCED_CLEAR
    assert r.direction is SellDirection.CLEAR
    assert r.confidence == pytest.approx(1.0)
    assert r.challenge_count == 3
    assert r.metadata["forced_clear"] is True


def test_forced_clear_threshold_custom():
    """自定义阈值 K≥2 → 第2次失败即强制清仓。"""
    det = BreakoutFailureDetector(forced_clear_threshold=2)
    r = det.detect("000001.SZ", 10.50, 10.30, challenge_count=1, now=T0)  # 第2次
    assert r.status is BreakoutStatus.FORCED_CLEAR


def test_forced_clear_not_triggered_below_threshold():
    """挑战次数 < 阈值 → 仍是 FAILURE。"""
    det = BreakoutFailureDetector(forced_clear_threshold=5)
    r = det.detect("000001.SZ", 10.50, 10.30, challenge_count=3, now=T0)  # 第4次 < 5
    assert r.status is BreakoutStatus.FAILURE


# ── 输入校验 ──


def test_invalid_empty_symbol():
    with pytest.raises(InvalidBreakoutInputError, match="symbol"):
        detect(symbol="")


def test_invalid_resistance_zero():
    with pytest.raises(InvalidBreakoutInputError, match="resistance_level"):
        detect(resistance=0)


def test_invalid_resistance_negative():
    with pytest.raises(InvalidBreakoutInputError, match="resistance_level"):
        detect(resistance=-1.0)


def test_invalid_price_zero():
    with pytest.raises(InvalidBreakoutInputError, match="current_price"):
        detect(price=0)


def test_invalid_negative_challenge_count():
    with pytest.raises(InvalidBreakoutInputError, match="challenge_count"):
        detect(challenge=-1)


# ── 构造器校验 ──


def test_detector_invalid_threshold_zero():
    with pytest.raises(InvalidBreakoutInputError, match="forced_clear_threshold"):
        BreakoutFailureDetector(forced_clear_threshold=0)


def test_detector_invalid_success_confidence():
    with pytest.raises(InvalidBreakoutInputError, match="success_confidence"):
        BreakoutFailureDetector(success_confidence=1.5)


# ── BreakoutResult 校验 ──


def test_result_invalid_confidence_overflow():
    with pytest.raises(InvalidBreakoutInputError, match="confidence"):
        BreakoutResult(
            symbol="X",
            status=BreakoutStatus.SUCCESS,
            resistance_level=10.0,
            current_price=11.0,
            challenge_count=0,
            confidence=1.5,
            direction=SellDirection.REPLACE,
        )


def test_result_invalid_resistance_zero():
    with pytest.raises(InvalidBreakoutInputError, match="resistance_level"):
        BreakoutResult(
            symbol="X",
            status=BreakoutStatus.SUCCESS,
            resistance_level=0,
            current_price=11.0,
            challenge_count=0,
            confidence=0.8,
            direction=SellDirection.REPLACE,
        )


# ── 事件回调 ──


def test_on_detected_callback_invoked():
    """检测完成触发回调。"""
    received: list[BreakoutResult] = []
    det = BreakoutFailureDetector()
    det.on_detected(received.append)
    det.detect("000001.SZ", 10.50, 10.30, 0, now=T0)
    assert len(received) == 1
    assert received[0].status is BreakoutStatus.FAILURE


def test_on_detected_callback_failure_isolated():
    """回调异常不阻断检测。"""

    def bad_cb(_):
        raise RuntimeError("callback boom")

    det = BreakoutFailureDetector()
    det.on_detected(bad_cb)
    # 不应抛异常
    r = det.detect("000001.SZ", 10.50, 10.30, 0, now=T0)
    assert r.status is BreakoutStatus.FAILURE


# ── 时钟注入 ──


def test_custom_clock_injection():
    """自定义时钟用于测试。"""
    fixed = datetime(2025, 1, 1, tzinfo=timezone.utc)
    det = BreakoutFailureDetector(clock=lambda: fixed)
    r = det.detect("000001.SZ", 10.50, 10.80, 0)
    assert r.timestamp == fixed


# ── 多标的混合 ──


def test_multiple_symbols_independent():
    """多标的独立检测。"""
    det = BreakoutFailureDetector()
    r1 = det.detect("000001.SZ", 10.50, 10.30, 0, now=T0)
    r2 = det.detect("600000.SH", 5.00, 5.20, 0, now=T0)
    assert r1.status is BreakoutStatus.FAILURE
    assert r2.status is BreakoutStatus.SUCCESS
    assert r1.symbol != r2.symbol
