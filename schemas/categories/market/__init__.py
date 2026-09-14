# [BLUEPRINT] MOD-L04-001 | schemas/categories/market/__init__.py | §
# [MODULE] schemas.categories.market
# [DOMAIN] D_DATA
# [TTL] permanent
"""A 股行情与另类数据 DDL 真源子目录（market_*，92+ 文件，2026-09-14 第二批拆分）。

范围：个股/指数/板块/两融/龙虎榜/日历/港股美股/期权期货/另类数据等 market_ 前缀全量——
不含 market_kline_*（kline/ 持有）与盘中微结构（intraday/ 持有）。
新表落位：market_*（非 kline/非盘中微结构）一律入本目录（见上级 __init__.py 前缀约定）。
"""
