# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.multi_agent
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_multi_agent | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
multi_agent.py —— Multi-Agent 编排基座（Phase 14 | 盲点 B33）

Core data contracts (TaskStatus, MergeStrategy, DispatchedTask, ResultMerge)
are imported from zephyr.shared.protocols.a2a.a2a_coordination.

Local types (AgentRole, AgentCard, TaskDispatch) are multi-agent-specific
and differ from the shared Protocol-level types of the same name.
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
class AgentRole(str, Enum):
    """Multi-agent orchestration role (differs from shared AgentRole IntEnum for arbitration)."""

    COORDINATOR = "coordinator"
    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"


# class-name-alias: MOD-INF_multi_agent 多Agent编排 AgentCard（dataclass, role-based），与 shared.protocols.a2a.a2a_registry 的 Pydantic AgentCard（A2A discovery 协议契约）同名不同义，本地编排变体
@dataclass
class AgentCard:
    """Multi-agent orchestration AgentCard (dataclass; differs from shared Pydantic AgentCard)."""

    agent_id: str
    role: AgentRole
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
            role=AgentRole(data["role"]),
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

    def assign(self, task_id: str, description: str, required_role: AgentRole | None = None) -> DispatchedTask | None:
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

    def list_by_role(self, role: AgentRole) -> list[AgentCard]:
        return [card for card in self.agents.values() if card.role == role]


__all__ = [
    "AgentCard",
    "AgentRole",
    "DispatchedTask",
    "MergeStrategy",
    "ResultMerge",
    "TaskDispatch",
    "TaskStatus",
]
