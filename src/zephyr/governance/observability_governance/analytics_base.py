# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.governance.observability_governance.analytics_base
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.reporting.analytics_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; canonical at zephyr.reporting.analytics_base
# [MODIFY-GUARD] truth source at zephyr.reporting.analytics_base
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L07-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: analytics_base canonical at zephyr.reporting.analytics_base.

收敛双源——reporting.analytics_base 为真源（蓝图 MOD-L07-001 submodule_path=src/zephyr/reporting），
本模块仅 re-export 以保持向后兼容。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: shim 导入请求
#   fields: import zephyr.governance.observability_governance.analytics_base
#   code: L23 from-import
# 层: 算法
# - id: A1
#   name_zh: 真源透传
#   name_en: ssot_reexport
#   intro: 无逻辑——两个引擎基类从 zephyr.reporting.analytics_base 真源原样再导出
# 层: 输出
# - id: O1
#   name_zh: 兼容符号
#   name_en: compat_symbols
#   intro: AttributionEngineBase / TCAEngineBase
#   downstream: 存量旧路径消费者
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from zephyr.reporting.analytics_base import AttributionEngineBase, TCAEngineBase

__all__ = ["AttributionEngineBase", "TCAEngineBase"]
