# [A_module] module_id=MOD-PRT-contracts_portfolio_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: PerformanceAttributionReport, Money, MoneyCurrencyMismatchError, Mone…
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Money, MoneyCurrencyMismatchError, MoneyPrecisionError, PerformanceAttribut…
#   desc: __init__ import L44；__all__ 9 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（9 符号）
#   name_en: __all__
#   intro: Money, MoneyCurrencyMismatchError, MoneyPrecisionError, PerformanceAttributionR…
#   downstream: reporting; ex_core
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport
from zephyr.shared.contracts.portfolio.money import (
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
