# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TESTS] tests/governance/test_intelligence_governance_facade.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 1 个测试）
# [TTL] permanent
# [A_module] module_id=MOD-GOV-intelligence_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/intelligence_governance/intelligence_governance__init__.yaml
"""

from __future__ import annotations

_SYMBOL_TO_MODULE: dict[str, str] = {
    # agent_debate
    "AgentDebate": "agent_debate",
    "DebateVerdict": "agent_debate",
    "ModelResponse": "agent_debate",
    # ai_self_diagnosis
    "AutoFixLayer": "ai_self_diagnosis",
    "auto_fix_known_pattern": "ai_self_diagnosis",
    # multi_model_consensus
    "ConsensusProtocol": "multi_model_consensus",
    "escalate_to_owner": "multi_model_consensus",
    # aisg_sandbox
    "AISGSandbox": "aisg_sandbox",
    "SandboxResult": "aisg_sandbox",
    # confidence_estimator
    "ConfidenceEstimator": "confidence_estimator",
    "ConfidenceLevel": "confidence_estimator",
    # confidence_quantifier
    "ConfidenceQuantifier": "confidence_quantifier",
    "ConfidenceResult": "confidence_quantifier",
    # continuous_trust
    "ContinuousTrust": "continuous_trust",
    "TrustScore": "continuous_trust",
    # cross_agent_conflict_detector
    "CrossAgentConflictDetector": "cross_agent_conflict_detector",
    "ConflictReport": "cross_agent_conflict_detector",
    # cross_assistant_adapter
    "CrossAssistantAdapter": "cross_assistant_adapter",
    # delegation_engine
    "DelegationEngine": "delegation_engine",
    # delegation_manager
    "DelegationManager": "delegation_manager",
    "DelegateResult": "delegation_manager",
    # memory_provider
    "MemoryProvider": "memory_provider",
    # meta_confidence
    "MetaConfidence": "meta_confidence",
    # model_router
    "ModelRouter": "model_router",
    "TaskComplexity": "model_router",
    "RoutingDecision": "model_router",
    # model_version_detector
    "ModelVersionDetector": "model_version_detector",
    # mvep_orchestrator
    "MVEPOrchestrator": "mvep_orchestrator",
    # provider_base
    "QuoteProviderBase": "provider_base",
    "QuoteProviderMeta": "provider_base",
    # provider_failover
    "ProviderFailover": "provider_failover",
    # self_benchmark
    "SelfBenchmark": "self_benchmark",
    "KnownAnswerTest": "self_benchmark",
    "BenchmarkResult": "self_benchmark",
    # self_test
    "HealthLevel": "self_test",
    "CheckResult": "self_test",
    "SelfTestReport": "self_test",
    "run_self_test": "self_test",
    # self_validator
    "SelfValidator": "self_validator",
    # subagent_hook_propagator
    "SubagentHookPropagator": "subagent_hook_propagator",
    # autonomy_dashboard
    "AutonomyDashboard": "autonomy_dashboard",
    "AutonomyMetrics": "autonomy_dashboard",
}

__all__ = sorted(_SYMBOL_TO_MODULE)


def __getattr__(name: str):
    """PEP 562 惰性外观：按需 import 子模块再取符号，包级 import 零 eager 子模块加载。"""
    module_name = _SYMBOL_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    module = importlib.import_module(f"{__name__}.{module_name}")
    return getattr(module, name)
