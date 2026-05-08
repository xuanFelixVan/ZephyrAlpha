"""G-CT-006 — BudgetAlert Pydantic V2 BaseModel 预算告急事件."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class BudgetSeverity(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class BudgetType(str, Enum):
    TOKEN = "TOKEN"
    TIME = "TIME"
    MEMORY = "MEMORY"
    API_CALLS = "API_CALLS"


class BudgetAlert(BaseModel):
    alert_id: str
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str = ""
    budget_type: BudgetType = BudgetType.TOKEN
    burn_rate: float = 0.0
    burn_rate_threshold: float = 0.8
    remaining_budget: float = 0.0
    severity: BudgetSeverity = BudgetSeverity.WARNING

    @classmethod
    def from_burn_rate(cls, alert_id: str, burn_rate: float, threshold: float, remaining: float, session_id: str = "", budget_type: BudgetType = BudgetType.TOKEN) -> BudgetAlert:
        if remaining <= 0:
            severity = BudgetSeverity.CRITICAL
        elif burn_rate > threshold:
            severity = BudgetSeverity.WARNING
        else:
            severity = BudgetSeverity.WARNING

        return cls(
            alert_id=alert_id,
            session_id=session_id,
            budget_type=budget_type,
            burn_rate=burn_rate,
            burn_rate_threshold=threshold,
            remaining_budget=remaining,
            severity=severity,
        )
