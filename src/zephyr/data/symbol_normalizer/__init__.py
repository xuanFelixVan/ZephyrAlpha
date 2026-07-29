# [BLUEPRINT] MOD-L00-004 | docs/03_modules/ | §symbol_normalizer
# [MODULE] zephyr.data.symbol_normalizer
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.market_data.normalized_market_data_producer.producer; zephyr.data.c1_market_writer; zephyr.data.symbol_normalizer.normalizer (内部)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] symbol 标准化唯一真源（TRAE-082）；裸码 symbol + exchange 列 + 派生 symbol_canonical 三字段模型；前缀推断幂等（已带后缀原样返回）；纯函数无副作用
# [MODIFY-GUARD] schema-change（exchange 推导规则变更需同步 TRAE-082 + provider 写入路径）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入→空输出；未知前缀→exchange=None（不擅自推断）
# [TESTS] tests/data/test_symbol_normalizer.py
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-001 TRAE-082 #ARCH-SYMBOL-NORMALIZE-001
"""Symbol 标准化模块——TRAE-082 symbol 约定铁律的实现真源。

治本 #ARCH-DATA-SYMBOL-001：000001 裸码跨表碰撞（kline_daily 平安银行 vs kline_index 上证指数）。
三字段模型：symbol(裸码) + exchange(交易所码) + symbol_canonical(派生 = symbol.exchange)。

本模块集中 symbol 标准化逻辑（单一真源），替代散落在 producer/writer 中的重复实现：
  - derive_exchange(symbol)：从裸码首位推导交易所码（A 股编码规则）
  - split_suffix_symbol(symbol)：拆分带后缀 symbol（159865.SZ → ('159865', 'SZ')）
  - split_prefix_symbol(symbol)：拆分前缀式 symbol（sh501001 → ('501001', 'SH')）
  - to_canonical(symbol, exchange)：构造 canonical key（600519 + SH → '600519.SH'）
  - normalize_symbol(symbol)：归一化任意格式为 (裸码, exchange)

exchange 码体系（TRAE-082）：
  A 股：SH / SZ / BJ
  港股：HK
  美股：US
  期货：CFFEX / SHFE / CZCE / DCE / INE / GFEX

前缀推断规则（A 股标准编码，对标 tushare ts_code 后缀）：
  6/9 → SH（沪市股票：600519 / 900901 B 股）
  0/3 → SZ（深市股票：000001 / 300750）
  5   → SH（沪市基金/ETF：510050 / 588000 / 501001 LOF）
  1   → SZ（深市基金/ETF：159915 / 150018 LOF）
  8/4 → BJ（北交所：830799 / 430047）
"""
from zephyr.data.symbol_normalizer.normalizer import (
    EXCHANGE_SH,
    EXCHANGE_SZ,
    EXCHANGE_BJ,
    EXCHANGE_HK,
    EXCHANGE_US,
    _PREFIX_TO_EXCHANGE,
    derive_exchange,
    split_suffix_symbol,
    split_prefix_symbol,
    to_canonical,
    normalize_symbol,
    is_bare_symbol,
)

__all__ = [
    "EXCHANGE_SH",
    "EXCHANGE_SZ",
    "EXCHANGE_BJ",
    "EXCHANGE_HK",
    "EXCHANGE_US",
    "derive_exchange",
    "split_suffix_symbol",
    "split_prefix_symbol",
    "to_canonical",
    "normalize_symbol",
    "is_bare_symbol",
]
