# [BLUEPRINT] MOD-FE-005 | docs/03_modules/_domain_frontend/graph_view_renderer/blueprint.md
# [MODULE] zephyr.frontend.graph_view_renderer
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（渲染数据底座纯内存；依赖图节点/边快照注入，装配批自 depgraph_reader 适配）
# [CONSUMERS] 运行时装配批（依赖图面板分层布局/状态着色/钻取邻居子图数据供给）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 节点id唯一非空; 边端点须在节点集且无自环(重复边幂等去重); DAG闭合(环拒绝); 层分配=最长路径; 层内序=barycenter降交叉+node_id兜底; 钻取子图=双向N跳诱导子图; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/graph_view_renderer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GraphViewError(占位 ZA-FE-UNREGISTERED-GRAPH-VIEW)——空节点集/空id/重复节点/非法状态/未知边端点/自环/环/非法间距/未知钻取节点/非法hops时抛
# [TESTS] tests/frontend/test_graph_view_renderer.py
# [A_module] module_id=MOD-FE-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""GraphViewRenderer — 依赖图DAG渲染数据器（MOD-FE-005）。

B10-02408（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-006，A1 M5-S07）：
依赖图DAG渲染**数据底座**（只做后端数据不做页面接线）——分层布局坐标
计算（dagre 思想：层分配=最长路径 + 层内排序=barycenter 降交叉）+ 节点状
态着色映射 + 点击钻取详情 payload（节点 N 跳邻居诱导子图）。

查重分工（蓝图 §0）：depgraph_reader=依赖图 PG 查询接口（本件不查库，
节点/边快照经 DI 注入）；lineage_view_renderer=血缘专用渲染（N跳闭包/变更
影响着色语义特化）；value_stream_view=五段泳道（段词表闭合+顺流边约束）；
本件=通用依赖图布局/着色/钻取数据，与三者零交集。纯内存确定性，无时钟/
随机源依赖。
"""

from __future__ import annotations

import heapq
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "DepEdge",
    "DepNode",
    "DrilldownPayload",
    "GraphLayout",
    "GraphViewError",
    "GraphViewRenderer",
    "LayoutEdge",
    "LayoutNode",
    "NodeStatus",
]


class GraphViewError(Exception):
    """依赖图视图输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-GRAPH-VIEW。
    """


class NodeStatus(str, Enum):
    """节点状态词表（闭合）。"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


#: 状态→着色映射（前端色板键，确定性）
_STATUS_COLORS: Final[dict[NodeStatus, str]] = {
    NodeStatus.HEALTHY: "green",
    NodeStatus.DEGRADED: "amber",
    NodeStatus.FAILED: "red",
    NodeStatus.UNKNOWN: "gray",
}

#: barycenter 降交叉下扫轮数（固定常数保证确定性）
_BARYCENTER_PASSES: Final[int] = 2


@dataclass(frozen=True)
class DepNode:
    """依赖图节点（DI 注入快照形态，frozen）。"""

    node_id: str
    label: str
    status: NodeStatus


@dataclass(frozen=True)
class DepEdge:
    """依赖图有向边（source → target，frozen）。"""

    source: str
    target: str


@dataclass(frozen=True)
class LayoutNode:
    """布局后节点（层/层内序/坐标/着色）。"""

    node_id: str
    label: str
    status: NodeStatus
    color: str
    layer: int
    order: int
    x: float
    y: float


@dataclass(frozen=True)
class LayoutEdge:
    """布局后边（与输入边一一对应，排序确定性）。"""

    source: str
    target: str


@dataclass(frozen=True)
class GraphLayout:
    """整图布局 payload（节点按 (layer, order) 排序，frozen）。"""

    nodes: tuple[LayoutNode, ...]
    edges: tuple[LayoutEdge, ...]
    layer_count: int


@dataclass(frozen=True)
class DrilldownPayload:
    """钻取邻居子图 payload（双向 N 跳诱导子图，确定性排序）。"""

    center: str
    hops: int
    nodes: tuple[DepNode, ...]
    edges: tuple[LayoutEdge, ...]


