# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_cross_agent_semantic_flow
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_a2a_cross_agent_semantic_flow | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 跨 Agent 语义流追踪 — 知识+意图在 Agent 间传递

追踪一个任务从 Agent A 传递到 Agent B 再到 Agent C 的过程中:
  - 初始意图是什么
  - 中间 Agent 如何解释/转化意图
  - 最终输出是否与初始意图一致
  - 中间有语义漂移吗?

对标: Cross-Agent Intent Preservation (跨Agent意图保真)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SemanticFlowNode:
    agent_id: str
    task_id: str
    intent_summary: str
    output_summary: str


@dataclass
class SemanticFlow:
    flow_id: str
    nodes: list[SemanticFlowNode] = field(default_factory=list)

    @property
    def depth(self) -> int:
        return len(self.nodes)

    @property
    def agents_involved(self) -> list[str]:
        return list(dict.fromkeys(n.agent_id for n in self.nodes))


class CrossAgentSemanticFlow:
    def __init__(self):
        self._flows: dict[str, SemanticFlow] = {}

    def open_flow(self, flow_id: str):
        self._flows[flow_id] = SemanticFlow(flow_id=flow_id)

    def add_node(
        self,
        flow_id: str,
        agent_id: str,
        task_id: str,
        intent_summary: str,
        output_summary: str,
    ):
        if flow_id in self._flows:
            self._flows[flow_id].nodes.append(
                SemanticFlowNode(
                    agent_id=agent_id,
                    task_id=task_id,
                    intent_summary=intent_summary,
                    output_summary=output_summary,
                )
            )

    def get_flow(self, flow_id: str) -> SemanticFlow | None:
        return self._flows.get(flow_id)

    def trace(self, flow_id: str) -> list[dict]:
        flow = self._flows.get(flow_id)
        if flow is None:
            return []
        return [
            {
                "step": i + 1,
                "agent": node.agent_id,
                "task": node.task_id,
                "intent": node.intent_summary[:80],
                "output": node.output_summary[:80],
            }
            for i, node in enumerate(flow.nodes)
        ]
