"""
ZephyrAlpha 任务系统核心数据模型
================================
依据：MOD-INF-006 v0.3.0 §3.2 接口契约
基座：shared/schemas.py Task（31字段：28业务 + 3 DB追踪 + 10状态机 Pydantic V2）
扩展：TaskCard 继承 Task + Vibe Coding 执行层字段（防漂移六维 + 门禁 + 管线）
版本：v0.3.0 — inheritance complete，Task 31字段全链路贯通
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import (
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
    """全生命周期门禁：Orc G0/G7、KMS G1–G6、交易 G10–G12。

    说明：磁盘上的 YAML 文件名仍保留历史命名（如 ``g7_position_limits.yaml`` 对应
    ``gate_id: G10``），以避免大范围重命名；逻辑门编号以本枚举与 ``gate_engine._GATE_FILES`` 为准。
    """

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

    继承 shared/schemas.py Task（31字段：28业务 + is_deleted/deleted_at/schema_version，metadata-registry.md §7 真源）：
      task_id({NAMESPACE}-{SEQ}), namespace, seq, title, status(10态), priority(P0-P4),
      phase, execution_model, model_rationale, fallback_model, safety_level,
      directive, idempotent, classification, evolution_policy, estimate_hours,
      actual_hours, files_in_scope, deliverables, acceptance, depends_on,
      tags(扁平[]), session_id, waiting_for, ready_at, completed_at, created_at, updated_at

    本类追加 Vibe Coding 执行层字段——防漂移六维 + 门禁 + 管线

    model_config 与 Task 一致（ADR-0040 extra=forbid）——扩展字段已全部在本类声明，
    禁止静默吞掉 AI typo 的多余字段。
    """

    model_config = BASE_CONFIG

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

    approval_required: bool = Field(
        default=False,
        description="GOV-TASK-004 §2.4: 优先级升级需 Owner 审批——True 时 actual priority 不变，priority_proposed 存目标值",
    )
    priority_proposed: str | None = Field(
        default=None,
        description="GOV-TASK-004 §2.4: AI 提议的目标优先级；审批通过后写入 priority 字段",
    )
    rejection_cooldown_until: str | None = Field(
        default=None,
        description="GOV-TASK-004 §2.4: 升级被拒绝后的 48h 冷却期截止时间（ISO 8601）",
    )

    block_sessions_count: int = Field(
        default=0,
        ge=0,
        description="GOV-TASK-004 §2.7: 任务累计被 BLOCKED 的次数，用于升级检测（P0≥2 / 任意≥5 触发升级）",
    )

    pipeline_task_type: str | None = Field(
        default=None,
        description="CT-PIPE-ORC-001 任务类型（如 MODEL_BUILD / AUDIT）；None 且 tags 无 ct_pipe.task_type= 时按整链 M1 或 M6 入口",
    )
    target_layer: str | None = Field(
        default=None,
        description="CT-PIPE-ORC-001 目标层标识（如 L01），与 DOC_WRITE/REFACTOR 路由共用",
    )
    estimated_complexity: str | None = Field(
        default=None,
        description="CT-PIPE-ORC-001 复杂度：HIGH / MEDIUM / LOW；None 时 MODEL_BUILD 可由 estimated_tokens≥6000 推断为 HIGH",
    )


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
