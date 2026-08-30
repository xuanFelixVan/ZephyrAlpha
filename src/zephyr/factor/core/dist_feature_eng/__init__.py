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
"""
D_FACTOR core dist_feature_eng 子包——分布式特征工程引擎。

用 ProcessPoolExecutor 跨进程并行计算因子（绕开 GIL，适合 CPU 密集计算）。
按标的分片，每片在子进程内独立调用因子 compute。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, DistEngConfig, DistEngResult, DistributedFeatureEngine,…
#   code: __init__.py import L50
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 DistEngConfig, DistEngResult, DistributedFeatureEngine, compute_factor_for_…
#   desc: __init__ import L50；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: DistEngConfig, DistEngResult, DistributedFeatureEngine, compute_factor_for_symb…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
