# [A_test] module_id: MOD-GOV_broker_settlement_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_broker_settlement_adapter
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.broker_settlement_adapter; zephyr.shared.contracts.fill
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全mock隔离(不连真QMT)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""56号文 G4 测试：券商侧适配器（Fill 列表 → BrokerSettlementRecord）。

覆盖：业务配对键格式/同标的组内时间序编号、乱序输入重排、字段映射
（价格/数量/佣金/settlement_date/order_id 保留参考）、编排函数走通。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from zephyr.shared.contracts.fill import Fill
from zephyr.trading.broker_settlement_adapter import (
    fetch_broker_settlement_records,
    fills_to_broker_records,
    make_business_pair_key,
)

TRADE_DATE = "2026-08-21"


def _fill(
    traded_id: str,
    symbol: str,
    price: str,
    qty: str,
    minute: int,
    commission: str = "0.85",
) -> Fill:
    """构造券商侧 Fill（query_trades_today 产出口径：broker_fill_id=traded_id）。"""
    return Fill(
        fill_id=f"qmt-{traded_id}",
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 8, 21, 2, minute, tzinfo=UTC),  # UTC 02:xx=本地 10:xx
        filled_quantity=Decimal(qty),
        idempotency_key=f"qmt-trade-{traded_id}",
        order_id=f"ord-{traded_id}",
        strategy_id="S1",
        symbol=symbol,
        broker_fill_id=traded_id,
        commission=Decimal(commission),
    )


class TestBusinessPairKey:
    def test_format(self):
        assert make_business_pair_key("600000.SH", 1) == "600000.SH|001"
        assert make_business_pair_key("000001.SZ", 12) == "000001.SZ|012"


class TestFillsToBrokerRecords:
    def test_field_mapping(self):
        records = fills_to_broker_records([_fill("1001", "600000.SH", "10.50", "100", 30)], TRADE_DATE)
        assert len(records) == 1
        rec = records[0]
        assert rec.trade_id == "600000.SH|001"  # 业务配对键（优先配对键）
        assert rec.order_id == "ord-1001"  # 券商原始订单号保留参考
        assert rec.symbol == "600000.SH"
        assert rec.settlement_price == Decimal("10.50")
        assert rec.settlement_quantity == Decimal("100")
        assert rec.commission == Decimal("0.85")  # 参考列透传（56号文 C9）
        assert rec.settlement_date == TRADE_DATE

    def test_seq_per_symbol_time_ordered(self):
        """同标的组内按成交时间升序编号；乱序输入被重排；不同标的各自编号。"""
        fills = [
            _fill("1003", "600000.SH", "10.70", "100", 45),  # 同标的第 2 笔
            _fill("1001", "600000.SH", "10.50", "100", 30),  # 同标的第 1 笔
            _fill("1002", "000001.SZ", "20.00", "200", 35),  # 另一标的第 1 笔
        ]
        records = fills_to_broker_records(fills, TRADE_DATE)
        by_broker_order = {r.order_id: r for r in records}
        assert by_broker_order["ord-1001"].trade_id == "600000.SH|001"
        assert by_broker_order["ord-1003"].trade_id == "600000.SH|002"
        assert by_broker_order["ord-1002"].trade_id == "000001.SZ|001"
        # 输出整体按时间升序
        assert [r.order_id for r in records] == ["ord-1001", "ord-1002", "ord-1003"]

    def test_empty_input(self):
        assert fills_to_broker_records([], TRADE_DATE) == []


class TestFetchBrokerSettlementRecords:
    def test_orchestration_with_mock_broker(self):
        """编排 query_trades_today → 适配（mock broker，不连真 QMT）。"""

        class MockBroker:
            def __init__(self):
                self.called_with: list[str | None] = []

            def query_trades_today(self, trade_date=None):
                self.called_with.append(trade_date)
                return [_fill("1001", "600000.SH", "10.50", "100", 30)]

        broker = MockBroker()
        records = fetch_broker_settlement_records(broker, TRADE_DATE)
        assert broker.called_with == [TRADE_DATE]
        assert len(records) == 1
        assert records[0].trade_id == "600000.SH|001"
        assert records[0].settlement_date == TRADE_DATE
