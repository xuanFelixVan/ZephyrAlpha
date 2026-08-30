# [BLUEPRINT] MOD-MODEL_ROUTER_ORCH | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md | §3.3/§4.3
# [MODULE] zephyr.intelligence.model_routing
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
"""
model_routing — 模型路由级联编排包（11号文 §3.3：L1 能力门 -> L2 任务适配排序 -> L3 成本/层级路由）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: CascadeDecision, CascadeOrchestrator, CascadeRoutingError
#   code: __init__.py import L35
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 CascadeDecision, CascadeOrchestrator, CascadeRoutingError（共 3 符号）
#   desc: __init__ import L35；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: CascadeDecision, CascadeOrchestrator, CascadeRoutingError
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.intelligence.model_routing.cascade_orchestrator import (
    CascadeDecision,
    CascadeOrchestrator,
    CascadeRoutingError,
)

__all__ = [
    "CascadeDecision",
    "CascadeOrchestrator",
    "CascadeRoutingError",
]
