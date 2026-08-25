# [BLUEPRINT] MOD-SIG-111 | docs/03_modules/_domain_fundamental_signal/trace_context_store/blueprint.md
# [MODULE] zephyr.signal_fundamental.audit.trace_context_store
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] sqlite3(stdlib); lineage_sink/clock 注入（不 import D_DATA_GOV）
# [CONSUMERS] 运行时装配批（FactorSignal/SynthesizedSignal 生产侧填充 trace_context 后写入 / EX_CORE 订单层 span 写入 / D_DATA_GOV lineage_tracker sink 绑定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] (trace_id,span_id) 主键幂等(重复写拒绝); layer 词表闭合(data|factor|signal|order); trace_chain 按 (recorded_at,span_id) 确定性排序; lineage sink 异常不阻断本地写入; 单写者语义; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_fundamental_signal/trace_context_store/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TraceContextStoreError(占位 ZA-SIG-UNREGISTERED-TRACE-STORE)——空trace_id/span_id/ref_id/非法layer/未知signal_id/未知packet 时抛
# [TESTS] tests/signal_fundamental/audit/test_trace_context_store.py
# [A_module] module_id=MOD-SIG-111 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TraceContextStore — 信号追踪上下文存储（MOD-SIG-111）。

B2-05117（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-FUNDAMEN-002，D-SIGNAL
§1.1）：因子→信号→下单链路的**运行时实例级追踪上下文存储**——SQLite
追踪上下文表（trace_id→因子批次/信号/订单 span）+ 单笔信号**反查**因子
批次与原始行情引用 + 与 lineage_tracker 对接（结构级血缘边登记，sink DI
注入，不 import D_DATA_GOV）。

查重分工（蓝图 §0）：CTR-002/CTR-P1-015 契约 trace_context **字段已在案**
（codegen 不改）；signal_audit_logger=WORM 审计事件流（合规留痕，非反查
表）；lineage_tracker=结构级血缘 DAG（本件=实例级，链路摘要登记为边而不
重建 DAG）；ctr002_producer_validator=出厂验证（零交集）。
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "SignalOrigin",
    "TraceContextStore",
    "TraceContextStoreError",
    "TraceLayer",
    "TraceSpanRecord",
]

_LAYER_ORDER: Final[dict[str, int]] = {"data": 0, "factor": 1, "signal": 2, "order": 3}


class TraceContextStoreError(Exception):
    """追踪上下文存储输入非法/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-TRACE-STORE。
    """


class TraceLayer(str, Enum):
    """链路层级（词表闭合）。"""

    DATA = "data"
    FACTOR = "factor"
    SIGNAL = "signal"
    ORDER = "order"


@dataclass(frozen=True)
class TraceSpanRecord:
    """追踪 span 记录（frozen）。"""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    layer: TraceLayer
    ref_id: str
    recorded_at: datetime.datetime
    detail: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.layer, TraceLayer):
            raise TraceContextStoreError(f"非法 layer: {self.layer!r}")


@dataclass(frozen=True)
class SignalOrigin:
    """单笔信号反查结果。"""

    signal_span: TraceSpanRecord
    factor_spans: tuple[TraceSpanRecord, ...]
    data_spans: tuple[TraceSpanRecord, ...]
    order_spans: tuple[TraceSpanRecord, ...]


_DDL: Final[str] = """
CREATE TABLE IF NOT EXISTS trace_span (
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT,
    layer TEXT NOT NULL,
    ref_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (trace_id, span_id)
)
"""


