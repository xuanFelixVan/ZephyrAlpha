"""
ZephyrAlpha AI 结构化输出契约模型（T-1-13）
==========================================
依据：ADR-0040（AI 结构化输出契约采用 Pydantic v2）

五类核心模型
-----------
1. Task          — 任务登记（10 状态机 + directive + classification + evolution_policy）
2. AuditReport   — 审计 / 扫描产物
3. KnowledgeEntry — KE 索引（KE-NNN）
4. FailurePattern — 失败模式登记（F-NNN）
5. HandoffPackage — Session 交接包（8 必填字段）

ConfigDict 基线（ADR-0040 §4.2）
------------------------------------
  extra            = "forbid"         AI typo 的 extra 字段立即报错
  str_strip_whitespace = True         移除尾部空白
  populate_by_name = True             支持 alias
  validate_assignment = True          运行时字段重写也触发校验

禁止反模式（ADR-0040 §4.5）
-------------------------------
  - 裸 dict / TypedDict 作为对外输出契约
  - Any 类型字段（除明注 payload 等透传场景）
  - 跳过 ValidationError 静默重试
  - 在模型里定义 DB 会话 / ORM 方法
  - 多处复制粘贴字段——必须从本文件统一 import
"""
from __future__ import annotations


from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = [
    "TaskStatus",
    "TaskNamespace",
    "ExecutionModel",
    "normalize_execution_model",
    "SafetyLevel",
    "Classification",
    "EvolutionPolicy",
    "AuditSeverity",
    "Priority",
    "CircuitBreakerState",
    "KeCategory",
    "Task",
    "AuditFinding",
    "AuditReport",
    "KnowledgeEntry",
    "FailurePattern",
    "BlockedItem",
    "Decision",
    "NextAction",
    "HandoffPackage",
    "BASE_CONFIG",
]

# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------


class TaskStatus(str, Enum):
    """任务状态机（ADR-0030 §2）。"""

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


class SafetyLevel(str, Enum):
    """任务安全等级。"""

    L = "L"
    M = "M"
    H = "H"


class Classification(str, Enum):
    """访问分类。"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class EvolutionPolicy(str, Enum):
    """文件演进策略。"""

    FROZEN = "frozen"
    EXTENDABLE = "extendable"
    REWRITABLE = "rewritable"


class TaskNamespace(str, Enum):
    """任务命名空间（#21 裁定：分类字段，不是 ID 的一部分）。"""

    ADR = "ADR"
    CP = "CP"
    KE = "KE"
    STD = "STD"
    DW = "DW"
    SRC = "SRC"
    OPS = "OPS"


class ExecutionModel(str, Enum):
    """主执行模型——与 SQLite ``tasks.execution_model`` CHECK 严格对齐（ADR-0030）。"""

    deepseek = "deepseek"
    glm = "glm"
    claude = "claude"
    kimi = "kimi"
    qwen = "qwen"


def normalize_execution_model(value: str | ExecutionModel) -> Self:
    """将自由文本模型名映射为 ``ExecutionModel``（落库前与 SQLite CHECK 一致）。"""

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


