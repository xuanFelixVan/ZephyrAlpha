# [A_test] module_id: MOD-GOV_g3_fill_persistence | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_g3_fill_persistence
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.ex_core.fill_handler; zephyr.ex_core.adapters.miniqmt_broker; zephyr.shared.contracts.fill; zephyr.shared.contracts.order
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全tmp/mock隔离(不连真QMT不写真库)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""56号文 G3 测试：Fill JSONL 落盘/回放 + QMT 盘后成交查询兜底封装。

覆盖：
- FillHandler(fills_dir=tmp)：process_fill 尾部落盘 JSONL（按成交日分文件）
- 新实例 query_fills_by_date 回放（进程退出不丢当日 Fill 的病根修复）
- 幂等拦截的 fill 不重复落盘；坏行容错跳过；未配置 fills_dir 报错
- MiniQmtBroker.query_trades_today：mock xttrader 验证 Fill 字段映射、
  交易日过滤、时间升序、未连接报错（40 号戒律：仅盘后/回调外场景）
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
from zephyr.ex_core.fill_handler import FillHandler
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

# 固定交易日（本地时区口径，与 _trade_date_of / query_trades_today 一致）
TRADE_DATE = "2026-08-21"
TRADE_DAY = "20260821"


def _ts(hour: int, minute: int) -> datetime:
    """构造当日带 UTC 时区的成交时间。"""
    return datetime(2026, 8, 21, hour, minute, tzinfo=UTC)


def _make_order(order_id: str = "ord-001", quantity: Decimal = Decimal("100")) -> Order:
    return Order(
        order_id=order_id,
        symbol="600000.SH",
        strategy_id="S1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("10.00"),
        status=OrderStatus.SUBMITTED,
        created_at=datetime.now(UTC),
        idempotency_key=f"ik-{order_id}",
    )


