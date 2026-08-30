# [BLUEPRINT] MOD-GOVERNANCE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-GOV_CONTEXT_GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BandwidthDimension, BandwidthScore, CompressedContext, ContextRecycling, Ha…
#   desc: __init__ import L0；__all__ 20 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（20 符号）
#   name_en: __all__
#   intro: BandwidthDimension, BandwidthScore, CompressedContext, ContextRecycling, Halluc…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "BandwidthDimension",
    "BandwidthScore",
    "CompressedContext",
    "ContextRecycling",
    "HallucinationLevel",
    "OptimizationRecommendation",
    "PromptVersion",
    "TokenTier",
    "prompt_lifecycle",
    "recommend",
    "command_chain_length_gate",
    "context_budget",
    "context_package",
    "context_switch_governor",
    "context_waste_detector",
    "conversation_tax_detector",
    "instruction_bloat_detector",
    "multi_turn_intent_analyzer",
    "protocol_self_context",
    "think_time_model",
]
