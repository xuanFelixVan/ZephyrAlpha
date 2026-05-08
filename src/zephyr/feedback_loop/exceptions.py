from __future__ import annotations

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
