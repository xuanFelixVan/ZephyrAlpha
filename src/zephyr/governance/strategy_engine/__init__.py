# [A_module] module_id=MOD-PRT_strategy_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain-pf_core/portfolio-core/blueprint.md
# [MODULE] zephyr.pf_core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""L05 — Portfolio Construction Strategies

Phase C 具体策略实现包。

实现清单：
  - DefaultEquityStrategy : StrategyBase 的具体实现（等权/信号加权/最小方差配置）
"""

from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)

__all__ = ["DefaultEquityStrategy", "RebalanceMode", "default_equity_strategy"]
