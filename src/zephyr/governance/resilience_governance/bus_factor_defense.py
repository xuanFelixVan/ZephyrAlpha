# [BLUEPRINT] SRC-068 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.bus_factor_defense
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_bus_factor_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

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
    last_adr_update: str | None = None

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
    review_date: str | None = None


class OpsRunbook(BaseModel):
    module_id: str
    auto_generated: bool = True
    content: str = ""
    generated_at: str = ""
    last_update: str | None = None


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

    review_date = (datetime.now(UTC) + timedelta(days=review_days)).isoformat()
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
        generated_at=datetime.now(UTC).isoformat(),
    )
