# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infra_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.gate.gate_result
# [DOMAIN] D-SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.contracts.gate
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export only — canonical source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] do not add business logic here
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_gate_result | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

import importlib

_GATE_RESULT_NAMES = {
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
}


def __getattr__(name):
    if name in _GATE_RESULT_NAMES:
        _mod = importlib.import_module("zephyr.governance.rule_enforcement.gate_types")
        _val = getattr(_mod, name)
        globals()[name] = _val
        return _val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
]
