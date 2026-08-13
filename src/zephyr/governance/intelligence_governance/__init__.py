# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV-intelligence_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.governance.intelligence_governance
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.governance.intelligence_governance.__init__
#   intro: __unmanaged__src/zephyr/governance/intelligence_governance/__init__.py 包入口
#   desc: MOD-GOV-intelligence_governance 包入口，模块命名空间声明并声明 __all__（33项）
#   inputs: I1
#   outputs: zephyr.governance.intelligence_governance 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（33项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.intelligence_governance 包公共 API
#   name_en: __all__ 33项
#   intro: __unmanaged__src/zephyr/governance/intelligence_governance/__init__.py 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "AgentDebate",
    "AutoFixLayer",
    "ConsensusProtocol",
    "DebateRound",
    "DebateVerdict",
    "DriftConfig",
    "DriftType",
    "KnowledgeEntry",
    "KnowledgeIndex",
    "ModelResponse",
    "ai_self_diagnosis",
    "auto_fix_known_pattern",
    "escalate_to_owner",
    "get_drift_config",
    "get_index",
    "multi_model_consensus",
'aisg_sandbox', 'confidence_estimator', 'cross_assistant_adapter', 'delegation_engine', 'delegation_manager', 'memory_provider', 'meta_confidence', 'model_provider_data', 'model_router', 'model_version_detector', 'mvep_orchestrator', 'provider_base', 'provider_failover', 'self_benchmark', 'self_test', 'self_validator', 'subagent_hook_propagator']
