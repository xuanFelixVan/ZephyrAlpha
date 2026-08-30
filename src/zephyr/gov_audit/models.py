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
# [TESTS] tests/audit/test_audit_models.py; tests/audit/test_audit_core.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 治本（裁定#18 G2）：本文件原为桩实现——AuditEventType/FileActionType/ProvenanceDepth/
# ProvenanceLevel 用类常量模拟枚举（非 Enum，value 大写），ProvenanceLight/Standard/
# AuditEntryV1/TaskAuditSummary/FileAuditDetail 是可变普通类，LamportClock 接口与测试
# 契约不符（不接受 ide_source/counter，tick/now 不返回元组），_generate_entry_id 不接受
# 位置参数，IntegrityReport 用 valid 字段而非 is_valid。现按 tests/audit/ 契约重写为
# Enum + frozen dataclass，values 全部小写对齐 compliance_map.py 测试期望。
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: entry 参数
#   fields: 参数 entry，类型注解 tuple[str, int] | object
#   code: models.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LamportClock
#   name_en: LamportClock
#   intro: Lamport 逻辑时钟——治本（ G2）：对齐测试契约。
#   desc: Lamport 逻辑时钟——治本（ G2）：对齐测试契约。 旧实现仅接受 initial:int，tick() 返回 int，无 ide_source。现对齐契约： - Lamp…；公共方法（定义序）: tick, m…
#   inputs: ide_source counter
#   outputs: 返回值
# - id: A2
#   name_zh: ② IntegrityReport
#   name_en: IntegrityReport
#   intro: 完整性报告——治本（ G2）：frozen dataclass。
#   desc: 完整性报告——治本（ G2）：frozen dataclass。 对齐 test_audit_models.py / test_audit_core.py / test_quer…；公共方法（定义序）: valid,…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ AuditChain
#   name_en: AuditChain
#   intro: 审计哈希链——治本（ G2）：dataclass 接受 chain_hash/entry_count 构造。
#   desc: 审计哈希链——治本（ G2）：dataclass 接受 chain_hash/entry_count 构造。 对齐 test_audit_models.py 契约：AuditCh…；公共方法（定义序）: add_ent…
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ audit_entry_sort_key
#   name_en: audit_entry_sort_key
#   intro: 审计条目排序键——治本（ G2）：接受 (ide, counter) 元组。
#   desc: 审计条目排序键——治本（ G2）：接受 (ide, counter) 元组。 对齐 test_audit_models.py 契约： audit_entry_sort_key((…；源码 L541-L551
#   inputs: entry
#   outputs: tuple[str, int] | int
#   （注：A4 之后另有 22 个公共定义未列入（含 22 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[str, int] | int
#   name_en: tuple[str, int] | int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: audit-orchestrator.*; gates; pipeline
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "AuditChain",
    "AuditContext",
    "AuditEntryV1",
    "AuditEventType",
    "AuditIssue",
    "AuditMetrics",
    "AuditType",
    "ChangedFile",
    "DiscoveryReport",
    "FileActionType",
    "FileAuditDetail",
    "FixLevel",
    "GlobalAuditReport",
    "IntegrityRecord",
    "IntegrityReport",
    "LamportClock",
    "OrchestratorStatus",
    "Priority",
    "ProvenanceDepth",
    "ProvenanceFull",
    "ProvenanceLevel",
    "ProvenanceLight",
    "ProvenanceStandard",
    "Severity",
    "TaskAuditSummary",
    "audit_entry_sort_key",
]


# ---------------------------------------------------------------------------
# 原 pydantic 模型（audit-orchestrator 流程使用，保持不变）
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 治本（裁定#18 G2）：对齐 tests/audit/ 契约的枚举与不可变数据类
# ---------------------------------------------------------------------------


