# [A_module] module_id=MOD-INT_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-178 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.gate
# [INVARIANTS] re-export only — canonical source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] do not add business logic here
# [CONSUMERS] zephyr.data_governance.persistence.task_repo; zephyr.data_governance.persistence.transition; zephyr.knowledge.kb.pipeline.*
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]

from zephyr.integration.shared_08.contracts.gate.gate_result import (
    GateEngineError,
    GateResult,
    GateViolation,
    GateViolationError,
)

__all__ = [
    "GateViolation",
    "GateResult",
    "GateEngineError",
    "GateViolationError",
    "gate_result",
]
