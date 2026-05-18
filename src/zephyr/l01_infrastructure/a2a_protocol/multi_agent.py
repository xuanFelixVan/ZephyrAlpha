# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.multi_agent

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
multi_agent.py —— Multi-Agent 编排基座（Phase 14 | 盲点 B33）

痛点修复：Multi-Agent 团队无统一编排基座——每个 Agent 各自定义角色/能力，无法互操作。
需要 A2A v1.0 对齐的 Agent 间通信协议。

设计对标：
  - Google A2A v1.0: AgentCard——Agent 能力声明
  - CrewAI / AutoGen: role-based task dispatch + result merge
  - Anthropic Multi-Agent: sub-agent delegation patterns

核心抽象：
  - AgentCard Protocol → agent_id / role / capabilities / endpoint
  - TaskDispatch Protocol → assign() / status() / result()
  - ResultMerge Protocol → merge_strategy（vote/chain/consensus）

SSoT: MOD-INF-025 §12 盲点 B33
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from typing import Any


@unique
class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"


@unique
class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@unique
class MergeStrategy(str, Enum):
    VOTE = "vote"
    CHAIN = "chain"
    CONSENSUS = "consensus"


@dataclass
class AgentCard:
    """Agent 能力卡片——A2A v1.0 对齐。

    Usage::

        card = AgentCard(
            agent_id="builder-01",
            role=AgentRole.BUILDER,
            capabilities=["python", "pytest", "yaml"],
            description="Code generation and testing agent",
        )
    """

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
    def from_dict(cls, data: dict[str, Any]) -> "AgentCard":
        return cls(
            agent_id=data["agent_id"],
            role=AgentRole(data["role"]),
            capabilities=data.get("capabilities", []),
            description=data.get("description", ""),
            endpoint=data.get("endpoint"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DispatchedTask:
    """已分派的任务——含状态追踪和结果收集。"""

    task_id: str
    agent_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_at: str | None = None
    completed_at: str | None = None
    result: Any = None
    error: str | None = None

    def assign(self) -> None:
        self.status = TaskStatus.ASSIGNED
        self.assigned_at = datetime.now(UTC).isoformat()

    def start(self) -> None:
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, result: Any) -> None:
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now(UTC).isoformat()

    def fail(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(UTC).isoformat()


@dataclass
class TaskDispatch:
    """任务分派器——将 task 分派给合适的 Agent。

    Usage::

        dispatch = TaskDispatch()
        dispatch.register_agent(builder_card)
        assigned = dispatch.assign("build-module-x")
    """

    agents: dict[str, AgentCard] = field(default_factory=dict)

    def register_agent(self, card: AgentCard) -> None:
        self.agents[card.agent_id] = card

    def unregister_agent(self, agent_id: str) -> AgentCard | None:
        return self.agents.pop(agent_id, None)

    def assign(self, task_id: str, description: str, required_role: AgentRole | None = None) -> DispatchedTask | None:
        candidates = [
            (aid, card)
            for aid, card in self.agents.items()
            if required_role is None or card.role == required_role
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
        candidates = [
            (aid, card)
            for aid, card in self.agents.items()
            if required_capability in card.capabilities
        ]

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


@dataclass
class ResultMerge:
    """结果合并器——多 Agent 输出的合并策略。

    Usage::

        merge = ResultMerge(strategy=MergeStrategy.VOTE)
        result = merge.merge([agent_results])
    """

    strategy: MergeStrategy = MergeStrategy.CONSENSUS

    def merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {"merged": True, "results": []}

        if self.strategy == MergeStrategy.VOTE:
            return self._merge_vote(results)
        elif self.strategy == MergeStrategy.CHAIN:
            return self._merge_chain(results)
        elif self.strategy == MergeStrategy.CONSENSUS:
            return self._merge_consensus(results)
        return {"merged": True, "results": results}

    def _merge_vote(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        votes: dict[str, int] = {}
        for r in results:
            answer = str(r.get("answer", r.get("result", "")))
            votes[answer] = votes.get(answer, 0) + 1

        winner = max(votes, key=votes.get) if votes else ""
        return {
            "merged": True,
            "strategy": "vote",
            "winner": winner,
            "vote_count": votes[winner],
            "total_votes": len(results),
            "all_votes": votes,
        }

    def _merge_chain(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        chain_output: list[Any] = []
        context: dict[str, Any] = {}
        for r in results:
            chain_output.append(r.get("result", r))
            context.update(r.get("context", {}))
        return {
            "merged": True,
            "strategy": "chain",
            "outputs": chain_output,
            "context": context,
        }

    def _merge_consensus(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        all_agree = True
        first_result = None
        for r in results:
            current = str(r.get("result", r.get("answer", "")))
            if first_result is None:
                first_result = current
            elif current != first_result:
                all_agree = False
                break

        return {
            "merged": True,
            "strategy": "consensus",
            "consensus_reached": all_agree,
            "result": first_result if all_agree else None,
            "disagreements": 0 if all_agree else sum(
                1 for r in results
                if str(r.get("result", r.get("answer", ""))) != first_result
            ),
            "total": len(results),
        }


__all__ = [
    "AgentRole",
    "MergeStrategy",
    "TaskStatus",
    "AgentCard",
    "DispatchedTask",
    "TaskDispatch",
    "ResultMerge",
]
