"""
Post-Action Verifier — auto_guard 后验检查

MOD-INF-018 §2.11  D-018-02
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VerificationResult(str, Enum):
    VERIFIED = "verified"
    DISCREPANCY = "discrepancy"
    FAILED = "failed"


@dataclass
class ActionVerification:
    agent_id: str
    operation: str
    expected_outcome: str
    actual_outcome: str = ""
    result: VerificationResult = VerificationResult.VERIFIED
    details: list[str] = field(default_factory=list)
    rollback_required: bool = False


class PostActionVerifier:
    def __init__(self) -> None:
        self._verifications: list[ActionVerification] = []
        self._discrepancy_threshold = 3

    def verify(
        self,
        agent_id: str,
        operation: str,
        expected: str,
        actual: str,
    ) -> ActionVerification:
        result = (
            VerificationResult.VERIFIED if expected == actual
            else VerificationResult.DISCREPANCY
        )
        verification = ActionVerification(
            agent_id=agent_id,
            operation=operation,
            expected_outcome=expected,
            actual_outcome=actual,
            result=result,
            details=[] if result == VerificationResult.VERIFIED else [f"Expected '{expected}', got '{actual}'"],
            rollback_required=result != VerificationResult.VERIFIED,
        )
        self._verifications.append(verification)
        return verification

    def get_discrepancy_count(self, agent_id: str) -> int:
        return sum(1 for v in self._verifications if v.agent_id == agent_id and v.result != VerificationResult.VERIFIED)

    def should_escalate(self, agent_id: str) -> bool:
        return self.get_discrepancy_count(agent_id) >= self._discrepancy_threshold

    def reset_agent(self, agent_id: str) -> None:
        self._verifications = [v for v in self._verifications if v.agent_id != agent_id]
