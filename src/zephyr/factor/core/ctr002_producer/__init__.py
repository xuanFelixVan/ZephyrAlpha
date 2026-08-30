# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr002_producer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.factor_signal
# [CONSUMERS] zephyr.signal_fundamental.pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——as_of_date必须对齐因子计算的数据截面日期
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/factor/test_ctr002_producer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-002 FactorSignal 生产者包入口。

导出公共 API:
- to_signals: pd.Series → list[FactorSignal]

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: to_signals
#   code: __init__.py import L50
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 to_signals（共 1 符号）
#   desc: __init__ import L50；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: to_signals
#   downstream: zephyr.signal_fundamental.pipeline
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.factor.core.ctr002_producer.converter import to_signals

__all__ = ["to_signals"]
