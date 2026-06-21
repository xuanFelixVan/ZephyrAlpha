# [A_module] module_id=MOD-INF_observer_effect_compensator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md

# [MODULE] zephyr.infrastructure.capacity_assurance.observer_effect_compensator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Observer Effect Compensator — 容量监控污染 SLI (盲点 #30, M-33)
特性：
  - 观测开销扣除：SLI 报告值 = raw_value - overhead_estimate
  - compensated 字段标记补偿后的值写入 capacity_metrics
"""

import time
from dataclasses import dataclass
from typing import Any, Optional


class ObserverEffectCompensator:
    """
    观察者效应补偿器 (M-33, 盲点 #30)
    """

    def __init__(self):
        self._overhead_pct: dict[str, float] = {}

    def set_overhead(self, sli_id: str, overhead_pct: float):
        self._overhead_pct[sli_id] = max(0, min(overhead_pct, 1.0))

    def compensate(self, sli_id: str, raw_value: float) -> dict:
        overhead = self._overhead_pct.get(sli_id, 0)
        compensated_value = raw_value * (1 - overhead)
        return {
            "sli_id": sli_id,
            "raw_value": raw_value,
            "overhead_pct": overhead,
            "compensated_value": round(compensated_value, 6),
            "compensated": overhead > 0,
            "timestamp": time.time(),
        }
