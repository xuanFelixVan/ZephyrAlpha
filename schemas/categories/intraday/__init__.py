# [BLUEPRINT] MOD-L04-001 | schemas/categories/intraday/__init__.py | §
# [MODULE] schemas.categories.intraday
# [DOMAIN] D_DATA
# [TTL] permanent
"""盘中微结构 DDL 真源子目录（10+ 文件）。

范围：tick 及逐档深度（market_tick/market_tick_depth_5）、L2 逐笔
（market_l2_tick）、集合竞价（market_auction/market_auction_book）、
大宗交易（market_block_trade*）、成交回报（market_execution_report）、
资金流（market_money_flow）、实时快照（market_realtime_snapshot）。
新表落位：盘中微结构新表一律入本目录（见上级 __init__.py 前缀约定）。
"""
