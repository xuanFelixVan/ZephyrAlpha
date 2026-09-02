# [BLUEPRINT] MOD-CMP-011 | 待统筹登记（blueprint 未建，真源=43_compliance_discipline.md §7.3/§10）
# [MODULE] tests.compliance.test_intraday_manipulation_detector
# [DOMAIN] D_COMPLIANCE
# [INVARIANTS] 检测规则唯一真源=TradingComplianceDetector（批层只做窗口化+去重+报告）；30min 滚动窗口；首命中去重（每标的每日每类≤1 条报告命中）；provider 缺失→Spoofing 跳过不误判；检出事件落 compliance_log 兼容格式；输入乱序等价
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ManipulationBatchError(ZA-CMP-0014)
# [TESTS] self
# [TTL] permanent
"""盘中操纵检测离线批处理口径测试（43 号 §7.3 三规则，MOD-CMP-011）。

实证目标：
    1. Spoofing：30min 窗内大额快撤 ≥3 次命中；窗宽外散布不命中；小额/慢撤不命中
    2. Layering：同侧 ≥3 档梯度序列撤单率 >80% 命中；低撤单率/2 档不命中
    3. WashTrade：自成交零容忍命中（立即人工复核）；正常成交不命中
    4. 批处理口径：多标的聚合 / 首命中去重 / 空批 / 输入乱序等价 / provider 缺失降级
    5. compliance_log 兼容：MANIPULATION_VERDICT 逐命中留痕 + MANIPULATION_BATCH_SCAN 汇总
    6. 输入非法：空 trade_date / 空 symbol → ManipulationBatchError(ZA-CMP-0014)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.intraday_manipulation_detector import (
    IntradayManipulationDetector,
    ManipulationBatchError,
    ManipulationBatchInput,
)
from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationType,
    TradingComplianceDetector,
)

_T0 = datetime(2026, 8, 24, 10, 0, tzinfo=UTC)
_TD = "2026-08-24"


def _order(
    order_id: str,
    price: float,
    qty: float,
    side: str = "BUY",
    symbol: str = "600000",
    placed_at: datetime = _T0,
    cancelled_at: datetime | None = None,
) -> ComplianceOrderRecord:
    return ComplianceOrderRecord(
        order_id=order_id,
        symbol=symbol,
        side=side,
        price=price,
        qty=qty,
        placed_at=placed_at,
        cancelled_at=cancelled_at,
    )


def _fast_cancel(
    order_id: str, idx: int, *, minutes: int = 5, qty: float = 3000, symbol: str = "600000"
) -> ComplianceOrderRecord:
    """大额（>20%×10000=2000）挂单后 10s 内撤单记录。"""
    placed = _T0 + timedelta(minutes=idx * minutes)
    return _order(order_id, 10.0, qty, symbol=symbol, placed_at=placed, cancelled_at=placed + timedelta(seconds=5))


def _gradient(symbol: str = "600000", levels: int = 3, cancelled: int = 3) -> list[ComplianceOrderRecord]:
    """同侧价格梯度单序列（10.0/10.1/... 递增），前 cancelled 档撤单。"""
    orders = []
    for i in range(levels):
        placed = _T0 + timedelta(seconds=i)
        orders.append(
            _order(
                f"L{i}",
                round(10.0 + i * 0.1, 2),
                500,
                symbol=symbol,
                placed_at=placed,
                cancelled_at=(placed + timedelta(seconds=30)) if i < cancelled else None,
            )
        )
    return orders


@pytest.fixture()
def logger(tmp_path: Path) -> ComplianceLogger:
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


@pytest.fixture()
def detector(logger: ComplianceLogger) -> TradingComplianceDetector:
    return TradingComplianceDetector(logger=logger)


@pytest.fixture()
def batch_detector(detector: TradingComplianceDetector, logger: ComplianceLogger) -> IntradayManipulationDetector:
    return IntradayManipulationDetector(
        detector,
        minute_volume_provider=lambda s: 10000.0,
        logger=logger,
    )


# ── Spoofing 批扫描 ──


class TestSpoofingBatch:
    def test_three_fast_cancels_within_window_hit(
        self, batch_detector: IntradayManipulationDetector, logger: ComplianceLogger
    ) -> None:
        orders = [_fast_cancel(f"o{i}", i) for i in range(3)]  # 10min 内 3 次大额快撤
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        spoof_hits = [h for h in report.hits if h.verdict.mtype is ManipulationType.SPOOFING]
        assert len(spoof_hits) == 1
        assert spoof_hits[0].symbol == "600000"
        # 检出事件落 compliance_log（detector 逐命中留痕）
        verdict_logs = [r for r in logger.read_all() if r.event_type == "MANIPULATION_VERDICT"]
        assert any(r.payload["mtype"] == "SPOOFING" for r in verdict_logs)

    def test_pattern_spread_beyond_window_no_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        # 每次间隔 40min——任意 30min 窗内至多 1 次
        orders = [_fast_cancel(f"o{i}", i, minutes=40) for i in range(3)]
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        assert all(h.verdict.mtype is not ManipulationType.SPOOFING for h in report.hits)

    def test_small_orders_no_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        orders = [_fast_cancel(f"o{i}", i, qty=100) for i in range(3)]  # 小额
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        assert report.hits == ()

    def test_provider_missing_degrades_skip_spoofing(
        self, detector: TradingComplianceDetector, logger: ComplianceLogger
    ) -> None:
        batch = IntradayManipulationDetector(detector, logger=logger)  # 无 provider
        orders = [_fast_cancel(f"o{i}", i) for i in range(3)]
        report = batch.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        assert all(h.verdict.mtype is not ManipulationType.SPOOFING for h in report.hits)

    def test_zero_minute_volume_skips_spoofing(
        self, detector: TradingComplianceDetector, logger: ComplianceLogger
    ) -> None:
        batch = IntradayManipulationDetector(detector, minute_volume_provider=lambda s: 0.0, logger=logger)
        orders = [_fast_cancel(f"o{i}", i) for i in range(3)]
        report = batch.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        assert all(h.verdict.mtype is not ManipulationType.SPOOFING for h in report.hits)


# ── Layering 批扫描 ──


class TestLayeringBatch:
    def test_gradient_all_cancelled_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(_gradient())))
        layer_hits = [h for h in report.hits if h.verdict.mtype is ManipulationType.LAYERING]
        assert len(layer_hits) == 1

    def test_low_cancel_ratio_no_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        report = batch_detector.run_batch(
            ManipulationBatchInput(trade_date=_TD, orders=tuple(_gradient(cancelled=1)))  # 撤单率 33% < 80%
        )
        assert all(h.verdict.mtype is not ManipulationType.LAYERING for h in report.hits)

    def test_two_levels_no_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        report = batch_detector.run_batch(
            ManipulationBatchInput(trade_date=_TD, orders=tuple(_gradient(levels=2, cancelled=2)))
        )
        assert report.hits == ()


# ── WashTrade 批扫描 ──


class TestWashTradeBatch:
    def test_self_trade_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        trade = ComplianceTradeRecord(
            symbol="600000", price=10.0, qty=100, traded_at=_T0, buyer_account="ACC1", seller_account="ACC1"
        )
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, trades=(trade,)))
        wash_hits = [h for h in report.hits if h.verdict.mtype is ManipulationType.WASH_TRADE]
        assert len(wash_hits) == 1
        assert wash_hits[0].symbol == "600000"
        assert "人工复核" in wash_hits[0].verdict.detail

    def test_normal_trade_no_hit(self, batch_detector: IntradayManipulationDetector) -> None:
        trade = ComplianceTradeRecord(
            symbol="600000", price=10.0, qty=100, traded_at=_T0, buyer_account="ACC1", seller_account="ACC2"
        )
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, trades=(trade,)))
        assert report.hits == ()


# ── 批处理聚合口径 ──


class TestBatchAggregation:
    def test_multi_symbol_aggregation(self, batch_detector: IntradayManipulationDetector) -> None:
        orders = [_fast_cancel(f"A{i}", i, symbol="600000") for i in range(3)]
        orders += _gradient(symbol="000001")
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        assert report.symbols_scanned == 2
        by_symbol = {(h.symbol, h.verdict.mtype) for h in report.hits}
        assert ("600000", ManipulationType.SPOOFING) in by_symbol
        assert ("000001", ManipulationType.LAYERING) in by_symbol

    def test_first_hit_dedup_per_symbol(self, batch_detector: IntradayManipulationDetector) -> None:
        # 6 次大额快撤——报告内同标的 SPOOFING 仅 1 条（防告警风暴；日志保留全量证据）
        orders = [_fast_cancel(f"o{i}", i) for i in range(6)]
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        spoof_hits = [h for h in report.hits if h.verdict.mtype is ManipulationType.SPOOFING]
        assert len(spoof_hits) == 1

    def test_empty_batch(self, batch_detector: IntradayManipulationDetector, logger: ComplianceLogger) -> None:
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD))
        assert report.hits == ()
        assert report.symbols_scanned == 0
        assert report.orders_scanned == 0
        assert report.trades_scanned == 0
        # 空批也落汇总扫描事件（自证清白：扫过且零命中）
        scan_logs = [r for r in logger.read_all() if r.event_type == "MANIPULATION_BATCH_SCAN"]
        assert len(scan_logs) == 1
        assert scan_logs[0].payload["trade_date"] == _TD
        assert scan_logs[0].payload["hit_count"] == 0

    def test_unsorted_input_equivalent(self, batch_detector: IntradayManipulationDetector) -> None:
        orders = [_fast_cancel(f"o{i}", i) for i in range(3)]
        shuffled = (orders[2], orders[0], orders[1])  # 乱序输入
        report = batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=shuffled))
        assert any(h.verdict.mtype is ManipulationType.SPOOFING for h in report.hits)

    def test_batch_scan_summary_payload(
        self, batch_detector: IntradayManipulationDetector, logger: ComplianceLogger
    ) -> None:
        orders = [_fast_cancel(f"o{i}", i) for i in range(3)]
        batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=tuple(orders)))
        scan_logs = [r for r in logger.read_all() if r.event_type == "MANIPULATION_BATCH_SCAN"]
        assert len(scan_logs) == 1
        payload = scan_logs[0].payload
        assert payload["trade_date"] == _TD
        assert payload["orders_scanned"] == 3
        assert payload["symbols_scanned"] == 1
        assert payload["hit_count"] == 1
        assert payload["hit_types"] == ["SPOOFING"]
        assert scan_logs[0].source == "intraday_manipulation_detector"


# ── 输入非法 ──


class TestInvalidInput:
    def test_empty_trade_date_rejected(self, batch_detector: IntradayManipulationDetector) -> None:
        with pytest.raises(ManipulationBatchError) as exc_info:
            batch_detector.run_batch(ManipulationBatchInput(trade_date="  "))
        assert exc_info.value.error_code == "ZA-CMP-0014"

    def test_empty_symbol_rejected(self, batch_detector: IntradayManipulationDetector) -> None:
        bad = _order("o0", 10.0, 3000, symbol="")
        with pytest.raises(ManipulationBatchError):
            batch_detector.run_batch(ManipulationBatchInput(trade_date=_TD, orders=(bad,)))

    def test_scan_symbol_orders_public_entry(self, batch_detector: IntradayManipulationDetector) -> None:
        """实时兼容入口：单标的订单序列直扫（未来盘中流按标的喂同一方法）。"""
        hits = batch_detector.scan_symbol_orders("600000", [_fast_cancel(f"o{i}", i) for i in range(3)])
        assert len(hits) == 1
        assert hits[0].verdict.mtype is ManipulationType.SPOOFING
