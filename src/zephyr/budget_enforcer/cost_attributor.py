# [BLUEPRINT] MOD-INF-024 | 03_modules/l01_infrastructure/budget-enforcer/blueprint.md | §

# [MODULE] zephyr.budget_enforcer.cost_attributor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import defaultdict

from .budget_models import BudgetDimension


@dataclass
class CostAttribution:
    action_id: str
    action_type: str
    tokens: int
    cost: float
    dimension: BudgetDimension
    parent_id: str = ""
    session_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class CostSummary:
    total_tokens: int = 0
    total_cost: float = 0.0
    by_action_type: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    by_dimension: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    top_expensive: list[CostAttribution] = field(default_factory=list)


class CostAttributor:
    def __init__(self, top_n: int = 10):
        self._top_n = top_n
        self._attributions: list[CostAttribution] = []
        self._counter: int = 0

    def attribute(
        self,
        action_type: str,
        tokens: int,
        cost: float,
        dimension: BudgetDimension = BudgetDimension.TOKEN,
    ) -> CostAttribution:
        self._counter += 1
        attr = CostAttribution(
            action_id=f"attr-{self._counter:06d}",
            action_type=action_type,
            tokens=tokens,
            cost=cost,
            dimension=dimension,
        )
        self._attributions.append(attr)
        return attr

    def summarize(self) -> CostSummary:
        s = CostSummary()
        sorted_attrs = sorted(self._attributions, key=lambda a: a.cost, reverse=True)
        s.top_expensive = sorted_attrs[: self._top_n]

        for a in self._attributions:
            s.total_tokens += a.tokens
            s.total_cost += a.cost
            s.by_action_type[a.action_type] += a.cost
            s.by_dimension[a.dimension.value] += a.cost

        s.total_cost = round(s.total_cost, 6)
        s.by_action_type = dict(s.by_action_type)
        s.by_dimension = dict(s.by_dimension)
        return s

    def recent(self, n: int = 20) -> list[CostAttribution]:
        return self._attributions[-n:]

    def clear(self) -> None:
        self._attributions.clear()
        self._counter = 0
