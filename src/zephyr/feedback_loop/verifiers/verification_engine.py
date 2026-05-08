from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    INEFFECTIVE = "INEFFECTIVE"
    HARMFUL = "HARMFUL"


@dataclass
class VerificationResult:
    anomaly_id: str
    pre_value: float
    post_value: float
    delta: float
    verdict: Verdict
    timestamp: float


@dataclass
class VerificationEngine:

    def verify(
        self,
        anomaly_id: str,
        pre_value: float,
        post_value: float,
        timestamp: float,
    ) -> VerificationResult:
        delta = post_value - pre_value
        if delta < -0.01:
            verdict = Verdict.HARMFUL
        elif abs(delta) < 0.01:
            verdict = Verdict.INEFFECTIVE
        else:
            verdict = Verdict.EFFECTIVE
        return VerificationResult(
            anomaly_id=anomaly_id,
            pre_value=pre_value,
            post_value=post_value,
            delta=delta,
            verdict=verdict,
            timestamp=timestamp,
        )
