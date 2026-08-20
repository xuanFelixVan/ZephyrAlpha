# [BLUEPRINT] MOD-CMP-007 | docs/03_modules/_domain_compliance/trading_compliance_detector/blueprint.md
# [MODULE] tests.compliance.test_manipulation_stream_driver
# [DOMAIN] D_COMPLIANCE
# [INVARIANTS] 同一detector实例驱动; 30min窗口; WashTrade即时; provider缺失降级跳过; 事件非法拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStreamEventError
# [TESTS] self
# [TTL] permanent
"""市场操纵实时流驱动适配测试（43 号 §10 边界项，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.compliance.manipulation_stream_driver import (
    InvalidStreamEventError,
    ManipulationStreamDriver,
)
from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationType,
    TradingComplianceDetector,
)

_T0 = datetime(2026, 8, 20, 10, 0, tzinfo=UTC)


def _order(
    order_id: str,
    price: float,
    qty: float,
    side: str = "BUY",
    symbol: str = "600000",
    placed_at: datetime = _T0,
) -> ComplianceOrderRecord:
    return ComplianceOrderRecord(order_id=order_id, symbol=symbol, side=side, price=price, qty=qty, placed_at=placed_at)


class TestSpoofingViaStream:
    def test_three_large_quick_cancels_hit(self):
        driver = ManipulationStreamDriver(minute_volume_provider=lambda s: 10000.0)
        # 大额（>20%×10000=2000）挂单后 10s 内撤单 ×3 → SPOOFING
        for i in range(3):
            driver.on_order_placed(_order(f"o{i}", 10.0, 3000, placed_at=_T0 + timedelta(minutes=i * 5)))
            verdicts = driver.on_order_cancelled("600000", f"o{i}", _T0 + timedelta(minutes=i * 5, seconds=5))
        assert any(v.mtype is ManipulationType.SPOOFING for v in verdicts)

    def test_provider_missing_degrades_skip(self):
        driver = ManipulationStreamDriver()  # 无 provider → Spoofing 跳过
        for i in range(3):
            driver.on_order_placed(_order(f"o{i}", 10.0, 3000, placed_at=_T0 + timedelta(minutes=i)))
            verdicts = driver.on_order_cancelled("600000", f"o{i}", _T0 + timedelta(minutes=i, seconds=5))
        assert verdicts == []  # 降级不误判

    def test_small_orders_no_hit(self):
        driver = ManipulationStreamDriver(minute_volume_provider=lambda s: 10000.0)
        verdicts = []
        for i in range(3):
            driver.on_order_placed(_order(f"o{i}", 10.0, 100, placed_at=_T0 + timedelta(minutes=i)))  # 小额
            verdicts = driver.on_order_cancelled("600000", f"o{i}", _T0 + timedelta(minutes=i, seconds=5))
        assert verdicts == []

    def test_slow_cancel_no_hit(self):
        driver = ManipulationStreamDriver(minute_volume_provider=lambda s: 10000.0)
        verdicts = []
        for i in range(3):
            driver.on_order_placed(_order(f"o{i}", 10.0, 3000, placed_at=_T0 + timedelta(minutes=i)))
            verdicts = driver.on_order_cancelled(
                "600000",
                f"o{i}",
                _T0 + timedelta(minutes=i, seconds=30),  # 超 10s 窗口
            )
        assert verdicts == []


class TestLayeringViaStream:
    def test_gradient_orders_all_cancelled_hit(self):
        driver = ManipulationStreamDriver()
        # 同侧 3 档价格梯度（10.0/10.1/10.2 递增）+ 全撤（撤单率 100% > 80%）
        for i, price in enumerate([10.0, 10.1, 10.2]):
            driver.on_order_placed(_order(f"L{i}", price, 500, placed_at=_T0 + timedelta(seconds=i)))
            verdicts = driver.on_order_cancelled("600000", f"L{i}", _T0 + timedelta(seconds=30 + i))
        assert any(v.mtype is ManipulationType.LAYERING for v in verdicts)

    def test_low_cancel_ratio_no_hit(self):
        driver = ManipulationStreamDriver()
        verdicts = []
        for i, price in enumerate([10.0, 10.1, 10.2]):
            driver.on_order_placed(_order(f"L{i}", price, 500, placed_at=_T0 + timedelta(seconds=i)))
        # 仅撤 1/3（33% < 80%）
        verdicts = driver.on_order_cancelled("600000", "L0", _T0 + timedelta(seconds=30))
        assert verdicts == []

    def test_two_levels_no_hit(self):
        driver = ManipulationStreamDriver()
        verdicts = []
        for i, price in enumerate([10.0, 10.1]):  # 仅 2 档 < min_levels=3
            driver.on_order_placed(_order(f"L{i}", price, 500, placed_at=_T0 + timedelta(seconds=i)))
            verdicts = driver.on_order_cancelled("600000", f"L{i}", _T0 + timedelta(seconds=30))
        assert verdicts == []


class TestWashTradeViaStream:
    def test_self_trade_hit_immediately(self):
        driver = ManipulationStreamDriver()
        trade = ComplianceTradeRecord(
            symbol="600000",
            price=10.0,
            qty=100,
            traded_at=_T0,
            buyer_account="ACC1",
            seller_account="ACC1",
        )
        verdicts = driver.on_trade(trade)
        assert len(verdicts) == 1
        assert verdicts[0].mtype is ManipulationType.WASH_TRADE

    def test_distinct_accounts_no_hit(self):
        driver = ManipulationStreamDriver()
        trade = ComplianceTradeRecord(
            symbol="600000",
            price=10.0,
            qty=100,
            traded_at=_T0,
            buyer_account="ACC1",
            seller_account="ACC2",
        )
        assert driver.on_trade(trade) == []


class TestWindowMaintenance:
    def test_trim_before_evicts_old(self):
        driver = ManipulationStreamDriver()
        driver.on_order_placed(_order("old", 10.0, 100, placed_at=_T0))
        driver.on_order_placed(_order("new", 10.0, 100, placed_at=_T0 + timedelta(minutes=35)))
        removed = driver.trim_before(_T0 + timedelta(minutes=30))
        assert removed == 1
        assert driver.window_size("600000") == 1

    def test_trim_removes_empty_symbol_bucket(self):
        driver = ManipulationStreamDriver()
        driver.on_order_placed(_order("old", 10.0, 100, placed_at=_T0))
        driver.trim_before(_T0 + timedelta(minutes=31))
        assert driver.window_size("600000") == 0

    def test_cancel_unknown_order_no_error(self):
        driver = ManipulationStreamDriver()
        assert driver.on_order_cancelled("600000", "ghost", _T0) == []


class TestEventValidation:
    def test_empty_symbol_rejected(self):
        driver = ManipulationStreamDriver()
        with pytest.raises(InvalidStreamEventError):
            driver.on_order_placed(_order("o1", 10.0, 100, symbol=""))

    def test_empty_order_id_rejected(self):
        driver = ManipulationStreamDriver()
        with pytest.raises(InvalidStreamEventError):
            driver.on_order_placed(_order("", 10.0, 100))

    def test_cancel_before_place_rejected(self):
        driver = ManipulationStreamDriver()
        driver.on_order_placed(_order("o1", 10.0, 100, placed_at=_T0))
        with pytest.raises(InvalidStreamEventError):
            driver.on_order_cancelled("600000", "o1", _T0 - timedelta(seconds=1))

    def test_trade_empty_symbol_rejected(self):
        driver = ManipulationStreamDriver()
        with pytest.raises(InvalidStreamEventError):
            driver.on_trade(
                ComplianceTradeRecord(
                    symbol="  ",
                    price=10.0,
                    qty=1,
                    traded_at=_T0,
                    buyer_account="A",
                    seller_account="B",
                )
            )

    def test_same_detector_instance_reused(self):
        detector = TradingComplianceDetector()
        driver = ManipulationStreamDriver(detector=detector)
        assert driver._detector is detector  # 同一实例驱动（43 号 §10 口径）
