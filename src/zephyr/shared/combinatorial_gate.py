"""
Combinatorial Gate — 门禁沙漠交叉检测 (盲点 #58)
特性：
  - N >= 3 变更时全组合模拟
  - 组合放大 > 1.3x → BLOCK + 分拆方案
"""
import itertools
from typing import Any, Callable, Optional


class CombinatorialGate:
    """
    组合门禁 (盲点 #58)
    """

    COMBINATION_AMPLIFICATION_THRESHOLD = 1.3

    def __init__(self):
        self._baseline_costs: dict[str, float] = {}

    def set_baselines(self, baselines: dict[str, float]):
        self._baseline_costs = baselines

    def evaluate(self, changes: list[dict], cost_fn: Callable[[list[dict]], float]) -> dict:
        if len(changes) < 3:
            return {"blocked": False, "max_amplification": 1.0}

        single_costs = {}
        for change in changes:
            change_id = change.get("id", str(id(change)))
            single_costs[change_id] = cost_fn([change])

        max_amplification = 1.0
        blocked_combinations = []

        for r in range(2, len(changes) + 1):
            for combo in itertools.combinations(changes, r):
                combo_list = list(combo)
                combo_cost = cost_fn(combo_list)
                sum_single = sum(
                    single_costs.get(c.get("id", str(id(c))), 0)
                    for c in combo_list
                )
                amplification = combo_cost / max(sum_single, 0.0001)
                if amplification > max_amplification:
                    max_amplification = amplification
                if amplification > self.COMBINATION_AMPLIFICATION_THRESHOLD:
                    blocked_combinations.append({
                        "changes": [c.get("id", str(id(c))) for c in combo_list],
                        "amplification": round(amplification, 2),
                    })

        return {
            "blocked": len(blocked_combinations) > 0,
            "max_amplification": round(max_amplification, 2),
            "blocked_combinations": blocked_combinations,
            "suggestion": "Split changes" if blocked_combinations else "",
        }
