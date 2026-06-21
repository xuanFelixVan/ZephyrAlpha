# [A_module] module_id=MOD-GOV_audit_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [INVARIANTS] 所有审计模块健康检查通过才允许操作; AdmissionResult为唯一准入判定结果
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-orchestrator/__init__.py __all__
# [CONSUMERS] gates; orchestrator; pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdmissionResult.allowed=False on any check failure
# [TESTS] tests/audit-orchestrator/

from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController, AdmissionResult
from zephyr.governance.audit_trail.resource_aware_pool import ResourceAwarePool, PoolStats
from zephyr.governance.audit_trail.cli import main as cli_main
from zephyr.governance.audit_trail.pipeline_runner import PipelineRunner, PipelineResult, DimensionResult, ScriptResult
from zephyr.governance.audit_orchestrator.text_to_finding_adapter import TextToFindingAdapter
from zephyr.governance.audit_trail.models import (
    AuditType,
    Severity,
    Priority,
    FixLevel,
    DiscoveryReport,
    ChangedFile,
    AuditIssue,
    GlobalAuditReport,
    OrchestratorStatus,
    AuditContext,
)
from zephyr.governance.audit_trail.contracts import (
    AuditDiscoverer,
    AuditIndexer as AuditIndexerContract,
    AuditWriter as AuditWriterContract,
    AuditQuery as AuditQueryContract,
    IntegrityChecker,
    ContractViolationError,
)
from zephyr.governance.audit_trail.bridge import OrchestratorBridge
from zephyr.governance.audit_trail.writer import AuditReportWriter
from zephyr.governance.audit_trail.query import AuditQueryEngine
from zephyr.governance.audit_trail.indexer import AuditIndexer
from zephyr.governance.audit_trail.cold_start import BootstrapCache
from zephyr.governance.audit_orchestrator.integrity import IntegrityGuard
from zephyr.governance.audit_trail.trust_engine import TrustEngine, TrustLevel
from zephyr.governance.audit_trail.trust_bridge import TrustBridge
from zephyr.governance.audit_orchestrator.merkle_hourly import MerkleHourlyBridge
from zephyr.governance.audit_orchestrator.evidence_pack import EvidencePack
from zephyr.governance.audit_trail.delegation_bridge import DelegationBridge
from zephyr.governance.audit_trail.delegation_auditor import DelegationAuditor
from zephyr.governance.audit_trail.drift_bridge import DriftBridge
from zephyr.governance.audit_trail.feedback_bridge import FeedbackBridge
from zephyr.governance.audit_trail.feedback_policy import FeedbackPolicy, PolicyDecision
from zephyr.governance.audit_trail.tiered_storage import TieredStorage
from zephyr.governance.audit_trail.tiered_storage_bridge import TieredStorageBridge
from zephyr.governance.audit_trail.log_rotation import LogRotation
from zephyr.governance.audit_trail.retention import RetentionPolicy
from zephyr.governance.audit_trail.self_monitor import SelfMonitor
from zephyr.governance.audit_trail.anomaly import AnomalyDetector
from zephyr.governance.audit_trail.external_tool_audit import ExternalToolAuditor
from zephyr.governance.audit_trail.genesis import GenesisBlock
from zephyr.governance.audit_trail.replay_engine import ReplayEngine

__all__ = [
    "AuditAdmissionController",
    "AdmissionResult",
    "ResourceAwarePool",
    "PoolStats",
    "cli_main",
    "PipelineRunner",
    "PipelineResult",
    "DimensionResult",
    "ScriptResult",
    "TextToFindingAdapter",
    "AuditType",
    "Severity",
    "Priority",
    "FixLevel",
    "DiscoveryReport",
    "ChangedFile",
    "AuditIssue",
    "GlobalAuditReport",
    "OrchestratorStatus",
    "AuditContext",
    "AuditDiscoverer",
    "AuditIndexerContract",
    "AuditWriterContract",
    "AuditQueryContract",
    "IntegrityChecker",
    "ContractViolationError",
    "OrchestratorBridge",
    "AuditReportWriter",
    "AuditQueryEngine",
    "AuditIndexer",
    "BootstrapCache",
    "IntegrityGuard",
    "TrustEngine",
    "TrustLevel",
    "TrustBridge",
    "MerkleHourlyBridge",
    "EvidencePack",
    "DelegationBridge",
    "DelegationAuditor",
    "DriftBridge",
    "FeedbackBridge",
    "FeedbackPolicy",
    "PolicyDecision",
    "TieredStorage",
    "TieredStorageBridge",
    "LogRotation",
    "RetentionPolicy",
    "SelfMonitor",
    "AnomalyDetector",
    "ExternalToolAuditor",
    "GenesisBlock",
    "ReplayEngine",
    "anomaly",
    "bridge",
    "cli",
    "cold_start",
    "contracts",
    "external_tool_audit",
    "genesis",
    "indexer",
    "integrity",
    "merkle_hourly",
    "models",
    "query",
    "retention",
    "writer",
    "__main__",
    "audit_admission_controller",
    "delegation_auditor",
    "delegation_bridge",
    "drift_bridge",
    "evidence_pack",
    "feedback_bridge",
    "feedback_policy",
    "log_rotation",
    "pipeline_runner",
    "replay_engine",
    "resource_aware_pool",
    "self_monitor",
    "text_to_finding_adapter",
    "tiered_storage",
    "tiered_storage_bridge",
    "trust_bridge",
    "trust_engine",
]
