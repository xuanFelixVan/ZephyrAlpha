# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.2
# [MODULE] zephyr.gov_audit.models
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.*; gates; pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AuditType三分类不变; Severity三色红灯不变; Priority四级不变
# [MODIFY-GUARD] 字段变更必须同步 contracts.py + cli.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 反序列化失败抛ValidationError
# [TESTS] tests/audit-orchestrator/test_models.py
# [A_module] module_id=MOD-GOV_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from datetime import datetime
from enum import Enum
from typing import Any

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


class AuditChain:
    def __init__(self) -> None:
        self.entries: list[Any] = []
        self.chain_hash: str = ""

    def add_entry(self, entry: Any) -> None:
        self.entries.append(entry)

    def verify(self) -> bool:
        return True


class _AuditEventTypeMember:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"AuditEventType.{self.value}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _AuditEventTypeMember):
            return self.value == other.value
        return self.value == other

    def __hash__(self) -> int:
        return hash(self.value)


class AuditEventType:
    CREATE = _AuditEventTypeMember("CREATE")
    UPDATE = _AuditEventTypeMember("UPDATE")
    DELETE = _AuditEventTypeMember("DELETE")
    READ = _AuditEventTypeMember("READ")
    EXECUTE = _AuditEventTypeMember("EXECUTE")
    DELEGATE = _AuditEventTypeMember("DELEGATE")
    ESCALATE = _AuditEventTypeMember("ESCALATE")
    ROLLBACK = _AuditEventTypeMember("ROLLBACK")
    MIGRATE = _AuditEventTypeMember("MIGRATE")
    COMPLIANCE_CHECK = _AuditEventTypeMember("COMPLIANCE_CHECK")
    PERMISSION_VIOLATION = _AuditEventTypeMember("PERMISSION_VIOLATION")
    FILE_CREATE = _AuditEventTypeMember("FILE_CREATE")
    FILE_READ = _AuditEventTypeMember("FILE_READ")
    FILE_MODIFY = _AuditEventTypeMember("FILE_MODIFY")
    FILE_DELETE = _AuditEventTypeMember("FILE_DELETE")
    FILE_MOVE = _AuditEventTypeMember("FILE_MOVE")
    FILE_WRITE = _AuditEventTypeMember("FILE_WRITE")
    FILE_RENAME = _AuditEventTypeMember("FILE_RENAME")
    PERMISSION_CHANGE = _AuditEventTypeMember("PERMISSION_CHANGE")
    ANOMALY_DETECTED = _AuditEventTypeMember("ANOMALY_DETECTED")
    DRIFT_DETECTED = _AuditEventTypeMember("DRIFT_DETECTED")
    COMPLIANCE_VIOLATION = _AuditEventTypeMember("COMPLIANCE_VIOLATION")
    TRUST_SCORE_CHANGE = _AuditEventTypeMember("TRUST_SCORE_CHANGE")
    CONFIGURATION_CHANGE = _AuditEventTypeMember("CONFIGURATION_CHANGE")
    SYSTEM_EVENT = _AuditEventTypeMember("SYSTEM_EVENT")
    IMPORT = _AuditEventTypeMember("IMPORT")
    KB_POISONING_ATTEMPT = _AuditEventTypeMember("KB_POISONING_ATTEMPT")
    SECURITY_SCAN = _AuditEventTypeMember("SECURITY_SCAN")
    POLICY_CHANGE = _AuditEventTypeMember("POLICY_CHANGE")
    SUPPLY_CHAIN_INSTALL = _AuditEventTypeMember("SUPPLY_CHAIN_INSTALL")
    DEPENDENCY_UPDATE = _AuditEventTypeMember("DEPENDENCY_UPDATE")
    RESOURCE_ALLOCATION = _AuditEventTypeMember("RESOURCE_ALLOCATION")
    DELEGATION_CHAIN_ISSUE = _AuditEventTypeMember("DELEGATION_CHAIN_ISSUE")
    AUDIT_ANOMALY = _AuditEventTypeMember("AUDIT_ANOMALY")
    RETENTION_EXPIRY = _AuditEventTypeMember("RETENTION_EXPIRY")
    FEEDBACK_LOOP_SELF_REINFORCING = _AuditEventTypeMember("FEEDBACK_LOOP_SELF_REINFORCING")
    METRIC_THRESHOLD_BREACH = _AuditEventTypeMember("METRIC_THRESHOLD_BREACH")
    CAPACITY_WARNING = _AuditEventTypeMember("CAPACITY_WARNING")
    EXPORT = _AuditEventTypeMember("EXPORT")
    RESTORE = _AuditEventTypeMember("RESTORE")
    BACKUP = _AuditEventTypeMember("BACKUP")
    HEALTH_CHECK = _AuditEventTypeMember("HEALTH_CHECK")
    SYSTEM_SHUTDOWN = _AuditEventTypeMember("SYSTEM_SHUTDOWN")
    SYSTEM_STARTUP = _AuditEventTypeMember("SYSTEM_STARTUP")


