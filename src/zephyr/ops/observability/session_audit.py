# [A_module] module_id=MOD-SHR_session_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.ops.observability.session_audit

# [INVARIANTS] Re-exports only; real implementation in zephyr.shared.session_audit

# [MODIFY-GUARD] Do not add logic here; this is a shim

# [CONSUMERS] zephyr.ops.observability

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Re-export shim: zephyr.shared.session_audit → zephyr.ops.observability.session_audit"""

from zephyr.shared.session_audit import (  # noqa: F401
    CostRecord,
    DecisionRecord,
    ErrorRecord,
    OutcomeRecord,
    PromptRecord,
    SessionAuditTrail,
    SessionRecord,
    ToolCallRecord,
)

__all__ = [
    "CostRecord",
    "DecisionRecord",
    "ErrorRecord",
    "OutcomeRecord",
    "PromptRecord",
    "SessionAuditTrail",
    "SessionRecord",
    "ToolCallRecord",
]
