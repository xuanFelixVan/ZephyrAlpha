# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
  - EventSentimentAdapter : 事件策略情绪分适配层
    （news_sentiment_window 情绪分 → eventdriven-sleeve 富负载 → 权重面板）
  - DefaultEquityStrategy : StrategyBase 的具体实现（等权/信号加权/最小方差配置）
  - 路径 B tick 级做T策略（TickStrategyBase 子类，@TickStrategyBase.register 注册，
    经 StrategyRunner.run_tick_strategy_backtest 显式 import + autodiscover 注册）：
    * IntradaySurgeFallStrategy : 30秒冲高回落做T（动量反转）
    * VWAPReversionStrategy     : VWAP 回归做T（均值回归）
    * OrderBookImbalanceStrategy: 盘口失衡反转做T（订单流反转）
"""

from zephyr.pf_core.default_equity_strategy import (
    DefaultEquityStrategy,
    RebalanceMode,
)
from zephyr.pf_core.strategy_engine.event_sentiment_adapter import (
    EventSentimentAdapter,
)
from zephyr.pf_core.strategy_engine.strategy_runner import (
    StrategyRunner,
    StrategyRunnerConfig,
)

__all__ = [
    "DefaultEquityStrategy",
    "EventSentimentAdapter",
    "RebalanceMode",
    "StrategyRunner",
    "StrategyRunnerConfig",
]
