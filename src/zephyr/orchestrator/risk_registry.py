# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.orchestrator.risk_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
风险注册表与集成冲突裁决器（Risk Registry）

依据：MOD-MASTER-002 蓝图 §十一 风险注册表
实现集成冲突裁决 + R-MOD-1~34 风险缓解状态追踪。
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class RiskStatus(str, Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Risk(BaseModel):
    risk_id: str
    severity: RiskSeverity
    description: str = ""
    mitigation_plan: str = ""
    affected_contracts: list[str] = Field(default_factory=list)
    status: RiskStatus = RiskStatus.OPEN
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConflictResolution(BaseModel):
    conflict_id: str
    contract_a: str
    contract_b: str
    resolution: str
    rationale: str = ""
    resolved_by: str = ""


RISKS: dict[str, Risk] = {
    f"R-MOD-{i}": Risk(
        risk_id=f"R-MOD-{i}",
        severity=RiskSeverity.MEDIUM,
        description=f"风险 R-MOD-{i}——待缓解",
        mitigation_plan="TBD",
        affected_contracts=[],
    )
    for i in range(1, 35)
}


class RiskRegistry:
    def get(self, risk_id: str) -> Risk | None:
        return RISKS.get(risk_id)

    def list_all(self) -> list[Risk]:
        return list(RISKS.values())

    def list_open(self) -> list[Risk]:
        return [r for r in RISKS.values() if r.status == RiskStatus.OPEN]

    def mitigate(self, risk_id: str) -> bool:
        risk = RISKS.get(risk_id)
        if risk is None:
            return False
        risk.status = RiskStatus.MITIGATED
        risk.updated_at = datetime.now(timezone.utc)
        return True

    def accept(self, risk_id: str) -> bool:
        risk = RISKS.get(risk_id)
        if risk is None:
            return False
        risk.status = RiskStatus.ACCEPTED
        risk.updated_at = datetime.now(timezone.utc)
        return True