def _make_fill(
    fill_id: str = "fill-001",
    order_id: str = "ord-001",
    price: str = "10.00",
    qty: str = "100",
    timestamp: datetime | None = None,
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal(price),
        fill_timestamp=timestamp or _ts(2, 30),  # UTC 02:30 = 本地 10:30
        filled_quantity=Decimal(qty),
        idempotency_key=f"ik-{fill_id}",
        order_id=order_id,
        strategy_id="S1",
        symbol="600000.SH",
        broker_fill_id=f"b-{fill_id}",
        commission=Decimal("0.85"),
        slippage=Decimal("0.0001"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# FillHandler JSONL 落盘 + 回放
# ──────────────────────────────────────────────────────────────────────────────


class TestFillJsonlPersistence:
    def test_process_fill_appends_jsonl(self, tmp_path: Path):
        """process_fill 尾部追加落盘到 {fills_dir}/YYYYMMDD.jsonl。"""
        handler = FillHandler(fills_dir=tmp_path)
        handler.process_fill(_make_fill(), _make_order())

        path = tmp_path / f"{TRADE_DAY}.jsonl"
        assert path.is_file()
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["trade_date"] == TRADE_DAY
        assert record["fill"]["fill_id"] == "fill-001"
        assert record["fill"]["fill_price"] == "10.00"  # Decimal→str

    def test_replay_after_restart(self, tmp_path: Path):
        """新实例（模拟进程重启）可按交易日完整回放当日 Fill——病根修复验证。"""
        handler = FillHandler(fills_dir=tmp_path)
        handler.process_fill(_make_fill("f1", order_id="o1", timestamp=_ts(2, 30)), _make_order("o1"))
        handler.process_fill(_make_fill("f2", order_id="o2", timestamp=_ts(5, 0)), _make_order("o2"))

        reloaded = FillHandler(fills_dir=tmp_path)  # 全新实例，内存为空
        fills = reloaded.query_fills_by_date(TRADE_DATE)
        assert [f.fill_id for f in fills] == ["f1", "f2"]  # 行序=写入序
        assert fills[0].fill_price == Decimal("10.00")
        assert fills[0].filled_quantity == Decimal("100")
        assert fills[0].commission == Decimal("0.85")
        assert fills[0].slippage == Decimal("0.0001")
        assert fills[0].broker_fill_id == "b-f1"
        assert fills[1].fill_timestamp == _ts(5, 0)

    def test_dedup_fill_not_persisted_twice(self, tmp_path: Path):
        """幂等拦截的重复 fill_id 不重复落盘。"""
        handler = FillHandler(fills_dir=tmp_path)
        fill, order = _make_fill(), _make_order()
        handler.process_fill(fill, order)
        handler.process_fill(fill, order)  # 同 fill_id 重放 → 幂等拦截
        lines = (tmp_path / f"{TRADE_DAY}.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

    def test_query_date_without_file_returns_empty(self, tmp_path: Path):
        handler = FillHandler(fills_dir=tmp_path)
        assert handler.query_fills_by_date("2026-08-20") == []

    def test_query_supports_compact_date(self, tmp_path: Path):
        """trade_date 兼容 YYYYMMDD 格式。"""
        handler = FillHandler(fills_dir=tmp_path)
        handler.process_fill(_make_fill(), _make_order())
        assert len(handler.query_fills_by_date(TRADE_DAY)) == 1

    def test_bad_line_skipped(self, tmp_path: Path):
        """crash 残行/坏行跳过不阻断回放（AppendOnlyDedupSet 同风格）。"""
        handler = FillHandler(fills_dir=tmp_path)
        handler.process_fill(_make_fill("f1", order_id="o1"), _make_order("o1"))
        with open(tmp_path / f"{TRADE_DAY}.jsonl", "a", encoding="utf-8") as f:
            f.write('{"trade_date": "20260821", "fill": {"broken":')  # 残行
            f.write("\n")
        handler.process_fill(_make_fill("f2", order_id="o2"), _make_order("o2"))
        fills = handler.query_fills_by_date(TRADE_DATE)
        assert [f.fill_id for f in fills] == ["f1", "f2"]

    def test_query_without_fills_dir_raises(self):
        handler = FillHandler()  # 未配置 fills_dir
        with pytest.raises(ValueError, match="fills_dir"):
            handler.query_fills_by_date(TRADE_DATE)

    def test_no_persist_when_dir_not_configured(self, tmp_path: Path):
        """fills_dir=None 保持既有纯内存行为（不落盘）。"""
        handler = FillHandler()
        handler.process_fill(_make_fill(), _make_order())
        assert handler.total_fill_count == 1


# ──────────────────────────────────────────────────────────────────────────────
# MiniQmtBroker.query_trades_today（mock xttrader，不连真 QMT）
# ──────────────────────────────────────────────────────────────────────────────


def _xt_trade(
    traded_id: int,
    traded_time: float,
    symbol: str = "600000.SH",
    price: float = 10.5,
    volume: int = 100,
    order_id: int = 2001,
) -> SimpleNamespace:
    """伪造 xtquant XtTrade（duck 类型）。"""
    return SimpleNamespace(
        traded_id=traded_id,
        traded_time=traded_time,
        stock_code=symbol,
        traded_price=price,
        traded_volume=volume,
        order_id=order_id,
        strategy_name="S1",
        order_remark="remark",
        commission=0.85,
    )


def _local_epoch(hour: int, minute: int) -> float:
    """当日本地时刻 → Unix 秒（xtquant traded_time 口径）。"""
    return datetime(2026, 8, 21, hour, minute).timestamp()


class _FakeXtTrader:
    """伪造 XtQuantTrader：query_stock_trades 返回预设列表。"""

    def __init__(self, trades: list):
        self._trades = trades

    def query_stock_trades(self, _account) -> list:
        return self._trades


def _make_broker(trades: list) -> MiniQmtBroker:
    """构造不连真 QMT 的 broker：注入 fake xttrader + connected 状态。"""
    broker = MiniQmtBroker(path="", session_id="test-session", account_id="SIM001")
    broker.xttrader = _FakeXtTrader(trades)  # Stage 4 公共化 setter
    broker.connected = True
    broker._account = object()  # StockAccount 替身（fake xttrader 不校验）
    return broker


class TestQueryTradesToday:
    def test_field_mapping_and_sort(self):
        """XtTrade → Fill 契约字段映射；按成交时间升序。"""
        broker = _make_broker(
            [
                _xt_trade(1002, _local_epoch(13, 0), price=10.6, volume=200),
                _xt_trade(1001, _local_epoch(10, 30), price=10.5, volume=100),
            ]
        )
        fills = broker.query_trades_today(TRADE_DATE)
        assert [f.broker_fill_id for f in fills] == ["1001", "1002"]  # 时间升序
        f0 = fills[0]
        assert f0.fill_id == "qmt-1001"
        assert f0.idempotency_key == "qmt-trade-1001"
        assert f0.order_id == "2001"
        assert f0.symbol == "600000.SH"
        assert f0.strategy_id == "S1"
        assert f0.fill_price == Decimal("10.5")
        assert f0.filled_quantity == Decimal("100")
        assert f0.commission == Decimal("0.85")
        assert f0.fill_timestamp == datetime.fromtimestamp(_local_epoch(10, 30), tz=UTC)

    def test_trade_date_filter(self):
        """非当日记录被过滤（xtquant 返回当日全部，防御跨日脏数据）。"""
        yesterday = datetime(2026, 8, 20, 15, 0).timestamp()
        broker = _make_broker(
            [
                _xt_trade(1001, yesterday),
                _xt_trade(1002, _local_epoch(10, 30)),
            ]
        )
        fills = broker.query_trades_today(TRADE_DATE)
        assert [f.broker_fill_id for f in fills] == ["1002"]

    def test_invalid_traded_time_skipped(self):
        broker = _make_broker([_xt_trade(1001, 0), _xt_trade(1002, _local_epoch(10, 30))])
        fills = broker.query_trades_today(TRADE_DATE)
        assert [f.broker_fill_id for f in fills] == ["1002"]

    def test_missing_commission_defaults_zero(self):
        """xtquant 版本间 commission 可能缺失 → 默认 0（参考列口径）。"""
        trade = _xt_trade(1001, _local_epoch(10, 30))
        delattr(trade, "commission")
        fills = _make_broker([trade]).query_trades_today(TRADE_DATE)
        assert fills[0].commission == Decimal("0")

    def test_empty_result(self):
        assert _make_broker([]).query_trades_today(TRADE_DATE) == []

    def test_not_connected_raises(self):
        broker = MiniQmtBroker(path="", session_id="s", account_id="SIM001")
        with pytest.raises(MiniQmtBrokerError):
            broker.query_trades_today(TRADE_DATE)
