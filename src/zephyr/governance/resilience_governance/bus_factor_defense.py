# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.bus_factor_defense
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.factor.bus_factor_defense
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
# Re-export shim: canonical source = zephyr.factor.bus_factor_defense (SSoT 收敛，消除多真源)

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: bus_factor_defense.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BusFactorRisk, DecisionLog, ModuleOwnership, OpsRunbook, check_bus_factor,…
#   desc: __init__ import L0；__all__ 7 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（7 符号）
#   name_en: __all__
#   intro: BusFactorRisk, DecisionLog, ModuleOwnership, OpsRunbook, check_bus_factor, crea…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.factor.bus_factor_defense import (
    BusFactorRisk,
    DecisionLog,
    ModuleOwnership,
    OpsRunbook,
    check_bus_factor,
    create_decision_log,
    generate_runbook,
)

__all__ = [
    "BusFactorRisk",
    "DecisionLog",
    "ModuleOwnership",
    "OpsRunbook",
    "check_bus_factor",
    "create_decision_log",
    "generate_runbook",
]