class AuditEventType(str, Enum):
    """审计事件类型枚举——治本（裁定#18 G2）：转为真 Enum，values 全部小写。

    对齐 test_audit_models.py / test_audit_core.py / test_compliance_map.py 契约：
    FILE_WRITE.value == "file_write"（小写），compliance_map.py 用 .value 作为 dict key。
    writer.py 的 _KNOWN_EVENT_TYPES 白名单通过 .value.lower() 生成，小写值兼容。
    """

    UNKNOWN = "unknown"
    HEARTBEAT = "heartbeat"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    EXECUTE = "execute"
    DELEGATE = "delegate"
    ESCALATE = "escalate"
    ROLLBACK = "rollback"
    MIGRATE = "migrate"
    COMPLIANCE_CHECK = "compliance_check"
    PERMISSION_VIOLATION = "permission_violation"
    FILE_CREATE = "file_create"
    FILE_READ = "file_read"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"
    FILE_MOVE = "file_move"
    FILE_WRITE = "file_write"
    FILE_RENAME = "file_rename"
    PERMISSION_CHANGE = "permission_change"
    ANOMALY_DETECTED = "anomaly_detected"
    DRIFT_DETECTED = "drift_detected"
    COMPLIANCE_VIOLATION = "compliance_violation"
    TRUST_SCORE_CHANGE = "trust_score_change"
    CONFIGURATION_CHANGE = "configuration_change"
    SYSTEM_EVENT = "system_event"
    IMPORT = "import"
    KB_POISONING_ATTEMPT = "kb_poisoning_attempt"
    SECURITY_SCAN = "security_scan"
    POLICY_CHANGE = "policy_change"
    SUPPLY_CHAIN_INSTALL = "supply_chain_install"
    DEPENDENCY_UPDATE = "dependency_update"
    RESOURCE_ALLOCATION = "resource_allocation"
    DELEGATION_CHAIN_ISSUE = "delegation_chain_issue"
    AUDIT_ANOMALY = "audit_anomaly"
    RETENTION_EXPIRY = "retention_expiry"
    FEEDBACK_LOOP_SELF_REINFORCING = "feedback_loop_self_reinforcing"
    METRIC_THRESHOLD_BREACH = "metric_threshold_breach"
    CAPACITY_WARNING = "capacity_warning"
    EXPORT = "export"
    RESTORE = "restore"
    BACKUP = "backup"
    HEALTH_CHECK = "health_check"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_STARTUP = "system_startup"
    # 运行时桥接/红蓝验证/异常检测使用的事件类型（对齐 test_anomaly.py 等契约）
    GATE_FAIL = "gate_fail"
    GATE_BYPASS = "gate_bypass"
    AGENT_IMPERSONATION = "agent_impersonation"
    COLLUSION_PATTERN = "collusion_pattern"
    INDIRECT_OPERATION = "indirect_operation"
    DRY_RUN_MISMATCH = "dry_run_mismatch"


class FileActionType(str, Enum):
    """文件操作类型枚举——治本（裁定#18 G2）：values 小写对齐测试契约。"""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    MODIFY = "modify"
    RENAME = "rename"
    MOVE = "move"


class ProvenanceDepth(str, Enum):
    """溯源深度枚举——治本（裁定#18 G2）：values 小写对齐测试契约。"""

    LIGHT = "light"
    STANDARD = "standard"
    FULL = "full"


class ProvenanceLevel(str, Enum):
    """溯源层级枚举——治本（裁定#18 G2）：DIRECT_AGENT/DELEGATED/INDIRECT。"""

    DIRECT_AGENT = "direct_agent"
    DELEGATED = "delegated"
    INDIRECT = "indirect"


@dataclass(frozen=True)
class ProvenanceLight:
    """轻量溯源——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py 契约：ProvenanceLight(agent_id, timestamp, action_type)
    + 默认 ide_source=""。
    """

    agent_id: str = ""
    timestamp: str = ""
    action_type: str = ""
    ide_source: str = ""


