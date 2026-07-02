# [A_module] module_id=MOD-GOV_audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [INVARIANTS] 所有审计模块健康检查通过才允许操作; AdmissionResult为唯一准入判定结果
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-orchestrator/__init__.py __all__
# [CONSUMERS] gates; orchestrator; pipeline
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdmissionResult.allowed=False on any check failure
# [TESTS] tests/audit-orchestrator/
# [TTL] task_bound

from zephyr.governance.audit_trail.anomaly import AnomalyDetector
from zephyr.governance.audit_trail.bridge import OrchestratorBridge
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

# STUB: from zephyr.governance.audit_trail.cli import main as cli_main
# Reason: lazy import to break circular import with audit_trail.cli → audit_admission_controller → __init__
# STUB: from zephyr.governance.audit_trail.audit_admission_controller import AuditAdmissionController, AdmissionResult
# Reason: lazy import to break circular import with audit_admission_controller → finding_model → __init__
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
from zephyr.governance.evidence_pack import EvidencePack  # ARCH-031: EvidencePack canonical 在根目录 governance/evidence_pack.py
from zephyr.governance.integrity import IntegrityGuard  # ARCH-031: IntegrityGuard canonical 在根目录 governance/integrity.py
from zephyr.governance.merkle_hourly import MerkleHourlyBridge  # ARCH-031: MerkleHourlyBridge canonical 在根目录


def __getattr__(name):
    if name == "TextToFindingAdapter":
        from zephyr.governance.audit_trail.text_to_finding_adapter import TextToFindingAdapter

        return TextToFindingAdapter
    if name in ("PipelineRunner", "PipelineResult", "DimensionResult", "ScriptResult"):
        from zephyr.governance.audit_trail.pipeline_runner import (
            DimensionResult,
            PipelineResult,
            PipelineRunner,
            ScriptResult,
        )

        return {
            "PipelineRunner": PipelineRunner,
            "PipelineResult": PipelineResult,
            "DimensionResult": DimensionResult,
            "ScriptResult": ScriptResult,
        }[name]
    if name in ("AuditAdmissionController", "AdmissionResult"):
        from zephyr.governance.audit_trail.audit_admission_controller import AdmissionResult, AuditAdmissionController

        return {"AuditAdmissionController": AuditAdmissionController, "AdmissionResult": AdmissionResult}[name]
    if name == "cli_main":
        from zephyr.governance.audit_trail.cli import main as cli_main

        return cli_main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    "agent_signer",
    "anomaly",
    "api_lifecycle",
    "audit_admission_controller",
    "bridge",
    "changelog_manager",
    "cli",
    "cli_main",
    "code_archaeology",
    "cold_start",
    "compliance_map",
    "contracts",
    "corporate_actions",
    "delegation_auditor",
    "delegation_bridge",
    "dora_metrics",
    "drift_bridge",
    "evidence_pack",
    "external_tool_audit",
    "feedback_bridge",
    "feedback_policy",
    "feedback_self_audit",
    "finding_model",
    "genesis",
    "glossary_matrix",
    "incremental_review",
    "indexer",
    "integrity",
    "kb_gate",
    "log_rotation",
    "merkle_hourly",
    "models",
    "observability_dashboard",
    "orchestrator",
    "pipeline_runner",
    "privacy",
    "provenance_tracker",
    "query",
    "replay_engine",
    "resource_aware_pool",
    "retention",
    "sbom_generator",
    "self_monitor",
    "spec_auditor",
    "supply_chain",
    "supply_chain_security",
    "tiered_storage",
    "tiered_storage_bridge",
    "trust_bridge",
    "trust_engine",
    "wqa_scorer",
    "writer",
'action_history', 'audit_schema', 'audit_write_failure_protector', 'event_store', 'finding_ingest', 'forensic_package', 'integrity_verifier', 'merkle_audit', 'trust_ring_manager']
