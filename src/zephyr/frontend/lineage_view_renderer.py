# [BLUEPRINT] MOD-FE-008 | docs/03_modules/_domain_frontend/lineage_view_renderer/blueprint.md
# [MODULE] zephyr.frontend.lineage_view_renderer
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（纯内存；血缘实体/边快照注入，装配批自 lineage_tracker 适配）
# [CONSUMERS] 运行时装配批（血缘面板N跳高亮/变更影响着色/布局分层数据供给）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 实体id唯一非空; 边端点须在实体集且无自环(重复边幂等去重); 血缘DAG闭合(环拒绝); N跳闭包=双向BFS(跳数有界); 影响着色changed优先于impacted; 层分配=最长路径; 输出确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/lineage_view_renderer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LineageViewError(占位 ZA-FE-UNREGISTERED-LINEAGE-VIEW)——空实体集/空id/重复实体/未知边端点/自环/环/未知查询实体/非法hops/空变更集/未知变更实体时抛
# [TESTS] tests/frontend/test_lineage_view_renderer.py
# [A_module] module_id=MOD-FE-008 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""LineageViewRenderer — 血缘DAG渲染数据器（MOD-FE-008）。

B10-02413（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-009，A1 M8-S08）：
血缘DAG渲染**数据底座**（只做后端数据不做页面接线）——上下游高亮闭包
（选中实体 N 跳邻居）+ 变更影响范围着色（变更实体→下游影响集合着色映
射，changed 优先于 impacted）+ 布局分层数据（最长路径层分配）。

