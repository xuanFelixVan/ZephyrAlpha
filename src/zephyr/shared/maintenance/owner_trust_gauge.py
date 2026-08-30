# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.maintenance.owner_trust_gauge
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: default_score 参数
#   fields: 参数 default_score（无注解）
#   code: owner_trust_gauge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OwnerTrustGauge
#   name_en: OwnerTrustGauge
#   intro: class OwnerTrustGauge 源码 L69-L89
#   desc: 公共方法（定义序）: update, assess；源码 L69-L89
#   inputs: default_score
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: OwnerTrustGauge
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TrustLevel(Enum):
    FULL_AUTONOMY = "full_autonomy"
    SUPERVISED = "supervised"
    HUMAN_GATED = "human_gated"
    REVOKED = "revoked"


@dataclass
class TrustAssessment:
    agent_id: str
    trust_level: TrustLevel
    score: float
    reason: str


class OwnerTrustGauge:
    def __init__(self, default_score: float = 0.5):
        self._scores: dict[str, float] = {}
        self._default = default_score

    def update(self, agent_id: str, delta: float) -> TrustAssessment:
        current = self._scores.get(agent_id, self._default)
        new_score = max(0.0, min(1.0, current + delta))
        self._scores[agent_id] = new_score
        if new_score >= 0.8:
            level = TrustLevel.FULL_AUTONOMY
        elif new_score >= 0.5:
            level = TrustLevel.SUPERVISED
        elif new_score >= 0.2:
            level = TrustLevel.HUMAN_GATED
        else:
            level = TrustLevel.REVOKED
        return TrustAssessment(agent_id, level, new_score, f"score={new_score:.2f}")

    def assess(self, agent_id: str) -> TrustAssessment:
        return self.update(agent_id, 0.0)
