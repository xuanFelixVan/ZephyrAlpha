# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.multi_agent
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_coordination
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a where identical; local AgentRole/AgentCard are multi-agent-specific (different from shared versions)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
multi_agent.py —— Multi-Agent 编排基座（Phase 14 | 盲点 B33）

Core data contracts (TaskStatus, MergeStrategy, DispatchedTask, ResultMerge)
are imported from zephyr.shared.protocols.a2a.a2a_coordination.

Local types (AgentRole, AgentCard, TaskDispatch) are multi-agent-specific
and differ from the shared Protocol-level types of the same name.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: multi_agent.py
# 层: 算法
# - id: A1
#   name_zh: ① AgentCard
#   name_en: AgentCard
#   intro: Multi-agent orchestration AgentCard (dataclass; differs fro…
#   desc: Multi-agent orchestration AgentCard (dataclass; differs from shared Pydantic AgentCard).；公共方法（定义序）: to_dict,…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② TaskDispatch
#   name_en: TaskDispatch
#   intro: 任务分派器——将 task 分派给合适的 Agent。
#   desc: 任务分派器——将 task 分派给合适的 Agent。；公共方法（定义序）: register_agent, unregister_agent, assign, assign_to_capable, get_agent…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: AgentCard, TaskDispatch
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
from enum import Enum, unique
from typing import Any

from zephyr.shared.protocols.a2a.a2a_coordination import (
    DispatchedTask,
    MergeStrategy,
    ResultMerge,
    TaskStatus,
)


@unique
class MultiAgentRole(str, Enum):
    """Multi-agent orchestration role (P1-3: renamed from AgentRole to avoid conflict with RbacRole/ArbitrationRole/RoutingRole)."""

    COORDINATOR = "coordinator"
    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"


# P1-3 兼容层：旧名 AgentRole 保留为 MultiAgentRole 别名
AgentRole = MultiAgentRole  # noqa: F811  # [DEPRECATED] [TTL] task_bound — P1-3 兼容层


# class-name-alias: MOD-INF_multi_agent 多Agent编排 AgentCard（dataclass, role-based），与 shared.protocols.a2a.a2a_registry 的 Pydantic AgentCard（A2A discovery 协议契约）同名不同义，本地编排变体
@dataclass
class AgentCard:
    """Multi-agent orchestration AgentCard (dataclass; differs from shared Pydantic AgentCard)."""

    agent_id: str
    role: MultiAgentRole
    capabilities: list[str] = field(default_factory=list)
    description: str = ""
    endpoint: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "description": self.description,
            "endpoint": self.endpoint,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentCard:
        return cls(
            agent_id=data["agent_id"],
            role=MultiAgentRole(data["role"]),
            # 5.147.9 修复: JSON 中 capabilities/metadata 为 null 时 d.get 返回 None 而非默认值
            capabilities=data.get("capabilities") or [],
            description=data.get("description", ""),
            endpoint=data.get("endpoint"),
            metadata=data.get("metadata") or {},
        )


@dataclass
class TaskDispatch:
    """任务分派器——将 task 分派给合适的 Agent。"""

    agents: dict[str, AgentCard] = field(default_factory=dict)

    def register_agent(self, card: AgentCard) -> None:
        self.agents[card.agent_id] = card

    def unregister_agent(self, agent_id: str) -> AgentCard | None:
        return self.agents.pop(agent_id, None)

    def assign(
        self, task_id: str, description: str, required_role: MultiAgentRole | None = None
    ) -> DispatchedTask | None:
        candidates = [
            (aid, card) for aid, card in self.agents.items() if required_role is None or card.role == required_role
        ]

        if not candidates:
            candidates = list(self.agents.items())

        if not candidates:
            return None

        agent_id, card = candidates[0]
        task = DispatchedTask(task_id=task_id, agent_id=agent_id, description=description)
        task.assign()
        return task

    def assign_to_capable(self, task_id: str, description: str, required_capability: str) -> DispatchedTask | None:
        candidates = [(aid, card) for aid, card in self.agents.items() if required_capability in card.capabilities]

        if not candidates:
            return None

        agent_id, card = candidates[0]
        task = DispatchedTask(task_id=task_id, agent_id=agent_id, description=description)
        task.assign()
        return task

    def get_agent(self, agent_id: str) -> AgentCard | None:
        return self.agents.get(agent_id)

    def list_by_role(self, role: MultiAgentRole) -> list[AgentCard]:
        return [card for card in self.agents.values() if card.role == role]


__all__ = [
    "AgentCard",
    "AgentRole",  # P1-3 兼容层（= MultiAgentRole）
    "MultiAgentRole",
    "DispatchedTask",
    "MergeStrategy",
    "ResultMerge",
    "TaskDispatch",
    "TaskStatus",
]
