# [BLUEPRINT] MOD-BT-018 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""

[A_module] module_id=MOD-BT-001 | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable

ZephyrAlpha — D_BACKTEST 回测引擎域

SSoT: docs/03_modules/_domain_backtest/blueprint.md (MOD-BT-001)

架构归属: D_BACKTEST域 (depgraph编号24)
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/backtest__init__.yaml
# I3 --> A1
# A1 --> O1
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

# v1.3.0 新增 io/ 子包（#ARCH-047, 配合前端 Streamlit->Panel+HoloViz 重构）
from zephyr.backtest.io import (
    ArtifactNotFoundError,
    BacktestRunArtifact,
    BacktestSinkData,
    build_artifact_from_data,
    get_artifact,
    list_artifacts,
    save_artifact,
    sink_backtest_result,
)

# SOP-D run 过程档案图书馆 API（R1 裁定：落盘走 API 禁手 mkdir）
from zephyr.backtest.run_archive import (
    RunArchiveError,
    create_run,
    finalize_run,
    iter_run_ids,
    load_meta,
    log_iteration,
    write_step,
)

__all__ = [
    "BacktestEngineBase",
    "BacktestResult",
    "FactorDiscovery",
    "BacktestConfig",
    "DefaultBacktestEngine",
    "core",
    "implementations",
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
    # SOP-D run 档案图书馆（R1）
    "RunArchiveError",
    "create_run",
    "write_step",
    "finalize_run",
    "load_meta",
    "log_iteration",
    "iter_run_ids",
]