class AuditEntryV1:
    def __init__(
        self,
        entry_id: str = "",
        event_type: str = "",
        timestamp: datetime | None = None,
        actor: str = "",
        target: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.entry_id = entry_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.actor = actor
        self.target = target
        self.details = details or {}


class AuditMetrics:
    def __init__(
        self,
        total_entries: int = 0,
        by_type: dict[str, int] | None = None,
        by_actor: dict[str, int] | None = None,
        period: str = "",
    ) -> None:
        self.total_entries = total_entries
        self.by_type = by_type or {}
        self.by_actor = by_actor or {}
        self.period = period


class FileActionType:
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    RENAME = "RENAME"
    MOVE = "MOVE"


class ProvenanceDepth:
    DIRECT = 0
    ONE_HOP = 1
    TWO_HOP = 2
    FULL_CHAIN = 3


class FileAuditDetail:
    def __init__(
        self,
        path: str = "",
        action: str | None = None,
        actor: str = "",
        timestamp: datetime | None = None,
        hash_before: str = "",
        hash_after: str = "",
    ) -> None:
        self.path = path
        self.action = action
        self.actor = actor
        self.timestamp = timestamp
        self.hash_before = hash_before
        self.hash_after = hash_after


class ProvenanceLevel:
    DIRECT = 0
    ONE_HOP = 1
    TWO_HOP = 2
    FULL_CHAIN = 3


class IntegrityReport:
    def __init__(
        self,
        report_id: str = "",
        valid: bool = True,
        entry_count: int = 0,
        violations: list[Any] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.report_id = report_id
        self.valid = valid
        self.entry_count = entry_count
        self.violations = violations or []
        self.timestamp = timestamp


class IntegrityRecord:
    def __init__(
        self,
        record_id: str = "",
        entry_id: str = "",
        hash_value: str = "",
        algorithm: str = "sha256",
        timestamp: datetime | None = None,
        verified: bool = True,
    ) -> None:
        self.record_id = record_id
        self.entry_id = entry_id
        self.hash_value = hash_value
        self.algorithm = algorithm
        self.timestamp = timestamp
        self.verified = verified


class ProvenanceLight:
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    MINIMAL = "MINIMAL"
    NONE = "NONE"


class LamportClock:
    def __init__(self, initial: int = 0) -> None:
        self._counter = initial

    def tick(self) -> int:
        self._counter += 1
        return self._counter

    def merge(self, other_counter: int) -> int:
        self._counter = max(self._counter, other_counter) + 1
        return self._counter

    @property
    def value(self) -> int:
        return self._counter


class ProvenanceFull:
    def __init__(
        self,
        entry_id: str = "",
        chain: list[Any] | None = None,
        depth: int = 0,
    ) -> None:
        self.entry_id = entry_id
        self.chain = chain or []
        self.depth = depth


class ProvenanceStandard:
    FULL = "FULL"
    STANDARD = "STANDARD"
    LIGHT = "LIGHT"
    MINIMAL = "MINIMAL"


class TaskAuditSummary:
    def __init__(
        self,
        task_id: str = "",
        total_events: int = 0,
        by_type: dict[str, int] | None = None,
        by_actor: dict[str, int] | None = None,
        period: str = "",
    ) -> None:
        self.task_id = task_id
        self.total_events = total_events
        self.by_type = by_type or {}
        self.by_actor = by_actor or {}
        self.period = period


def _generate_entry_id() -> str:
    import uuid

    return str(uuid.uuid4())


def audit_entry_sort_key(entry: Any) -> Any:
    return getattr(entry, "timestamp", None) or 0
