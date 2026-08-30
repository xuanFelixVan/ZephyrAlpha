# [BLUEPRINT] MOD-INF-087 | docs/03_modules/_domain_infrastructure_operations/runtime_topology_visualizer/blueprint.md
# [MODULE] zephyr.infra_ops.runtime_topology_visualizer
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 无（纯内存数据模型；clock 注入，随健康检查注入刷新）
# [CONSUMERS] 运行时装配批（进程/Redis/GPU/消息/数据馈节点注册与心跳上报 / 仪表盘 JSON 消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 节点/边词表闭合; 心跳新鲜度确定性着色(≤yellow→green, ≤red→yellow, 否则 red; 无心跳→red); snapshot 节点按 node_id 排序、边按 (from,to,label) 排序; 只产后端 JSON 数据不做前端; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/runtime_topology_visualizer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RuntimeTopologyError(占位 ZA-INF-UNREGISTERED-RUNTIME-TOPOLOGY)——空id/重复节点/未知节点/未知端点边/阈值非法时抛
# [TESTS] tests/infra_ops/test_runtime_topology_visualizer.py
# [A_module] module_id=MOD-INF-087 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
RuntimeTopologyVisualizer — 运行时依赖拓扑数据模型（MOD-INF-087）。

B14-04635（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-005，A9运维
架构）：P1~P5 进程 / Redis / GPU / miniQMT(BROKER) / iFind(DATAFEED) 节
点注册 + 心跳状态着色（green/yellow/red 由心跳新鲜度与注入时钟判定）+
数据流边标注（Pub/Sub/KV/List），snapshot() 输出 JSON 字典供仪表盘消费
（本件只做后端数据，不做前端页面接线），随健康检查注入刷新。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: runtime_topology_visualizer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: yellow_after_s 参数
#   fields: 参数 yellow_after_s（无注解）
#   code: runtime_topology_visualizer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: red_after_s 参数
#   fields: 参数 red_after_s（无注解）
#   code: runtime_topology_visualizer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RuntimeTopologyVisualizer
#   name_en: RuntimeTopologyVisualizer
#   intro: 运行时依赖拓扑件（节点/边注册 + 心跳着色 + JSON 快照）。
#   desc: 运行时依赖拓扑件（节点/边注册 + 心跳着色 + JSON 快照）。；公共方法（定义序）: register_node, register_edge, heartbeat, refresh_status, snapsh…
#   inputs: clock yellow_after_s red_after_s
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: RuntimeTopologyVisualizer
#   downstream: 运行时装配批（进程/Redis/GPU/消息/数据馈节点注册与心跳上报 / 仪表盘 JSON 消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "EdgeLabel",
    "NodeKind",
    "NodeStatus",
    "RuntimeTopologyError",
    "RuntimeTopologyVisualizer",
    "TopoEdge",
    "TopoNode",
]


class RuntimeTopologyError(Exception):
    """运行时拓扑输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-RUNTIME-TOPOLOGY。
    """


class NodeKind(str, Enum):
    """节点类别（词表闭合）。"""

    PROCESS = "process"
    REDIS = "redis"
    GPU = "gpu"
    BROKER = "broker"
    DATAFEED = "datafeed"


class NodeStatus(str, Enum):
    """节点健康着色。"""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class EdgeLabel(str, Enum):
    """数据流边标注（词表闭合）。"""

    PUB = "Pub"
    SUB = "Sub"
    KV = "KV"
    LIST = "List"


@dataclass
class TopoNode:
    """拓扑节点（status 随 refresh_status 刷新，可变）。"""

    node_id: str
    kind: NodeKind
    heartbeat_at: datetime.datetime | None = None
    status: NodeStatus = field(default=NodeStatus.RED)


@dataclass(frozen=True)
class TopoEdge:
    """数据流边（frozen）。"""

    from_node: str
    to_node: str
    label: EdgeLabel


