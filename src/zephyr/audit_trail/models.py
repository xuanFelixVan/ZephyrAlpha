# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.models

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.models — MOD-INF-020 · Pydantic V2 全量审计模型
=============================================================
蓝图 §2 · 蓝图 v1.4.0 Phase scaffold 审计数据结构

模型清单
--------
  AuditEventType  — 29+ 种审计事件类型枚举（蓝图 §3.1 对齐）
  ProvenanceDepth — 3 级溯源深度枚举（蓝图 §2.3）
  ProvenanceLight / Standard / Full — 分级 Provenance 模型
  FileActionType  — 文件操作类型枚举
  TaskAuditSummary — 任务级审计摘要（蓝图 §2.1 D-020-01）
  FileAuditDetail  — 文件级审计明细（蓝图 §2.1 D-020-01）
  AuditEntryV1    — v1 核心审计条目（蓝图 §2.4 全字段）
  LamportClock    — Lamport 逻辑时钟（蓝图 §2.5 D-020-09）
  IntegrityReport — 完整性校验报告（蓝图 §4.1）
  AuditChain      — 哈希链快照
  AuditMetrics    — 审计指标聚合
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


class AuditEventType(str, Enum):
    TASK_SUMMARY = "task_summary"
    FILE_DETAIL = "file_detail"
    ANOMALY_DETECTED = "anomaly_detected"
    PERMISSION_VIOLATION = "permission_violation"
    BULK_OPERATION = "bulk_operation"
    GATE_BYPASS = "gate_bypass"
    OFF_HOURS_ACTIVITY = "off_hours_activity"
    DRIFT_DETECTED = "drift_detected"
    INDEX_REBUILD = "index_rebuild"
    LOG_ROTATION = "log_rotation"
    TIER_MIGRATION = "tier_migration"
    INTEGRITY_CHECK = "integrity_check"
    INTEGRITY_FAILURE = "integrity_failure"
    AUDIT_QUERY = "audit_query"
    AUDIT_SYSTEM_HEALTH = "audit_system_health"
    POLICY_FEEDBACK_SENT = "policy_feedback_sent"
    DRY_RUN_AUDIT = "dry_run_audit"
    COLD_START_BOOTSTRAP = "cold_start_bootstrap"
    AGENT_IMPERSONATION = "agent_impersonation"
    DELEGATION_CHAIN_ISSUE = "delegation_chain_issue"
    TRUST_SCORE_CHANGE = "trust_score_change"
    EXTERNAL_TOOL_CALL = "external_tool_call"
    INDIRECT_OPERATION = "indirect_operation"
    SUPPLY_CHAIN_INSTALL = "supply_chain_install"
    LATENT_RISK_DETECTED = "latent_risk_detected"
    COLLUSION_PATTERN = "collusion_pattern"
    DRY_RUN_MISMATCH = "dry_run_mismatch"
    KB_POISONING_ATTEMPT = "kb_poisoning_attempt"
    FEEDBACK_LOOP_SELF_REINFORCING = "feedback_loop_self_reinforcing"
    VOLUME_DOS = "volume_dos"
    CROSS_IDE_CONFLICT = "cross_ide_conflict"
    FILE_WRITE = "file_write"
    FILE_READ = "file_read"
    FILE_DELETE = "file_delete"
    GATE_PASS = "gate_pass"
    GATE_FAIL = "gate_fail"
    HEARTBEAT = "heartbeat"
    RBAC_DECISION = "rbac_decision"
    ROLLBACK_OPERATION = "rollback_operation"
    MCP_TOOL_CALL = "mcp_tool_call"
    SKILL_LOADED = "skill_loaded"
    SKILL_APPLIED = "skill_applied"
    SKILL_DRIFT_DETECTED = "skill_drift_detected"
    A2A_MESSAGE = "a2a_message"
    DRIFT_TAMPER_PROOF_AUDIT = "drift_tamper_proof_audit"
    AI_AUDIT_GUARD = "ai_audit_guard"
    LLM_BEHAVIOR_AUDIT = "llm_behavior_audit"
    SESSION_HANDOFF = "session_handoff"
    SESSION_RECORD = "session_record"
    BUDGET_ENFORCEMENT = "budget_enforcement"
    ROLLBACK_DISCARD = "rollback_discard"
    ROLLBACK_NEXUS = "rollback_nexus"
    DRIFT_HOTFIX_BYPASS = "drift_hotfix_bypass"
    GATE_AUDIT = "gate_audit"
    UNKNOWN = "unknown"


