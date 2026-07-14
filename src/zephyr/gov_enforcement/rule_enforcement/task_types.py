# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.task_types
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.integration.shared.schema.base_config; zephyr.integration.shared.schema.severity_types; zephyr.integration.shared.schema.execution_model
# [CONSUMERS] db.task_repo; db.base_repo; db.transition; db.query; pipeline.pipeline_orchestrator; pipeline.preemptionManager; orchestrator.file_task_mapper; kb.kb_gate_task; kb.migration.kb_gate_task; mcp.task_manager_server; core.blueprint_decomposer; shared.events.event_schemas; core.models
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Task model fields MUST align with SQLite tasks table (KBG-0030 §4.2); Task=SSoT for all task card fields (was Task+TaskCard dual-source, merged 2026-05-28)
# [MODIFY-GUARD] core/models.py; db/task_repo.py; sqlite_schema.py; PS-STD-001 §7.1~§7.1.1; task-card-standard.md
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValidationError on invalid task_id format or field constraint violation
# [TESTS] tests/task/test_task_types.py
# [A_module] module_id=MOD-GOV_task_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from zephyr.integration.shared.schema.base_config import BASE_CONFIG, Classification, EvolutionPolicy
from zephyr.integration.shared.schema.execution_model import ExecutionModel, normalize_execution_model
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel


class TaskNamespace(str, Enum):
    KBG = "KBG"
    CP = "CP"
    KE = "KE"
    STD = "STD"
    DW = "DW"
    SRC = "SRC"
    OPS = "OPS"
    DM = "DM"


__all__ = [
    "ExecutionModel",
    "GateLevel",
    "Task",
    "TaskAuditFinding",
    "TaskNamespace",
    "TaskStatus",
    "normalize_execution_model",
]

_NAMESPACE_NAMES = "|".join(sorted(ns.value for ns in TaskNamespace))
_TASK_ID_PATTERN = rf"^({_NAMESPACE_NAMES})-\d+$"


class TaskStatus(str, Enum):
    """TaskStatus 真源（SSoT）— 全项目唯一 TaskStatus 定义。

    派生方（禁止反向修改）：
      - zephyr.infrastructure.lifecycle.task_lifecycle_manager.TaskStatus -> 本类 re-export
      - zephyr.shared.protocols.a2a.a2a_coordination.TaskStatus -> 本类 re-export
    """

    PENDING = "PENDING"
    CREATED = "CREATED"
    LOCKED = "LOCKED"
    ASSIGNED = "ASSIGNED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEWING = "REVIEWING"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    WAITING = "WAITING"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


class GateLevel(str, Enum):
    G0 = "G0"
    G7 = "G7"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"
    G6 = "G6"
    G10 = "G10"
    G11 = "G11"
    G12 = "G12"


class TaskAuditFinding(BaseModel):
    model_config = BASE_CONFIG

    finding_id: Annotated[str, Field(pattern=r"^F-\d{4}$")]
    dimension: str
    severity: Annotated[str, Field(pattern=r"^(critical|high|medium|low|info)$")]
    description: str
    source_task: str
    resolved: bool = False
    resolution_note: str | None = None


_DESCRIPTION_REQUIRED_KEYWORDS = ("根因", "治根", "施工步骤", "验收标准")
_DESCRIPTION_MIN_MEANINGFUL_LENGTH = 100


