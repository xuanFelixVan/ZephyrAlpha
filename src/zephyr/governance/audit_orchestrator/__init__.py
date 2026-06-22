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

from zephyr.governance.audit_orchestrator.evidence_pack import EvidencePack
from zephyr.governance.audit_orchestrator.integrity import IntegrityGuard
from zephyr.governance.audit_orchestrator.merkle_hourly import MerkleHourlyBridge
from zephyr.governance.audit_orchestrator.text_to_finding_adapter import TextToFindingAdapter
from zephyr.governance.audit_trail.anomaly import AnomalyDetector
from zephyr.governance.audit_trail.audit_admission_controller import AdmissionResult, AuditAdmissionController
from zephyr.governance.audit_trail.bridge import OrchestratorBridge
from zephyr.governance.audit_trail.cli import main as cli_main
from zephyr.governance.audit_trail.cold_start import BootstrapCache
from zephyr.governance.audit_trail.contracts import (
    AuditDiscoverer,
    ContractViolationError,
    IntegrityChecker,
)
from zephyr.governance.audit_trail.contracts import (
    AuditIndexer as AuditIndexerContract,
)
from zephyr.governance.audit_trail.contracts import (
    AuditQuery as AuditQueryContract,
)
from zephyr.governance.audit_trail.contracts import (
    AuditWriter as AuditWriterContract,
)
from zephyr.governance.audit_trail.delegation_auditor import DelegationAuditor
from zephyr.governance.audit_trail.delegation_bridge import DelegationBridge
from zephyr.governance.audit_trail.drift_bridge import DriftBridge
from zephyr.governance.audit_trail.external_tool_audit import ExternalToolAuditor
from zephyr.governance.audit_trail.feedback_bridge import FeedbackBridge
from zephyr.governance.audit_trail.feedback_policy import FeedbackPolicy, PolicyDecision
from zephyr.governance.audit_trail.genesis import GenesisBlock
from zephyr.governance.audit_trail.indexer import AuditIndexer
from zephyr.governance.audit_trail.log_rotation import LogRotation
from zephyr.governance.audit_trail.models import (
    AuditContext,
    AuditIssue,
    AuditType,
    ChangedFile,
    DiscoveryReport,
    FixLevel,
    GlobalAuditReport,
    OrchestratorStatus,
    Priority,
    Severity,
)
from zephyr.governance.audit_trail.pipeline_runner import DimensionResult, PipelineResult, PipelineRunner, ScriptResult
from zephyr.governance.audit_trail.query import AuditQueryEngine
from zephyr.governance.audit_trail.replay_engine import ReplayEngine
from zephyr.governance.audit_trail.resource_aware_pool import PoolStats, ResourceAwarePool
from zephyr.governance.audit_trail.retention import RetentionPolicy
from zephyr.governance.audit_trail.self_monitor import SelfMonitor
from zephyr.governance.audit_trail.tiered_storage import TieredStorage
from zephyr.governance.audit_trail.tiered_storage_bridge import TieredStorageBridge
from zephyr.governance.audit_trail.trust_bridge import TrustBridge
from zephyr.governance.audit_trail.trust_engine import TrustEngine, TrustLevel
from zephyr.governance.audit_trail.writer import AuditReportWriter

__all__ = [
    "AdmissionResult",
    "AnomalyDetector",
    "AuditAdmissionController",
    "AuditContext",
    "AuditDiscoverer",
    "AuditIndexer",
    "AuditIndexerContract",
    "AuditIssue",
    "AuditQueryContract",
    "AuditQueryEngine",
    "AuditReportWriter",
    "AuditType",
    "AuditWriterContract",
    "BootstrapCache",
    "ChangedFile",
    "ContractViolationError",
    "DelegationAuditor",
    "DelegationBridge",
    "DimensionResult",
    "DiscoveryReport",
    "DriftBridge",
    "EvidencePack",
    "ExternalToolAuditor",
    "FeedbackBridge",
    "FeedbackPolicy",
    "FixLevel",
    "GenesisBlock",
    "GlobalAuditReport",
    "IntegrityChecker",
    "IntegrityGuard",
    "LogRotation",
    "MerkleHourlyBridge",
    "OrchestratorBridge",
    "OrchestratorStatus",
    "PipelineResult",
    "PipelineRunner",
    "PolicyDecision",
    "PoolStats",
    "Priority",
    "ReplayEngine",
    "ResourceAwarePool",
    "RetentionPolicy",
    "ScriptResult",
    "SelfMonitor",
    "Severity",
    "TextToFindingAdapter",
    "TieredStorage",
    "TieredStorageBridge",
    "TrustBridge",
    "TrustEngine",
    "TrustLevel",
    "__main__",
    "anomaly",
    "audit_admission_controller",
    "bridge",
    "cli",
    "cli_main",
    "cold_start",
    "contracts",
    "delegation_auditor",
    "delegation_bridge",
    "drift_bridge",
    "evidence_pack",
    "external_tool_audit",
    "feedback_bridge",
    "feedback_policy",
    "genesis",
    "indexer",
    "integrity",
    "log_rotation",
    "merkle_hourly",
    "models",
    "pipeline_runner",
    "query",
    "replay_engine",
    "resource_aware_pool",
    "retention",
    "self_monitor",
    "text_to_finding_adapter",
    "tiered_storage",
    "tiered_storage_bridge",
    "trust_bridge",
    "trust_engine",
    "writer",
]