class RuntimeTopologyVisualizer:
    """运行时依赖拓扑件（节点/边注册 + 心跳着色 + JSON 快照）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        yellow_after_s: float = 30.0,
        red_after_s: float = 90.0,
    ) -> None:
        if yellow_after_s < 0 or red_after_s < 0:
            raise RuntimeTopologyError("着色阈值不可为负")
        if yellow_after_s >= red_after_s:
            raise RuntimeTopologyError(f"着色阈值非法: yellow({yellow_after_s}) 须严格小于 red({red_after_s})")
        self._clock = clock or datetime.datetime.now
        self._yellow_s = yellow_after_s
        self._red_s = red_after_s
        self._nodes: dict[str, TopoNode] = {}
        self._edges: set[TopoEdge] = set()

    # ── 注册 ─────────────────────────────────────────────────────────────

    def register_node(
        self,
        node_id: str,
        kind: NodeKind,
        heartbeat_at: datetime.datetime | None = None,
    ) -> TopoNode:
        """登记节点：空 id/重复/非法类别 → Fail-Closed。"""
        if not node_id:
            raise RuntimeTopologyError("node_id 为空")
        if not isinstance(kind, NodeKind):
            raise RuntimeTopologyError(f"非法节点类别: {kind!r}")
        if node_id in self._nodes:
            raise RuntimeTopologyError(f"节点重复注册: {node_id!r}")
        node = TopoNode(node_id=node_id, kind=kind, heartbeat_at=heartbeat_at)
        self._nodes[node_id] = node
        return node

    def register_edge(self, from_node: str, to_node: str, label: EdgeLabel) -> None:
        """登记数据流边：端点须已注册；重复边幂等。"""
        if not isinstance(label, EdgeLabel):
            raise RuntimeTopologyError(f"非法边标注: {label!r}")
        for endpoint in (from_node, to_node):
            if endpoint not in self._nodes:
                raise RuntimeTopologyError(f"边端点未注册: {endpoint!r}")
        self._edges.add(TopoEdge(from_node=from_node, to_node=to_node, label=label))

    # ── 心跳与着色 ────────────────────────────────────────────────────────

    def heartbeat(self, node_id: str, at: datetime.datetime | None = None) -> None:
        """上报心跳（at 缺省取注入时钟）。"""
        node = self._nodes.get(node_id)
        if node is None:
            raise RuntimeTopologyError(f"未知节点: {node_id!r}")
        node.heartbeat_at = at if at is not None else self._clock()

    def _color(self, node: TopoNode, now: datetime.datetime) -> NodeStatus:
        if node.heartbeat_at is None:
            return NodeStatus.RED
        age = (now - node.heartbeat_at).total_seconds()
        if age <= self._yellow_s:
            return NodeStatus.GREEN
        if age <= self._red_s:
            return NodeStatus.YELLOW
        return NodeStatus.RED

    def refresh_status(self) -> None:
        """按注入时钟重算全部节点着色（随健康检查注入刷新）。"""
        now = self._clock()
        for node in self._nodes.values():
            node.status = self._color(node, now)

    # ── 快照 ─────────────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        """JSON 快照（先刷新着色；节点/边确定性排序，供仪表盘消费）。"""
        self.refresh_status()
        now = self._clock()
        nodes = [
            {
                "node_id": n.node_id,
                "kind": n.kind.value,
                "heartbeat_at": n.heartbeat_at.isoformat() if n.heartbeat_at else None,
                "status": n.status.value,
            }
            for n in sorted(self._nodes.values(), key=lambda n: n.node_id)
        ]
        edges = [
            {"from": e.from_node, "to": e.to_node, "label": e.label.value}
            for e in sorted(self._edges, key=lambda e: (e.from_node, e.to_node, e.label.value))
        ]
        _log.debug("拓扑快照: nodes=%d edges=%d", len(nodes), len(edges))
        return {"generated_at": now.isoformat(), "nodes": nodes, "edges": edges}
