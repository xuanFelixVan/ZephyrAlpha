"""[A_module] module_id=MOD-BT-001_core | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable"""

from zephyr.backtest.core.data_handler import BacktestDataHandler, DataHandlerError
from zephyr.backtest.core.decision_gate import (
    DecisionGate,
    DecisionGateConfig,
    DecisionGateError,
    DecisionGateResult,
)
from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)
from zephyr.backtest.core.matching_engine import MatchingConfig, MatchingEngine, MatchingError
from zephyr.backtest.core.metrics import (
    DEFAULT_RISK_FREE_RATE,
    calculate_dsr,
    calculate_full_metrics,
    calculate_ic_ir,
    calculate_metrics,
)
from zephyr.backtest.core.overfitting_detector import (
    OverfittingConfig,
    OverfittingDetector,
    OverfittingError,
)
from zephyr.backtest.core.pit_manager import PITConfig, PITError, PITManager
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio, PortfolioError, Position
from zephyr.backtest.core.walk_forward import (
    WalkForwardAnalyzer,
    WalkForwardConfig,
    WalkForwardError,
)

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
    "calculate_full_metrics",
    "calculate_dsr",
    "calculate_ic_ir",
    "DEFAULT_RISK_FREE_RATE",
    "Portfolio",
    "Position",
    "BacktestFill",
    "PortfolioError",
    "PITManager",
    "PITConfig",
    "PITError",
    "OverfittingDetector",
    "OverfittingConfig",
    "OverfittingError",
    "WalkForwardAnalyzer",
    "WalkForwardConfig",
    "WalkForwardError",
    "DecisionGate",
    "DecisionGateConfig",
    "DecisionGateError",
    "DecisionGateResult",
    "engine_base",
]
