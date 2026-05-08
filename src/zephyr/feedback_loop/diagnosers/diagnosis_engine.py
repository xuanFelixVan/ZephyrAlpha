from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Diagnosis:
    diagnosis_id: str
    root_cause: str
    confidence: float
    evidence_chain: list[str] = field(default_factory=list)


@dataclass
class DiagnosisEngine:

    def diagnose(self, anomaly_id: str, anomaly_evidence: dict[str, Any]) -> Diagnosis:
        diagnosis_id = str(uuid.uuid4())[:8]
        metric_name = anomaly_evidence.get("metric_name", "unknown")
        z_score = abs(anomaly_evidence.get("z_score", 2.5))
        root_cause = f"Elevated {metric_name} (z={z_score:.2f})"
        confidence = min(0.5 + z_score / 10.0, 0.95)
        evidence_chain = [
            f"metric={metric_name}",
            f"z_score={z_score:.2f}",
            f"confidence={confidence:.2f}",
        ]
        return Diagnosis(
            diagnosis_id=diagnosis_id,
            root_cause=root_cause,
            confidence=confidence,
            evidence_chain=evidence_chain,
        )
