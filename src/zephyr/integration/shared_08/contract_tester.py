# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.contract_tester
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_contract_tester | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Re-export wrapper — canonical implementation at zephyr.infrastructure.contract_tester.

TD-SHARED-001: 发散副本统一为 re-export wrapper，消除代码漂移。
"""

import importlib as _importlib

_mod = _importlib.import_module("zephyr.infrastructure.contract_tester")
ContractTester = _mod.ContractTester
ContractTestResult = _mod.ContractTestResult
__all__ = [name for name in dir(_mod) if not name.startswith("_")]
