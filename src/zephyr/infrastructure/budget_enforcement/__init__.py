# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.infrastructure.budget_enforcement
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.financial_governance.budget_enforcement; zephyr.infrastructure.budget_enforcement.rbac_bridge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 包聚合层——re-export 真源 + 注册子模块 rbac_bridge
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-budget_enforcement | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""budget_enforcement 包聚合层。

test_phase4_gate_check 期望 zephyr.infrastructure.budget_enforcement 可导入。
真源在 zephyr.governance.financial_governance.budget_enforcement；本 __init__.py
做包聚合（re-export 真源 + 注册子模块 rbac_bridge）。

__init__.py 包聚合豁免 PURE-SHIM 检测（check_pure_shim.is_pure_reexport_shim）。
"""

from zephyr.governance.financial_governance.budget_enforcement import *  # noqa: F401,F403
from zephyr.governance.financial_governance.budget_enforcement import __all__, __version__

# 注册子模块 rbac_bridge（infra 层适配器，非 shim）
from zephyr.infrastructure.budget_enforcement import rbac_bridge  # noqa: F401

__all__ = list(__all__) + ["rbac_bridge"]
