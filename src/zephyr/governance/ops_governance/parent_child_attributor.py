# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.parent_child_attributor
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
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
#   name: max_depth 参数
#   fields: 参数 max_depth（无注解）
#   code: parent_child_attributor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_delegation 参数
#   fields: 参数 max_delegation（无注解）
#   code: parent_child_attributor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ParentChildAttributor
#   name_en: ParentChildAttributor
#   intro: class ParentChildAttributor 源码 L78-L146
#   desc: 公共方法（定义序）: max_depth, record_delegation, analyze, children_of, chain_for, clear；源码 L78-L146
#   inputs: max_depth max_delegation
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ParentChildAttributor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class AttributionChain:
    parent_id: str
    child_id: str
    tokens_delegated: int
    cost_delegated: float
    depth: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class DelegationReport:
    total_delegated_tokens: int
    total_delegated_cost: float
    chain_depth: int
    max_depth: int
    bottleneck: str
    advice: str


class ParentChildAttributor:
    def __init__(self, max_depth: int = 5, max_delegation: int = 100000):
        self._max_depth = max_depth
        self._max_delegation = max_delegation
        self._chains: list[AttributionChain] = []
        self._delegation_map: dict[str, list[AttributionChain]] = defaultdict(list)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_depth(self):
        """只读：max_depth（Stage 4 公共化）。"""
        return self._max_depth

    @max_depth.setter
    def max_depth(self, value):
        """写入：max_depth（Stage 4 公共化）。"""
        self._max_depth = value

    def record_delegation(
        self, parent_id: str, child_id: str, tokens: int, cost: float, depth: int = 1
    ) -> AttributionChain:
        chain = AttributionChain(
            parent_id=parent_id,
            child_id=child_id,
            tokens_delegated=tokens,
            cost_delegated=cost,
            depth=depth,
        )
        self._chains.append(chain)
        self._delegation_map[parent_id].append(chain)
        return chain

    def analyze(self) -> DelegationReport:
        total_tokens = sum(c.tokens_delegated for c in self._chains)
        total_cost = sum(c.cost_delegated for c in self._chains)
        max_depth = max((c.depth for c in self._chains), default=0)

        if max_depth > self._max_depth:
            bottleneck = f"委托链深度 {max_depth} > 最大 {self._max_depth}"
            advice = "委托链过深，建议扁平化任务结构"
        elif total_tokens > self._max_delegation:
            bottleneck = f"总委托 {total_tokens} tokens > 最大 {self._max_delegation}"
            advice = "总委托量超限，建议限制子任务数量"
        else:
            bottleneck = "NONE"
            advice = "委托链健康"

        return DelegationReport(
            total_delegated_tokens=total_tokens,
            total_delegated_cost=round(total_cost, 6),
            chain_depth=len(self._chains),
            max_depth=max_depth,
            bottleneck=bottleneck,
            advice=advice,
        )

    def children_of(self, parent_id: str) -> list[AttributionChain]:
        return self._delegation_map.get(parent_id, [])

    def chain_for(self, child_id: str) -> list[AttributionChain]:
        result: list[AttributionChain] = []
        for chain in self._chains:
            if child_id == chain.child_id:
                result.append(chain)
        return result

    def clear(self) -> None:
        self._chains.clear()
        self._delegation_map.clear()
