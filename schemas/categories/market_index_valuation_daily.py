# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_index_valuation_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.c1_market_writer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] index_valuation_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""index_valuation_daily 表 DDL-as-Code（category_id: market_index_valuation_daily, calc_mode: preload）。

本文件是 c1_market.index_valuation_daily 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

来源：S2 估值"路A"指数级估值管道新建表（2026-08-28 S2 治本方案 §5.1）。
    不复用个股级 daily_valuation（粒度语义不符），Owner 已裁定③新建独立表。
    主源：akshare stock_zh_index_hist_csindex（中证官网，含滚动市盈率/股息率）。
    fallback：akshare stock_index_pe_lg（乐咕月度，交叉验证）。
    内部计算列：CAPE/分位/ERP 由 internal compute 管道产出。

TRAE-082 派生列适用性说明：
    本表含 symbol 列（指数代码 000300/000905/399006），属 securities 表范畴，
    但指数代码无交易所后缀语义（000300 非个股），exchange/symbol_canonical
    MATERIALIZED 派生规则不适用——参照同库无个股语义表先例
    （market_index_kline/market_index_meta）不挂 TRAE-082 派生列；
    惯例遵循点=data_source LowCardinality + ingest_ts DateTime64(3,'UTC') DEFAULT now()
    审计列（audit 1.7 #ARCH-CH-025）+ ReplacingMergeTree + 月分区。

引擎选型说明：
    日频指数估值快照写入表（daily_kline 族增量），ReplacingMergeTree 按
    (symbol, trade_date) 去重——同日重跑/补跑同键静默替换，无写前 DELETE 开销
    （同 daily_valuation/money_flow 等日频表选型口径）。

口径备注：
    - pe_ttm 为中证官网滚动市盈率（市盈率2，TTM 口径）；pb_mrq 一期暂缺（乐咕
      月度 PB 频率不足，二期升级）。
    - cape_5y 为 5 年真 CAPE（非 PE 中位平滑近似），Earnings E_i=P_i/PE_i，
      real E_i=E_i/CPI_i，CAPE_t=P_t/mean_{近5年}(real E×CPI_t)。
    - cape_5y_pct / pe_pct / pb_pct 为全历史扩展窗分位（expanding percentile）。
    - erp = 1/PE_TTM - 10Y国债收益率（百分数口径），erp_pct 为其全历史分位。
    - broken_net_ratio / buffett_ratio 为二期预留字段，一期恒 NULL。
"""

from __future__ import annotations

from typing import Final

# category_id: market_index_valuation_daily
# calc_mode: preload

MARKET_INDEX_VALUATION_DAILY_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.index_valuation_daily
(
    trade_date       Date                     COMMENT '交易日期',
    symbol           String                   COMMENT '指数代码(000300/000905/399006)',
    pe_ttm           Decimal(18, 4)           COMMENT '市盈率TTM(中证官网滚动市盈率)',
    pb_mrq           Nullable(Decimal(18, 4)) COMMENT '市净率MRQ(一期暂缺,二期升级)',
    dividend_yield   Nullable(Decimal(18, 4)) COMMENT '股息率(中证官网股息率1,%)',
    cape_5y          Nullable(Decimal(18, 4)) COMMENT '5年真CAPE(P_t/mean_5y(real_E))',
    cape_5y_pct      Nullable(Decimal(18, 4)) COMMENT 'CAPE_5Y全历史分位(0~1)',
    pe_pct           Nullable(Decimal(18, 4)) COMMENT 'PE_TTM全历史分位(0~1)',
    pb_pct           Nullable(Decimal(18, 4)) COMMENT 'PB全历史分位(0~1,一期暂缺)',
    erp              Nullable(Decimal(18, 4)) COMMENT '股权风险溢价(1/PE-10Y国债,%)',
    erp_pct          Nullable(Decimal(18, 4)) COMMENT 'ERP全历史分位(0~1)',
    broken_net_ratio Nullable(Decimal(18, 4)) COMMENT '全市场破净率(二期预留)',
    buffett_ratio    Nullable(Decimal(18, 4)) COMMENT '总市值/GDP(二期预留)',
    data_source      LowCardinality(String)   DEFAULT 'akshare_csindex' COMMENT '数据来源',
    ingest_ts        DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "index_valuation_daily"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_index_valuation_daily"
CALC_MODE: Final = "preload"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS: Final = (
    "(trade_date, symbol, pe_ttm, pb_mrq, dividend_yield, "
    "cape_5y, cape_5y_pct, pe_pct, pb_pct, erp, erp_pct, "
    "broken_net_ratio, buffett_ratio, data_source)"
)
