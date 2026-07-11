# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.parent_child_attributor
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-RES_parent_child_attributor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
