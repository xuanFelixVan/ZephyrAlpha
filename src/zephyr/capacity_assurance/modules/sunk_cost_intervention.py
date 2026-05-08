"""
Sunk Cost Intervention — 沉没成本干预 (盲点 #37)
特性：
  - 检测某个基建占 Token 消耗>30% 超过 48 小时
  - 触发精简替换决策建议
"""
import time
from collections import defaultdict
from typing import Any, Optional


class SunkCostIntervention:
    """
    沉没成本干预 (盲点 #37)
    """

    TOKEN_SHARE_THRESHOLD = 0.30
    WINDOW_HOURS = 48

    def __init__(self):
        self._module_costs: dict[str, list[tuple[float, float]]] = {}

    def record(self, module: str, tokens_used: int, cost_usd: float):
        if module not in self._module_costs:
            self._module_costs[module] = []
        self._module_costs[module].append((time.time(), tokens_used))

    def analyze(self) -> dict:
        total_tokens = sum(
            sum(r[1] for r in recs) for recs in self._module_costs.values()
        )
        if total_tokens == 0:
            return {"interventions": []}

        interventions = []
        for module, records in self._module_costs.items():
            module_tokens = sum(r[1] for r in records)
            share = module_tokens / max(total_tokens, 1)
            if share > self.TOKEN_SHARE_THRESHOLD:
                interventions.append({
                    "module": module,
                    "token_share": round(share, 2),
                    "suggestion": f"Module {module} consumes {share:.1%} of tokens — consider replacing or simplifying.",
                })

        return {"interventions": interventions, "total_tokens": total_tokens}
