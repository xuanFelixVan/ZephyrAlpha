# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-intelligence_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入/属性访问请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.intelligence_governance；pkg.<Symbol> 触发 PEP 562 __getattr__
# 层: 算法
# - id: A1
#   name_zh: ① 惰性外观（PEP 562 __getattr__ 按需 import 子模块）
#   name_en: zephyr.governance.intelligence_governance.__init__
#   intro: __unmanaged__src/zephyr/governance/intelligence_governance/__init__.py 包入口
#   desc: MOD-GOV-intelligence_governance 包入口，__getattr__ 按 _SYMBOL_TO_MODULE 映射惰性 import 子模块再取符号，__all__ 仅保留真实存在且无歧义的公开符号（42项）
#   inputs: I1
#   outputs: zephyr.governance.intelligence_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（42项）；包级 import 不 eager import 任何子模块；DebateRound 双义（agent_debate.BaseModel vs multi_model_consensus.Enum）包级不导出，子模块路径自取
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.intelligence_governance 包公共 API
#   name_en: __all__ 42项
#   intro: __unmanaged__src/zephyr/governance/intelligence_governance/__init__.py 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
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
