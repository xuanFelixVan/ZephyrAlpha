"""
ZephyrAlpha 任务系统核心数据模型
================================
依据：MOD-INF-006 v0.3.0 §3.2 接口契约
基座：shared/schemas.py Task（28字段 + 10状态机 Pydantic V2）
扩展：TaskCard 继承 Task + Vibe Coding 执行层字段（防漂移六维 + 门禁 + 管线）
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from zephyr.shared.schemas import (
    BASE_CONFIG,
    Task,
    TaskNamespace,
    TaskStatus,
)

__all__ = [
    "TaskStatus",
    "TaskNamespace",
    "GateLevel",
    "TaskCard",
    "DecompositionResult",
    "GateCheckResult",
    "TaskAuditFinding",
]


class GateLevel(str, Enum):
    """全生命周期门禁 G0-G7——蓝图 MOD-INF-006 §3.2.1"""

    G0 = "G0"
    G7 = "G7"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"
    G6 = "G6"


class TaskAuditFinding(BaseModel):
    """任务专属审计发现——蓝图 MOD-INF-006 §3.2.2

    注意：这是任务执行上下文中记录的审计发现，不同于 shared/schemas.py 的
    AuditFinding（后者是扫描器产出的通用审计报告格式）。两者是不同概念，
    仅因历史命名冲突——本轮审计（2026-05-02）已裁决为独立实体。"""

    model_config = BASE_CONFIG

    finding_id: Annotated[str, Field(pattern=r"^F-\d{4}$")]
    dimension: str
    severity: Annotated[str, Field(pattern=r"^(critical|high|medium|low|info)$")]
    description: str
    source_task: str
    resolved: bool = False
    resolution_note: str | None = None


class TaskCard(Task):
    """
    Vibe Coding 任务模型——蓝图 MOD-INF-006 v0.3.0 §3.2.1

    继承 shared/schemas.py Task（28字段，metadata-registry.md §7 真源）：
      task_id({NAMESPACE}-{SEQ}), namespace, seq, title, status(10态), priority(P0-P3),
      phase, execution_model, model_rationale, fallback_model, safety_level,
      directive, idempotent, classification, evolution_policy, estimate_hours,
      actual_hours, files_in_scope, deliverables, acceptance, depends_on,
      tags(扁平[]), session_id, waiting_for, ready_at, completed_at, created_at, updated_at

    本类追加 Vibe Coding 执行层字段——防漂移六维 + 门禁 + 管线
    """

    model_config = ConfigDict(extra="allow")

    source_blueprint: str = Field(min_length=1, description="来源蓝图 module_id")
    source_section: str = Field(min_length=1, description="来源蓝图节号")
    description: str = Field(min_length=10, max_length=800, description="任务详细描述")

    upstream_files: list[str] = Field(
        default_factory=list,
        description="执行前必须读取的文件完整绝对路径列表",
    )
    downstream_outputs: list[dict] = Field(
        default_factory=list,
        description="执行后必须产出的文件 [{path: 完整绝对路径, description: 说明}]",
    )
    allowed_touch: list[str] = Field(
        default_factory=list,
        description="可以修改的文件白名单——完整绝对路径",
    )
    forbidden_touch: list[str] = Field(
        default_factory=list,
        description="禁止修改的文件黑名单——完整绝对路径或 glob",
    )
    applicable_rules: list[dict] = Field(
        default_factory=list,
        description="必须遵守的治理规则 [{module_id, section, reason}]",
    )
    context_assembly_manifest: list[dict] = Field(
        default_factory=list,
        description="上下文装配清单 [{file_path, reason}]——G3 门禁校验依据",
    )
    rollback_instructions: str = Field(
        default="",
        description="失败时如何撤销已有修改",
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


class DecompositionResult(BaseModel):
    """蓝图拆解结果——蓝图 MOD-INF-006 §3.2.2"""

    model_config = BASE_CONFIG

    total_tasks: int = Field(ge=0)
    tasks: list[TaskCard]
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    unassigned_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GateCheckResult(BaseModel):
    """门禁检查结果——蓝图 MOD-INF-006 §3.2.2"""

    model_config = BASE_CONFIG

    gate_id: GateLevel
    task_id: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    checked_at: str = Field(default_factory=lambda: datetime.now().isoformat())
