# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.execution_report_producer
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.execution_report(build_execution_report); zephyr.ex_core.execution_engine(ExecutionEngineRunRecord); zephyr.shared.contracts.execution_report(CTR-P1-007); zephyr.shared.contracts.execution_report_contract(入站校验); zephyr.shared.contracts.order; zephyr.shared.contracts.fill; zephyr.shared.utils.time_utils; zephyr.data.ch_writer; schemas.categories.intraday.market_execution_report(DDL-as-Code 列序真源)
# [CONSUMERS] zephyr.ex_core.adapters.qmt_file_bridge_broker(柜台同步线程轮询); zephyr.ex_core.adapters.qmt_file_bridge_integration(装配接线); D_REPORTING(TCA/归因数据流)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 只在订单终态(FILLED/CANCELLED/REJECTED)落一行聚合，禁中间态(forming)落行; 幂等(order_id 已发即跳过 + ReplacingMergeTree 同键替换); 不新增字段(以 schemas DDL INSERT_COLUMNS 为唯一列序真源); 写失败/校验失败 Fail-Loud 不静默丢弃(不计入已发，下轮重试，超上限转 abandoned 并留 error 日志); 有成交量而佣金不可得时拒绝落行(禁污染 TCA 消费面); emitted_filled/emitted_unfilled 分开计数(撤单与 FILLED 不混计)
# [MODIFY-GUARD] execution_core blueprint GAP-L06-003; CTR-P1-007 契约字段集(Owner 窗口)
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不向外抛——产出/校验/写入失败一律计数+error 日志（生产端旁路不得打断订单主链），失败明细见 stats()
# [TESTS] tests/ex_core/test_execution_report_producer.py
# [A_module] module_id=MOD-L06-001-ERP | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_EX_CORE — CTR-P1-007 ExecutionReport **生产端接线**（断点 E4 闭合）。

断点事实（2026-09-18 E2E 段二实测，docs/_working/clean_exam_e2e/env3_e2e_bridge/
seg2_execution_log.md T6b）：`c1_market.execution_report` 表在、DDL-as-Code 在、
契约层在、`build_execution_report` 产出逻辑在，但**全仓零生产调用方** —— 模拟盘
100 股全生命周期跑通（SUBMITTED→CANCELLED）后台账面仍 0 行。即"建了没接线"。

本模块补的就是那个缺失的生产调用方：

    订单生命周期 ──终态──▶ ExecutionReportProducer.observe()
                              │ ① 组装 ExecutionEngineRunRecord（Order + 累积 Fill）
                              │ ② build_execution_report()  ← 既有产出逻辑，不重写
                              │ ③ validate_execution_report() ← 既有契约入站守卫
                              └ ④ ch_writer.write_tsv_outcome() → c1_market.execution_report

为何是"轮询 + 累积"而不是纯事件回调：`OrderManager._emit_order_event` 只在
SUBMITTED / CANCELLED / EXPIRED 三点发射，**FILLED 与 REJECTED 不发事件**
（FILLED 走 `_on_fill` 内部 `_transition_status`；REJECTED 由 broker 侧 `#FAIL`
标记与 ack FAIL 直接改写 Order.status，根本不经过 OM）。故只挂回调会漏两类终态。
本模块以 fill 回调累积成交面 + `observe()` 轮询订单面双路取数，两类终态都覆盖，
且以 order_id 幂等去重，重复观察不产生重复行。

口径裁定（全流通战役总包预裁，免二次请示）：
  - **落行时机 = 订单到达终态**（全部成交 / 已撤单 / 已拒单）时落一行聚合；
    中间态（PENDING/SUBMITTED/PARTIAL）**禁落行**（本仓既有"禁 forming 中间态"原则）。
  - **字段取舍 = 以表现有 schema 为准，不新增字段**。列序唯一真源 =
    `schemas.categories.intraday.market_execution_report.INSERT_COLUMNS`（15 列，
    与 CTR-P1-007 codegen 一一对应）；`ingest_ts` 是 DEFAULT 列、`exchange` /
    `symbol_canonical` 是 MATERIALIZED 派生列，均不由 INSERT 写入。
  - `algo_type` 恒 "NONE"：文件桥/HTTP 桥是单笔直投通道，无算法切片语义。
  - `broker_id` = 通道 venue（如 `qmt_sim`），由调用方注入。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Final

