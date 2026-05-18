# [BLUEPRINT] MOD-INF-022 | docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
# [MODULE] zephyr.escalation_engine
# [INVARIANTS] 升级裁决;四级约束;Kill Switch
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md;src/zephyr/escalation_engine/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-020;MOD-INF-018
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EscalationError;TimeoutError
# [TESTS] tests/test_escalation_engine/

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BusFactorRisk(str, Enum):
    SAFE = "SAFE"
    AT_RISK = "AT_RISK"
    DANGER = "DANGER"


class ModuleOwnership(BaseModel):
    module_id: str
    owners: list[str] = Field(default_factory=list)
    bus_factor: int = 0
    risk: BusFactorRisk = BusFactorRisk.DANGER
    onboarding_readme: bool = False
    onboarding_diagram: bool = False
    onboarding_key_funcs: bool = False
    last_adr_update: Optional[str] = None

    @property
    def onboarding_complete(self) -> bool:
        return self.onboarding_readme and self.onboarding_diagram and self.onboarding_key_funcs

    @property
    def onboarding_time_estimate(self) -> str:
        if self.onboarding_complete:
            return "<15min"
        return ">15min — INCOMPLETE"


class DecisionLog(BaseModel):
    adr_id: str
    problem: str
    options: list[str] = Field(default_factory=list)
    decision: str = ""
    rationale: str = ""
    review_date: Optional[str] = None


class OpsRunbook(BaseModel):
    module_id: str
    auto_generated: bool = True
    content: str = ""
    generated_at: str = ""
    last_update: Optional[str] = None


def check_bus_factor(ownership: ModuleOwnership) -> ModuleOwnership:
    ownership.bus_factor = len(ownership.owners)
    if ownership.bus_factor >= 2:
        ownership.risk = BusFactorRisk.SAFE
    elif ownership.bus_factor == 1:
        ownership.risk = BusFactorRisk.AT_RISK
    else:
        ownership.risk = BusFactorRisk.DANGER
    return ownership


def create_decision_log(
    adr_id: str,
    problem: str,
    options: list[str],
    decision: str,
    rationale: str,
    review_days: int = 90,
) -> DecisionLog:
    from datetime import timedelta

    review_date = (datetime.now(timezone.utc) + timedelta(days=review_days)).isoformat()
    return DecisionLog(
        adr_id=adr_id,
        problem=problem,
        options=options,
        decision=decision,
        rationale=rationale,
        review_date=review_date,
    )


def generate_runbook(module_id: str, content: str = "") -> OpsRunbook:
    return OpsRunbook(
        module_id=module_id,
        auto_generated=True,
        content=content or f"# Runbook: {module_id}\n\n## TBD",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
