# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_convertible_bond_clause
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] market_convertible_bond_clause 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""market_convertible_bond_clause（可转债条款日快照：强赎/触发/到期/最后交易）DDL-as-Code
（category_id: market_convertible_bond_clause）.

altdata_line 09 清单 D6 行情补充·A10 可转债族条款层（2026-09-18 夜班施工，st-datapack-20260918）。
全市场存续/强赎进程转债的条款状态日快照：强赎触发价/触发比/天计数、强赎状态
（已公告强赎/临近到期/基本面差被炒作等源端标签）、最后交易日、到期日、转股价等。

设计要点：**快照积累制**——每日一行/券，条款状态随时间变化（触发→公告→停止交易），
历史快照保留状态演变轨迹（消费端可回看"某日该券处于什么条款状态"）；
状态时点语义由 snapshot_date 承担（PIT 诚实锚：状态自观察日起才可知）。

源：akshare bond_cb_redeem_jsl（集思录可转债强赎汇总页，免费无 key）。
实测（2026-09-18）：~315 券 × 18 列（代码/名称/正股/规模/转股起止/到期/转股价/
强赎触发比/触发价/强赎价/天计数/条款原文/状态）。强赎天计数形如"21/15 | 30"
（已满足/需要天数 | 统计窗口）如实字符串存储。

与既有可转债表族的关系（查重声明）：
    convertible_bond_list=发行清单（bond_zh_cov 口径，月初刷新）；
    kline_cb=转债日 K 线（新浪）；convertible_bond_iv=隐含波动率派生；
    本表=条款/强赎状态层（集思录口径），互不重叠不构成双真源。
    回售条款（面值+利息回售触发）：源端本接口未含回售计数，挂账 DS-CAND（bond_zh_cov_info
    逐券条款原文可评估后续解析）。

PIT 双轴：snapshot_date=观察日（事实时间锚）；ingest_ts=采集时间。
单位：规模/剩余规模=亿元（源端原始口径）；价格列=元。

引擎选型：ReplacingMergeTree（同 (snapshot_date, bond_code) 幂等替换）。
PARTITION BY toYYYYMM(snapshot_date)。ORDER BY (snapshot_date, bond_code)。
"""

from __future__ import annotations

# category_id: market_convertible_bond_clause
# calc_mode: preload

MARKET_CONVERTIBLE_BOND_CLAUSE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_convertible_bond_clause
(
    snapshot_date       Date                        COMMENT '观察日(快照事实时间锚)',
    bond_code           LowCardinality(String)      COMMENT '转债代码(如 123258)',
    bond_name           String                      COMMENT '转债简称',
    stock_code          LowCardinality(String)      COMMENT '正股代码',
    stock_name          String                      COMMENT '正股简称',
    bond_price          Nullable(Decimal(12, 4))    COMMENT '转债现价(元;观察日快照)',
    scale               Nullable(Decimal(12, 4))    COMMENT '发行规模(亿元)',
    remain_scale        Nullable(Decimal(12, 4))    COMMENT '剩余规模(亿元)',
    conv_start_date     Nullable(Date)              COMMENT '转股起始日',
    last_trade_date     Nullable(Date)              COMMENT '最后交易日(强赎/到期停止交易锚)',
    maturity_date       Nullable(Date)              COMMENT '到期日',
    conv_price          Nullable(Decimal(12, 4))    COMMENT '转股价(元)',
    redeem_trigger_ratio Nullable(Decimal(10, 4))   COMMENT '强赎触发比(如 130=130%)',
    redeem_trigger_price Nullable(Decimal(12, 4))   COMMENT '强赎触发价(元)',
    stock_price         Nullable(Decimal(12, 4))    COMMENT '正股价(元;观察日快照)',
    redeem_price        Nullable(Decimal(12, 4))    COMMENT '强赎价(元;无值=未公告)',
    redeem_count_desc   String                      COMMENT '强赎天计数(源端原文,如 21/15 | 30)',
    redeem_clause       String                      COMMENT '强赎条款原文(源端如实)',
    redeem_status       LowCardinality(String)      COMMENT '强赎状态(已公告强赎/承诺不强赎/临近到期等,源端标签)',
    data_source         LowCardinality(String)      DEFAULT 'akshare_jsl' COMMENT '数据来源(akshare bond_cb_redeem_jsl=集思录)',
    quality_flag        UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts           DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(snapshot_date)
ORDER BY (snapshot_date, bond_code)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "market_convertible_bond_clause"
DATABASE = "c1_market"
CATEGORY_ID = "market_convertible_bond_clause"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(snapshot_date)"
ORDER_BY = "(snapshot_date, bond_code)"

INSERT_COLUMNS = (
    "(snapshot_date, bond_code, bond_name, stock_code, stock_name, bond_price, scale,"
    " remain_scale, conv_start_date, last_trade_date, maturity_date, conv_price,"
    " redeem_trigger_ratio, redeem_trigger_price, stock_price, redeem_price,"
    " redeem_count_desc, redeem_clause, redeem_status, data_source, quality_flag)"
)
