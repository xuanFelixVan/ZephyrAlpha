# [A_module] module_id=MOD-ORC_cm_token_budget_proxy | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.autonomy_core.token_budget
# [INVARIANTS] 代理模块——重定向到 zephyr.autonomy_core.token_budget
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] shared.observability_02.token_utils; shared.observability.token_utils; shared.shared_services.observability_02.token_utils
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if zephyr.autonomy_core.token_budget missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.autonomy_core.token_budget — 代理模块

代理目标：zephyr.autonomy_core.token_budget（物理真源）
创建原因：24个文件通过 import_module("zephyr.autonomy_core.token_budget") 访问，
但 zephyr.orchestration 包不存在。本代理模块保持调用方不变，仅提供导入兼容。
"""
from zephyr.autonomy_core.token_budget import *  # noqa: F401, F403

# 显式 re-export（避免 __all__ 缺失时遗漏）
import importlib as _il
_mod = _il.import_module("zephyr.autonomy_core.token_budget")
for _n in getattr(_mod, "__all__", [n for n in dir(_mod) if not n.startswith("_")]):
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
