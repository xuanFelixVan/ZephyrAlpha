# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.governance.strategies.strategy_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.strategy_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:OCP-002-REGISTRY ====
# ---
# domain: pf_core
# category: ocp_extension
# status: auto_generated
# created: "2026-05-05"
# ---
"""
StrategyRegistry 卫星模块（OCP-002）

仅从 ``strategy_base`` re-export，使 ``registry_path`` 与包内 import 习惯一致。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: strategy_registry.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 StrategyBase, StrategyMeta, StrategyRegistry（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: StrategyBase, StrategyMeta, StrategyRegistry
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from .strategy_base import StrategyBase, StrategyMeta, StrategyRegistry

__all__ = ["StrategyBase", "StrategyMeta", "StrategyRegistry"]

# ==== END CODGEN:OCP-002-REGISTRY ====
