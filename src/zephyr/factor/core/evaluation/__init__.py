# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-03
# [MODULE] zephyr.factor.core.evaluation
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——IC计算仅使用同期因子值与已实现前向收益，禁止未来函数
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/factor/test_evaluation_metrics.py; tests/factor/test_evaluation_backtest.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-03 因子评估包——IC/IR/OOS 正率/过拟合检测。

子模块：
- metrics: 纯函数模块（无 IO 依赖），可独立用合成数据测试
- backtest: 回测运行器，封装 ch_reader 数据访问 + metrics 计算

设计原则：
- metrics.py 是纯函数，无 IO 依赖，可完全用合成数据测试
- backtest.py 封装数据访问，metrics.py 做计算——职责分离
- INV-004 PIT 铁律：backtest 使用 ch_reader（自动注入 FINAL）保证去重
"""

from __future__ import annotations

from zephyr.factor.core.evaluation.backtest import (
    EvaluationResult,
    evaluate_factor,
    load_history,
)
from zephyr.factor.core.evaluation.metrics import (
    check_overfitting,
    compute_ic,
    compute_ic_series,
    compute_ir,
    compute_oos_positive_rate,
)

__all__ = [
    "EvaluationResult",
    "check_overfitting",
    "compute_ic",
    "compute_ic_series",
    "compute_ir",
    "compute_oos_positive_rate",
    "evaluate_factor",
    "load_history",
]
