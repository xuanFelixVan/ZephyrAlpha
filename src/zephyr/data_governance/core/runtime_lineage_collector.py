# [BLUEPRINT] MOD-DATA_GOV-006 | docs/03_modules/_domain_data_governance/runtime_lineage_collector/blueprint.md
# [MODULE] zephyr.data_governance.core.runtime_lineage_collector
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.lineage_tracker; zephyr.data_governance.core.lineage_parser
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-open 不阻塞交易主链路(emit/flush 不抛异常); 畸形事件与缓冲溢出丢弃计 dropped; sink 失败事件回滚不丢; 幂等与环检测复用 MOD-DATA_GOV-002 不重造; 盘后汇总入图语义复用 MOD-DATA_GOV-004 不重造
# [MODIFY-GUARD] tests/data_governance/test_runtime_lineage_collector.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeLineageError(未登记错误码-申请中，仅构造/汇总面 Fail-Closed)
# [TESTS] tests/data_governance/test_runtime_lineage_collector.py
# [A_module] module_id=MOD-DATA_GOV-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""M8-S03 动态采集器（MOD-DATA_GOV-006）。

真源：construction_backlog_dig.tsv B10-02315（A1 交易决策架构 §30.4.3，
裁定=做 P1）+ CAND-DATGOV-003。

定位：运行时血缘动态采集缺失（TSV 现状）。在数据接入/因子计算/信号生成关键
路径插桩 emit 血缘事件（轻量缓冲写，**fail-open 不阻塞交易主链路**），盘后
汇总入 lineage_tracker。

  ① emit=内存缓冲 append（O(1)），畸形事件/缓冲溢出丢弃计 dropped，**不抛异常**；
     异步落盘/消息队列接线归运行时装配批（本模块不建后台线程/异步框架）；
  ② flush 交注入式 sink 回调；sink 失败事件回滚入缓冲（不丢数据）记 flush_errors；
  ③ 盘后汇总 `aggregate_into_tracker`：排空缓冲 → LineageEdge → 复用 S01
     `ingest_into_tracker`（批内去重首条胜出/幂等 updated/环 rejected 不中断）；
     幂等与环检测复用 MOD-DATA_GOV-002 不重造。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Final

from zephyr.data_governance.core.lineage_parser import LineageParseReport, ingest_into_tracker
from zephyr.data_governance.core.lineage_tracker import LineageEdge, LineageTracker

__all__: Final = [
    "CollectorStats",
    "RuntimeLineageCollector",
    "RuntimeLineageError",
    "RuntimeLineageEvent",
]

_log = logging.getLogger(__name__)

DEFAULT_MAX_BUFFER: Final[int] = 4096


class RuntimeLineageError(ValueError):
    """动态采集器构造/汇总面输入非法（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class RuntimeLineageEvent:
    """运行时血缘事件（不可变）。

    Attributes:
        source: 源节点（数据接入点/表/因子）
        target: 目标节点
        transformation: 变换描述（compute/generate/ingest 等）
        run_id: 运行批次标识（盘后汇总追溯）
        emitted_at: 事件时间（ISO 字符串，调用方供给）
        context: 附加上下文（任务名/主机等，可选）
    """

    source: str
    target: str
    transformation: str = "runtime"
    run_id: str = ""
    emitted_at: str = ""
    context: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CollectorStats:
    """采集计数（如实可查）。

    Attributes:
        emitted: 成功入缓冲事件数
        dropped: 丢弃事件数（畸形 + 缓冲溢出）
        flush_errors: sink 失败次数（事件已回滚）
        buffered: 当前缓冲内事件数
    """

    emitted: int
    dropped: int
    flush_errors: int
    buffered: int


class RuntimeLineageCollector:
    """运行时血缘采集器——轻量缓冲 + fail-open + 盘后汇总。

    emit/flush 路径不抛异常（fail-open 不阻塞交易主链路）；构造参数与
    汇总面 tracker 为空 Fail-Closed（RuntimeLineageError）。
    """

    def __init__(self, *, max_buffer: int = DEFAULT_MAX_BUFFER) -> None:
        if not isinstance(max_buffer, int) or max_buffer <= 0:
            raise RuntimeLineageError(f"max_buffer 必须为正整数: {max_buffer!r}")
        self._max_buffer = max_buffer
        self._buffer: list[RuntimeLineageEvent] = []
        self._emitted = 0
        self._dropped = 0
        self._flush_errors = 0

    def emit(
        self,
        source: str,
        target: str,
        transformation: str = "runtime",
        *,
        run_id: str = "",
        emitted_at: str = "",
        context: Mapping[str, str] | None = None,
    ) -> bool:
        """关键路径插桩入口（fail-open：畸形/溢出丢弃计数，永不抛出）。"""
        try:
            return self.emit_event(
                RuntimeLineageEvent(
                    source=source,
                    target=target,
                    transformation=transformation,
                    run_id=run_id,
                    emitted_at=emitted_at,
                    context=context or {},
                )
            )
        except Exception:  # noqa: BLE001 — fail-open 铁律：主链路永不因采集失败中断
            _log.exception("血缘事件 emit 异常（fail-open 丢弃）")
            self._dropped += 1
            return False

    def emit_event(self, event: RuntimeLineageEvent) -> bool:
        """事件对象入缓冲（fail-open；返回是否成功入缓冲）。"""
        try:
            if (
                not isinstance(event.source, str)
                or not event.source.strip()
                or not isinstance(event.target, str)
                or not event.target.strip()
            ):
                self._dropped += 1
                _log.warning("畸形血缘事件丢弃: source=%r target=%r", event.source, event.target)
                return False
            if len(self._buffer) >= self._max_buffer:
                self._dropped += 1
                _log.warning("血缘事件缓冲溢出丢弃（max_buffer=%d）", self._max_buffer)
                return False
            self._buffer.append(event)
            self._emitted += 1
            return True
        except Exception:  # noqa: BLE001 — fail-open 铁律
            _log.exception("血缘事件入缓冲异常（fail-open 丢弃）")
            self._dropped += 1
            return False

    def flush(self, sink: Callable[[list[RuntimeLineageEvent]], None]) -> int:
        """排空缓冲交 sink 回调（fail-open；sink 失败事件回滚不丢，返回成功交付数）。"""
        if not self._buffer:
            return 0
        drained = self._buffer
        self._buffer = []
        try:
            sink(drained)
        except Exception:  # noqa: BLE001 — fail-open 铁律：sink 故障不阻塞主链路
            _log.exception("血缘事件 sink 失败（事件回滚入缓冲）")
            self._buffer = drained + self._buffer
            self._flush_errors += 1
            return 0
        return len(drained)

    def aggregate_into_tracker(self, tracker: LineageTracker) -> LineageParseReport:
        """盘后汇总：排空缓冲 → LineageEdge → 复用 S01 入图语义（tracker 空 Fail-Closed）。"""
        if tracker is None:
            raise RuntimeLineageError("tracker 不能为空（Fail-Closed）")
        drained = self._buffer
        self._buffer = []
        edges = [
            LineageEdge(ev.source.strip(), ev.target.strip(), ev.transformation)
            for ev in drained
        ]
        return ingest_into_tracker(edges, tracker, sources=("runtime",))

    def stats(self) -> CollectorStats:
        """采集计数快照。"""
        return CollectorStats(
            emitted=self._emitted,
            dropped=self._dropped,
            flush_errors=self._flush_errors,
            buffered=len(self._buffer),
        )