class GraphViewRenderer:
    """依赖图渲染数据件（分层布局 + 状态着色 + 钻取子图）。"""

    def __init__(
        self,
        *,
        nodes: Iterable[DepNode],
        edges: Iterable[DepEdge],
        x_spacing: float = 200.0,
        y_spacing: float = 120.0,
    ) -> None:
        node_list = list(nodes)
        if not node_list:
            raise GraphViewError("节点集为空（无图可渲染）")
        self._nodes: dict[str, DepNode] = {}
        for node in node_list:
            if not isinstance(node, DepNode):
                raise GraphViewError(f"节点类型错误: {node!r}")
            if not node.node_id:
                raise GraphViewError("node_id 为空")
            if not isinstance(node.status, NodeStatus):
                raise GraphViewError(f"非法节点状态: {node.status!r}")
            if node.node_id in self._nodes:
                raise GraphViewError(f"node_id 重复: {node.node_id!r}")
            self._nodes[node.node_id] = node

        edge_set: set[tuple[str, str]] = set()
        for edge in edges:
            if not isinstance(edge, DepEdge):
                raise GraphViewError(f"边类型错误: {edge!r}")
            if edge.source == edge.target:
                raise GraphViewError(f"自环非法: {edge.source!r}")
            for endpoint in (edge.source, edge.target):
                if endpoint not in self._nodes:
                    raise GraphViewError(f"边端点未知节点: {endpoint!r}")
            edge_set.add((edge.source, edge.target))  # set 幂等去重
        self._edges: tuple[tuple[str, str], ...] = tuple(sorted(edge_set))

        if x_spacing <= 0 or y_spacing <= 0:
            raise GraphViewError("x_spacing/y_spacing 须为正数")
        self._x_spacing = float(x_spacing)
        self._y_spacing = float(y_spacing)

        self._succ: dict[str, list[str]] = {nid: [] for nid in self._nodes}
        self._pred: dict[str, list[str]] = {nid: [] for nid in self._nodes}
        for source, target in self._edges:
            self._succ[source].append(target)
            self._pred[target].append(source)
        self._layers = self._assign_layers()  # 含环检测（Fail-Closed）

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _assign_layers(self) -> dict[str, int]:
        """层分配=最长路径（Kahn 拓扑 + heapq 确定性出队；环 → Fail-Closed）。"""
        indeg = {nid: len(self._pred[nid]) for nid in self._nodes}
        layer = {nid: 0 for nid in self._nodes}
        heap = [nid for nid, deg in indeg.items() if deg == 0]
        heapq.heapify(heap)
        processed = 0
        while heap:
            nid = heapq.heappop(heap)
            processed += 1
            for nxt in self._succ[nid]:
                if layer[nxt] < layer[nid] + 1:
                    layer[nxt] = layer[nid] + 1
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    heapq.heappush(heap, nxt)
        if processed != len(self._nodes):
            raise GraphViewError("依赖图含环（DAG 闭合约束拒绝）")
        return layer

    def _order_layers(self) -> list[list[str]]:
        """层内排序：初序 node_id → barycenter 下扫降交叉（node_id 兜底确定性）。"""
        layer_count = max(self._layers.values()) + 1
        ordered = [
            sorted(nid for nid, li in self._layers.items() if li == layer_idx) for layer_idx in range(layer_count)
        ]
        pos = {nid: float(idx) for members in ordered for idx, nid in enumerate(members)}
        for _ in range(_BARYCENTER_PASSES):
            for layer_idx in range(1, layer_count):
                members = ordered[layer_idx]

                def _key(nid: str) -> tuple[float, str]:
                    preds = self._pred[nid]
                    if not preds:
                        return (pos[nid], nid)
                    barycenter = sum(pos[p] for p in preds) / len(preds)
                    return (barycenter, nid)

                members.sort(key=_key)
                for idx, nid in enumerate(members):
                    pos[nid] = float(idx)
        return ordered

    # ── 布局 / 着色 ───────────────────────────────────────────────────────

    def layout(self) -> GraphLayout:
        """整图分层布局坐标（节点按 (layer, order) 排序，边按 (source, target) 排序）。"""
        ordered = self._order_layers()
        layout_nodes: list[LayoutNode] = []
        for layer_idx, members in enumerate(ordered):
            for order, nid in enumerate(members):
                node = self._nodes[nid]
                layout_nodes.append(
                    LayoutNode(
                        node_id=nid,
                        label=node.label,
                        status=node.status,
                        color=_STATUS_COLORS[node.status],
                        layer=layer_idx,
                        order=order,
                        x=order * self._x_spacing,
                        y=layer_idx * self._y_spacing,
                    )
                )
        return GraphLayout(
            nodes=tuple(layout_nodes),
            edges=tuple(LayoutEdge(source=s, target=t) for s, t in self._edges),
            layer_count=len(ordered),
        )

    def color_map(self) -> dict[str, str]:
        """节点状态着色映射（node_id → 色板键，按 node_id 排序）。"""
        return {nid: _STATUS_COLORS[self._nodes[nid].status] for nid in sorted(self._nodes)}

    # ── 钻取 ─────────────────────────────────────────────────────────────

    def drilldown(self, node_id: str, hops: int = 1) -> DrilldownPayload:
        """点击钻取：双向 BFS N 跳邻居诱导子图（节点/边确定性排序）。"""
        if node_id not in self._nodes:
            raise GraphViewError(f"未知钻取节点: {node_id!r}")
        if not isinstance(hops, int) or isinstance(hops, bool) or hops < 1:
            raise GraphViewError(f"非法 hops: {hops!r}（须为正整数）")
        visited = {node_id}
        frontier = {node_id}
        for _ in range(hops):
            nxt: set[str] = set()
            for nid in frontier:
                nxt.update(self._succ[nid])
                nxt.update(self._pred[nid])
            nxt -= visited
            visited |= nxt
            frontier = nxt
            if not frontier:
                break
        sub_nodes = tuple(self._nodes[nid] for nid in sorted(visited))
        sub_edges = tuple(LayoutEdge(source=s, target=t) for s, t in self._edges if s in visited and t in visited)
        _log.debug("钻取子图: center=%s hops=%d nodes=%d edges=%d", node_id, hops, len(sub_nodes), len(sub_edges))
        return DrilldownPayload(center=node_id, hops=hops, nodes=sub_nodes, edges=sub_edges)
