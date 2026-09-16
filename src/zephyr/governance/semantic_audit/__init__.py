# [BLUEPRINT] MOD-INF-024 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-semantic_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/semantic_audit/semantic_audit__init__.yaml
"""

import importlib
import logging

logger = logging.getLogger(__name__)

# 治本（AI-AUDIT12 门面断裂修复）：原 __init__ 仅声明 __all__（65项）而零导入——
# `from zephyr.governance.semantic_audit import KBAuditGate` 必 ImportError，
# hasattr(pkg, "LLMBridge") 恒 False，包级契约名存实亡（实证 2026-08-17）。
# 采用与 gov_audit/__init__.py 同款的 PEP 562 惰性导入（ARCH-036 模式）：
# __getattr__ 首次访问时才 import 子模块，避免包 import 与外层预获取的 module lock
# 冲突导致 _DeadlockError；import * 面与 hasattr 契约同时恢复。
# 映射目标经逐符号实证（2026-08-17 grep 全部定义点）：
# - models 仅含 Severity/SafetyDecision/Trigger*/ExtractedReferences/LLMFixResult/
#   AlignmentReport/HealResult/SemanticAuditReport，其余模型类散布各功能子模块；
# - PackageRecord/AuditPackageResult/IntegrityVerifyResult/SupplyChainAuditor 真源在
#   zephyr.gov_audit.supply_chain（跨包 re-export，与 5 项示例一致）；
# - PIICategory 真源 zephyr.governance.rule_patterns（ARCH-033 Phase 7 合并）。
_LAZY_IMPORTS = {
    "AlignmentEngine": ("zephyr.governance.semantic_audit.alignment_engine", "AlignmentEngine"),
    "AlignmentReport": ("zephyr.governance.semantic_audit.models", "AlignmentReport"),
    "AuditPackageResult": ("zephyr.gov_audit.supply_chain", "AuditPackageResult"),
    "CircularDependencyResult": ("zephyr.governance.semantic_audit.feedback_self_audit", "CircularDependencyResult"),
    "ComplianceFramework": ("zephyr.governance.semantic_audit.compliance_map", "ComplianceFramework"),
    "ComplianceMapper": ("zephyr.governance.semantic_audit.compliance_map", "ComplianceMapper"),
    "ComplianceMapping": ("zephyr.governance.semantic_audit.compliance_map", "ComplianceMapping"),
    "ComplianceRequirement": ("zephyr.governance.semantic_audit.compliance_map", "ComplianceRequirement"),
    "ExtractedReferences": ("zephyr.governance.semantic_audit.models", "ExtractedReferences"),
    "FeedbackNode": ("zephyr.governance.semantic_audit.feedback_self_audit", "FeedbackNode"),
    "FeedbackSelfAuditor": ("zephyr.governance.semantic_audit.feedback_self_audit", "FeedbackSelfAuditor"),
    "FilteredTrigger": ("zephyr.governance.semantic_audit.safety_boundary", "FilteredTrigger"),
    "FixPrioritizer": ("zephyr.governance.semantic_audit.fix_prioritizer", "FixPrioritizer"),
    "HealResult": ("zephyr.governance.semantic_audit.self_healer", "HealResult"),
    "HealthLevel": ("zephyr.governance.semantic_audit.self_health", "HealthLevel"),
    "HealthStatus": ("zephyr.governance.semantic_audit.self_health", "HealthStatus"),
    "IntegrityVerifyResult": ("zephyr.gov_audit.supply_chain", "IntegrityVerifyResult"),
    "IssueAggregator": ("zephyr.governance.semantic_audit.issue_aggregator", "IssueAggregator"),
    "KBAuditGate": ("zephyr.governance.semantic_audit.kb_gate", "KBAuditGate"),
    "KBWriteCheckResult": ("zephyr.governance.semantic_audit.kb_gate", "KBWriteCheckResult"),
    "LLMBridge": ("zephyr.governance.semantic_audit.llm_bridge", "LLMBridge"),
    "LLMFixResult": ("zephyr.governance.semantic_audit.models", "LLMFixResult"),
    "PIICategory": ("zephyr.governance.rule_patterns", "PIICategory"),
    "PIIDetection": ("zephyr.governance.semantic_audit.privacy", "PIIDetection"),
    "PIIScanResult": ("zephyr.governance.semantic_audit.privacy", "PIIScanResult"),
    "PackageRecord": ("zephyr.gov_audit.supply_chain", "PackageRecord"),
    "PoisoningScanResult": ("zephyr.governance.semantic_audit.kb_gate", "PoisoningScanResult"),
    "PrioritizedFix": ("zephyr.governance.semantic_audit.fix_prioritizer", "PrioritizedFix"),
    "PrivacyGuard": ("zephyr.governance.semantic_audit.privacy", "PrivacyGuard"),
    "RedactionPolicy": ("zephyr.governance.semantic_audit.privacy", "RedactionPolicy"),
    "ReferenceExtractor": ("zephyr.governance.semantic_audit.reference_extractor", "ReferenceExtractor"),
    "SLIResult": ("zephyr.governance.semantic_audit.self_health", "SLIResult"),
    "SafetyBoundary": ("zephyr.governance.semantic_audit.safety_boundary", "SafetyBoundary"),
    "SafetyDecision": ("zephyr.governance.semantic_audit.models", "SafetyDecision"),
    "SelfHealError": ("zephyr.governance.semantic_audit.self_healer", "SelfHealError"),
    "SelfHealer": ("zephyr.governance.semantic_audit.self_healer", "SelfHealer"),
    "SelfHealth": ("zephyr.governance.semantic_audit.self_health", "SelfHealth"),
    "SelfReinforcementResult": ("zephyr.governance.semantic_audit.feedback_self_audit", "SelfReinforcementResult"),
    "SemanticAuditReport": ("zephyr.governance.semantic_audit.models", "SemanticAuditReport"),
    "Severity": ("zephyr.governance.semantic_audit.models", "Severity"),
    "SupplyChainAuditor": ("zephyr.gov_audit.supply_chain", "SupplyChainAuditor"),
    "TriggerDecision": ("zephyr.governance.semantic_audit.models", "TriggerDecision"),
    "TriggerEngine": ("zephyr.governance.semantic_audit.trigger_engine", "TriggerEngine"),
    "TriggerResult": ("zephyr.governance.semantic_audit.models", "TriggerResult"),
    "hash_path": ("zephyr.governance.semantic_audit.privacy", "hash_path"),
    "record_agent_spec": ("zephyr.governance.semantic_audit.spec_auditor", "record_agent_spec"),
}


def __getattr__(name):
    # 1. 类名/函数名/模块级对象惰性导入
    entry = _LAZY_IMPORTS.get(name)
    if entry is not None:
        module_path, attr = entry
        mod = importlib.import_module(module_path)
        val = getattr(mod, attr)
        globals()[name] = val  # 缓存到模块全局，后续直接命中
        return val
    # 2. 尝试作为子模块导入（__all__ 里的子模块名: models, kb_gate, privacy 等）
    try:
        mod = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = mod
        return mod
    except ModuleNotFoundError:
        pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AlignmentEngine",
    "AlignmentReport",
    "AuditPackageResult",
    "CircularDependencyResult",
    "ComplianceFramework",
    "ComplianceMapper",
    "ComplianceMapping",
    "ComplianceRequirement",
    "ExtractedReferences",
    "FeedbackNode",
    "FeedbackSelfAuditor",
    "FilteredTrigger",
    "FixPrioritizer",
    "HealResult",
    "HealthLevel",
    "HealthStatus",
    "IntegrityVerifyResult",
    "IssueAggregator",
    "KBAuditGate",
    "KBWriteCheckResult",
    "LLMBridge",
    "LLMFixResult",
    "PIICategory",
    "PIIDetection",
    "PIIScanResult",
    "PackageRecord",
    "PoisoningScanResult",
    "PrioritizedFix",
    "PrivacyGuard",
    "RedactionPolicy",
    "ReferenceExtractor",
    "SLIResult",
    "SafetyBoundary",
    "SafetyDecision",
    "SelfHealError",
    "SelfHealer",
    "SelfHealth",
    "SelfReinforcementResult",
    "SemanticAuditReport",
    "Severity",
    "SupplyChainAuditor",
    "TriggerDecision",
    "TriggerEngine",
    "TriggerResult",
    "alignment_engine",
    "compliance_map",
    "feedback_self_audit",
    "fix_prioritizer",
    "fix_result_prioritizer",
    "hash_path",
    "issue_aggregator",
    "kb_gate",
    "llm_bridge",
    "logger",
    "models",
    "orchestrator",
    "privacy",
    "record_agent_spec",
    "reference_extractor",
    "safety_boundary",
    "semantic_cache",
    "self_healer",
    "self_health",
    "spec_auditor",
    "trigger_engine",
]
