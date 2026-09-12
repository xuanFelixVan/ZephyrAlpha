# [BLUEPRINT] MOD-L04-001 | schemas/categories/kline/__init__.py | §
# [MODULE] schemas.categories.kline
# [DOMAIN] D_DATA
# [TTL] permanent
"""K 线族 DDL 真源子目录（market_kline_*，32+ 文件）。

范围：全资产类（股票/ETF/LOF/可转债/指数/板块/期货/全球/港美）× 全频率
（1m/5m/15m/30m/60m/日/周/月，含 hfq 后复权变体）。
新表落位：market_kline_* 一律入本目录（见上级 __init__.py 前缀约定）。
"""
