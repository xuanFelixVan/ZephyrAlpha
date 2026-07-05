# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.exceptions
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_exceptions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass, field


@dataclass
class ForensicContext:
    stack_trace: str | None = None
    causal_chain: list[str] = field(default_factory=list)
    decision_id: str | None = None


class FLEBaseException(Exception):
    def __init__(
        self,
        message: str,
        forensic_context: ForensicContext | None = None,
    ):
        super().__init__(message)
        self.forensic_context = forensic_context or ForensicContext()


class DiagnosisError(FLEBaseException):
    pass


class RepairError(FLEBaseException):
    pass


class GateBlockedError(FLEBaseException):
    pass


class AutonomyViolationError(FLEBaseException):
    pass
