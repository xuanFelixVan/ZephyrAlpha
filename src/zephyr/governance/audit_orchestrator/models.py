# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md | §4.2
# [MODULE] zephyr.governance.audit_trail.models
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestrator.__init__
# [CONSUMERS] audit-orchestrator.*; gates; pipeline
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AuditType三分类不变; Severity三色红灯不变; Priority四级不变
# [MODIFY-GUARD] 字段变更必须同步 contracts.py + cli.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 反序列化失败抛ValidationError
# [TESTS] tests/audit-orchestrator/test_models.py
# [A_module] module_id=MOD-GOV_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

__all__ = [
    "AuditContext",
    "AuditIssue",
    "AuditType",
    "ChangedFile",
    "DiscoveryReport",
    "FixLevel",
    "GlobalAuditReport",
    "OrchestratorStatus",
    "Priority",
    "Severity",
]


class AuditType(str, Enum):
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"


class Severity(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class Priority(str, Enum):
    P0_SEC = "P0_SEC"
    P0 = "P0"
    P1 = "P1"
    OPT = "OPT"


class FixLevel(str, Enum):
    L1_AUTO = "L1_AUTO"
    L2_LLM = "L2_LLM"
    L3_HUMAN = "L3_HUMAN"


class ChangedFile(BaseModel):
    path: str
    audit_type: AuditType = AuditType.STRUCTURAL
    old_hash: str = ""
    new_hash: str = ""
    priority: int = 3


class DiscoveryReport(BaseModel):
    changed_files: list[ChangedFile] = Field(default_factory=list)
    total_scanned: int = 0
    skipped_unchanged: int = 0
    audit_type_distribution: dict[str, int] = Field(default_factory=dict)


class AuditIssue(BaseModel):
    issue_id: str = Field(..., description="唯一标识")
    dim_id: str = Field(default="", description="维度ID")
    check_id: str = Field(default="", description="检查项ID")
    target_file: str = Field(default="", description="目标文件路径")
    severity: Severity = Field(default=Severity.GREEN, description="严重程度")
    auto_fixable: bool = Field(default=False, description="是否可自动修复")
    fix_level: FixLevel = Field(default=FixLevel.L3_HUMAN, description="修复级别")
    suggested_fix: str | None = Field(default=None, description="修复建议")


class GlobalAuditReport(BaseModel):
    audit_id: str = ""
    started_at: datetime = Field(default_factory=datetime.now)
    finished_at: datetime | None = None
    global_rounds: int = 0
    global_converged: bool = False
    total_issues_found: int = 0
    total_issues_fixed: int = 0
    is_incremental: bool = False
    skipped_by_cache: int = 0
    issues: list[AuditIssue] = Field(default_factory=list)


class OrchestratorStatus(BaseModel):
    phase: str = "IDLE"
    active_sessions: int = 0
    pending_tasks: int = 0
    circuit_breakers: dict[str, str] = Field(default_factory=dict)
    last_audit_id: str | None = None


class AuditContext(BaseModel):
    session_id: str = ""
    mode: str = "incremental"
    dimensions: list[str] = Field(default_factory=list)
    auto_fix: bool = False
    max_rounds: int = 3
