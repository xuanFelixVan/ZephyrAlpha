# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §
# [MODULE] zephyr.gates.task_types
# [INVARIANTS] Task model fields MUST align with SQLite tasks table (ADR-0030 §4.2)
# [MODIFY-GUARD] sqlite_schema.py; PS-STD-001 §7.1~§7.1.1; task-card-standard.md
# [CONSUMERS] gates.check_types.*; db.task_repo; db.base_repo; db.transition; db.query; pipeline.pipeline_orchestrator; pipeline.preemptionManager; orchestrator.file_task_mapper; orchestrator.state.file_task_mapper; kb.kb_gate_task; kb.migration.kb_gate_task; mcp.task_manager_server; core.blueprint_decomposer; shared.events.event_schemas
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValidationError on invalid task_id format or field constraint violation
# [TESTS] tests/unit/test_schemas.py; tests/unit/gates/test_gate_engine.py; tests/unit/db/test_task_repo.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

from zephyr.shared.schema.base_config import BASE_CONFIG, Classification, EvolutionPolicy
from zephyr.shared.schema.severity_types import Priority, SafetyLevel

__all__ = [
    "Task",
    "TaskStatus",
    "TaskNamespace",
    "ExecutionModel",
    "normalize_execution_model",
]

_TASK_ID_PATTERN = r"^(ADR|CP|KE|STD|DW|SRC|OPS)-\d+$"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    WAITING = "WAITING"
    READY = "READY"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


class TaskNamespace(str, Enum):
    ADR = "ADR"
    CP = "CP"
    KE = "KE"
    STD = "STD"
    DW = "DW"
    SRC = "SRC"
    OPS = "OPS"


class ExecutionModel(str, Enum):
    deepseek = "deepseek"
    glm = "glm"
    claude = "claude"
    kimi = "kimi"
    qwen = "qwen"


def normalize_execution_model(value: str | ExecutionModel) -> Self:
    if isinstance(value, ExecutionModel):
        return value
    v = str(value).strip().lower()
    try:
        return ExecutionModel(v)
    except ValueError:
        pass
    if v.startswith("claude"):
        return ExecutionModel.claude
    if v.startswith("glm"):
        return ExecutionModel.glm
    if "deepseek" in v or v in ("ds", "deep_seek"):
        return ExecutionModel.deepseek
    if v.startswith("kimi"):
        return ExecutionModel.kimi
    if v.startswith("qwen"):
        return ExecutionModel.qwen
    if v == "system":
        return ExecutionModel.qwen
    return ExecutionModel.deepseek


class Task(BaseModel):
    model_config = BASE_CONFIG

    task_id: Annotated[
        str, Field(pattern=_TASK_ID_PATTERN, description="Task ID, format {NAMESPACE}-{SEQ}")
    ]
    namespace: TaskNamespace = Field(description="Task namespace")
    seq: int = Field(ge=1, description="Sequence number within namespace")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    priority: Priority = Field(default=Priority.P2, description="Priority P0-P4")
    phase: int = Field(ge=0, le=9, description="Phase (0-9)")
    execution_model: ExecutionModel = Field(
        default=ExecutionModel.deepseek,
        description="Primary execution model",
    )
    model_rationale: str | None = Field(default=None, description="Model selection rationale")
    fallback_model: str | None = Field(default=None, description="Fallback model")
    safety_level: SafetyLevel = Field(description="Safety level L/M/H")
    directive: str = Field(default="", description="Directive IDs, e.g. '313+325+999'")
    idempotent: bool = Field(default=False, description="Whether task is idempotent")
    classification: Classification = Field(default=Classification.INTERNAL, description="Access classification")
    evolution_policy: EvolutionPolicy = Field(default=EvolutionPolicy.EXTENDABLE, description="File evolution policy")
    estimate_hours: float = Field(default=0.0, ge=0, description="Estimated hours")
    actual_hours: float | None = Field(default=None, ge=0, description="Actual hours")
    files_in_scope: list[str] = Field(default_factory=list, description="Files in scope")
    deliverables: list[str] = Field(default_factory=list, description="Deliverables list")
    acceptance: list[str] = Field(default_factory=list, description="Acceptance criteria")
    depends_on: list[str] = Field(default_factory=list, description="Dependency task IDs")
    tags: list[str] = Field(default_factory=list, description="Tags")
    session_id: str | None = Field(default=None, description="Associated session ID")
    waiting_for: str | None = Field(default=None, description="Waiting for resource/event")
    ready_at: datetime | None = Field(default=None, description="READY state trigger time")
    completed_at: datetime | None = Field(default=None, description="Completion time")
    created_at: datetime = Field(description="Creation time")
    updated_at: datetime = Field(description="Last update time")
    is_deleted: int = Field(default=0, ge=0, le=1, description="Soft delete flag")
    deleted_at: datetime | None = Field(default=None, description="Soft delete time")
    schema_version: str = Field(default="", description="DB schema version")
    source_blueprint: str = Field(default="", description="Source blueprint module_id")
    source_section: str = Field(default="", description="Source blueprint section")

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be before created_at")
        return self
