"""MOD-CMP-007 交易合规检测 单元测试（43 号 §7，BM-BUY-15）。"""

from __future__ import annotations

from datetime import datetime, time, timedelta

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.trading_compliance_detector import (
    ComplianceAction,
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationType,
    TradingComplianceDetector,
)

_T0 = datetime(2026, 8, 14, 10, 0, 0)


def _detector(tmp_path) -> TradingComplianceDetector:
    return TradingComplianceDetector(logger=ComplianceLogger(tmp_path / "c.jsonl"))


def _order(i: int, qty: float, cancel_after_s: float | None, price: float = 10.0) -> ComplianceOrderRecord:
    placed = _T0 + timedelta(seconds=i * 60)
    return ComplianceOrderRecord(
        order_id=f"o{i}",
        symbol="600519",
        side="BUY",
        price=price,
        qty=qty,
        placed_at=placed,
        cancelled_at=(placed + timedelta(seconds=cancel_after_s)) if cancel_after_s is not None else None,
    )


# ── §7.2 异常交易 ──


def test_ramp_dump_hit(tmp_path):
    v = _detector(tmp_path).check_ramp_dump(0.035, 0.35)
    assert v is not None and v.mtype is ManipulationType.RAMP_DUMP
    assert v.action is ComplianceAction.HARD_BLOCK


def test_ramp_dump_below_threshold_pass(tmp_path):
    assert _detector(tmp_path).check_ramp_dump(0.02, 0.35) is None
    assert _detector(tmp_path).check_ramp_dump(0.035, 0.20) is None


def test_large_trade_hit(tmp_path):
    v = _detector(tmp_path).check_large_trade(6_000, 10_000)
    assert v is not None and v.mtype is ManipulationType.LARGE_TRADE


def test_large_trade_pass(tmp_path):
    assert _detector(tmp_path).check_large_trade(4_000, 10_000) is None
    assert _detector(tmp_path).check_large_trade(1_000, 0) is None  # 零均量不误判


# ── §7.3 操纵 4 类 ──


def test_spoofing_hit(tmp_path):
    """3 次大额快撤（>20% 分钟均量，10s 内撤）→ 幌骗。"""
    orders = [_order(i, qty=2_100, cancel_after_s=5) for i in range(3)]
    v = _detector(tmp_path).check_spoofing(orders, minute_avg_volume=10_000)
    assert v is not None and v.mtype is ManipulationType.SPOOFING


def test_spoofing_repeat_not_reached(tmp_path):
    orders = [_order(i, qty=2_100, cancel_after_s=5) for i in range(2)]
    assert _detector(tmp_path).check_spoofing(orders, 10_000) is None


def test_spoofing_slow_cancel_not_spoof(tmp_path):
    """撤单间隔 >10s 不算幌骗（正常改单防误伤）。"""
    orders = [_order(i, qty=2_100, cancel_after_s=30) for i in range(3)]
    assert _detector(tmp_path).check_spoofing(orders, 10_000) is None


def test_layering_hit(tmp_path):
    orders = [_order(i, qty=100, cancel_after_s=60, price=10.0 + i * 0.01) for i in range(3)]
    v = _detector(tmp_path).check_layering(orders)
    assert v is not None and v.mtype is ManipulationType.LAYERING


def test_layering_low_cancel_ratio_pass(tmp_path):
    """3 档梯度但多数未撤（真实挂单意图）→ 放行。"""
    orders = [
        _order(0, 100, 60, 10.00),
        _order(1, 100, None, 10.01),
        _order(2, 100, None, 10.02),
        _order(3, 100, None, 10.03),
    ]
    assert _detector(tmp_path).check_layering(orders) is None


def test_layering_min_levels(tmp_path):
    orders = [_order(i, 100, 60, 10.0 + i * 0.01) for i in range(2)]
    assert _detector(tmp_path).check_layering(orders) is None


def test_wash_trade_zero_tolerance(tmp_path):
    t = ComplianceTradeRecord("600519", 10.0, 100, _T0, "ACC1", "ACC1")
    v = _detector(tmp_path).check_wash_trade(t)
    assert v is not None and v.mtype is ManipulationType.WASH_TRADE
    assert "人工复核" in v.detail


def test_wash_trade_different_accounts_pass(tmp_path):
    t = ComplianceTradeRecord("600519", 10.0, 100, _T0, "ACC1", "ACC2")
    assert _detector(tmp_path).check_wash_trade(t) is None


def test_close_manipulation_hit(tmp_path):
    v = _detector(tmp_path).check_close_manipulation(
        order_price=10.31,
        order_qty=4_000,
        pre_close_vwap=10.0,
        window_total_volume=10_000,
        at_time=time(14, 58),
    )
    assert v is not None and v.mtype is ManipulationType.CLOSE_MANIPULATION


def test_close_manipulation_before_window_pass(tmp_path):
    """14:56 同参数不命中（窗口外）。"""
    assert _detector(tmp_path).check_close_manipulation(10.31, 4_000, 10.0, 10_000, time(14, 56)) is None


def test_close_manipulation_small_share_pass(tmp_path):
    assert _detector(tmp_path).check_close_manipulation(10.31, 1_000, 10.0, 10_000, time(14, 58)) is None


def test_run_all_aggregation(tmp_path):
    d = _detector(tmp_path)
    verdicts = d.run_all(
        d.check_ramp_dump(0.035, 0.35),
        d.check_large_trade(100, 10_000),  # None
        d.check_wash_trade(ComplianceTradeRecord("s", 1.0, 1, _T0, "A", "A")),
    )
    assert [v.mtype for v in verdicts] == [ManipulationType.RAMP_DUMP, ManipulationType.WASH_TRADE]


def test_verdict_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    TradingComplianceDetector(logger=log).check_ramp_dump(0.035, 0.35)
    assert log.read_all()[-1].event_type == "MANIPULATION_VERDICT"
