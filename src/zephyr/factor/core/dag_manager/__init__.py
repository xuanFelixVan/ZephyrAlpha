# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DM
# [MODULE] zephyr.factor.core.dag_manager
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.factor_dag; zephyr.factor.core.backpressure; zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层间串行（依赖约束）；层内并行（ThreadPoolExecutor）；上游失败下游跳过
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单因子失败不阻断同层其他因子；下游因子标记 upstream failed；超时标记 timeout
# [TESTS] tests/factor/test_dag_manager.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core dag_manager 子包——DAG 调度执行器。

输入 FactorDAG + 数据，按拓扑层串行推进、层内并发执行因子计算（ThreadPoolExecutor），
受 BackpressureLimiter 限流。适合 IO/轻计算场景。
"""

from __future__ import annotations

from zephyr.factor.core.dag_manager.executor import (
    DagExecutionReport,
    DagExecutor,
    DagExecutorConfig,
    FactorExecutionResult,
)

__all__ = [
    "DagExecutionReport",
    "DagExecutor",
    "DagExecutorConfig",
    "FactorExecutionResult",
]
