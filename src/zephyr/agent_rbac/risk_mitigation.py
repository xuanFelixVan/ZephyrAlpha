"""风险缓解——自动化风险评分+缓解策略+RAG pipeline."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    category: str
    likelihood_pct: float = 0.0
    impact_score: float = 0.0
    risk_level: str = "LOW"
    mitigation: str = ""
    owner_acknowledged: bool = False


class RiskMitigation:
    @staticmethod
    def assess(category: str, likelihood: float, impact: float) -> RiskAssessment:
        risk_score = likelihood * impact
        if risk_score > 0.64:
            level = "CRITICAL"
        elif risk_score > 0.36:
            level = "HIGH"
        elif risk_score > 0.16:
            level = "MEDIUM"
        else:
            level = "LOW"

        return RiskAssessment(
            category=category,
            likelihood_pct=likelihood,
            impact_score=impact,
            risk_level=level,
            mitigation="requires_review" if level in ("CRITICAL", "HIGH") else "monitor",
        )

    @staticmethod
    def get_mitigation_playbook(risk_level: str) -> dict[str, Any]:
        playbooks = {
            "CRITICAL": {"action": "BLOCK_AND_ESCALATE", "timeout_minutes": 5},
            "HIGH": {"action": "RESTRICT_TO_READONLY", "timeout_minutes": 30},
            "MEDIUM": {"action": "LOG_AND_MONITOR", "timeout_minutes": 120},
            "LOW": {"action": "ALLOW_WITH_METRICS", "timeout_minutes": 1440},
        }
        return playbooks.get(risk_level, {"action": "ALLOW", "timeout_minutes": 0})
