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

# 波12 统一跑批窗口（MOD-BT-226）静态依赖边声明——TYPE_CHECKING 块运行时零执行。
# 运行时消费方=scripts/backtest/compute_window_gate.py（E0 问闸，scripts/ 不在
# ORPHAN-MODULE 的 src/**/*.py 搜索范围）——按 src/zephyr/governance/audit/
# reconciliation_registry.py 同款先例在 src 面声明真实依赖边，防新模块被判孤儿
# （实证死信 q-20260928-st-zcloseout-20260926-0004/0005 同族）。
from typing import TYPE_CHECKING  # noqa: I001

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

if TYPE_CHECKING:
    from zephyr.backtest.core import batch_window_preflight  # noqa: F401

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