查重分工（蓝图 §0）：lineage_tracker=血缘记录/查询引擎（本件不重建追
踪器，实体/边快照经 DI 注入）；graph_view_renderer=通用依赖图布局（无
血缘 N 跳/影响着色语义）；value_stream_view=五段泳道（全链无界闭包，
本件 N 跳有界）。纯内存确定性，无时钟/随机源依赖。
"""

from __future__ import annotations

import heapq
import logging
from dataclasses import dataclass
from typing import Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "COLOR_CHANGED",
    "COLOR_IMPACTED",
    "COLOR_NORMAL",
    "LayerData",
    "LineageEdge",
    "LineageViewError",
    "LineageViewRenderer",
    "NeighborhoodPayload",
]


class LineageViewError(Exception):
    """血缘视图输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-LINEAGE-VIEW。
    """


#: 影响着色词表（前端色板键）
COLOR_CHANGED: Final[str] = "red"
COLOR_IMPACTED: Final[str] = "amber"
COLOR_NORMAL: Final[str] = "gray"


@dataclass(frozen=True)
class LineageEdge:
    """血缘边（source → target，transformation 描述与 lineage_tracker 对齐，frozen）。"""

    source: str
    target: str
    transformation: str = ""


@dataclass(frozen=True)
class LayerData:
    """布局分层数据（层号 + 层内实体清单，确定性排序）。"""

    layer: int
    entities: tuple[str, ...]


@dataclass(frozen=True)
class NeighborhoodPayload:
    """N 跳邻居闭包 payload（上下游分侧，确定性排序，不含选中实体自身）。"""

    selected: str
    hops: int
    upstream: tuple[str, ...]
    downstream: tuple[str, ...]


class LineageViewRenderer:
    """血缘DAG渲染数据件（N跳闭包高亮 + 变更影响着色 + 布局分层）。"""

    def __init__(
        self,
        *,
        entities: Iterable[str],
        edges: Iterable[LineageEdge],
    ) -> None:
        entity_list = list(entities)
        if not entity_list:
            raise LineageViewError("血缘实体集为空")
        self._entities: set[str] = set()
        for entity_id in entity_list:
            if not entity_id:
                raise LineageViewError("entity_id 为空")
            if entity_id in self._entities:
                raise LineageViewError(f"entity_id 重复: {entity_id!r}")
            self._entities.add(entity_id)

        edge_set: set[tuple[str, str]] = set()
        for edge in edges:
            if not isinstance(edge, LineageEdge):
                raise LineageViewError(f"边类型错误: {edge!r}")
            if edge.source == edge.target:
                raise LineageViewError(f"自环非法: {edge.source!r}")
            for endpoint in (edge.source, edge.target):
                if endpoint not in self._entities:
                    raise LineageViewError(f"边端点未知实体: {endpoint!r}")
            edge_set.add((edge.source, edge.target))  # set 幂等去重
        self._edges: tuple[tuple[str, str], ...] = tuple(sorted(edge_set))

        self._succ: dict[str, list[str]] = {eid: [] for eid in self._entities}
        self._pred: dict[str, list[str]] = {eid: [] for eid in self._entities}
        for source, target in self._edges:
            self._succ[source].append(target)
            self._pred[target].append(source)
        self._layers = self._assign_layers()  # 含环检测（Fail-Closed）

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _assign_layers(self) -> dict[str, int]:
        """层分配=最长路径（Kahn 拓扑 + heapq 确定性出队；环 → Fail-Closed）。"""
        indeg = {eid: len(self._pred[eid]) for eid in self._entities}
        layer = {eid: 0 for eid in self._entities}
        heap = [eid for eid, deg in indeg.items() if deg == 0]
        heapq.heapify(heap)
        processed = 0
        while heap:
            eid = heapq.heappop(heap)
            processed += 1
            for nxt in self._succ[eid]:
                if layer[nxt] < layer[eid] + 1:
                    layer[nxt] = layer[eid] + 1
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    heapq.heappush(heap, nxt)
        if processed != len(self._entities):
            raise LineageViewError("血缘图含环（DAG 闭合约束拒绝）")
        return layer

    def _require_entity(self, entity_id: str) -> None:
        if entity_id not in self._entities:
            raise LineageViewError(f"未知血缘实体: {entity_id!r}")

    def _n_hop(self, start: str, adjacency: dict[str, list[str]], hops: int) -> set[str]:
        """单侧 N 跳 BFS（不含 start 自身）。"""
        visited: set[str] = set()
        frontier = {start}
        for _ in range(hops):
            nxt: set[str] = set()
            for eid in frontier:
                nxt.update(adjacency[eid])
            nxt -= visited | {start}
            visited |= nxt
            frontier = nxt
            if not frontier:
                break
        return visited

    # ── N 跳高亮闭包 ──────────────────────────────────────────────────────

    def neighborhood(self, entity_id: str, hops: int = 1) -> NeighborhoodPayload:
        """上下游高亮闭包：选中实体 N 跳邻居（上下游分侧）。"""
        self._require_entity(entity_id)
        if not isinstance(hops, int) or isinstance(hops, bool) or hops < 1:
            raise LineageViewError(f"非法 hops: {hops!r}（须为正整数）")
        upstream = self._n_hop(entity_id, self._pred, hops)
        downstream = self._n_hop(entity_id, self._succ, hops)
        _log.debug("血缘闭包: %s hops=%d upstream=%d downstream=%d", entity_id, hops, len(upstream), len(downstream))
        return NeighborhoodPayload(
            selected=entity_id,
            hops=hops,
            upstream=tuple(sorted(upstream)),
            downstream=tuple(sorted(downstream)),
        )

    # ── 变更影响着色 ──────────────────────────────────────────────────────

    def impact_colors(self, changed_entities: Iterable[str]) -> dict[str, str]:
        """变更影响范围着色：changed=红 / 下游impacted=琥珀 / 其余=灰。

        changed 优先于 impacted（既变更又被上游变更波及的实体仍着 changed）。
        返回覆盖全部实体的映射（按 entity_id 排序确定性）。
        """
        changed = set(changed_entities)
        if not changed:
            raise LineageViewError("变更实体集为空（无影响着色对象）")
        for entity_id in changed:
            self._require_entity(entity_id)
        impacted: set[str] = set()
        for entity_id in changed:
            impacted |= self._n_hop(entity_id, self._succ, hops=len(self._entities))
        impacted -= changed
        return {
            eid: (COLOR_CHANGED if eid in changed else COLOR_IMPACTED if eid in impacted else COLOR_NORMAL)
            for eid in sorted(self._entities)
        }

    # ── 布局分层 ──────────────────────────────────────────────────────────

    def layout_layers(self) -> tuple[LayerData, ...]:
        """布局分层数据（层号升序，层内实体按 entity_id 排序）。"""
        layer_count = max(self._layers.values()) + 1
        return tuple(
            LayerData(
                layer=layer_idx,
                entities=tuple(sorted(eid for eid, li in self._layers.items() if li == layer_idx)),
            )
            for layer_idx in range(layer_count)
        )
