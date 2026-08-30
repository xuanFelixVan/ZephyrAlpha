# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.infrastructure.budget_enforcement
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.financial_governance.budget_enforcement; zephyr.infrastructure.budget_enforcement.rbac_bridge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 包聚合层——re-export 真源 + 注册子模块 rbac_bridge
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
budget_enforcement 包聚合层。

test_phase4_gate_check 期望 zephyr.infrastructure.budget_enforcement 可导入。
真源在 zephyr.governance.financial_governance.budget_enforcement；本 __init__.py
做包聚合（re-export 真源 + 注册子模块 rbac_bridge）。

__init__.py 包聚合豁免 PURE-SHIM 检测（check_pure_shim.is_pure_reexport_shim）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: *, __all__, __version__, rbac_bridge
#   code: __init__.py import L54
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 *, __all__, __version__, rbac_bridge（共 4 符号）
#   desc: __init__ import L54；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: *, __all__, __version__, rbac_bridge
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.governance.financial_governance.budget_enforcement import *  # noqa: F401,F403
from zephyr.governance.financial_governance.budget_enforcement import __all__, __version__

# 注册子模块 rbac_bridge（infra 层适配器，非 shim）
from zephyr.infrastructure.budget_enforcement import rbac_bridge  # noqa: F401

__all__ = list(__all__) + ["rbac_bridge"]
