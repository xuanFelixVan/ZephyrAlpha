# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.exceptions
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
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
    error_code = "ZA-TR-0006"

    def __init__(
        self,
        message: str,
        forensic_context: ForensicContext | None = None,
        error_code: str | None = None,
    ):
        super().__init__(message)
        self.forensic_context = forensic_context or ForensicContext()
        if error_code is not None:
            self.error_code = error_code


class DiagnosisError(FLEBaseException):
    error_code = "ZA-TR-0007"


class RepairError(FLEBaseException):
    error_code = "ZA-TR-0008"


class GateBlockedError(FLEBaseException):
    error_code = "ZA-TR-0009"


class AutonomyViolationError(FLEBaseException):
    error_code = "ZA-TR-0010"
