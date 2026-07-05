# [BLUEPRINT] SRC-114 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.lifecycle.task_lifecycle_manager
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_task_lifecycle_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Task Lifecycle Manager — G0-G7 任务生命周期门禁。

依据：
    蓝图 MOD-TASK_SYSTEM §3.1.2 + v0.6.0
    任务卡 TASK-INF-0106

功能：
    - G0-G7 八级生命周期门禁
    - 状态转换：created→locked→assigned→in_progress→reviewing→completed
    - gate_g7_output: downstream_outputs 完整度 + rollback_instructions 非空
    - 与 task_completion_gate.py 互补（委托层）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class TaskStatus(str, Enum):
    CREATED = "created"
    LOCKED = "locked"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class GateID(str, Enum):
    G0 = "G0_LOCK_VERIFICATION"
    G1 = "G1_CONTEXT_ASSEMBLY"
    G2 = "G2_BLUEPRINT_COMPLIANCE"
    G3 = "G3_CODE_GENERATION"
    G4 = "G4_VERIFICATION_TESTS"
    G5 = "G5_LINTING"
    G6 = "G6_ARTIFACT_COLLECTION"
    G7 = "G7_OUTPUT_COMPLETENESS"


@dataclass
class GateResult:
    gate_id: GateID
    passed: bool
    details: str
    timestamp_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class LifecycleState:
    task_id: str
    status: TaskStatus
    completed_gates: list[GateID]
    blocked_gates: dict[GateID, str]
    transition_history: list[str]
    last_updated: str


class TaskLifecycleManager:
    VALID_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
        TaskStatus.CREATED: [TaskStatus.LOCKED, TaskStatus.FAILED],
        TaskStatus.LOCKED: [TaskStatus.ASSIGNED, TaskStatus.CREATED, TaskStatus.FAILED],
        TaskStatus.ASSIGNED: [TaskStatus.IN_PROGRESS, TaskStatus.FAILED],
        TaskStatus.IN_PROGRESS: [TaskStatus.REVIEWING, TaskStatus.FAILED],
        TaskStatus.REVIEWING: [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS, TaskStatus.FAILED],
        TaskStatus.COMPLETED: [],
        TaskStatus.FAILED: [TaskStatus.CREATED],
    }

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._states: dict[str, LifecycleState] = {}

    def initialize(self, task_id: str) -> LifecycleState:
        state = self._states.get(task_id)
        if state is None:
            state = LifecycleState(
                task_id=task_id,
                status=TaskStatus.CREATED,
                completed_gates=[],
                blocked_gates={},
                transition_history=[f"{datetime.now(UTC).isoformat()}: INITIALIZED → CREATED"],
                last_updated=datetime.now(UTC).isoformat(),
            )
            self._states[task_id] = state
        return state

    def transition(self, task_id: str, to_status: TaskStatus) -> tuple[bool, str]:
        state = self.initialize(task_id)

        if to_status not in self.VALID_TRANSITIONS.get(state.status, []):
            return False, (
                f"Invalid transition: {state.status.value} → {to_status.value}. "
                f"Allowed: {[s.value for s in self.VALID_TRANSITIONS.get(state.status, [])]}"
            )

        old_status = state.status
        state.status = to_status
        state.last_updated = datetime.now(UTC).isoformat()
        state.transition_history.append(f"{state.last_updated}: {old_status.value} → {to_status.value}")

        return True, f"Transition succeeded: {old_status.value} → {to_status.value}"

    def pass_gate(self, task_id: str, gate_id: GateID, details: str = "") -> GateResult:
        state = self.initialize(task_id)

        result = GateResult(gate_id=gate_id, passed=True, details=details)
        if gate_id not in state.completed_gates:
            state.completed_gates.append(gate_id)
        if gate_id in state.blocked_gates:
            del state.blocked_gates[gate_id]
        state.last_updated = datetime.now(UTC).isoformat()

        return result

    def block_gate(self, task_id: str, gate_id: GateID, reason: str) -> GateResult:
        state = self.initialize(task_id)

        state.blocked_gates[gate_id] = reason
        state.last_updated = datetime.now(UTC).isoformat()

        return GateResult(gate_id=gate_id, passed=False, details=reason)

    def gate_g7_output(self, task_card: dict[str, Any]) -> GateResult:
        downstream = task_card.get("downstream_outputs", [])
        if not downstream:
            return GateResult(
                gate_id=GateID.G7,
                passed=False,
                details="G7 FAILED: downstream_outputs is empty",
            )

        for output in downstream:
            path_str = output.get("path", "")
            if not path_str:
                return GateResult(
                    gate_id=GateID.G7,
                    passed=False,
                    details="G7 FAILED: downstream_output missing 'path' field",
                )

            output_path = self._project_root / path_str
            if not output_path.exists():
                return GateResult(
                    gate_id=GateID.G7,
                    passed=False,
                    details=f"G7 FAILED: downstream_output path not found: {path_str}",
                )

        rollback = task_card.get("rollback_instructions", "")
        if not rollback or not rollback.strip():
            return GateResult(
                gate_id=GateID.G7,
                passed=False,
                details="G7 FAILED: rollback_instructions is empty",
            )

        manifest = task_card.get("context_assembly_manifest", [])
        for entry in manifest:
            fp = entry.get("file_path", "")
            if fp and not (self._project_root / fp).exists():
                return GateResult(
                    gate_id=GateID.G7,
                    passed=False,
                    details=f"G7 FAILED: context_assembly_manifest path not found: {fp}",
                )

        return GateResult(
            gate_id=GateID.G7,
            passed=True,
            details="G7 PASSED: all downstream outputs exist, rollback instructions present, manifest valid",
        )

    def get_state(self, task_id: str) -> LifecycleState | None:
        return self._states.get(task_id)

    def all_gates_passed(self, task_id: str) -> bool:
        state = self._states.get(task_id)
        if state is None:
            return False
        all_gates = list(GateID)
        return all(g in state.completed_gates for g in all_gates)
