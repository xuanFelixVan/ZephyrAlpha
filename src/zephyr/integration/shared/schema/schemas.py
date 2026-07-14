# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.schema.schemas
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared.schema.base_config; zephyr.integration.shared.schema.severity_types; zephyr.integration.shared.schema.execution_model
# [CONSUMERS] gates; context-engine; orchestrator; kb; runtime; db; pipeline; mcp; core; shared.events; scripts; tests
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] All public symbols MUST be re-exported; __all__ MUST match actual exports; Task types canonical source is gates.task_types; severity types canonical source is shared.schema.severity_types; base config canonical source is shared.schema.base_config
# [MODIFY-GUARD] GOV-TASK-004
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ImportError on missing sub-module
# [TESTS] tests/test_schemas.py; tests/contract/test_schema_stability.py
# [A_module] module_id=MOD-SHR_schemas | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from zephyr.integration.shared.schema.base_config import BASE_CONFIG, Classification, EvolutionPolicy
from zephyr.integration.shared.schema.execution_model import (
    ExecutionModel,
    normalize_execution_model,
)
from zephyr.integration.shared.schema.severity_types import (
    AuditSeverity,
    CircuitBreakerState,
    Priority,
    SafetyLevel,
)

__all__ = [
    "BASE_CONFIG",
    "AuditFinding",
    "AuditReport",
    "AuditSeverity",
    "BlockedItem",
    "CircuitBreakerState",
    "Classification",
    "Decision",
    "EvolutionPolicy",
    "ExecutionModel",
    "FailurePattern",
    "FailureType",
    "HandoffPackage",
    "KeCategory",
    "KnowledgeEntry",
    "NextAction",
    "Priority",
    "SafetyLevel",
    "Task",
    "TaskNamespace",
    "TaskStatus",
    "normalize_execution_model",
]

_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(__all__)

# Lazy-load governance task types to break circular dependency:
# integration.shared.schema.schemas -> governance.rule_enforcement.task_types -> integration.shared.schema.*
# These symbols are re-export only (zero business usage in this module).
_GOVERNANCE_TASK_TYPES = {
    "Task": "zephyr.gov_enforcement.rule_enforcement.task_types",
    "TaskNamespace": "zephyr.gov_enforcement.rule_enforcement.task_types",
    "TaskStatus": "zephyr.gov_enforcement.rule_enforcement.task_types",
}


def __getattr__(name: str):
    if name in _GOVERNANCE_TASK_TYPES:
        import importlib

        _mod = importlib.import_module(_GOVERNANCE_TASK_TYPES[name])
        _val = getattr(_mod, name)
        globals()[name] = _val
        return _val
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.integration.shared.schema.schemas",
            name,
        )
    raise AttributeError(f"module 'zephyr.integration.shared.schema.schemas' has no attribute {name!r}")


class KeCategory(str, Enum):
    blueprint_decision = "blueprint_decision"
    strategy = "strategy"
    factor = "factor"
    best_practice = "best_practice"
    lesson_learned = "lesson_learned"
    architecture = "architecture"
    risk_control = "risk_control"
    data_governance = "data_governance"
    operations = "operations"
    compliance = "compliance"


class FailureType(str, Enum):
    VALIDATION = "validation"
    LOGIC = "logic"
    INFRASTRUCTURE = "infrastructure"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class AuditFinding(BaseModel):
    model_config = BASE_CONFIG

    finding_id: str = Field(min_length=1)
    severity: AuditSeverity
    description: str = Field(min_length=1, max_length=1000)
    file_path: str | None = None
    suggestion: str | None = None


class AuditReport(BaseModel):
    model_config = BASE_CONFIG

    report_id: str = Field(min_length=1, description="Report unique ID")
    scanner: str = Field(min_length=1, description="Scanner name")
    scan_target: str = Field(min_length=1, description="Scan target path or scope")
    findings: list[AuditFinding] = Field(default_factory=list)
    p0_count: int = Field(default=0, ge=0)
    p1_count: int = Field(default=0, ge=0)
    p2_count: int = Field(default=0, ge=0)
    passed: bool = Field(default=True, description="Overall pass (P0 count = 0)")
    session_id: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def sync_passed_with_p0(self) -> Self:
        if self.p0_count > 0:
            object.__setattr__(self, "passed", False)
        return self

    @model_validator(mode="after")
    def sync_counts(self) -> Self:
        if self.findings:
            p0 = sum(1 for f in self.findings if f.severity is AuditSeverity.P0)
            p1 = sum(1 for f in self.findings if f.severity is AuditSeverity.P1)
            p2 = sum(1 for f in self.findings if f.severity is AuditSeverity.P2)
            object.__setattr__(self, "p0_count", p0)
            object.__setattr__(self, "p1_count", p1)
            object.__setattr__(self, "p2_count", p2)
            object.__setattr__(self, "passed", p0 == 0)
        return self


