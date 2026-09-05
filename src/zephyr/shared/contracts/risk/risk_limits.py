# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.risk.risk_limits
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Backward-compat shim — canonical location is zephyr.shared.contracts.risk_limits
（CTR-003 登记真源；B3 治本 2026-09-05 方向修正：原指向 trading_contracts 副本，
与 cross_layer_contracts.yaml physical_path 登记方向相反）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 真源模块公共符号
#   fields: RiskLimits
#   code: zephyr.shared.contracts.risk_limits
# 层: 算法
# - id: A1
#   name_zh: ① 符号转发
#   name_en: re-export
#   intro: 惰性转发全部公共符号，保证本导入路径兼容
#   desc: __getattr__ + importlib，无自有实现
#   inputs: I1
#   outputs: 真源符号
#   invariant: re-export shim，不包含任何自有实现
# 层: 输出
# - id: O1
#   name_zh: RiskLimits 契约类
#   name_en: risk_limits symbols
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import importlib

_TARGET_MODULE = "zephyr.shared.contracts.risk_limits"


def __getattr__(name):
    mod = importlib.import_module(_TARGET_MODULE)
    if hasattr(mod, name):
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
