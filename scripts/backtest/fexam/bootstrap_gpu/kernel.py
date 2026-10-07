# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | bootstrap统一族GPU核（薄 re-export）
# [MODULE] scripts.backtest.fexam.bootstrap_gpu.kernel.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.accel.bootstrap_kernel
# [CONSUMERS] run_fexam.py 或手工 CLI；tests/backtest/fexam/test_bootstrap_gpu_parity.py
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 真源已迁移 src/zephyr/backtest/accel/bootstrap_kernel.py（MOD-BT-237）；
#   本件只 re-export 保旧 import 路径（st-mx07-L3 P1-3 接线），语义零分叉
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 随真源（见 zephyr.backtest.accel.bootstrap_kernel docstring）
# [TESTS] tests/backtest/fexam/；tests/backtest/test_bootstrap_kernel_wiring.py
# [TTL] permanent
# create-guard-not-dup: 真源迁移转正后的兼容 re-export 门面（同一能力唯一真源在 src 侧）
# -*- coding: utf-8 -*-
"""bootstrap 统一族 xp 纯函数核——薄 re-export 门面（真源=src/zephyr/backtest/accel/bootstrap_kernel.py）。

st-mx07-L3 P1-3 接线：核体迁入 src（MOD-BT-237）供 walk_forward WRC /
E2 stationary bootstrap / G07 多元相关 bootstrap 三处内循环消费；
本文件保持 `from bootstrap_gpu.kernel import ...` 旧 import 路径可用，
全部公共名零丢失、语义零分叉（同一模块对象，无复制体）。
"""

from zephyr.backtest.accel.bootstrap_kernel import (  # noqa: F401  re-export 门面
    BACKEND_ENV,
    corr_boot_pair_stats,
    degrade_log,
    e2_boot_sharpe_diffs,
    resolve_backend,
    stationary_bootstrap_index_matrix,
    wrc_boot_tstats,
)

__all__ = [
    "BACKEND_ENV",
    "degrade_log",
    "resolve_backend",
    "stationary_bootstrap_index_matrix",
    "wrc_boot_tstats",
    "e2_boot_sharpe_diffs",
    "corr_boot_pair_stats",
]
