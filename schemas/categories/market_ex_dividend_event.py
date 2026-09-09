# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_ex_dividend_event
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider(_fetch_stk_limit 公式法除权修正)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] ex_dividend_event 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""ex_dividend_event 表 DDL-as-Code（category_id: ex_dividend_event, calc_mode: preload）。

本文件是 c3_fundamental.ex_dividend_event 表结构的唯一真源（DDL-as-Code 模式）。

背景（2026-09-09 长城任务方案 D，Owner 立项）：
    c3_fundamental.dividend（东财研究口径 20 列）与 miniqmt _fetch_dividend（6 列要素口径）
    schema 不匹配 → dividend_incremental 任务写入持续失败 → 表 2026-07-13 后断供。
    裁定：除权修正要素独立成表（QMT get_divid_factors 口径，含配股要素与 dr 综合
    除权因子），stk_limit 公式法直接消费 dr（pre_close = prev_close / dr），摆脱
    adj_factor 因子洞依赖；dividend 东财研究表的 7/14 起缺口登记 follow-up（无消费方）。

    dr 语义实证：600000.SH 2026-07-16 行 dr=1.047244，prev_close=9.29 → 除权参考价
    9.29/1.047244≈8.87（每股派现 0.42 元官方公式吻合）。

列清单：
#   trade_date: Date              除权除息日
#   symbol: String
#   divid_per_share: 每股税前派现（interest）
#   bonus_per_share: 每股送股比例（stockBonus）
#   gift_per_share: 每股转增比例（stockGift）
#   allot_ratio: 每股配股比例（allotNum）
#   allot_price: 配股价（allotPrice）
#   dr: 当日综合除权因子 = 昨收/除权参考价
#   gugai: 股改因子（历史遗留，恒 0 备档）
#   data_source: String
#   quality_flag: UInt8
#   ingest_ts: DateTime64(3, 'UTC')
"""

from __future__ import annotations

# category_id: ex_dividend_event
# calc_mode: preload

MARKET_EX_DIVIDEND_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.ex_dividend_event
(
    trade_date               Date,
    symbol                   String  COMMENT '6位数字证券代码',
    divid_per_share          Nullable(Decimal(12, 6))  COMMENT '每股税前派现(interest)',
    bonus_per_share          Nullable(Decimal(12, 6))  COMMENT '每股送股比例(stockBonus)',
    gift_per_share           Nullable(Decimal(12, 6))  COMMENT '每股转增比例(stockGift)',
    allot_ratio              Nullable(Decimal(12, 6))  COMMENT '每股配股比例(allotNum)',
    allot_price              Nullable(Decimal(12, 6))  COMMENT '配股价(allotPrice)',
    dr                       Nullable(Decimal(18, 10))  COMMENT '当日综合除权因子=昨收/除权参考价',
    gugai                    Nullable(Decimal(12, 6))  COMMENT '股改因子(历史遗留)',
    data_source              String,
    quality_flag             UInt8  DEFAULT 1,
    ingest_ts                DateTime64(3, 'UTC')  DEFAULT now(),
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
"""

# 表元数据
TABLE_NAME = "ex_dividend_event"
DATABASE = "c3_fundamental"
CATEGORY_ID = "ex_dividend_event"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = ("(trade_date, symbol, divid_per_share, bonus_per_share, gift_per_share, "
                  "allot_ratio, allot_price, dr, gugai, data_source)")
