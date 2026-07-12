# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_coordination
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.task_types
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; Protocol interfaces and data contracts only
# [MODIFY-GUARD] interface changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Protocol violations caught at type-check time
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHR_a2a_coordination | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A Coordination — shared interface definitions for multi-agent coordination.

Data contracts and Protocol interfaces for A2A coordination:
  - AgentRole: arbitration priority enum
  - TaskStatus: multi-agent task status enum
  - MergeStrategy: result merge strategy enum
  - DispatchedTask: dispatched task data contract
  - ResultMerge: result merge data contract
  - TaskDispatchProtocol: interface for task dispatch
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Protocol, runtime_checkable

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus


class AgentRole(IntEnum):
    """Agent role with arbitration priority (higher = more authority)."""

    SUPERADMIN = 100
    SAFETY_OPERATOR = 90
    GOVERNANCE = 80
    REVIEWER = 70
    SITE_OWNER = 60
    BUILDER = 50
    OBSERVER = 10

    @classmethod
    def from_string(cls, s: str) -> AgentRole:
        mapping = {e.name.lower(): e for e in cls}
        return mapping.get(s.lower(), cls.OBSERVER)


class MergeStrategy(str, Enum):
    """Result merge strategy for multi-agent output."""

    VOTE = "vote"
    CHAIN = "chain"
    CONSENSUS = "consensus"


@dataclass
class DispatchedTask:
    """Dispatched task with status tracking and result collection."""

    task_id: str
    agent_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_at: str | None = None
    completed_at: str | None = None
    result: object = None
    error: str | None = None

    def assign(self) -> None:
        self.status = TaskStatus.ASSIGNED
        from datetime import UTC, datetime

        self.assigned_at = datetime.now(UTC).isoformat()

    def start(self) -> None:
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, result: Any) -> None:
        self.status = TaskStatus.COMPLETED
        self.result = result
        from datetime import UTC, datetime

        self.completed_at = datetime.now(UTC).isoformat()

    def fail(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error = error
        from datetime import UTC, datetime

        self.completed_at = datetime.now(UTC).isoformat()


@dataclass
class ResultMerge:
    """Result merge with configurable strategy."""

    strategy: MergeStrategy = MergeStrategy.CONSENSUS

    def merge(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {"merged": True, "results": []}

        if self.strategy is MergeStrategy.VOTE:
            return self._merge_vote(results)
        elif self.strategy is MergeStrategy.CHAIN:
            return self._merge_chain(results)
        elif self.strategy is MergeStrategy.CONSENSUS:
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
            "disagreements": 0
            if all_agree
            else sum(1 for r in results if str(r.get("result", r.get("answer", ""))) != first_result),
            "total": len(results),
        }


@runtime_checkable
class TaskDispatchProtocol(Protocol):
    """Protocol interface for task dispatch to agents."""

    def register_agent(self, card: Any) -> None: ...

    def unregister_agent(self, agent_id: str) -> Any | None: ...

    def assign(
        self, task_id: str, description: str, required_role: AgentRole | None = None
    ) -> DispatchedTask | None: ...


__all__ = [
    "AgentRole",
    "DispatchedTask",
    "MergeStrategy",
    "ResultMerge",
    "TaskDispatchProtocol",
    "TaskStatus",
]
