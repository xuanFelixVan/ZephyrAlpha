# [BLUEPRINT] MOD-FE-007 | docs/03_modules/_domain_frontend/value_stream_view/blueprint.md
# [MODULE] zephyr.frontend.value_stream_view
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（纯内存；模块段归属/依赖边快照注入，装配批自 depgraph_reader 适配）
# [CONSUMERS] 运行时装配批（价值流泳道面板段归属/段间边/全链高亮数据供给）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五段词表闭合(data|factor|signal|execution|portfolio); 段间边仅顺流(源段序号<目标段序号,同段/逆流/自环拒绝,故天然无环); 重复边幂等去重; 高亮=选中节点全链上下游传递闭包; 输出确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/value_stream_view/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueStreamError(占位 ZA-FE-UNREGISTERED-VALUE-STREAM)——空归属表/空模块id/非法段/未知边端点/自环/同段或逆流边/未知查询模块时抛
# [TESTS] tests/frontend/test_value_stream_view.py
# [A_module] module_id=MOD-FE-007 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ValueStreamView — 价值流泳道视图器（MOD-FE-007）。

B10-02410（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-008，A1 M7-S06）：
价值流（数据→因子→信号→执行→组合**五段词表闭合**）端到端泳道视图
**数据底座**（只做后端数据不做页面接线）——模块→段归属映射 + 段间依赖
边（仅顺流）+ 依赖高亮（选中节点的全链上下游传递闭包）。

查重分工（蓝图 §0）：depgraph_reader=依赖图 PG 查询接口（本件不查库，
段归属/边快照经 DI 注入）；graph_view_renderer=通用 DAG 布局（无段词表/
顺流约束语义）；lineage_view_renderer=血缘 N 跳闭包（本件=全链闭包，
跳数无界）。纯内存确定性，无时钟/随机源依赖。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "HighlightPayload",
    "StreamEdge",
    "StreamStage",
    "ValueStreamError",
    "ValueStreamView",
]


class ValueStreamError(Exception):
    """价值流视图输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-VALUE-STREAM。
    """


class StreamStage(str, Enum):
    """价值流段词表（闭合，序即主流向）。"""

    DATA = "data"
    FACTOR = "factor"
    SIGNAL = "signal"
    EXECUTION = "execution"
    PORTFOLIO = "portfolio"


#: 段序号（依赖方向只能序号增大顺流）
_STAGE_RANK: Final[dict[StreamStage, int]] = {
    StreamStage.DATA: 0,
    StreamStage.FACTOR: 1,
    StreamStage.SIGNAL: 2,
    StreamStage.EXECUTION: 3,
    StreamStage.PORTFOLIO: 4,
}


@dataclass(frozen=True)
class StreamEdge:
    """段间依赖边（source 段序号须 < target 段序号，frozen）。"""

    source: str
    target: str


@dataclass(frozen=True)
class HighlightPayload:
    """依赖高亮 payload（全链上下游传递闭包，确定性排序，不含选中节点自身）。"""

    selected: str
    upstream: tuple[str, ...]
    downstream: tuple[str, ...]


class ValueStreamView:
    """价值流泳道数据件（段归属 + 段间边 + 全链闭包高亮）。"""

    def __init__(
        self,
        *,
        module_stages: Mapping[str, StreamStage],
        edges: Iterable[StreamEdge] = (),
    ) -> None:
        if not module_stages:
            raise ValueStreamError("module_stages 为空（无模块段归属声明）")
        self._stages: dict[str, StreamStage] = {}
        for module_id, stage in module_stages.items():
            if not module_id:
                raise ValueStreamError("module_id 为空")
            if not isinstance(stage, StreamStage):
                raise ValueStreamError(f"非法价值流段: {stage!r}")
            self._stages[module_id] = stage

        edge_set: set[tuple[str, str]] = set()
        for edge in edges:
            if not isinstance(edge, StreamEdge):
                raise ValueStreamError(f"边类型错误: {edge!r}")
            if edge.source == edge.target:
                raise ValueStreamError(f"自环非法: {edge.source!r}")
            for endpoint in (edge.source, edge.target):
                if endpoint not in self._stages:
                    raise ValueStreamError(f"边端点未知模块: {endpoint!r}")
            src_rank = _STAGE_RANK[self._stages[edge.source]]
            tgt_rank = _STAGE_RANK[self._stages[edge.target]]
            if src_rank >= tgt_rank:
                raise ValueStreamError(
                    f"段间边仅顺流: {edge.source}({self._stages[edge.source].value}) -> "
                    f"{edge.target}({self._stages[edge.target].value}) 同段/逆流拒绝"
                )
            edge_set.add((edge.source, edge.target))  # set 幂等去重
        self._edges: tuple[tuple[str, str], ...] = tuple(sorted(edge_set))

        self._succ: dict[str, list[str]] = {mid: [] for mid in self._stages}
        self._pred: dict[str, list[str]] = {mid: [] for mid in self._stages}
        for source, target in self._edges:
            self._succ[source].append(target)
            self._pred[target].append(source)

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _closure(self, start: str, adjacency: Mapping[str, list[str]]) -> tuple[str, ...]:
        """传递闭包 BFS（不含 start 自身，排序确定性）。"""
        visited: set[str] = set()
        stack = list(adjacency[start])
        while stack:
            nid = stack.pop()
            if nid in visited:
                continue
            visited.add(nid)
            stack.extend(adjacency[nid])
        return tuple(sorted(visited))

    # ── 段归属查询 ────────────────────────────────────────────────────────

    def stage_of(self, module_id: str) -> StreamStage:
        """模块段归属（未知 → Fail-Closed）。"""
        stage = self._stages.get(module_id)
        if stage is None:
            raise ValueStreamError(f"未知模块: {module_id!r}（未在段归属声明中）")
        return stage

    def modules_in_stage(self, stage: StreamStage) -> tuple[str, ...]:
        """段内模块清单（确定性排序；非法段词表 → Fail-Closed）。"""
        if not isinstance(stage, StreamStage):
            raise ValueStreamError(f"非法价值流段: {stage!r}")
        return tuple(sorted(mid for mid, st in self._stages.items() if st is stage))

    # ── 段间边 ───────────────────────────────────────────────────────────

    def stream_edges(self) -> tuple[StreamEdge, ...]:
        """段间依赖边（按 (source, target) 排序确定性）。"""
        return tuple(StreamEdge(source=s, target=t) for s, t in self._edges)

    def stage_pairs(self) -> tuple[tuple[StreamStage, StreamStage], ...]:
        """段级依赖对（去重排序，泳道间连线数据）。"""
        pairs = {(self._stages[s], self._stages[t]) for s, t in self._edges}
        return tuple(sorted(pairs, key=lambda p: (_STAGE_RANK[p[0]], _STAGE_RANK[p[1]])))

    # ── 高亮 ─────────────────────────────────────────────────────────────

    def highlight(self, module_id: str) -> HighlightPayload:
        """依赖高亮：选中节点的全链上下游传递闭包（跳数无界）。"""
        self.stage_of(module_id)  # 未知模块 Fail-Closed
        upstream = self._closure(module_id, self._pred)
        downstream = self._closure(module_id, self._succ)
        _log.debug("价值流高亮: %s upstream=%d downstream=%d", module_id, len(upstream), len(downstream))
        return HighlightPayload(selected=module_id, upstream=upstream, downstream=downstream)
