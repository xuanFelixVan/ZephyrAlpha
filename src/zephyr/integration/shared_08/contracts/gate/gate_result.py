# [BLUEPRINT] SRC-179 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.gate.gate_result
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] zephyr.integration.shared_08.contracts.gate
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export only — canonical source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] do not add business logic here
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_gate_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

import importlib as _importlib

_mod = _importlib.import_module("zephyr.governance.rule_enforcement.gate_types")
GateEngineError = _mod.GateEngineError
GateResult = _mod.GateResult
GateViolation = _mod.GateViolation
GateViolationError = _mod.GateViolationError

__all__ = [
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
]
