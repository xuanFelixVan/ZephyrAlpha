# [A_module] module_id=MOD-PRT-strategy_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategy_engine
# [DOMAIN] D_PF_CORE
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_PORTFOLIO_CORE — Portfolio Construction Strategies

策略引擎包：策略运行器 + 具体策略实现。

实现清单：
  - StrategyRunner : 策略运行器（因子→合成→策略→回测 胶水层，盘后回测入口）
  - DefaultEquityStrategy : StrategyBase 的具体实现（等权/信号加权/最小方差配置）
"""

from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)
from zephyr.pf_core.strategy_engine.strategy_runner import (
    StrategyRunner,
    StrategyRunnerConfig,
)

__all__ = [
    "DefaultEquityStrategy",
    "RebalanceMode",
    "StrategyRunner",
    "StrategyRunnerConfig",
]
