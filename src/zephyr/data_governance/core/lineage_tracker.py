# [BLUEPRINT] MOD-DATA_GOV-002 | docs/03_modules/_domain_data_governance/blueprint.md
# [MODULE] zephyr.data_governance.core.lineage_tracker
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 边唯一(source,target); 有向无环检测; 幂等添加
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 环检测->ValueError; 节点不存在->返回空列表
# [TESTS] tests/data_governance/test_lineage_tracker.py
# [A_module] module_id=MOD-DATA_GOV-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-DATA-GOV Lineage Tracker——数据血缘追踪。

记录数据流转路径：source → transformation → target。
支持上下游查询和环检测（防止循环依赖）。

用法：
    tracker = LineageTracker()
    tracker.add_edge("market.kline_daily", "factor.momentum_20d", "compute")
    tracker.add_edge("factor.momentum_20d", "signal.alpha_signal", "generate")
    upstream = tracker.get_upstream("signal.alpha_signal")
    # → ["factor.momentum_20d", "market.kline_daily"]
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LineageEdge:
    """血缘边。

    Attributes:
        source: 源节点 (表名/因子ID/信号ID)
        target: 目标节点
        transformation: 变换描述 (如 "compute", "aggregate", "join")
    """

    source: str
    target: str
    transformation: str = ""


class LineageTracker:
    """数据血缘追踪器——内存级有向图管理。

    维护 source → target 的有向边，支持上下游查询和环检测。
    """

    def __init__(self) -> None:
        self._edges: dict[tuple[str, str], LineageEdge] = {}
        self._downstream: dict[str, set[str]] = defaultdict(set)
        self._upstream: dict[str, set[str]] = defaultdict(set)

    def add_edge(
        self, source: str, target: str, transformation: str = ""
    ) -> LineageEdge:
        """添加血缘边。如果 source→target 已存在则更新 transformation。

        Raises:
            ValueError: 添加后会形成环
        """
        if source == target:
            raise ValueError(f"自环不被允许: {source} → {target}")
        if self._would_create_cycle(source, target):
            raise ValueError(
                f"添加 {source} → {target} 会形成环（{target} 已是 {source} 的上游）"
            )
        edge = LineageEdge(source, target, transformation)
        self._edges[(source, target)] = edge
        self._downstream[source].add(target)
        self._upstream[target].add(source)
        return edge

    def get_upstream(self, node: str) -> list[str]:
        """获取节点的所有上游源（递归，按拓扑序）。"""
        visited: set[str] = set()
        result: list[str] = []
        self._collect_upstream(node, visited, result)
        return result

    def get_downstream(self, node: str) -> list[str]:
        """获取节点的所有下游消费者（递归，按拓扑序）。"""
        visited: set[str] = set()
        result: list[str] = []
        self._collect_downstream(node, visited, result)
        return result

    def get_direct_upstream(self, node: str) -> list[str]:
        """获取直接上游节点。"""
        return list(self._upstream.get(node, set()))

    def get_direct_downstream(self, node: str) -> list[str]:
        """获取直接下游节点。"""
        return list(self._downstream.get(node, set()))

    def get_edges(self) -> list[LineageEdge]:
        """返回所有血缘边。"""
        return list(self._edges.values())

    def get_nodes(self) -> list[str]:
        """返回所有节点。"""
        nodes: set[str] = set()
        for s, t in self._edges:
            nodes.add(s)
            nodes.add(t)
        return sorted(nodes)

    def _would_create_cycle(self, source: str, target: str) -> bool:
        """检查添加 source→target 后是否形成环。"""
        if source in self._upstream and target in self._upstream[source]:
            return True
        visited: set[str] = set()
        queue: deque[str] = deque([source])
        while queue:
            node = queue.popleft()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            queue.extend(self._upstream.get(node, set()))
        return False

    def _collect_upstream(
        self, node: str, visited: set[str], result: list[str]
    ) -> None:
        """递归收集上游节点（BFS 拓扑序）。"""
        queue: deque[str] = deque(self._upstream.get(node, set()))
        while queue:
            parent = queue.popleft()
            if parent in visited:
                continue
            visited.add(parent)
            result.append(parent)
            queue.extend(self._upstream.get(parent, set()))

    def _collect_downstream(
        self, node: str, visited: set[str], result: list[str]
    ) -> None:
        """递归收集下游节点（BFS 拓扑序）。"""
        queue: deque[str] = deque(self._downstream.get(node, set()))
        while queue:
            child = queue.popleft()
            if child in visited:
                continue
            visited.add(child)
            result.append(child)
            queue.extend(self._downstream.get(child, set()))
