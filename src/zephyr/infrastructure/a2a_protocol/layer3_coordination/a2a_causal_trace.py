# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A 因果追踪 — 跨 Agent 操作因果链图谱

构建 Agent 间操作的因果关系图:
  Agent A 写文件 X -> Agent B 读到 X 的旧版本 -> Agent B 输出错误 -> 错误传播
  通过序列表 + 时间戳 + 文件依赖关系追溯到根因

输出: CausalPath — 端到端因果路径

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_causal_trace.py
# 层: 算法
# - id: A1
#   name_zh: ① CausalGraph
#   name_en: CausalGraph
#   intro: class CausalGraph 源码 L85-L97
#   desc: 公共方法（定义序）: add_node, add_edge, trace_path；源码 L85-L97
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② A2ACausalTrace
#   name_en: A2ACausalTrace
#   intro: class A2ACausalTrace 源码 L100-L130
#   desc: 公共方法（定义序）: open_trace, add_node, add_dependency, get_graph, trace_path；源码 L100-L130
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: CausalGraph, A2ACausalTrace
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CausalNode:
    node_id: str
    agent_id: str
    action: str
    resource: str
    timestamp: float


@dataclass
class CausalEdge:
    from_node: str
    to_node: str
    dependency_type: str = "read_after_write"


@dataclass
class CausalGraph:
    nodes: dict[str, CausalNode] = field(default_factory=dict)
    edges: list[CausalEdge] = field(default_factory=list)

    def add_node(self, node: CausalNode):
        self.nodes[node.node_id] = node

    def add_edge(self, from_id: str, to_id: str, dep_type: str = "read_after_write"):
        self.edges.append(CausalEdge(from_node=from_id, to_node=to_id, dependency_type=dep_type))

    @property
    def trace_path(self) -> list[str]:
        return [f"{e.from_node} -> {e.to_node} ({e.dependency_type})" for e in self.edges]


class A2ACausalTrace:
    def __init__(self):
        self._graphs: dict[str, CausalGraph] = {}

    def open_trace(self, trace_id: str):
        self._graphs[trace_id] = CausalGraph()

    def add_node(self, trace_id: str, node_id: str, agent_id: str, action: str, resource: str, timestamp: float):
        if trace_id in self._graphs:
            self._graphs[trace_id].add_node(
                CausalNode(
                    node_id=node_id,
                    agent_id=agent_id,
                    action=action,
                    resource=resource,
                    timestamp=timestamp,
                )
            )

    def add_dependency(self, trace_id: str, from_node: str, to_node: str, dep_type: str = "read_after_write"):
        if trace_id in self._graphs:
            self._graphs[trace_id].add_edge(from_node, to_node, dep_type)

    def get_graph(self, trace_id: str) -> CausalGraph | None:
        return self._graphs.get(trace_id)

    def trace_path(self, trace_id: str) -> list[str]:
        graph = self._graphs.get(trace_id)
        if graph is None:
            return []
        return graph.trace_path
