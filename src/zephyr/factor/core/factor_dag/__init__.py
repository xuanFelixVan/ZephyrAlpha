# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-DAG
# [MODULE] zephyr.factor.core.factor_dag
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DAG 必须无环（topological_layers 检测到环时抛 ValueError）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validate 返回错误列表（不抛）；topological_layers 检测到环抛 ValueError
# [TESTS] tests/factor/test_factor_dag.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core factor_dag 子包——因子 DAG 数据结构 + Kahn 拓扑分层。

提供 FactorNode / FactorEdge / FactorDAG 数据结构及 build_dag_from_registry 工具。
是 dag_manager 和 dist_feature_eng 的基础。
"""

from __future__ import annotations

from zephyr.factor.core.factor_dag.dag import (
    FactorDAG,
    FactorEdge,
    FactorNode,
    build_dag_from_registry,
)

__all__ = ["FactorDAG", "FactorEdge", "FactorNode", "build_dag_from_registry"]
