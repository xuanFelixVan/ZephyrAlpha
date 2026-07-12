# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.model_drift_monitor
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_model_drift_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel


class ModelDriftType(str, Enum):
    CONCEPT = "CONCEPT"
    DATA = "DATA"
    PREDICTION = "PREDICTION"


class DriftConfig(BaseModel):
    drift_type: ModelDriftType
    metric: str
    threshold: str
    action: str


DRIFT_MONITORS: Final[dict[ModelDriftType, DriftConfig]] = {
    ModelDriftType.CONCEPT: DriftConfig(
        drift_type=ModelDriftType.CONCEPT,
        metric="Factor IC 30日滚动均值",
        threshold="下降 > 1σ",
        action="因子审查（§65）",
    ),
    ModelDriftType.DATA: DriftConfig(
        drift_type=ModelDriftType.DATA,
        metric="KL散度",
        threshold="> 阈值",
        action="重新训练",
    ),
    ModelDriftType.PREDICTION: DriftConfig(
        drift_type=ModelDriftType.PREDICTION,
        metric="Sharpe 30日",
        threshold="< 0",
        action="策略退役评估（§50）",
    ),
}


def get_drift_config(dt: ModelDriftType) -> DriftConfig | None:
    return DRIFT_MONITORS.get(dt)