class KnowledgeEntry(BaseModel):
    model_config = BASE_CONFIG

    ke_id: Annotated[str, Field(pattern=r"^KE-\d{3,}$", description="KE ID, format KE-NNN")]
    title: str = Field(min_length=1, max_length=300)
    category: KeCategory = Field(default=KeCategory.best_practice, description="Knowledge entry content type")
    source_file: str = Field(min_length=1, description="Source file relative path")
    source_git_deleted: bool = Field(default=False, description="Whether source file is git-deleted")
    fingerprint_sha256: str | None = Field(
        default=None,
        description="Source file SHA-256 fingerprint",
    )
    tags: list[str] = Field(default_factory=list)
    summary: str = Field(default="", max_length=2000)
    created_at: datetime
    updated_at: datetime

    @field_validator("fingerprint_sha256")
    @classmethod
    def validate_sha256(cls, v: str | None) -> str | None:
        if v is not None and len(v) != 64:
            raise ValueError("fingerprint_sha256 must be 64-char hex string")
        return v

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be before created_at")
        return self


class FailurePattern(BaseModel):
    model_config = BASE_CONFIG

    pattern_id: Annotated[str, Field(pattern=r"^F-\d{3,}$", description="Failure pattern ID, format F-NNN")]
    failure_type: FailureType = Field(description="Failure type")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    reproduction_steps: list[str] = Field(default_factory=list)
    root_cause: str = Field(default="", max_length=1000)
    mitigation: str = Field(default="", max_length=1000)
    affected_tasks: list[str] = Field(default_factory=list, description="Affected task_id list")
    recurrence_count: int = Field(default=1, ge=1)
    resolved: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be before created_at")
        return self


class BlockedItem(BaseModel):
    model_config = BASE_CONFIG

    task_id: str = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=500)
    blocked_since: datetime | None = None
    unblock_condition: str | None = Field(default=None, max_length=300)


class Decision(BaseModel):
    model_config = BASE_CONFIG

    decision_id: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=1000)
    kb_ref: str | None = Field(default=None, description="Associated KB decision record")


class NextAction(BaseModel):
    model_config = BASE_CONFIG

    priority: int = Field(ge=1, le=10, description="Priority 1-10 (1 highest)")
    action: str = Field(min_length=1, max_length=300)
    owner: str | None = Field(default=None, description="Suggested executor")
    task_ref: str | None = Field(default=None, description="Associated task_id")


class HandoffPackage(BaseModel):
    model_config = BASE_CONFIG

    session_id: str = Field(min_length=1, description="Current session unique ID")
    completed_tasks: list[str] = Field(description="Completed task_id list this session")
    in_progress_tasks: list[str] = Field(description="Still in-progress task_id list")
    blocked_items: list[BlockedItem] = Field(description="Blocked items")
    decisions_made: list[Decision] = Field(description="Decisions made this session")
    next_actions: list[NextAction] = Field(description="Next actions, sorted by priority")
    context_summary: str = Field(
        max_length=500,
        description="Session context summary (<=500 chars)",
    )
    open_questions: list[str] = Field(description="Open questions to resolve")
    created_at: datetime = Field(description="Handoff package generation time")
    phase: int | None = Field(default=None, ge=0, le=9, description="Current Phase")

    @field_validator("next_actions")
    @classmethod
    def next_actions_sorted(cls, v: list[NextAction]) -> list[NextAction]:
        return sorted(v, key=lambda a: a.priority)

    @model_validator(mode="after")
    def no_overlap_tasks(self) -> Self:
        overlap = set(self.completed_tasks) & set(self.in_progress_tasks)
        if overlap:
            raise ValueError(f"Tasks {overlap} appear in both completed_tasks and in_progress_tasks")
        return self

    def to_yaml_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        for key, val in data.items():
            if isinstance(val, datetime):
                data[key] = val.isoformat()
        return data
