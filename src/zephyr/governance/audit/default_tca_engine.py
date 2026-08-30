# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.governance.audit.default_tca_engine
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.reporting.default_tca_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; canonical at zephyr.reporting.default_tca_engine
# [MODIFY-GUARD] truth source at zephyr.reporting.default_tca_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L07-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Re-export wrapper: default_tca_engine canonical at zephyr.reporting.default_tca_engine.

收敛双定义——reporting.default_tca_engine 为真源（蓝图 MOD-L07-001），
本模块仅 re-export 以保持向后兼容。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: default_tca_engine.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 DefaultTCAEngine（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: DefaultTCAEngine
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.reporting.default_tca_engine import DefaultTCAEngine

__all__ = ["DefaultTCAEngine"]
