"""[A_module] module_id=MOD-BT-001 | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable"""

from zephyr.backtest.core.data_handler import BacktestDataHandler, DataHandlerError
from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)
from zephyr.backtest.core.matching_engine import MatchingConfig, MatchingEngine, MatchingError
from zephyr.backtest.core.metrics import (
    DEFAULT_RISK_FREE_RATE,
    calculate_ic_ir,
    calculate_metrics,
)
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio, PortfolioError, Position

__all__ = [
    "BacktestEngineBase",
    "BacktestResult",
    "FactorDiscovery",
    "BacktestDataHandler",
    "DataHandlerError",
    "MatchingConfig",
    "MatchingEngine",
    "MatchingError",
    "calculate_metrics",
    "calculate_ic_ir",
    "DEFAULT_RISK_FREE_RATE",
    "Portfolio",
    "Position",
    "BacktestFill",
    "PortfolioError",
    "engine_base",
]
