# [BLUEPRINT] MOD-FE-009 | docs/03_modules/_domain_frontend/trace_waterfall_view/blueprint.md
# [MODULE] zephyr.frontend.trace_waterfall_view
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（纯内存；span_store 注入不触网，装配批自 shared.observability.tracing 适配）
# [CONSUMERS] 运行时装配批（Trace瀑布面板检索/布局/采样/慢链路高亮数据供给）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四视图词表闭合(trade_main|data_chain|ai_ops|gpu_infer); span树闭合(父引用可解析/无环/单span单父); span.trace_id须等于检索id; 采样=sha256(trace_id)哈希确定性; 慢链路=视图阈值映射(duration>=threshold); 瀑布行=DFS先序父子嵌套; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/trace_waterfall_view/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TraceViewError(占位 ZA-FE-UNREGISTERED-TRACE-VIEW)——store缺失/非法采样率/非法阈值/空trace_id/未知trace/span类型或字段非法/父引用缺失/父链成环时抛
# [TESTS] tests/frontend/test_trace_waterfall_view.py
# [A_module] module_id=MOD-FE-009 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""TraceWaterfallView — 端到端追踪瀑布视图器（MOD-FE-009）。

B14-04627（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-010，A9 D-FRONTEND-15，
canonical 承接 CAND-FE-005 归并）：跨进程 Trace 瀑布图**数据底座**（只做
后端数据不做页面接线）——四视图词表闭合（交易主链路/数据链/AI运维链/
GPU推理链）+ trace_id 检索（注入 span 存储）+ span 瀑布布局（DFS 先序父
子嵌套时间轴）+ 采样率配置（sha256 哈希确定性采样）+ 慢链路高亮（视图
阈值映射）。