class ProvenanceDepth(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    FULL = "full"


class ProvenanceLevel(str, Enum):
    DIRECT_AGENT = "direct_agent"
    DELEGATED = "delegated"
    INDIRECT = "indirect"
    PEER_TO_PEER = "peer_to_peer"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"
    LEGACY = "legacy"


class ProvenanceLight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    timestamp: str = ""
    action_type: str = ""
    ide_source: str = ""
    decision_brief: str = ""


class ProvenanceStandard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    timestamp: str = ""
    action_type: str = ""
    ide_source: str = ""
    decision_basis: list[str] = Field(default_factory=list)
    guard_checks_executed: list[str] = Field(default_factory=list)
    guard_checks_passed: list[str] = Field(default_factory=list)
    guard_checks_failed: list[str] = Field(default_factory=list)
    guard_result: Optional[str] = None
    confidence_level: str = "high"


class ProvenanceFull(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    timestamp: str = ""
    action_type: str = ""
    ide_source: str = ""
    blocked_reason: str = ""
    attempted_action: str = ""
    rule_violated: str = ""
    escalation_triggered: bool = False
    escalation_target: Optional[str] = None


class FileActionType(str, Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"


class TaskAuditSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str = Field(default="", description="AUD-T-{UUID7}-{SEQ}")
    timestamp: str = ""
    agent_id: str = ""
    ide_source: str = ""
    lamport_counter: int = 0
    session_id: str = ""
    task_id: str = ""
    task_type: str = ""
    action_summary: str = ""
    files_affected: int = 0
    result: str = ""
    permission_level: str = ""
    provenance_depth: ProvenanceDepth = ProvenanceDepth.LIGHT
    tokens_used: Optional[int] = None
    cost_estimate_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    prev_entry_hash: str = ""
    entry_hash: str = ""
    hmac_signature: str = ""


class FileAuditDetail(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str = Field(default="", description="AUD-F-{UUID7}-{SEQ}")
    task_audit_id: str = ""
    timestamp: str = ""
    lamport_counter: int = 0
    file_path: str = ""
    action_type: FileActionType = FileActionType.READ
    sha256_before: Optional[str] = None
    sha256_after: Optional[str] = None
    diff_size_bytes: Optional[int] = None
    prev_entry_hash: str = ""
    entry_hash: str = ""
    hmac_signature: str = ""


class LamportClock(BaseModel):
    model_config = BASE_CONFIG

    ide_source: str = "unknown"
    counter: int = 0

    def tick(self) -> tuple[str, int]:
        self.counter += 1
        return (self.ide_source, self.counter)

    def merge(self, received: tuple[str, int]) -> int:
        self.counter = max(self.counter, received[1]) + 1
        return self.counter

    def now(self) -> tuple[str, int]:
        return (self.ide_source, self.counter)


def audit_entry_sort_key(lamport_clock: tuple[str, int]) -> tuple[int, str]:
    return (lamport_clock[1], lamport_clock[0])


def _generate_entry_id(prefix: str = "AUD-T", seq: int = 0) -> str:
    uuid7_like = uuid4().hex[:20]
    return f"{prefix}-{uuid7_like}-{seq:04d}"


class AuditEntryV1(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    entry_id: str = Field(default_factory=lambda: _generate_entry_id("AUD-T"))
    schema_version: str = "1.1.0"
    event_type: AuditEventType = AuditEventType.UNKNOWN
    prev_entry_hash: str = ""
    entry_hash: str = ""
    hmac_signature: str = ""
    agent_did: Optional[str] = None
    agent_signature: Optional[str] = None
    agent_public_key_pem: Optional[str] = None
    delegation_chain: list[str] = Field(default_factory=list)
    delegation_depth: int = 0
    merkle_batch_id: Optional[str] = None
    lamport_clock_ide: str = "unknown"
    lamport_clock_counter: int = 0
    timestamp: str = ""
    agent_id: str = ""
    ide_source: str = ""
    session_id: str = ""
    task_id: str = ""
    task_type: Optional[str] = None
    permission_level: str = ""
    provenance_depth: str = ""
    trust_score: Optional[float] = None
    action_type: str = ""
    target_path: str = ""
    file_path: Optional[str] = None
    operation: str = ""
    status: str = ""
    sha256_before: Optional[str] = None
    sha256_after: Optional[str] = None
    indirect_operation: bool = False
    indirect_method: Optional[str] = None
    indirect_target: Optional[str] = None
    decision_basis: list[str] = Field(default_factory=list)
    guard_checks_passed: list[str] = Field(default_factory=list)
    guard_checks_failed: list[str] = Field(default_factory=list)
    confidence_level: str = "high"
    reasoning_trace: Optional[str] = None
    cot_hash: Optional[str] = None
    blueprint_expected_action: Optional[str] = None
    drift_detected: bool = False
    drift_severity: Optional[str] = None
    drift_detail: Optional[str] = None
    anomaly_detected: bool = False
    anomaly_type: Optional[str] = None
    anomaly_score: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_estimate_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    dry_run: bool = False
    dry_run_real_diff: Optional[str] = None
    dry_run_real_diff_score: Optional[float] = None
    parent_entry_id: Optional[str] = None
    external_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    supply_chain_info: Optional[dict[str, Any]] = None
    contains_pii: bool = False
    redaction_policy: str = "none"
    retention_tier: str = "hot"
    provenance: ProvenanceLevel = ProvenanceLevel.DIRECT_AGENT
    cost_category: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrityReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    is_valid: bool = True
    total_entries: int = 0
    hash_chain_breaks: list[int] = Field(default_factory=list)
    hmac_failures: list[int] = Field(default_factory=list)
    merkle_mismatches: list[str] = Field(default_factory=list)
    checked_at: str = ""


class AuditChain(BaseModel):
    model_config = BASE_CONFIG

    chain_hash: str = ""
    prev_chain_hash: str = ""
    entry_count: int = 0
    last_lamport: int = 0
    last_entry_id: str = ""
    updated_at: str = ""
    verified: bool = False


class IntegrityRecord(BaseModel):
    model_config = BASE_CONFIG

    record_id: str = ""
    chain_hash: str = ""
    prev_hash: str = ""
    event_count: int = 0
    timestamp: str = ""
    verified: bool = False
    issues: list[str] = Field(default_factory=list)


class AuditMetrics(BaseModel):
    model_config = BASE_CONFIG

    total_entries: int = 0
    write_events: int = 0
    read_events: int = 0
    delete_events: int = 0
    decision_events: int = 0
    session_events: int = 0
    gate_events: int = 0
    failed_integrity_checks: int = 0
    last_event_time: str = ""
    file_size_mb: float = 0.0
