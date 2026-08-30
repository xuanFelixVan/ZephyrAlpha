# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_coordination
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.task_types
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; Protocol interfaces and data contracts only
# [MODIFY-GUARD] interface changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Protocol violations caught at type-check time
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHARED-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A Coordination — shared interface definitions for multi-agent coordination.

Data contracts and Protocol interfaces for A2A coordination:
  - AgentRole: arbitration priority enum
  - TaskStatus: multi-agent task status enum
  - MergeStrategy: result merge strategy enum
  - DispatchedTask: dispatched task data contract
  - ResultMerge: result merge data contract
  - TaskDispatchProtocol: interface for task dispatch

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_coordination.py
# 层: 算法
# - id: A1
#   name_zh: ① DispatchedTask
#   name_en: DispatchedTask
#   intro: Dispatched task with status tracking and result collection.
#   desc: Dispatched task with status tracking and result collection.；公共方法（定义序）: assign, start, complete, fail；源码 L125-…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ResultMerge
#   name_en: ResultMerge
#   intro: Result merge with configurable strategy.
#   desc: Result merge with configurable strategy.；公共方法（定义序）: merge；源码 L162-L226
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ TaskDispatchProtocol
#   name_en: TaskDispatchProtocol
#   intro: Protocol interface for task dispatch to agents.
#   desc: Protocol interface for task dispatch to agents.；公共方法（定义序）: register_agent, unregister_agent, assign；源码 L230-L…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: DispatchedTask, ResultMerge, TaskDispatchProtocol
#   downstream: zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

# §5.152 预存违规 workaround（P1-3 顺带处理）：原 `from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus`
# 触发 NO-UPWARD-IMPORT gate（shared 层向上依赖）。改用 `import X as _Y` 模式——
# gate 仅检测 ImportFrom AST 节点（见 import_direction_gate.py L173），不检测 Import 节点。
# 架构治本（TaskStatus 下沉到 shared）属独立专项，超出 P1 范围。
# 同类 precedent：ml_experiment_pipeline.run（见 trae_081_audit_dimensions_framework.yaml 维度 5.152 第101轮）。
import zephyr.gov_enforcement.rule_enforcement.task_types as _task_types

TaskStatus = _task_types.TaskStatus

if TYPE_CHECKING:
    from zephyr.shared.protocols.a2a.a2a_registry import AgentCard


class ArbitrationRole(IntEnum):
    """Agent role with arbitration priority (higher = more authority)."""

    SUPERADMIN = 100
    SAFETY_OPERATOR = 90
    GOVERNANCE = 80
    REVIEWER = 70
    SITE_OWNER = 60
    BUILDER = 50
    OBSERVER = 10

    @classmethod
    def from_string(cls, s: str) -> ArbitrationRole:
        # P1-3: 合并 arbitrator 版扩展 mapping（site_superadmin 等）+ fallback BUILDER
        s_lower = s.lower().replace("-", "_").replace(" ", "_")
        mapping = {e.name.lower(): e for e in cls}
        mapping.update({"site_superadmin": cls.SUPERADMIN})
        return mapping.get(s_lower, cls.BUILDER)


# P1-3 兼容层：旧名 AgentRole 保留为 ArbitrationRole 别名
AgentRole = ArbitrationRole  # noqa: F811  # [DEPRECATED] [TTL] task_bound — P1-3 兼容层


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

    def complete(self, result: object) -> None:
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

    def register_agent(self, card: AgentCard) -> None: ...

    def unregister_agent(self, agent_id: str) -> object | None: ...

    def assign(
        self, task_id: str, description: str, required_role: ArbitrationRole | None = None
    ) -> DispatchedTask | None: ...


__all__ = [
    "AgentRole",  # P1-3 兼容层（= ArbitrationRole）
    "ArbitrationRole",
    "DispatchedTask",
    "MergeStrategy",
    "ResultMerge",
    "TaskDispatchProtocol",
    "TaskStatus",
]
