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
"""
D_FACTOR core factor_dag 子包——因子 DAG 数据结构 + Kahn 拓扑分层。

提供 FactorNode / FactorEdge / FactorDAG 数据结构及 build_dag_from_registry 工具。
是 dag_manager 和 dist_feature_eng 的基础。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, FactorDAG, FactorEdge, FactorNode, build_dag_from_regist…
#   code: __init__.py import L50
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 FactorDAG, FactorEdge, FactorNode, build_dag_from_registry（共 4 符号）
#   desc: __init__ import L50；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: FactorDAG, FactorEdge, FactorNode, build_dag_from_registry
#   downstream: zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.factor.core.factor_dag.dag import (
    FactorDAG,
    FactorEdge,
    FactorNode,
    build_dag_from_registry,
)

__all__ = ["FactorDAG", "FactorEdge", "FactorNode", "build_dag_from_registry"]
