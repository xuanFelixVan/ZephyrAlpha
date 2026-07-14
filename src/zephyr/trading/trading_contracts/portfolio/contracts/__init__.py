# [A_module] module_id=MOD-PRT_contracts_portfolio_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md | §4
# [MODULE] zephyr.trading.trading_contracts.portfolio.contracts
# [INVARIANTS] Money immutability; currency precision
# [MODIFY-GUARD] trading-contracts/portfolio/contracts/money.py
# [CONSUMERS] reporting; ex_core
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MoneyCurrencyMismatchError; MoneyPrecisionError
# [TESTS] tests/trading/
# [TTL] permanent

from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport
from zephyr.trading.trading_contracts.portfolio.contracts.money import (
    Money,
    MoneyCurrencyMismatchError,
    MoneyPrecisionError,
    get_currency_precision,
)
from zephyr.trading.trading_contracts.portfolio.contracts.strategy_lifecycle_event import StrategyLifecycleEvent

__all__ = [
    "Money",
    "MoneyCurrencyMismatchError",
    "MoneyPrecisionError",
    "PerformanceAttributionReport",
    "StrategyLifecycleEvent",
    "get_currency_precision",
    "money",
    "performance_attribution_report",
    "strategy_lifecycle_event",
]
