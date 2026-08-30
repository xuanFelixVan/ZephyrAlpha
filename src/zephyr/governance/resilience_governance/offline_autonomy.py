# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.offline_autonomy
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.offline_autonomy
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.infrastructure.a2a_protocol.offline_autonomy (SSoT 收敛，消除多真源)

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: offline_autonomy.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AutonomyState, OfflineMode（共 2 符号）
#   desc: __init__ import L0；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: AutonomyState, OfflineMode
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.offline_autonomy import (
    AutonomyState,
    OfflineMode,
)

__all__ = [
    "AutonomyState",
    "OfflineMode",
]
