# [A_module] module_id=MOD-ORC_rc_orch_bs_proxy | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.trading.orchestrator.blueprint_scorer
# [INVARIANTS] 代理模块——重定向到 zephyr.trading.orchestrator.blueprint_scorer
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] integration.shared_08.utils.blueprint_scorer; integration.shared_08.blueprint_scorer
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if proxy target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.trading.orchestrator.blueprint_scorer — 代理模块

代理目标：zephyr.trading.orchestrator.blueprint_scorer（物理真源）
"""
from zephyr.trading.orchestrator.blueprint_scorer import *  # noqa: F401, F403

import importlib as _il
_mod = _il.import_module("zephyr.trading.orchestrator.blueprint_scorer")
for _n in getattr(_mod, "__all__", [n for n in dir(_mod) if not n.startswith("_")]):
    globals()[_n] = getattr(_mod, _n)
del _il, _mod, _n
