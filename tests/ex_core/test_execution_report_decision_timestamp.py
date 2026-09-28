# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_execution_report_decision_timestamp
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] pytest; zephyr.ex_core.execution_report; zephyr.ex_core.execution_report_producer; zephyr.shared.contracts.execution_report_contract; schemas.categories.intraday.market_execution_report
# [CONSUMERS] FAC-E9 IS 分解时间戳 FIELD-GAP 治本守卫（CTR-P1-007 V2 扩展 decision_timestamp 全链贯通）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] decision_timestamp=Order.created_at 原样贯通（None=未布点合法，禁墙钟伪造）；
#   payload 往返 None 容忍（缺键与显式 None 同语义）；TSV NULL=\N；列序真源=INSERT_COLUMNS
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-L06-001-ERP-TS | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E9 IS 分解时间戳链测试——决策时刻从 Order.created_at 到 TSV 落行全程贯通。

背景：FAC-E9 挖矿簿 FIELD-GAP 实证——execution_report 列族无决策时间戳，
Perold 1988 IS 四分解（延迟/执行/机会/费用）无锚点。本套件钉住 V2 扩展：
契约字段 → 产出写入点 → 序列化 NULL 语义，三环缺一即红。

测试纪律：writer 一律注入假实现，零接触生产库/网络。
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal

from schemas.categories.intraday.market_execution_report import INSERT_COLUMNS
from zephyr.ex_core.execution_engine import ExecutionEngineRunRecord
from zephyr.ex_core.execution_report import build_execution_report
from zephyr.ex_core.execution_report_producer import ExecutionReportProducer
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.execution_report_contract import (
    execution_report_from_payload,
    execution_report_to_payload,
)
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType

_DECISION_TS = datetime(2026, 9, 27, 1, 2, 3, tzinfo=UTC)


def _order(created_at: datetime | None = _DECISION_TS) -> Order:
    return Order(
        idempotency_key="smoke-ts-1",
        order_id="ord-ts-1",
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=OrderSide.BUY,
        strategy_id="smoke_e9_is",
        symbol="510300.SH",
        created_at=created_at,
        status=OrderStatus.FILLED,
    )


def _record() -> ExecutionEngineRunRecord:
    return ExecutionEngineRunRecord(
        report_id="rpt-ts-1",
        order_id="ord-ts-1",
        symbol="510300.SH",
        algo_type="NONE",
        total_quantity=Decimal("100"),
        filled_quantity=Decimal("100"),
        avg_fill_price=Decimal("4.08"),
        target_price=Decimal("4.07"),
        slippage_bps=Decimal("0"),
        commission=Decimal("5.00"),
        start_time=datetime(2026, 9, 27, 1, 2, 4, tzinfo=UTC),
        end_time=datetime(2026, 9, 27, 1, 2, 5, tzinfo=UTC),
        status="FILLED",
        venue="qmt_sim",
    )


class TestBuildWritePoint:
    def test_decision_timestamp_from_order_created_at(self):
        report = build_execution_report(_order(), _record())
        assert report.decision_timestamp == _DECISION_TS.isoformat()

    def test_decision_timestamp_none_when_upstream_absent(self):
        report = build_execution_report(_order(created_at=None), _record())
        assert report.decision_timestamp is None


class TestPayloadRoundtrip:
    def test_none_roundtrip_tolerated(self):
        report = build_execution_report(_order(created_at=None), _record())
        payload = execution_report_to_payload(report)
        assert payload["decision_timestamp"] is None
        back = execution_report_from_payload(payload)
        assert back.decision_timestamp is None

    def test_value_roundtrip_preserved(self):
        report = build_execution_report(_order(), _record())
        back = execution_report_from_payload(execution_report_to_payload(report))
        assert back.decision_timestamp == _DECISION_TS.isoformat()


class TestTsvSerialization:
    def _row_cells(self, report: ExecutionReport) -> dict[str, str]:
        producer = ExecutionReportProducer(venue="qmt_sim", writer=lambda *a, **k: None)  # type: ignore[arg-type,assignment]
        columns = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
        cells = producer._to_tsv_row(report).split("\t")
        return dict(zip(columns, cells))

    def test_none_serializes_to_null_literal(self):
        report = build_execution_report(_order(created_at=None), _record())
        assert self._row_cells(report)["decision_timestamp"] == "\\N"

    def test_value_serializes_to_ch_ts(self):
        report = build_execution_report(_order(), _record())
        assert self._row_cells(report)["decision_timestamp"] == "2026-09-27 01:02:03.000"

    def test_insert_columns_carries_new_field(self):
        cols = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
        assert cols.count("decision_timestamp") == 1
        assert cols.index("decision_timestamp") == cols.index("execution_end") + 1


class TestExistingConsumersUnbroken:
    def test_fifteen_legacy_fields_unchanged(self):
        """既有 15 字段消费者零破坏：基线字段集与 V2 前一致。"""
        legacy = {
            "order_id",
            "symbol",
            "direction",
            "intended_quantity",
            "actual_quantity",
            "intended_price",
            "vwap_price",
            "slippage_bps",
            "commission",
            "execution_start",
            "execution_end",
            "broker_id",
            "algo_type",
            "idempotency_key",
            "schema_version",
        }
        current = {f.name for f in ExecutionReport.__dataclass_fields__.values()}
        assert legacy <= current
        assert current - legacy == {"decision_timestamp"}

    def test_asdict_baseline_constructible_without_new_field(self):
        """缺省构造（不传 decision_timestamp）仍合法——旧调用点零改动。"""
        base = asdict(build_execution_report(_order(), _record()))
        base.pop("decision_timestamp")
        report = ExecutionReport(**base)
        assert report.decision_timestamp is None