查重分工（蓝图 §0）：shared.observability.tracing=span 产生/导出（本件
不埋点，span 经 store 回调注入只读检索）；alert_center=告警面板（零交集）；
CAND-FE-005（B1 稿追踪可视化）语义归并本件。纯内存确定性，无时钟/随机
源依赖（采样走哈希不走路径随机数）。
"""

from __future__ import annotations

import datetime
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "Span",
    "TraceChainView",
    "TraceViewError",
    "TraceWaterfallView",
    "WaterfallPayload",
    "WaterfallRow",
]


class TraceViewError(Exception):
    """Trace 瀑布视图输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-TRACE-VIEW。
    """


class TraceChainView(str, Enum):
    """链路视图词表（闭合）。"""

    TRADE_MAIN = "trade_main"
    DATA_CHAIN = "data_chain"
    AI_OPS = "ai_ops"
    GPU_INFER = "gpu_infer"


#: 默认慢链路阈值（ms/视图；注入映射可覆盖单项）
_DEFAULT_SLOW_THRESHOLD_MS: Final[dict[TraceChainView, float]] = {
    TraceChainView.TRADE_MAIN: 500.0,
    TraceChainView.DATA_CHAIN: 1000.0,
    TraceChainView.AI_OPS: 2000.0,
    TraceChainView.GPU_INFER: 800.0,
}


@dataclass(frozen=True)
class Span:
    """追踪 span（DI 注入存储的检索形态，frozen）。"""

    span_id: str
    trace_id: str
    parent_span_id: str | None
    name: str
    view: TraceChainView
    start_ts: datetime.datetime
    duration_ms: float


@dataclass(frozen=True)
class WaterfallRow:
    """瀑布布局行（DFS 先序父子嵌套 + 相对偏移时间轴 + 慢链路标记）。"""

    span_id: str
    parent_span_id: str | None
    name: str
    view: TraceChainView
    depth: int
    start_offset_ms: float
    duration_ms: float
    slow: bool


@dataclass(frozen=True)
class WaterfallPayload:
    """单 trace 瀑布 payload（行序=DFS 先序，frozen）。"""

    trace_id: str
    rows: tuple[WaterfallRow, ...]
    total_duration_ms: float
    slow_count: int


class TraceWaterfallView:
    """Trace 瀑布数据件（检索 + 瀑布布局 + 采样 + 慢链路高亮）。"""

    def __init__(
        self,
        *,
        span_store: Callable[[str], Iterable[Span]] | None,
        sampling_rate: float = 1.0,
        slow_threshold_ms: Mapping[TraceChainView, float] | None = None,
    ) -> None:
        if span_store is None or not callable(span_store):
            raise TraceViewError("span_store 未注入（trace_id 检索强制注入存储，禁止旁路）")
        if isinstance(sampling_rate, bool) or not 0 < sampling_rate <= 1:
            raise TraceViewError(f"非法采样率: {sampling_rate!r}（须在 (0,1] 区间）")
        self._store = span_store
        self._sampling_rate = float(sampling_rate)
        self._thresholds = dict(_DEFAULT_SLOW_THRESHOLD_MS)
        if slow_threshold_ms is not None:
            for view, value in slow_threshold_ms.items():
                if not isinstance(view, TraceChainView):
                    raise TraceViewError(f"非法阈值视图键: {view!r}")
                if value <= 0:
                    raise TraceViewError(f"非法慢链路阈值: {value!r}（须为正数）")
                self._thresholds[view] = float(value)

    # ── 词表 / 采样 ───────────────────────────────────────────────────────

    @classmethod
    def views(cls) -> tuple[TraceChainView, ...]:
        """四视图词表（闭合，枚举声明序）。"""
        return tuple(TraceChainView)

    def should_sample(self, trace_id: str) -> bool:
        """确定性采样：sha256(trace_id) 前 8 字节小数位 < 采样率（同输入必同输出）。"""
        if not trace_id:
            raise TraceViewError("trace_id 为空")
        digest = hashlib.sha256(trace_id.encode("utf-8")).digest()
        fraction = int.from_bytes(digest[:8], "big") / 2**64
        return fraction < self._sampling_rate

    # ── trace 检索 + 瀑布布局 ─────────────────────────────────────────────

    def waterfall(self, trace_id: str) -> WaterfallPayload:
        """trace_id 检索 + 瀑布布局（DFS 先序父子嵌套，偏移相对 trace 起点）。"""
        if not trace_id:
            raise TraceViewError("trace_id 为空")
        spans = list(self._store(trace_id))
        if not spans:
            raise TraceViewError(f"未知 trace: {trace_id!r}（span 存储无记录）")

        by_id: dict[str, Span] = {}
        for span in spans:
            if not isinstance(span, Span):
                raise TraceViewError(f"span 类型错误: {span!r}")
            if span.trace_id != trace_id:
                raise TraceViewError(f"span.trace_id 不符: {span.trace_id!r}（检索 {trace_id!r}）")
            if not span.span_id:
                raise TraceViewError("span_id 为空")
            if span.span_id in by_id:
                raise TraceViewError(f"span_id 重复: {span.span_id!r}")
            if not isinstance(span.view, TraceChainView):
                raise TraceViewError(f"非法链路视图: {span.view!r}")
            if not isinstance(span.start_ts, datetime.datetime):
                raise TraceViewError(f"非法 start_ts: {span.start_ts!r}")
            if span.duration_ms < 0:
                raise TraceViewError(f"非法 duration_ms: {span.duration_ms!r}（须非负）")
            if span.parent_span_id == span.span_id:
                raise TraceViewError(f"自父非法: {span.span_id!r}")
            by_id[span.span_id] = span

        depth_cache: dict[str, int] = {}

        def _depth(span: Span, visiting: frozenset[str]) -> int:
            if span.span_id in depth_cache:
                return depth_cache[span.span_id]
            if span.parent_span_id is None:
                depth_cache[span.span_id] = 0
                return 0
            parent = by_id.get(span.parent_span_id)
            if parent is None:
                raise TraceViewError(f"父引用缺失: {span.parent_span_id!r}")
            if span.span_id in visiting:
                raise TraceViewError(f"父链成环: {span.span_id!r}")
            depth = _depth(parent, visiting | {span.span_id}) + 1
            depth_cache[span.span_id] = depth
            return depth

        depths = {sid: _depth(span, frozenset()) for sid, span in by_id.items()}

        trace_start = min(span.start_ts for span in spans)
        trace_end = max(span.start_ts + datetime.timedelta(milliseconds=span.duration_ms) for span in spans)
        total_ms = (trace_end - trace_start).total_seconds() * 1000.0

        children: dict[str | None, list[Span]] = {}
        for span in spans:
            children.setdefault(span.parent_span_id, []).append(span)
        for group in children.values():
            group.sort(key=lambda s: (s.start_ts, s.span_id))

        rows: list[WaterfallRow] = []

        def _emit(span: Span) -> None:
            rows.append(
                WaterfallRow(
                    span_id=span.span_id,
                    parent_span_id=span.parent_span_id,
                    name=span.name,
                    view=span.view,
                    depth=depths[span.span_id],
                    start_offset_ms=(span.start_ts - trace_start).total_seconds() * 1000.0,
                    duration_ms=float(span.duration_ms),
                    slow=span.duration_ms >= self._thresholds[span.view],
                )
            )
            for child in children.get(span.span_id, []):
                _emit(child)

        for root in children.get(None, []):
            _emit(root)

        _log.debug("瀑布布局: trace=%s spans=%d slow=%d", trace_id, len(rows), sum(1 for r in rows if r.slow))
        return WaterfallPayload(
            trace_id=trace_id,
            rows=tuple(rows),
            total_duration_ms=total_ms,
            slow_count=sum(1 for row in rows if row.slow),
        )
