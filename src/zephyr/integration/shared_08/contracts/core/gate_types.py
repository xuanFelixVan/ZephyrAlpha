# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.integration.shared_08.contracts.core.gate_types
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.core.gate_types
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.core.gate_types
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.core.gate_types import GateResult, GateViolationError"
# [A_module] module_id=MOD-INT_gate_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.core.gate_types。

shared 版本使用 __getattr__ 动态转发至 zephyr.governance.rule_enforcement.gate_types，
本 shim 同样使用 __getattr__ 转发至 shared，保持动态导入语义。
"""


def __getattr__(name):
    _mod = __import__("zephyr.shared.contracts.core.gate_types", fromlist=[name])
    return getattr(_mod, name)
