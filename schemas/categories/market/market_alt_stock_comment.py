# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_stock_comment
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_stock_comment 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""alt_stock_comment 表 DDL-as-Code（category_id: market_alt_stock_comment, calc_mode: preload）.

千股千评全表日快照（akshare stock_comment_em，东财数据中心），另类数据第 1 批施工
（docs/_working/2026-09-12-alt-data-handoff.md §8-1）。

口径说明：
    - 关注指数/综合得分/机构参与度/排名 = 东财数据中心综合评价（关注度含股吧流量代理，
      akshare 无股吧发帖量直连接口，2026-09-12 实测确认；人气榜通道 stock_hot_rank 已在跑）。
    - 每日快照累积（接口仅返回当日全市场约 5200 行，无历史回补通道），ReplacingMergeTree
      按 (trade_date, symbol) 幂等去重。
    - 最新价/涨跌幅/换手率/市盈率为 L1 既有字段（stock_indicator/kline_daily），不重复落库。

数据源：akshare stock_comment_em
    列: 序号/代码/名称/最新价/涨跌幅/换手率/市盈率/主力成本/机构参与度/综合得分/上升/目前排名/关注指数/交易日
"""

from __future__ import annotations

# category_id: market_alt_stock_comment
# calc_mode: preload（回测/分析时预加载到内存）

ALT_STOCK_COMMENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_stock_comment
(
    trade_date        Date               COMMENT '快照交易日',
    symbol            String             COMMENT '股票代码(6位)',
    name              String             COMMENT '股票名称',
    org_participation Nullable(Float64)  COMMENT '机构参与度(0-1)',
    composite_score   Nullable(Float64)  COMMENT '综合得分',
    rank_change       Nullable(Float64)  COMMENT '排名变动(正=上升)',
    current_rank      Nullable(Int64)    COMMENT '目前排名',
    attention_index   Nullable(Float64)  COMMENT '关注指数(0-100，股吧关注度代理)',
    main_cost         Nullable(Float64)  COMMENT '主力成本',
    exchange          LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)',
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_stock_comment"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_stock_comment"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, symbol)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, symbol, name, org_participation, composite_score, "
    "rank_change, current_rank, attention_index, main_cost)"
)
