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
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: dt 参数
#   fields: 参数 dt，类型注解 ModelDriftType
#   code: model_drift_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_drift_config
#   name_en: get_drift_config
#   intro: get_drift_config(dt) 源码 L92-L93
#   desc: 源码 L92-L93
#   inputs: dt
#   outputs: DriftConfig | None
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DriftConfig | None
#   name_en: DriftConfig | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final

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