@dataclass(frozen=True)
class ProvenanceStandard:
    """标准溯源——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py 契约：ProvenanceStandard(agent_id, timestamp,
    decision_basis, guard_checks_passed, guard_checks_failed)。
    """

    agent_id: str = ""
    timestamp: str = ""
    decision_basis: list[str] = field(default_factory=list)
    guard_checks_passed: list[str] = field(default_factory=list)
    guard_checks_failed: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProvenanceFull:
    """完整溯源——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py 契约：ProvenanceFull(agent_id, blocked_reason,
    escalation_triggered)。
    """

    agent_id: str = ""
    blocked_reason: str = ""
    escalation_triggered: bool = False


class LamportClock:
    """Lamport 逻辑时钟——治本（裁定#18 G2）：对齐测试契约。

    旧实现仅接受 initial:int，tick() 返回 int，无 ide_source。现对齐契约：
    - LamportClock(ide_source="ide-1", counter=0) 构造
    - tick() 返回 (ide_source, counter) 元组，counter 自增
    - merge((ide, counter)) 接受元组，返回 max(local, other)+1 的 int
    - now() 返回 (ide_source, counter) 元组，不自增
    """

    def __init__(self, ide_source: str = "", counter: int = 0) -> None:
        self._ide_source = ide_source
        self._counter = counter

    def tick(self) -> tuple[str, int]:
        self._counter += 1
        return (self._ide_source, self._counter)

    def merge(self, other: tuple[str, int] | int) -> int:
        if isinstance(other, tuple):
            _other_ide, other_counter = other
        else:
            other_counter = int(other)
        self._counter = max(self._counter, other_counter) + 1
        return self._counter

    def now(self) -> tuple[str, int]:
        return (self._ide_source, self._counter)

    @property
    def value(self) -> int:
        """向后兼容：返回当前 counter（旧 API）。"""
        return self._counter


@dataclass(frozen=True)
class AuditEntryV1:
    """审计条目 V1——治本（裁定#18 G2）：frozen dataclass 对齐测试契约。

    对齐 test_audit_models.py / test_audit_core.py / test_verdict_engine.py 契约：
    - 默认 schema_version="1.1.0", event_type=AuditEventType.UNKNOWN,
      provenance=ProvenanceLevel.DIRECT_AGENT, dry_run=False
    - 支持 agent_id/target_path/session_id/operation/status
    - 支持 verdict_engine 使用的 permission_level/indirect_operation/
      guard_checks_passed/trust_score 字段
    - frozen：赋值抛 FrozenInstanceError
    """

    schema_version: str = "1.1.0"
    event_type: AuditEventType = AuditEventType.UNKNOWN
    provenance: ProvenanceLevel = ProvenanceLevel.DIRECT_AGENT
    dry_run: bool = False
    agent_id: str = ""
    target_path: str = ""
    session_id: str = ""
    operation: str = ""
    status: str = ""
    entry_id: str = ""
    timestamp: str = ""
    permission_level: str = ""
    indirect_operation: bool = False
    guard_checks_passed: list[str] = field(default_factory=list)
    trust_score: float | None = None


@dataclass(frozen=True)
class TaskAuditSummary:
    """任务审计摘要——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py 契约：TaskAuditSummary(event_id, agent_id, task_id)
    + 默认 provenance_depth=ProvenanceDepth.LIGHT。
    """

    event_id: str = ""
    agent_id: str = ""
    task_id: str = ""
    provenance_depth: ProvenanceDepth = ProvenanceDepth.LIGHT


@dataclass(frozen=True)
class FileAuditDetail:
    """文件审计详情——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py 契约：FileAuditDetail(event_id, file_path, action_type)。
    """

    event_id: str = ""
    file_path: str = ""
    action_type: FileActionType = FileActionType.READ


@dataclass(frozen=True)
class IntegrityReport:
    """完整性报告——治本（裁定#18 G2）：frozen dataclass。

    对齐 test_audit_models.py / test_audit_core.py / test_query.py 契约：
    - is_valid（非 valid）/ total_entries / hash_chain_breaks
    - test_query.py 使用的 hmac_failures / merkle_mismatches / checked_at
    """

    is_valid: bool = True
    total_entries: int = 0
    hash_chain_breaks: list[Any] = field(default_factory=list)
    hmac_failures: list[Any] = field(default_factory=list)
    merkle_mismatches: list[Any] = field(default_factory=list)
    checked_at: str = ""

    @property
    def valid(self) -> bool:
        """向后兼容别名：旧代码读 .valid。"""
        return self.is_valid

    @property
    def entry_count(self) -> int:
        """向后兼容别名：旧代码读 .entry_count。"""
        return self.total_entries


