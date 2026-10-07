# [BLUEPRINT] MOD-BT-237 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.accel
# [DOMAIN] D_BACKTEST
# [TTL] permanent
"""D_BACKTEST 统计加速核子包（bootstrap 统一族 xp 纯函数核）。

提供 walk_forward WRC / E2 Sharpe 差 / G07 多元相关 bootstrap 三热循环的
向量化核（numpy/cupy 同一 xp 代码路径），判定面不入核。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/accel__init__.yaml
# A1 --> O1
"""

from typing import Final

from zephyr.backtest.accel.bootstrap_kernel import (
    BACKEND_ENV,
    corr_boot_pair_stats,
    degrade_log,
    e2_boot_sharpe_diffs,
    resolve_backend,
    stationary_bootstrap_index_matrix,
    wrc_boot_tstats,
)

__all__: Final = [
    "BACKEND_ENV",
    "corr_boot_pair_stats",
    "degrade_log",
    "e2_boot_sharpe_diffs",
    "resolve_backend",
    "stationary_bootstrap_index_matrix",
    "wrc_boot_tstats",
]
