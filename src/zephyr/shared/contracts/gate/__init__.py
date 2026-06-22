# [A_module] module_id=MOD-SHR_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain-infra_runtime/runtime-integration/blueprint.md
# [MODULE] zephyr.shared.contracts.gate
# [INVARIANTS] re-export only — canonical source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] do not add business logic here
# [CONSUMERS] zephyr.infrastructure.db.task_repo; zephyr.infrastructure.db.transition; zephyr.knowledge.kb.pipeline.*
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

from zephyr.shared.contracts.gate.gate_result import (
    GateEngineError,
    GateResult,
    GateViolation,
    GateViolationError,
)

__all__ = [
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
    "gate_result",
]
