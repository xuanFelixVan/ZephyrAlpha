# [BLUEPRINT] SRC-045 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] zephyr.governance.model_drift_monitor
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-GOV_model_drift_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class DriftType(str, Enum):
    CONCEPT = "CONCEPT"
    DATA = "DATA"
    PREDICTION = "PREDICTION"


class DriftConfig(BaseModel):
    drift_type: DriftType
    metric: str
    threshold: str
    action: str


DRIFT_MONITORS: dict[DriftType, DriftConfig] = {
    DriftType.CONCEPT: DriftConfig(
        drift_type=DriftType.CONCEPT,
        metric="Factor IC 30日滚动均值",
        threshold="下降 > 1σ",
        action="因子审查（§65）",
    ),
    DriftType.DATA: DriftConfig(
        drift_type=DriftType.DATA,
        metric="KL散度",
        threshold="> 阈值",
        action="重新训练",
    ),
    DriftType.PREDICTION: DriftConfig(
        drift_type=DriftType.PREDICTION,
        metric="Sharpe 30日",
        threshold="< 0",
        action="策略退役评估（§50）",
    ),
}


def get_drift_config(dt: DriftType) -> DriftConfig | None:
    return DRIFT_MONITORS.get(dt)