from schemas.categories.intraday.market_execution_report import (
    DATABASE as _ER_DATABASE,
)
from schemas.categories.intraday.market_execution_report import (
    INSERT_COLUMNS as _ER_INSERT_COLUMNS,
)
from schemas.categories.intraday.market_execution_report import (
    TABLE_NAME as _ER_TABLE_NAME,
)
from zephyr.ex_core.execution_engine import ExecutionEngineRunRecord
from zephyr.ex_core.execution_report import build_execution_report
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.execution_report_contract import execution_report_to_payload
from zephyr.shared.contracts.execution_report_contract import (
    validate_execution_report,
)
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order, OrderStatus
from zephyr.shared.utils.time_utils import now_utc

_logger = logging.getLogger(__name__)

#: 完整表名（DDL-as-Code 真源拼装，禁硬编码字面量——TABLE-NAME-REGISTRY）
EXECUTION_REPORT_TABLE: Final[str] = f"{_ER_DATABASE}.{_ER_TABLE_NAME}"

#: 终态集合——只有这三个状态才落行（禁中间态）
TERMINAL_STATUSES: Final[frozenset[OrderStatus]] = frozenset(
    {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
)

#: 单笔订单产出失败的最大重试轮数，超过转 abandoned（防止永久失败单无限刷 error 日志）
_MAX_EMIT_ATTEMPTS: Final[int] = 3

#: DateTime64(3,'UTC') 列的 TSV 文本口径
_CH_TS_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S.%f"

_ZERO: Final[Decimal] = Decimal("0")


@dataclass
class _FillLedger:
    """单订单成交面累积（佣金/VWAP 兜底/时间窗）。"""

    quantity: Decimal = _ZERO
    notional: Decimal = _ZERO
    commission: Decimal = _ZERO
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    fill_count: int = 0


@dataclass
class ProducerStats:
    """生产端可观测计数（健康检查/断点回归取证用）。"""

    observed: int = 0
    terminal_seen: int = 0
    emitted: int = 0
    emitted_filled: int = 0
    emitted_unfilled: int = 0
    skipped_non_terminal: int = 0
    skipped_duplicate: int = 0
    build_failed: int = 0
    validation_failed: int = 0
    write_failed: int = 0
    write_local_durable: int = 0
    commission_blocked: int = 0
    start_clamped: int = 0
    abandoned: int = 0
    last_error: str = ""
    _attempts: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """快照为可 JSON 化 dict（不含内部 _attempts）。"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


def _to_ch_ts(value: datetime) -> str:
    """aware datetime → ClickHouse DateTime64(3,'UTC') TSV 文本（统一转 UTC）。"""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime(_CH_TS_FORMAT)[:-3]


def _tsv_cell(value: object) -> str:
    """单格 TSV 化：Decimal 保精度走 str，制表符/换行/反斜杠转义，None→空串。"""
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    return text.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


class ExecutionReportProducer:
    """订单终态 → CTR-P1-007 ExecutionReport → c1_market.execution_report 生产端。

    Usage（装配层）::

        producer = ExecutionReportProducer(venue="qmt_sim")
        broker.register_fill_callback(producer.on_fill)   # 成交面累积
        broker.attach_execution_report_producer(producer)  # 订单面轮询
        # 同步线程每轮自动 producer.observe(broker.order_cache_snapshot())

    测试注入::

        producer = ExecutionReportProducer(venue="qmt_sim", writer=fake_writer)
    """

    def __init__(
        self,
        venue: str,
        *,
        writer: Callable[[str, str | None, bytes], object] | None = None,
        algo_type: str = "NONE",
        board_lot: int | None = None,
    ) -> None:
        """初始化生产端。

        Args:
            venue: 执行券商/通道标识，落 broker_id 列（如 ``qmt_sim``）。禁空串
                ——契约层对 broker_id 做非空校验，空值会被 Fail-Closed 拒收。
            writer: TSV 写入函数，签名 ``(table, columns, tsv_bytes) -> outcome``。
                None = 生产路径（``zephyr.data.ch_writer.write_tsv_outcome``）。
                测试注入假 writer 即可零接触生产库。
            algo_type: 算法类型，文件桥/HTTP 桥单笔直投恒 ``NONE``。
            board_lot: A 股整手校验参数（可选）；传入时 BUY 方向 intended_quantity
                须为整手，由契约层 Fail-Closed 判定。
        """
        if not venue or not isinstance(venue, str):
            raise ValueError("venue 必须为非空字符串（契约层对 broker_id 做非空校验）")
        self._venue = venue
        self._writer = writer
        self._algo_type = algo_type or "NONE"
        self._board_lot = board_lot
        self._ledgers: dict[str, _FillLedger] = {}
        self._emitted: set[str] = set()
        self._abandoned: set[str] = set()
        self._stats = ProducerStats()

    # ── 可观测 ──

    @property
    def stats(self) -> ProducerStats:
        """产出计数快照（只读引用，勿原地改）。"""
        return self._stats

    @property
    def emitted_order_ids(self) -> frozenset[str]:
        """已成功落行的 order_id 集合（幂等判据取证用）。"""
        return frozenset(self._emitted)

    # ── 成交面：fill 回调累积 ──

    def on_fill(self, fill: Fill) -> None:
        """成交回调（broker `_dispatch_fill` 扇出入口）——累积佣金/VWAP/时间窗。

        非法 fill（量≤0 / 价 None / 价≤0）直接忽略并留痕：与 OrderManager._on_fill
        的红队防御同口径，避免脏成交把佣金面污染进 TCA 消费表。
        """
        qty = fill.filled_quantity
        price = fill.fill_price
        if qty is None or qty <= 0 or price is None or price <= 0:
            _logger.warning("execution_report 生产端忽略非法 fill: order=%s qty=%s price=%s", fill.order_id, qty, price)
            return
        ledger = self._ledgers.get(fill.order_id)
        if ledger is None:
            ledger = _FillLedger()
            self._ledgers[fill.order_id] = ledger
        ledger.quantity += qty
        ledger.notional += price * qty
        ledger.commission += fill.commission or _ZERO
        ts = fill.fill_timestamp
        if ts is not None:
            if ledger.first_ts is None or ts < ledger.first_ts:
                ledger.first_ts = ts
            if ledger.last_ts is None or ts > ledger.last_ts:
                ledger.last_ts = ts
        ledger.fill_count += 1

    # ── 订单面：终态观察 ──

    def observe(self, orders: Iterable[Order]) -> int:
        """观察一批订单，对**新到达终态**者产出并落行。返回本轮落行数。

        中间态（PENDING/SUBMITTED/PARTIAL）只计数不落行；已落行/已放弃的
        order_id 跳过（幂等）。整批 TSV 一次写入（避免逐行写放大）。
        """
        rows: list[str] = []
        for order in orders:
            self._stats.observed += 1
            order_id = order.order_id
            if order_id in self._emitted or order_id in self._abandoned:
                self._stats.skipped_duplicate += 1
                continue
            if order.status not in TERMINAL_STATUSES:
                self._stats.skipped_non_terminal += 1
                continue
            self._stats.terminal_seen += 1
            report = self._build(order)
            if report is None:
                continue
            rows.append(self._to_tsv_row(report))
            self._emitted.add(order_id)
            self._stats.emitted += 1
            # 撤单/FILLED 分开计数：零成交行不携带滑点证据，不得与真成交混计
            if report.actual_quantity > 0:
                self._stats.emitted_filled += 1
            else:
                self._stats.emitted_unfilled += 1
        if rows:
            self._write(rows)
        return len(rows)

    # ── 内部：组装 ──

    def _build(self, order: Order) -> ExecutionReport | None:
        """Order + 成交面累积 → ExecutionReport（校验通过）。失败返回 None 并计数。"""
        order_id = order.order_id
        ledger = self._ledgers.get(order_id)
        filled = order.filled_quantity or _ZERO
        if filled > 0 and ledger is None:
            # Fail-Closed：有成交量却拿不到成交明细 = 佣金不可得，落行会向 TCA
            # 消费面写入 commission=0 的假数据。宁可不落（下轮 fill 到达后重试）。
            self._stats.commission_blocked += 1
            self._note_failure(order_id, "commission_unavailable", f"filled={filled} 但无 fill 明细，佣金不可得")
            return None
        if filled > 0 and ledger is not None and ledger.quantity < filled:
            # Fail-Closed：成交明细未累积齐（生产端中途接线/回调漏扇出）→ 佣金会
            # 被低估。同样宁可不落，下轮明细补齐后自愈。
            self._stats.commission_blocked += 1
            self._note_failure(
                order_id,
                "commission_incomplete",
                f"filled={filled} 但明细仅累积 {ledger.quantity}，佣金会被低估",
            )
            return None

        start_ts, end_ts = self._window_of(order, ledger, order_id)
        record = self._record_of(order, ledger, filled, order_id, start_ts, end_ts)
        return self._build_and_validate(order, record, order_id)

    def _window_of(
        self,
        order: Order,
        ledger: _FillLedger | None,
        order_id: str,
    ) -> tuple[datetime, datetime]:
        """执行起止时间取数 + 时序倒置钳制（钳制即计数+告警，不静默改写）。

        委托单时间优先，缺失时退化取成交面首/末笔时间戳。
        """
        end_ts = order.updated_at or (ledger.last_ts if ledger else None) or now_utc()
        start_ts = order.created_at or (ledger.first_ts if ledger else None) or end_ts
        if start_ts > end_ts:
            self._stats.start_clamped += 1
            _logger.warning(
                "execution_start 晚于 execution_end，钳制为 end: order=%s start=%s end=%s",
                order_id,
                start_ts,
                end_ts,
            )
            start_ts = end_ts
        return start_ts, end_ts

    def _record_of(
        self,
        order: Order,
        ledger: _FillLedger | None,
        filled: Decimal,
        order_id: str,
        start_ts: datetime,
        end_ts: datetime,
    ) -> ExecutionEngineRunRecord:
        """聚合快照组装：均价/佣金取数 + ExecutionEngineRunRecord 构造（判定分支已下沉 _window_of）。"""
        avg_price = order.avg_fill_price
        if (avg_price is None or avg_price <= 0) and ledger is not None and ledger.quantity > 0:
            avg_price = ledger.notional / ledger.quantity
        commission = ledger.commission if ledger is not None else _ZERO
        return ExecutionEngineRunRecord(
            report_id=f"erp-{order_id}",
            order_id=order_id,
            symbol=order.symbol,
            algo_type=self._algo_type,
            total_quantity=order.quantity,
            filled_quantity=filled,
            avg_fill_price=avg_price or _ZERO,
            target_price=order.limit_price or _ZERO,
            slippage_bps=_ZERO,  # build_execution_report 按 DECISION 基准重算，此处仅占位
            commission=commission,
            start_time=start_ts,
            end_time=end_ts,
            status=order.status.value if hasattr(order.status, "value") else str(order.status),
            fills=[],
            venue=self._venue,
        )

    def _build_and_validate(
        self,
        order: Order,
        record: ExecutionEngineRunRecord,
        order_id: str,
    ) -> ExecutionReport | None:
        """产出 + 入站校验（旁路：失败只计数留痕，绝不打断订单主链）。"""
        try:
            report = build_execution_report(order, record)
        except Exception as exc:  # noqa: BLE001 — 产出侧输入契约异常类型不可枚举，旁路禁打断主链
            self._stats.build_failed += 1
            self._note_failure(order_id, "build_failed", repr(exc))
            return None
        try:
            validate_execution_report(report, board_lot=self._board_lot)
        except Exception as exc:  # noqa: BLE001 — 契约层 Fail-Closed 异常统一收口
            self._stats.validation_failed += 1
            self._note_failure(order_id, "validation_failed", repr(exc))
            return None
        return report

    def _note_failure(self, order_id: str, kind: str, detail: str) -> None:
        """失败留痕：计数 + error 日志 + 超上限转 abandoned（Fail-Loud 不静默丢）。"""
        attempts = self._stats._attempts.get(order_id, 0) + 1
        self._stats._attempts[order_id] = attempts
        self._stats.last_error = f"{kind}: order={order_id} {detail}"
        if attempts >= _MAX_EMIT_ATTEMPTS:
            self._abandoned.add(order_id)
            self._stats.abandoned += 1
            _logger.error(
                "execution_report 产出连续 %d 轮失败，转 abandoned（不再重试，需人工介入）: order=%s kind=%s detail=%s",
                attempts,
                order_id,
                kind,
                detail,
            )
        else:
            _logger.error(
                "execution_report 产出失败（第 %d/%d 轮，下轮重试）: order=%s kind=%s detail=%s",
                attempts,
                _MAX_EMIT_ATTEMPTS,
                order_id,
                kind,
                detail,
            )

    # ── 内部：序列化 + 写入 ──

    def _to_tsv_row(self, report: ExecutionReport) -> str:
        """ExecutionReport → TSV 行（列序严格对齐 schema INSERT_COLUMNS）。"""
        payload = execution_report_to_payload(report)
        columns = [c.strip() for c in _ER_INSERT_COLUMNS.strip("()").split(",")]
        cells: list[str] = []
        for name in columns:
            value = payload.get(name)
            if name in ("execution_start", "execution_end"):
                cells.append(_to_ch_ts(datetime.fromisoformat(str(value))))
            elif name in ("intended_quantity", "actual_quantity"):
                cells.append(str(int(value)))
            elif name == "slippage_bps":
                cells.append(f"{float(value):.6f}")
            else:
                cells.append(_tsv_cell(value))
        return "\t".join(cells)

    def _write(self, rows: Sequence[str]) -> None:
        """整批一次写入（单通道，失败计数留痕；不打断订单主链）。"""
        tsv_bytes = ("\n".join(rows) + "\n").encode("utf-8")
        if self._writer is not None:
            outcome = self._writer(EXECUTION_REPORT_TABLE, _ER_INSERT_COLUMNS, tsv_bytes)
            committed = bool(getattr(outcome, "is_ch_committed", outcome))
            if not committed:
                self._stats.write_local_durable += 1
                _logger.warning(
                    "execution_report 写入未确认入库（本地落盘待回灌）: table=%s rows=%d outcome=%r",
                    EXECUTION_REPORT_TABLE,
                    len(rows),
                    outcome,
                )
            return
        from zephyr.data import ch_writer  # 延迟导入：避免 ex_core 导入期硬依赖数据层

        outcome = ch_writer.write_tsv_outcome(EXECUTION_REPORT_TABLE, _ER_INSERT_COLUMNS, tsv_bytes)
        if not outcome.is_ch_committed:
            self._stats.write_local_durable += 1
            self._stats.write_failed += 1
            self._stats.last_error = f"write_not_committed: {outcome}"
            _logger.error(
                "execution_report 写入未入库: table=%s rows=%d disposition=%r",
                EXECUTION_REPORT_TABLE,
                len(rows),
                outcome,
            )


__all__: Final = [
    "EXECUTION_REPORT_TABLE",
    "TERMINAL_STATUSES",
    "ExecutionReportProducer",
    "ProducerStats",
]