@dataclass
class AuditChain:
    """审计哈希链——治本（裁定#18 G2）：dataclass 接受 chain_hash/entry_count 构造。

    对齐 test_audit_models.py 契约：AuditChain(chain_hash="abc", entry_count=5)。
    保留旧 add_entry/verify API 以向后兼容。
    """

    chain_hash: str = ""
    entry_count: int = 0
    entries: list[Any] = field(default_factory=list)

    def add_entry(self, entry: object) -> None:
        self.entries.append(entry)
        self.entry_count = len(self.entries)

    def verify(self) -> bool:
        """基础一致性校验——5.37.2 治本：原实现永返 True（stub，名实分离）。

        RULE-THREE 评估结论：全项目无生产调用方（仅 tests/audit/test_audit_models.py
        构造本类，从不调用 verify()），故不实现完整 hash 链校验，降级为 deprecated
        入口 + 诚实的一致性检查（entry_count 与实际加载的 entries 长度一致）。

        真实 hash 链校验请使用：
        - zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier.AuditChainVerifier.verify_chain()
        - zephyr.gov_audit.integrity（MerkleAggregator）
        """
        warnings.warn(
            "AuditChain.verify() 已废弃（仅做 entry_count 一致性检查，非 hash 链校验）；"
            "真实校验请用 AuditChainVerifier.verify_chain()",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.entry_count == len(self.entries)


@dataclass(frozen=True)
class IntegrityRecord:
    """完整性记录——治本（裁定#18 G2）：frozen dataclass 接受 record_id/chain_hash。

    对齐 test_audit_models.py 契约：IntegrityRecord(record_id="R1", chain_hash="abc")。
    """

    record_id: str = ""
    chain_hash: str = ""
    entry_id: str = ""
    hash_value: str = ""
    algorithm: str = "sha256"
    timestamp: str = ""
    verified: bool = True


@dataclass
class AuditMetrics:
    """审计指标——治本（裁定#18 G2）：dataclass 对齐测试契约。

    对齐 test_audit_models.py / test_audit_core.py 契约：
    AuditMetrics() → total_entries=0, write_events=0。
    保留旧 by_type/by_actor/period 字段向后兼容。
    """

    total_entries: int = 0
    write_events: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_actor: dict[str, int] = field(default_factory=dict)
    period: str = ""


def _generate_entry_id(prefix: str = "AUD-T", seq: int = 0) -> str:
    """生成审计条目 ID——治本（裁定#18 G2）：接受 2 个位置参数。

    对齐 test_audit_models.py 契约：
    - _generate_entry_id("AUD-T", 0) → 以 "AUD-T-" 开头，以 "-0000" 结尾
    - _generate_entry_id("AUD-F", 5) → 以 "-0005" 结尾

    格式：{prefix}-{seq:04d}。注意：writer.py 有自己的 _generate_entry_id（含
    timestamp+uuid），与此处独立——此处仅服务 tests/audit/ 契约与 _orchestrator_compat
    再导出。
    """
    return f"{prefix}-{seq:04d}"


def audit_entry_sort_key(entry: tuple[str, int] | object) -> tuple[str, int] | int:
    """审计条目排序键——治本（裁定#18 G2）：接受 (ide, counter) 元组。

    对齐 test_audit_models.py 契约：
    audit_entry_sort_key(("ide-1", 1)) < audit_entry_sort_key(("ide-1", 2))。
    元组按 (ide, counter) 字典序比较，counter 升序即可。
    保留对旧 entry 对象（含 timestamp 属性）的兼容。
    """
    if isinstance(entry, tuple):
        return entry
    return getattr(entry, "timestamp", None) or 0
