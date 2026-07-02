"""[A_module] module_id=MOD-BT-001 | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable

ZephyrAlpha — D_BACKTEST 回测引擎域

SSoT: docs/03_modules/_domain_backtest/blueprint.md (MOD-BT-001)

架构归属: D_BACKTEST域 (depgraph编号24)
架构决策: 回测引擎统一归口D_BACKTEST,消除research/intelligence/rollback多处置放
"""

from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

__all__ = [
    "BacktestEngineBase",
    "BacktestResult",
    "FactorDiscovery",
    "BacktestConfig",
    "DefaultBacktestEngine",
    "core",
    "engine_base",
    "implementations",
    "vectorized_engine",
]
