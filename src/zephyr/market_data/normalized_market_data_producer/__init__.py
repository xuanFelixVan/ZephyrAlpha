# [BLUEPRINT] MOD-MKT_DATA | docs/03_modules/MOD-MKT_DATA/ | §normalized_market_data_producer
# [MODULE] zephyr.market_data.normalized_market_data_producer
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.core.ctr001_consumer.converter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CP-03门禁：产出NormalizedMarketData实例供D_FACTOR消费; INV-004 PIT铁律(ch_reader注入FINAL)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/market_data/test_normalized_market_data_producer.py
# [A_module] module_id=MOD-MKT_DATA | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
NormalizedMarketData 生产者包——D_MKT_DATA→D_FACTOR 数据供给。

从 ClickHouse c1_market.kline_daily 加载日K，转为 CTR-001 NormalizedMarketData，
供 D_FACTOR 的 ctr001_consumer 消费。

公共接口：
- load_kline(symbols, start, end): 加载并转换
- produce(symbols, start, end): load_kline 的业务语义别名（对齐 CP-03 门禁命名）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, load_kline, produce
#   code: __init__.py import L54
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 load_kline, produce（共 2 符号）
#   desc: __init__ import L54；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: load_kline, produce
#   downstream: zephyr.factor.core.ctr001_consumer.converter
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.market_data.normalized_market_data_producer.producer import (
    load_kline,
    produce,
)

__all__ = ["load_kline", "produce"]
