# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DFE
# [MODULE] zephyr.factor.core.dist_feature_eng
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.factor_dag; zephyr.factor.core.backpressure; zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层间串行（依赖约束）；层内跨标的并行（ProcessPoolExecutor）；max_workers=1 退化为串行
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单标的失败不阻断其他标的；子进程入口 compute_factor_for_symbol 必须可 pickle
# [TESTS] tests/factor/test_dist_feature_eng.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core dist_feature_eng 子包——分布式特征工程引擎。

用 ProcessPoolExecutor 跨进程并行计算因子（绕开 GIL，适合 CPU 密集计算）。
按标的分片，每片在子进程内独立调用因子 compute。
"""

from __future__ import annotations

from zephyr.factor.core.dist_feature_eng.engine import (
    DistEngConfig,
    DistEngResult,
    DistributedFeatureEngine,
    compute_factor_for_symbol,
)

__all__ = [
    "DistEngConfig",
    "DistEngResult",
    "DistributedFeatureEngine",
    "compute_factor_for_symbol",
]
