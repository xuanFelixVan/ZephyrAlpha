# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.cost_attributor
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: top_n 参数
#   fields: 参数 top_n（无注解）
#   code: cost_attributor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CostAttributor
#   name_en: CostAttributor
#   intro: class CostAttributor 源码 L76-L152
#   desc: 公共方法（定义序）: attributions, counter, top_n, attribute, summarize, recent, clear；源码 L76-L152
#   inputs: top_n
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CostAttributor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field

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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def attributions(self) -> list[CostAttribution]:
        """只读：attributions（Stage 4 公共化）。"""
        return self._attributions

    @attributions.setter
    def attributions(self, value):
        """写入：attributions（Stage 4 公共化）。"""
        self._attributions = value

    @property
    def counter(self) -> int:
        """只读：counter（Stage 4 公共化）。"""
        return self._counter

    @counter.setter
    def counter(self, value):
        """写入：counter（Stage 4 公共化）。"""
        self._counter = value

    @property
    def top_n(self):
        """只读：top_n（Stage 4 公共化）。"""
        return self._top_n

    @top_n.setter
    def top_n(self, value):
        """写入：top_n（Stage 4 公共化）。"""
        self._top_n = value

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