class TraceContextStore:
    """SQLite 追踪上下文表 + 反查服务（:memory: 默认，文件路径注入）。"""

    def __init__(
        self,
        db_path: str = ":memory:",
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        lineage_sink: Callable[[str, str, str], None] | None = None,
    ) -> None:
        if not db_path:
            raise TraceContextStoreError("db_path 为空")
        self._clock = clock or (lambda: datetime.datetime(1970, 1, 1))
        self._lineage_sink = lineage_sink
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(_DDL)
        self._conn.commit()

    # ── 写入 ─────────────────────────────────────────────────────────────

    def record_span(self, record: TraceSpanRecord) -> bool:
        """写入 span；同 (trace_id, span_id) 幂等拒绝返回 False。"""
        if not record.trace_id:
            raise TraceContextStoreError("trace_id 为空")
        if not record.span_id:
            raise TraceContextStoreError("span_id 为空")
        if not record.ref_id:
            raise TraceContextStoreError("ref_id 为空")
        if not isinstance(record.layer, TraceLayer):
            raise TraceContextStoreError(f"非法 layer: {record.layer!r}")
        cur = self._conn.execute(
            "SELECT 1 FROM trace_span WHERE trace_id=? AND span_id=?",
            (record.trace_id, record.span_id),
        )
        if cur.fetchone() is not None:
            _log.warning("重复 span 拒绝: %s/%s", record.trace_id, record.span_id)
            return False
        self._conn.execute(
            "INSERT INTO trace_span (trace_id, span_id, parent_span_id, layer, ref_id, recorded_at, detail)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                record.trace_id,
                record.span_id,
                record.parent_span_id,
                record.layer.value,
                record.ref_id,
                record.recorded_at.isoformat(),
                record.detail,
            ),
        )
        self._conn.commit()
        return True

    # ── 反查 ─────────────────────────────────────────────────────────────

    def _row_to_span(self, row: tuple) -> TraceSpanRecord:
        return TraceSpanRecord(
            trace_id=row[0],
            span_id=row[1],
            parent_span_id=row[2],
            layer=TraceLayer(row[3]),
            ref_id=row[4],
            recorded_at=datetime.datetime.fromisoformat(row[5]),
            detail=row[6],
        )

    def trace_chain(self, trace_id: str) -> list[TraceSpanRecord]:
        """全链路 span：层级序(data→factor→signal→order)+同层 (recorded_at, span_id)。"""
        if not trace_id:
            raise TraceContextStoreError("trace_id 为空")
        cur = self._conn.execute(
            "SELECT trace_id, span_id, parent_span_id, layer, ref_id, recorded_at, detail"
            " FROM trace_span WHERE trace_id=?",
            (trace_id,),
        )
        spans = [self._row_to_span(r) for r in cur.fetchall()]
        spans.sort(key=lambda s: (_LAYER_ORDER[s.layer.value], s.recorded_at, s.span_id))
        return spans

    def signal_origin(self, signal_id: str) -> SignalOrigin:
        """单笔信号反查：信号 span + 上游因子批次/原始行情 + 下游订单。"""
        if not signal_id:
            raise TraceContextStoreError("signal_id 为空")
        cur = self._conn.execute(
            "SELECT trace_id, span_id, parent_span_id, layer, ref_id, recorded_at, detail"
            " FROM trace_span WHERE layer=? AND ref_id=?",
            (TraceLayer.SIGNAL.value, signal_id),
        )
        rows = cur.fetchall()
        if not rows:
            raise TraceContextStoreError(f"未知 signal_id: {signal_id!r}")
        signal_span = self._row_to_span(rows[0])
        chain = self.trace_chain(signal_span.trace_id)
        by_span = {s.span_id: s for s in chain}

        # 上游：沿 parent_span_id 回溯（信号→因子→数据）
        factor_spans: list[TraceSpanRecord] = []
        data_spans: list[TraceSpanRecord] = []
        cursor = signal_span.parent_span_id
        seen: set[str] = set()
        while cursor and cursor not in seen:
            seen.add(cursor)
            parent = by_span.get(cursor)
            if parent is None:
                break
            if parent.layer is TraceLayer.FACTOR:
                factor_spans.append(parent)
            elif parent.layer is TraceLayer.DATA:
                data_spans.append(parent)
            cursor = parent.parent_span_id

        # 下游：parent_span_id == 信号 span 的订单 span（确定性排序）
        order_spans = sorted(
            (s for s in chain if s.layer is TraceLayer.ORDER and s.parent_span_id == signal_span.span_id),
            key=lambda s: (s.recorded_at, s.span_id),
        )
        return SignalOrigin(
            signal_span=signal_span,
            factor_spans=tuple(factor_spans),
            data_spans=tuple(data_spans),
            order_spans=tuple(order_spans),
        )

    # ── lineage 对接 ──────────────────────────────────────────────────────

    def sync_to_lineage(self, trace_id: str) -> int:
        """链路摘要登记为结构级血缘边（sink 契约同 lineage_tracker.add_edge）。

        返回成功登记边数；sink 未注入或异常不阻断（log + 返回已登记数）。
        """
        chain = self.trace_chain(trace_id)
        if not chain or self._lineage_sink is None:
            return 0
        by_span = {s.span_id: s for s in chain}
        registered = 0
        for span in chain:
            if span.parent_span_id is None:
                continue
            parent = by_span.get(span.parent_span_id)
            if parent is None:
                continue
            try:
                self._lineage_sink(
                    parent.ref_id,
                    span.ref_id,
                    f"trace:{trace_id} {parent.layer.value}->{span.layer.value}",
                )
                registered += 1
            except Exception:  # noqa: BLE001 — sink 异常不阻断本地写入（蓝图 §1）
                _log.exception("lineage sink 登记失败: %s -> %s", parent.ref_id, span.ref_id)
        return registered

    def close(self) -> None:
        """关闭连接（单写者语义，文件库落盘后调用）。"""
        self._conn.close()
