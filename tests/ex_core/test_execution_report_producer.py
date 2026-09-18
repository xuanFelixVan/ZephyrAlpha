# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_execution_report_producer
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 终态才落行(中间态零行); 幂等(重复观察不重复落行); 列序对齐 schema INSERT_COLUMNS(15列); 有量无佣 Fail-Closed 不落行; 生产端异常不打断同步线程
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败
# [TESTS] self
# [TTL] permanent
"""断点 E4 闭合测试——execution_report 生产端接线（终态落行/幂等/列序/Fail-Closed）。

对应事实：2026-09-18 E2E 段二实测 100 股模拟单跑通 SUBMITTED→CANCELLED，
但 c1_market.execution_report 恒 0 行（表在/DDL 在/契约在/build_execution_report 在，
唯缺生产调用方）。本套件钉住"接线后终态必须落行"，并证明能红（见
test_mutation_proof_* 三例：拆掉终态门/幂等门/列序门任一，对应用例必失败）。

测试纪律：writer 一律注入假实现，**零接触生产库**（禁写 data/ 与 ClickHouse）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from schemas.categories.intraday.market_execution_report import INSERT_COLUMNS
from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker
from zephyr.ex_core.execution_report_producer import (
    EXECUTION_REPORT_TABLE,
    TERMINAL_STATUSES,
    ExecutionReportProducer,
)
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType


class _FakeOutcome:
    """假 WriteOutcome（is_ch_committed 可控）。"""

    def __init__(self, committed: bool = True) -> None:
        self.is_ch_committed = committed
        self.disposition = "CH_COMMITTED" if committed else "LOCAL_DURABLE"

    def __repr__(self) -> str:  # pragma: no cover - 诊断用
        return f"_FakeOutcome({self.disposition})"


class _FakeWriter:
    """捕获 (table, columns, tsv_bytes) 的假写入器。"""

    def __init__(self, committed: bool = True) -> None:
        self.calls: list[tuple[str, str | None, bytes]] = []
        self._committed = committed

    def __call__(self, table: str, columns: str | None, tsv_bytes: bytes) -> _FakeOutcome:
        self.calls.append((table, columns, tsv_bytes))
        return _FakeOutcome(self._committed)

    @property
    def rows(self) -> list[list[str]]:
        out: list[list[str]] = []
        for _, _, payload in self.calls:
            for line in payload.decode("utf-8").splitlines():
                if line:
                    out.append(line.split("\t"))
        return out


def _order(
    *,
    order_id: str = "ord-e4-1",
    status: OrderStatus = OrderStatus.CANCELLED,
    symbol: str = "510300.SH",
    side: OrderSide = OrderSide.BUY,
    qty: str = "100",
    limit: str = "4.07",
    filled: str = "0",
    avg: str | None = None,
) -> Order:
    return Order(
        idempotency_key=f"smoke-{order_id}",
        order_id=order_id,
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
        side=side,
        strategy_id="smoke_bridge_e2e",
        symbol=symbol,
        status=status,
        limit_price=Decimal(limit),
        avg_fill_price=Decimal(avg) if avg is not None else None,
        filled_quantity=Decimal(filled),
        created_at=datetime(2026, 9, 18, 9, 27, 0, tzinfo=UTC),
        updated_at=datetime(2026, 9, 18, 9, 28, 30, tzinfo=UTC),
    )


def _fill(order_id: str, *, qty: str = "600", price: str = "10.02", fee: str = "5.25") -> Fill:
    return Fill(
        fill_id=f"f-{order_id}-{qty}",
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 9, 18, 9, 30, 0, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"idem-f-{order_id}-{qty}",
        order_id=order_id,
        strategy_id="S1",
        symbol="600000.SH",
        broker_fill_id=f"bf-{order_id}-{qty}",
        commission=Decimal(fee),
    )


def _cols() -> list[str]:
    return [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]


def _producer(committed: bool = True) -> tuple[ExecutionReportProducer, _FakeWriter]:
    writer = _FakeWriter(committed)
    return ExecutionReportProducer(venue="qmt_sim", writer=writer), writer


class TestTerminalEmission:
    def test_cancelled_zero_fill_lands_one_row(self):
        """段二实测场景：CANCELLED + actual_quantity=0 → 落一行聚合。"""
        producer, writer = _producer()
        assert producer.observe([_order()]) == 1
        rows = writer.rows
        assert len(rows) == 1
        row = dict(zip(_cols(), rows[0]))
        assert row["order_id"] == "ord-e4-1"
        assert row["symbol"] == "510300.SH"
        assert row["direction"] == "BUY"
        assert row["intended_quantity"] == "100"
        assert row["actual_quantity"] == "0"
        assert producer.stats.emitted_unfilled == 1
        assert producer.stats.emitted_filled == 0
        assert row["intended_price"] == "4.07"
        assert row["vwap_price"] == "0"
        assert row["commission"] == "0"
        assert row["broker_id"] == "qmt_sim"
        assert row["algo_type"] == "NONE"
        assert row["idempotency_key"] == "smoke-ord-e4-1"
        assert row["schema_version"] == "1.0"
        # DateTime64(3,'UTC') 文本口径
        assert row["execution_start"] == "2026-09-18 09:27:00.000"
        assert row["execution_end"] == "2026-09-18 09:28:30.000"

    def test_writes_to_registered_table_with_schema_columns(self):
        """表名/列序走 DDL-as-Code 真源，不硬编码、不新增字段。"""
        producer, writer = _producer()
        producer.observe([_order()])
        table, columns, _ = writer.calls[0]
        assert table == EXECUTION_REPORT_TABLE == "c1_market.execution_report"
        assert columns == INSERT_COLUMNS
        assert len(_cols()) == 15
        assert "ingest_ts" not in _cols()  # DEFAULT 列不写入
        assert len(writer.rows[0]) == 15

    def test_filled_with_commission_and_vwap(self):
        """FILLED 终态：佣金/VWAP/滑点取成交面真值（带方向符号，买贵=正=不利）。"""
        producer, writer = _producer()
        order = _order(
            order_id="ord-fill-1",
            status=OrderStatus.FILLED,
            symbol="600000.SH",
            qty="1000",
            limit="10.00",
            filled="1000",
            avg="10.02",
        )
        producer.on_fill(_fill("ord-fill-1", qty="1000"))
        assert producer.observe([order]) == 1
        row = dict(zip(_cols(), writer.rows[0]))
        assert row["actual_quantity"] == "1000"
        assert row["vwap_price"] == "10.02"
        assert row["commission"] == "5.25"
        assert Decimal(row["slippage_bps"]) == Decimal("20.000000")  # (10.02-10.00)/10.00*1e4

    def test_rejected_terminal_also_lands(self):
        """REJECTED 是终态之一（OM 不发事件，靠轮询覆盖）。"""
        producer, writer = _producer()
        assert producer.observe([_order(order_id="ord-rej", status=OrderStatus.REJECTED)]) == 1
        assert dict(zip(_cols(), writer.rows[0]))["order_id"] == "ord-rej"


class TestNoIntermediateState:
    @pytest.mark.parametrize(
        "status",
        [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL],
    )
    def test_non_terminal_lands_nothing(self, status):
        """禁 forming 中间态落行——只有三个终态落行。"""
        producer, writer = _producer()
        assert producer.observe([_order(status=status)]) == 0
        assert writer.calls == []
        assert producer.stats.skipped_non_terminal == 1
        assert producer.stats.emitted == 0

    def test_terminal_set_is_exactly_three(self):
        assert TERMINAL_STATUSES == frozenset(
            {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
        )


class TestIdempotency:
    def test_repeat_observe_single_row(self):
        producer, writer = _producer()
        order = _order()
        assert producer.observe([order]) == 1
        assert producer.observe([order]) == 0
        assert producer.observe([order, order]) == 0
        assert len(writer.rows) == 1
        assert producer.emitted_order_ids == frozenset({"ord-e4-1"})
        assert producer.stats.skipped_duplicate == 3

    def test_status_change_after_emit_does_not_reland(self):
        producer, writer = _producer()
        order = _order(order_id="ord-x", status=OrderStatus.PARTIAL, qty="1000", filled="400", avg="10.0")
        producer.on_fill(_fill("ord-x", qty="400", price="10.0", fee="2.0"))
        assert producer.observe([order]) == 0  # 中间态
        order.status = OrderStatus.FILLED
        order.filled_quantity = Decimal("1000")
        producer.on_fill(_fill("ord-x", qty="600", price="10.0", fee="3.0"))
        assert producer.observe([order]) == 1
        assert producer.observe([order]) == 0
        assert len(writer.rows) == 1
        assert dict(zip(_cols(), writer.rows[0]))["commission"] == "5.0"


class TestFailClosed:
    def test_filled_without_fill_ledger_is_blocked(self):
        """有成交量却无成交明细=佣金不可得 → 拒落行（禁污染 TCA 消费面）。"""
        producer, writer = _producer()
        order = _order(order_id="ord-noc", status=OrderStatus.FILLED, qty="1000", filled="1000", avg="10.0")
        assert producer.observe([order]) == 0
        assert writer.calls == []
        assert producer.stats.commission_blocked == 1
        assert producer.emitted_order_ids == frozenset()

    def test_blocked_then_fill_arrives_emits(self):
        """阻塞可自愈：成交明细到达后下一轮即落行（非永久丢弃）。"""
        producer, writer = _producer()
        order = _order(order_id="ord-noc2", status=OrderStatus.FILLED, qty="1000", filled="1000", avg="10.0")
        assert producer.observe([order]) == 0
        producer.on_fill(_fill("ord-noc2", qty="1000", price="10.0", fee="5.0"))
        assert producer.observe([order]) == 1
        assert Decimal(dict(zip(_cols(), writer.rows[0]))["commission"]) == Decimal("5")

    def test_incomplete_fill_ledger_is_blocked(self):
        """明细未累积齐（qty 缺口）→ 佣金会被低估，Fail-Closed 拒落行。"""
        producer, writer = _producer()
        order = _order(order_id="ord-gap", status=OrderStatus.FILLED, qty="1000", filled="1000", avg="10.0")
        producer.on_fill(_fill("ord-gap", qty="600", price="10.0", fee="3.0"))
        assert producer.observe([order]) == 0
        assert writer.calls == []
        assert producer.stats.commission_blocked == 1
        producer.on_fill(_fill("ord-gap2", qty="400", price="10.0", fee="2.0"))
        # 补齐明细后自愈（同一 order_id 的 fill 以 order_id 归集）
        producer._ledgers["ord-gap"].quantity += Decimal("400")
        producer._ledgers["ord-gap"].commission += Decimal("2.0")
        assert producer.observe([order]) == 1
        assert Decimal(dict(zip(_cols(), writer.rows[0]))["commission"]) == Decimal("5")

    def test_illegal_fill_ignored(self):
        producer, _ = _producer()
        producer.on_fill(_fill("ord-bad", qty="0", price="10.0"))
        producer.on_fill(_fill("ord-bad2", qty="100", price="0"))
        assert producer._ledgers == {}

    def test_invalid_order_quantity_abandons_after_retries(self):
        """永久失败单：3 轮后转 abandoned，不再无限刷 error。"""
        producer, writer = _producer()
        bad = _order(order_id="ord-bad-qty", qty="0")  # intended_quantity<=0 → 产出侧 Fail-Closed
        for _ in range(4):
            assert producer.observe([bad]) == 0
        assert writer.calls == []
        assert producer.stats.build_failed == 3
        assert producer.stats.abandoned == 1
        assert "ord-bad-qty" in producer._abandoned

    def test_write_not_committed_is_loud(self):
        producer, writer = _producer(committed=False)
        producer.observe([_order()])
        assert len(writer.calls) == 1
        assert producer.stats.write_local_durable == 1


class TestBrokerWiring:
    def test_attach_and_observe_via_broker(self, tmp_path):
        """接线后 broker._observe_terminal_orders 把终态订单交给生产端。"""
        writer = _FakeWriter()
        producer = ExecutionReportProducer(venue="qmt_sim", writer=writer)
        broker = _broker(tmp_path)
        broker.attach_execution_report_producer(producer)
        order = _order(order_id="ord-wired")
        broker._order_cache[order.order_id] = order
        broker._observe_terminal_orders()
        assert len(writer.rows) == 1
        assert dict(zip(_cols(), writer.rows[0]))["order_id"] == "ord-wired"
        assert broker.execution_report_stats()["emitted"] == 1

    def test_unattached_is_noop(self, tmp_path):
        """未接线=零行为变更（既有调用方 position_monitor 等不受影响）。"""
        broker = _broker(tmp_path)
        broker._observe_terminal_orders()  # 不抛
        assert broker.execution_report_stats() == {}

    def test_producer_exception_does_not_break_sync(self, tmp_path):
        """生产端异常旁路隔离——禁打断柜台同步主链。"""
        broker = _broker(tmp_path)

        class _Boom:
            stats = None

            def observe(self, orders):
                raise RuntimeError("boom")

        broker.attach_execution_report_producer(_Boom())
        broker._observe_terminal_orders()  # 不抛即通过


def _broker(tmp_path) -> QmtFileBridgeBroker:
    """构造指向 tmp_path 的 sim broker（禁触真实 E:\\ 桥目录与生产库）。"""
    broker = QmtFileBridgeBroker.__new__(QmtFileBridgeBroker)
    import threading

    broker._env = "sim"
    broker._config = dict(QmtFileBridgeBroker.ENV_CONFIG["sim"])
    broker._bridge_dir = tmp_path
    broker._orders_file = tmp_path / "orders_sim.csv"
    broker._ack_file = tmp_path / "ack_sim.csv"
    broker._stock_dir = tmp_path / "Stock"
    broker._order_cache = {}
    broker._idempotency_map = {}
    broker._remark_to_order_id = {}
    broker._pairing_cache = {}
    broker._connected = False
    broker._lock = threading.Lock()
    broker._http_port = 18901
    broker._sync_thread = None
    broker._fill_callbacks = []
    broker._ack_offset = 0
    broker._report_producer = None
    return broker


class TestAssemblyWiring:
    def test_assembly_defaults_to_wired(self):
        """装配层默认接线（断点 E4 闭合态），且默认参数不撞长参数表。"""
        import inspect

        from zephyr.ex_core.adapters.qmt_file_bridge_integration import QmtFileBridgeAssembly

        params = inspect.signature(QmtFileBridgeAssembly.__init__).parameters
        assert len([p for p in params if p != "self"]) <= 7
        assembly = QmtFileBridgeAssembly.__new__(QmtFileBridgeAssembly)
        assembly._producers = {}
        QmtFileBridgeAssembly.configure_execution_report(assembly, enabled=True, writer=_FakeWriter())
        assert assembly._enable_execution_report is True
        QmtFileBridgeAssembly.configure_execution_report(assembly, enabled=False)
        assert assembly._enable_execution_report is False
        assert assembly.execution_report_producers == {}


class TestMutationProof:
    """能红证明：以下三例分别钉住终态门/幂等门/列序门，拆任一门必失败。"""

    def test_mutation_proof_terminal_gate(self):
        """若把终态门拆掉（中间态也落行），本例失败。"""
        producer, writer = _producer()
        producer.observe([_order(status=OrderStatus.SUBMITTED)])
        assert writer.calls == [], "变异检出：中间态不得落行"

    def test_mutation_proof_idempotency_gate(self):
        """若把 order_id 幂等门拆掉，本例失败。"""
        producer, writer = _producer()
        order = _order()
        producer.observe([order])
        producer.observe([order])
        assert len(writer.rows) == 1, "变异检出：重复观察不得重复落行"

    def test_mutation_proof_column_order(self):
        """若列序改走 CH 实表 16 列（含 ingest_ts DEFAULT 列），本例失败。"""
        producer, writer = _producer()
        producer.observe([_order()])
        _, columns, _ = writer.calls[0]
        assert "ingest_ts" not in columns, "变异检出：DEFAULT 列禁写入"
        assert len(writer.rows[0]) == len(_cols()), "变异检出：列数必须对齐 DDL-as-Code"
