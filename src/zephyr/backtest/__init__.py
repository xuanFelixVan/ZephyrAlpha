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
# v1.3.0 新增 io/ 子包（#ARCH-047, 配合前端 Streamlit→Panel+HoloViz 重构）
from zephyr.backtest.io import (
    ArtifactNotFoundError,
    BacktestSinkData,
    BacktestRunArtifact,
    build_artifact_from_data,
    get_artifact,
    list_artifacts,
    save_artifact,
    sink_backtest_result,
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
    # v1.3.0 新增（#ARCH-047）
    "io",
    "BacktestSinkData",
    "BacktestRunArtifact",
    "ArtifactNotFoundError",
    "sink_backtest_result",
    "save_artifact",
    "get_artifact",
    "list_artifacts",
    "build_artifact_from_data",
]