class AuditSeverity(str, Enum):
    """审计严重性级别（向后兼容别名，真源为 Priority）。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class Priority(str, Enum):
    """优先级（GOV-TASK-004 §2.2 真源，P0-P4 五级，对齐 Jira Priority + ITIL Urgency）。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class CircuitBreakerState(str, Enum):
    """熔断器状态枚举（真源：shared/schemas.py，AUDIT-07 P0-1 统一）。

    gates/circuit_breaker.py 和 pipeline/models.py 均从本定义导入，
    禁止在其他模块中重复定义。值使用大写，与 SQLite 存储一致。
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class KeCategory(str, Enum):
    """知识条目内容类型（metadata-registry.md §9.1 真源，10 值）。"""

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
    """失败类型分类。"""

    VALIDATION = "validation"
    LOGIC = "logic"
    INFRASTRUCTURE = "infrastructure"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# 公共 ConfigDict 基线（ADR-0040 §4.2）
# ---------------------------------------------------------------------------

BASE_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    populate_by_name=True,
    validate_assignment=True,
)

# ---------------------------------------------------------------------------
# 1. Task 模型
# ---------------------------------------------------------------------------

_TASK_ID_PATTERN = r"^(ADR|CP|KE|STD|DW|SRC|OPS)-\d+$"


class Task(BaseModel):
    """
    任务登记模型（31字段：28业务 + 3 DB追踪）。

    与 SQLite ``tasks`` 表字段严格对齐（ADR-0030 §4.2）。
    字段变更必须同步更新：本文件、``sqlite_schema.py``、
    PS-STD-001（``metadata-registry.md``）§7.1~§7.1.1、``task-card-standard.md``（操作指南）。
    """

    model_config = BASE_CONFIG

    task_id: Annotated[
        str, Field(pattern=_TASK_ID_PATTERN, description="任务 ID，格式 {NAMESPACE}-{SEQ}（命名空间内自增）")
    ]
    namespace: TaskNamespace = Field(description="任务命名空间（#21 裁定：分类字段）")
    seq: int = Field(ge=1, description="命名空间内自增序号")
    title: str = Field(min_length=1, max_length=200, description="任务标题（对齐 Jira Summary / Linear Title）")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: Priority = Field(default=Priority.P2, description="优先级 P0-P4（GOV-TASK-004 §2.2）")
    phase: int = Field(ge=0, le=9, description="所属 Phase（0-9）")
    execution_model: ExecutionModel = Field(
        default=ExecutionModel.deepseek,
        description="主执行模型（与 sqlite_schema tasks.execution_model CHECK 一致）",
    )
    model_rationale: str | None = Field(default=None, description="选模型理由（防 AI 乱选贵模型）")
    fallback_model: str | None = Field(default=None, description="降级模型")
    safety_level: SafetyLevel = Field(description="安全等级 L/M/H")
    directive: str = Field(default="", description="执行指令编号，如 '313+325+999'")
    idempotent: bool = Field(default=False, description="任务是否幂等")
    classification: Classification = Field(default=Classification.INTERNAL, description="访问分类")
    evolution_policy: EvolutionPolicy = Field(default=EvolutionPolicy.EXTENDABLE, description="文件演进策略")
    estimate_hours: float = Field(default=0.0, ge=0, description="预估工时（小时）")
    actual_hours: float | None = Field(default=None, ge=0, description="实际工时（对齐 Jira Time Spent）")
    files_in_scope: list[str] = Field(default_factory=list, description="本任务需读取的文件列表（防漂移核心字段）")
    deliverables: list[str] = Field(default_factory=list, description="交付物列表")
    acceptance: list[str] = Field(default_factory=list, description="验收标准列表")
    depends_on: list[str] = Field(default_factory=list, description="前置任务 ID 列表")
    tags: list[str] = Field(default_factory=list, description="标签列表（对齐 Jira Labels / Linear Labels）")
    session_id: str | None = Field(default=None, description="关联 session ID")
    waiting_for: str | None = Field(default=None, description="等待资源/事件描述")
    ready_at: datetime | None = Field(default=None, description="READY 状态触发时间")
    completed_at: datetime | None = Field(default=None, description="完成时间（对齐 Jira Resolution Date）")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最近更新时间")
    is_deleted: int = Field(default=0, ge=0, le=1, description="软删除标记（SQLite 0/1，MOD-INF-012）")
    deleted_at: datetime | None = Field(default=None, description="软删除时间")
    schema_version: str = Field(default="", description="数据库 schema 版本号（内部追踪用）")

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at 不得早于 created_at")
        return self


# ---------------------------------------------------------------------------
# 2. AuditReport 模型
# ---------------------------------------------------------------------------


class AuditFinding(BaseModel):
    """单条审计发现。"""

    model_config = BASE_CONFIG

    finding_id: str = Field(min_length=1)
    severity: AuditSeverity
    description: str = Field(min_length=1, max_length=1000)
    file_path: str | None = None
    suggestion: str | None = None


class AuditReport(BaseModel):
    """
    审计 / 扫描产物模型。

    用途：Sentinel L1、Phase 验收、validate_ssot.py 等扫描工具的结构化输出。
    """

    model_config = BASE_CONFIG

    report_id: str = Field(min_length=1, description="报告唯一 ID")
    scanner: str = Field(min_length=1, description="扫描器名称，如 'ssot_guard'")
    scan_target: str = Field(min_length=1, description="扫描目标路径或范围")
    findings: list[AuditFinding] = Field(default_factory=list)
    p0_count: int = Field(default=0, ge=0)
    p1_count: int = Field(default=0, ge=0)
    p2_count: int = Field(default=0, ge=0)
    passed: bool = Field(default=True, description="整体是否通过（P0 数量为 0 则 True）")
    session_id: str | None = None
    created_at: datetime

    @model_validator(mode="after")
    def sync_passed_with_p0(self) -> Self:
        """passed 字段由 p0_count 决定，保持一致性。"""
        if self.p0_count > 0:
            object.__setattr__(self, "passed", False)
        return self

    @model_validator(mode="after")
    def sync_counts(self) -> Self:
        """同步 findings 到计数字段。"""
        if self.findings:
            p0 = sum(1 for f in self.findings if f.severity == AuditSeverity.P0)
            p1 = sum(1 for f in self.findings if f.severity == AuditSeverity.P1)
            p2 = sum(1 for f in self.findings if f.severity == AuditSeverity.P2)
            object.__setattr__(self, "p0_count", p0)
            object.__setattr__(self, "p1_count", p1)
            object.__setattr__(self, "p2_count", p2)
            object.__setattr__(self, "passed", p0 == 0)
        return self


# ---------------------------------------------------------------------------
# 3. KnowledgeEntry 模型
# ---------------------------------------------------------------------------


class KnowledgeEntry(BaseModel):
    """
    知识库条目模型（KE-NNN）。

    与 SQLite ``knowledge`` 表字段对齐（ADR-0030 §4.2）。
    """

    model_config = BASE_CONFIG

    ke_id: Annotated[str, Field(pattern=r"^KE-\d{3,}$", description="KE 编号，格式 KE-NNN")]
    title: str = Field(min_length=1, max_length=300)
    category: KeCategory = Field(
        default=KeCategory.best_practice, description="知识条目内容类型（metadata-registry.md §9.1）"
    )
    source_file: str = Field(min_length=1, description="来源文件相对路径")
    source_git_deleted: bool = Field(default=False, description="来源文件是否已 git 删除")
    fingerprint_sha256: str | None = Field(
        default=None,
        description="来源文件 SHA-256 指纹",
    )
    tags: list[str] = Field(default_factory=list)
    summary: str = Field(default="", max_length=2000)
    created_at: datetime
    updated_at: datetime

    @field_validator("fingerprint_sha256")
    @classmethod
    def validate_sha256(cls, v: str | None) -> str | None:
        if v is not None and len(v) != 64:
            raise ValueError("fingerprint_sha256 必须是 64 位十六进制字符串")
        return v

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at 不得早于 created_at")
        return self


# ---------------------------------------------------------------------------
# 4. FailurePattern 模型
# ---------------------------------------------------------------------------


class FailurePattern(BaseModel):
    """
    失败模式登记模型（F-NNN）。

    用途：Carryover failure_context、调度器重试策略。
    """

    model_config = BASE_CONFIG

    pattern_id: Annotated[str, Field(pattern=r"^F-\d{3,}$", description="失败模式 ID，格式 F-NNN")]
    failure_type: FailureType = Field(description="失败类型")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    reproduction_steps: list[str] = Field(default_factory=list)
    root_cause: str = Field(default="", max_length=1000)
    mitigation: str = Field(default="", max_length=1000)
    affected_tasks: list[str] = Field(default_factory=list, description="受影响的 task_id 列表")
    recurrence_count: int = Field(default=1, ge=1)
    resolved: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def updated_not_before_created(self) -> Self:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at 不得早于 created_at")
        return self


# ---------------------------------------------------------------------------
# 5. HandoffPackage 模型（及子类型）
# ---------------------------------------------------------------------------


class BlockedItem(BaseModel):
    """交接包中的阻塞项。"""

    model_config = BASE_CONFIG

    task_id: str = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=500)
    blocked_since: datetime | None = None
    unblock_condition: str | None = Field(default=None, max_length=300)


class Decision(BaseModel):
    """交接包中的决策记录。"""

    model_config = BASE_CONFIG

    decision_id: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=1000)
    kb_ref: str | None = Field(default=None, description="关联 KB 决策记录编号，如 ADR-0030")


class NextAction(BaseModel):
    """交接包中的下一步行动。"""

    model_config = BASE_CONFIG

    priority: int = Field(ge=1, le=10, description="优先级 1-10（1 最高）")
    action: str = Field(min_length=1, max_length=300)
    owner: str | None = Field(default=None, description="建议执行者（模型或 Owner）")
    task_ref: str | None = Field(default=None, description="关联 task_id")


class HandoffPackage(BaseModel):
    """
    Session 交接包模型（ADR-0040 §4.1 + ADR-0041）。

    8 必填字段（session_id / completed_tasks / in_progress_tasks /
    blocked_items / decisions_made / next_actions / context_summary /
    open_questions）。
    """

    model_config = BASE_CONFIG

    session_id: str = Field(min_length=1, description="当前 session 唯一标识")
    completed_tasks: list[str] = Field(description="本 session 完成的 task_id 列表")
    in_progress_tasks: list[str] = Field(description="仍在进行中的 task_id 列表")
    blocked_items: list[BlockedItem] = Field(description="阻塞项列表")
    decisions_made: list[Decision] = Field(description="本 session 做出的决策")
    next_actions: list[NextAction] = Field(description="下一步行动，按优先级排序")
    context_summary: str = Field(
        max_length=500,
        description="本 session 上下文摘要（≤500 字符）",
    )
    open_questions: list[str] = Field(description="待解决的开放问题")
    created_at: datetime = Field(description="交接包生成时间")
    phase: int | None = Field(default=None, ge=0, le=9, description="当前 Phase")

    @field_validator("next_actions")
    @classmethod
    def next_actions_sorted(cls, v: list[NextAction]) -> list[NextAction]:
        """按优先级升序排序（低数字 = 高优先级）。"""
        return sorted(v, key=lambda a: a.priority)

    @model_validator(mode="after")
    def no_overlap_tasks(self) -> Self:
        """completed_tasks 和 in_progress_tasks 不得有交集。"""
        overlap = set(self.completed_tasks) & set(self.in_progress_tasks)
        if overlap:
            raise ValueError(f"任务 {overlap} 同时出现在 completed_tasks 和 in_progress_tasks 中")
        return self

    def to_yaml_dict(self) -> dict[str, Any]:
        """导出为 YAML 兼容字典（datetime 转 ISO 字符串）。"""
        data = self.model_dump()
        for key, val in data.items():
            if isinstance(val, datetime):
                data[key] = val.isoformat()
        return data