class Task(BaseModel):
    model_config = BASE_CONFIG

    task_id: Annotated[str, Field(pattern=_TASK_ID_PATTERN, description="Task ID, format {NAMESPACE}-{SEQ}")]
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
    description: str = Field(min_length=10, max_length=50000, description="任务详细描述（含完整施工规格）")
    allowed_touch: list[str] = Field(default_factory=list, description="可修改文件白名单——完整绝对路径")
    applicable_rules: list[dict] = Field(
        default_factory=list, description="必须遵守的治理规则 [{module_id, section, reason}]"
    )
    rollback_instructions: str = Field(default="", description="失败时如何撤销已有修改")
    post_sync_standard: list[str] = Field(default_factory=list, description="完成后必须执行的标准同步验证命令")
    dependency_type: str = Field(default="hard", description="依赖类型：hard/soft/none")
    upstream_files: list[str] = Field(default_factory=list, description="执行前必须读取的文件完整绝对路径列表")
    downstream_outputs: list[dict] = Field(
        default_factory=list, description="执行后必须产出的文件 [{path, description}]"
    )
    forbidden_touch: list[str] = Field(default_factory=list, description="禁止修改的文件黑名单")
    context_assembly_manifest: list[dict] = Field(
        default_factory=list, description="上下文装配清单 [{file_path, reason}]"
    )
    estimated_tokens: int = Field(default=8000, ge=500, description="预估 Token")
    timeout_minutes: int = Field(default=30, ge=5, description="超时时间（分钟）")
    completed_gates: list[GateLevel] = Field(default_factory=list)
    blocked_gates: dict[str, str] = Field(default_factory=dict)
    assigned_pipeline: str = Field(default="A", description="A区（生产）/B区（审计）")
    pipeline_modules: list[str] = Field(default_factory=list, description="M1-M11 模块链")
    blocked_by: list[str] = Field(default_factory=list, description="被哪些任务阻塞")
    artifact_paths: list[str] = Field(default_factory=list)
    audit_findings: list[TaskAuditFinding] = Field(default_factory=list)
    ke_entries: list[str] = Field(default_factory=list)
    ai_autonomy_level: str = Field(default="supervised")
    autonomy_checklist: list[str] = Field(default_factory=list)
    construction_status: str = Field(default="pending")
    verification_status: str = Field(default="unverified")
    approval_required: bool = Field(default=False, description="GOV-TASK-004 §2.4: 优先级升级需 Owner 审批")
    requires_rb_check: bool = Field(default=False, description="完成后是否自动触发 Red-Blue 对抗验证")
    priority_proposed: str | None = Field(default=None, description="AI 提议的目标优先级")
    rejection_cooldown_until: str | None = Field(
        default=None, description="升级被拒绝后的 48h 冷却期截止时间（ISO 8601）"
    )
    block_sessions_count: int = Field(default=0, ge=0, description="任务累计被 BLOCKED 的次数")
    pipeline_task_type: str | None = Field(default=None, description="CT-PIPE-ORC-001 任务类型")
    target_layer: str | None = Field(default=None, description="CT-PIPE-ORC-001 目标层标识")
    estimated_complexity: str | None = Field(default=None, description="CT-PIPE-ORC-001 复杂度")
    post_sync_specific: list[str] = Field(default_factory=list, description="完成后必须执行的特定同步更新")
    depgraph_nodes: list[str] = Field(default_factory=list, description="全景依赖图中对应的节点ID列表")
    depgraph_layer: str | None = Field(default=None, description="依赖图层")
    dependency_rationale: str = Field(default="", description="依赖关系说明")
    root_cause_analysis: str | None = Field(
        default=None, description="MTH-006 根源分析——COMPLETED 时如有 error 则 MUST 填写，含根因->治根->修复的完整追溯"
    )
    hallucination_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="幻觉风险评分（0=安全，1=极度危险）")
    drift_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="漂移风险评分（0=安全，1=极度危险）")
    granularity_level: str = Field(
        default="G5_ATOMIC", description="颗粒度级别: G5_ATOMIC/G4_FINE/G3_MEDIUM/G2_COARSE/G1_VAGUE"
    )

    @field_validator("ready_at", "completed_at", "deleted_at", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v: object) -> object:
        if v == "" or v == "None":
            return None
        return v

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        u = self.updated_at
        c = self.created_at
        if u.tzinfo is not None and c.tzinfo is None:
            c = c.replace(tzinfo=u.tzinfo)
        elif u.tzinfo is None and c.tzinfo is not None:
            u = u.replace(tzinfo=c.tzinfo)
        if u < c:
            raise ValueError("updated_at must not be before created_at")
        return self

    @model_validator(mode="after")
    def validate_description_structure(self) -> Self:
        missing_keywords = [kw for kw in _DESCRIPTION_REQUIRED_KEYWORDS if kw not in self.description]
        if missing_keywords and len(self.description) >= _DESCRIPTION_MIN_MEANINGFUL_LENGTH:
            import warnings

            warnings.warn(
                f"GOV-TASK-001 §2: description 缺少关键结构词 {missing_keywords}，"
                f"可能导致幻觉/漂移风险升高（GOV-TASK-001 §6 颗粒度安全阈值）",
                UserWarning,
                stacklevel=2,
            )
        return self


_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(__all__)


def __getattr__(name: str):
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.gov_enforcement.rule_enforcement.task_types",
            name,
        )
    raise AttributeError(f"module 'zephyr.gov_enforcement.rule_enforcement.task_types' has no attribute {name!r}")
