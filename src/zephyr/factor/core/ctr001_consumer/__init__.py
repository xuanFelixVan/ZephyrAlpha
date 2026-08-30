# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr001_consumer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.factor_base
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——仅使用timestamp做截面对齐
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/factor/test_ctr001_consumer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-001 NormalizedMarketData 消费者包入口。

导出公共 API:
- to_dataframe: NormalizedMarketData 列表 → pd.DataFrame
- filter_quality: 质量过滤

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: filter_quality, to_dataframe
#   code: __init__.py import L51
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 to_dataframe, filter_quality（共 2 符号）
#   desc: __init__ import L51；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: to_dataframe, filter_quality
#   downstream: zephyr.factor.factor_base
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.factor.core.ctr001_consumer.converter import filter_quality, to_dataframe

__all__ = ["to_dataframe", "filter_quality"]
