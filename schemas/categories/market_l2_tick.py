# [BLUEPRINT] MOD-L04-002 | docs/03_modules/_cross_layer/database/business_data_categories.yaml | §market_l2_tick
# [MODULE] schemas.categories.market_l2_tick
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl.py; zephyr.data.implementations.miniqmt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] l2_tick 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
# [ERROR_CONTRACT] DDL 变更需备份+trae_063三步验证；列类型变更走 ALTER MODIFY COLUMN
# [TESTS] scripts/ch/verify_schema_truth.py
# [A_module] module_id=MOD-L04-002 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [DR_ENFORCEMENT] NEW-FILE-DEPGRAPH-ENFORCEMENT
# [DOC_LINK] docs/02_enterprise_architecture/code_wiki/audit_02_pipeline_review.md §l2_tick
# [RULE_LINK] trae_063_data_ops_discipline.yaml
# [ISSUE_LINK] #ARCH-DATA-PIPELINE-001 l2_tick 子项
"""

l2_tick 表 DDL-as-Code（category_id: market_l2_tick, calc_mode: replay）。

本文件是 c1_market.l2_tick 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

设计决策（2026-07-28 建表，裁定 #ARCH-DATA-PIPELINE-001 l2_tick 子项）：
1. 背景：audit_02 P0-4 指出 l2_tick 表不存在但 tasks.yaml l2_tick_snapshot 任务引用，
   miniqmt_provider.fetch_l2_tick 已实现（line 3483）写入 9 列。表缺失导致写入必然失败。
   裁定建表治本（数据源就绪，摘除是回避）。
2. 字段对齐 fetch_l2_tick 写入列（miniqmt_provider.py:3514-3517）：
   trade_date, timestamp, symbol, price, volume, amount, bid_price, ask_price, data_source
   其余列靠 DEFAULT 自动填充（治理列 market_type/quality_flag/ingest_ts/recorded_time + L2 买卖量）。
3. 与 tick_data 风格对齐（#ARCH-CH-028 跳数索引 + #ARCH-CH-022 时区防线）：
   - ORDER BY (market_type, symbol, trade_date, timestamp, price) 与 tick_data 一致
   - INDEX idx_ts minmax + idx_symbol set(10000) 解决单标的裁剪（ORDER BY market_type 前缀）
   - timestamp DateTime64(3,'Asia/Shanghai') 业务墙钟；recorded_time/ingest_ts DateTime64(3,'UTC') 真 UTC
4. L2 逐笔特性：bid_volume/ask_volume Nullable（L2 报价含买卖量，当前 fetch_l2_tick 仅取首价，
   量列预留供未来 _parse_l2_records 扩展）。
5. ReplacingMergeTree（无版本列）：5 字段完全重复行自动合并（数据源重复导入保护）。
6. PARTITION BY toYYYYMM(trade_date) 月级分区（L2 数据量极大，日级分区过多）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: miniqmt L2逐笔 写入数据
#   fields: 9列 trade_date/timestamp/symbol/price/volume/amount/bid_price/ask_price/data_source
#   code: INSERT_COLUMNS L88-91（对齐 miniqmt_provider.fetch_l2_tick 写入列）
# 层: 算法
# - id: A1
#   name_zh: ① l2_tick 表DDL定义
#   name_en: L2_TICK_DDL
#   intro: 用DDL-as-Code定义ClickHouse逐笔表结构，是唯一真源
#   desc: ReplacingMergeTree（无版本列自动去重）+ PARTITION BY toYYYYMM(trade_date) 月分区 + ORDER BY (market_type,symbol,trade_date,timestamp,price) + idx_ts minmax / idx_symbol set(10000) 跳数索引（L47-75）
#   inputs: I1
#   outputs: c1_market.l2_tick 建表DDL
#   invariant: 本文件DDL必须与ClickHouse实际表结构一致，变更走 apply_market_tables_ddl.py
# - id: A2
#   name_zh: ② 交易所码派生
#   name_en: exchange MATERIALIZED 列
#   intro: 按证券代码前缀自动推导交易所
#   desc: multiIf 链按 symbol 数字前缀判 SH/SZ/BJ（如 5/6/9→SH，0/1/2/3→SZ，4/8→BJ）（L68）
#   inputs: I1
#   outputs: exchange 列（SH/SZ/BJ）
# - id: A3
#   name_zh: ③ canonical身份键派生
#   name_en: symbol_canonical MATERIALIZED 列
#   intro: 给无点符号拼上交易所后缀，供跨表JOIN
#   desc: symbol 含点原样保留，否则 concat(去前缀代码, '.', exchange)（L69）
#   inputs: I1 A2
#   outputs: symbol_canonical 列
# 层: 输出
# - id: O1
#   name_zh: l2_tick 表结构元数据
#   name_en: TABLE_NAME/DATABASE/INSERT_COLUMNS 等常量
#   intro: 对外暴露表名、库名、引擎、分区键、排序键与写入列清单
#   invariant: l2_tick 表 DDL 唯一真源
#   downstream: apply_market_tables_ddl.py 执行DDL / zephyr.data.implementations.miniqmt_provider 写入（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A2 --> A3
# A1 --> O1
# A3 --> O1
"""

from __future__ import annotations

# category_id: market_l2_tick
# calc_mode: replay（回测时逐笔回放，L2 微观结构）

L2_TICK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.l2_tick
(
    trade_date    Date                    COMMENT '交易日期',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '时间戳(毫秒级逐笔)',
    recorded_time DateTime64(3, 'UTC')  DEFAULT now() COMMENT '录制器本地接收时间(延迟分析)',
    symbol        String                  COMMENT '证券代码',
    market_type   LowCardinality(String)  DEFAULT '' COMMENT '市场类型(A_share/futures/index)',
    price         Decimal(18,4)           COMMENT '成交价',
    volume        UInt64                  COMMENT '成交量(股)',
    amount        Decimal(18,2)           COMMENT '成交额(元)',
    direction     LowCardinality(String)  DEFAULT '' COMMENT '买卖方向(买/卖/中性)',
    bid_price     Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price     Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume    Nullable(UInt64)        COMMENT '买一量',
    ask_volume    Nullable(UInt64)        COMMENT '卖一量',
    data_source   LowCardinality(String)  DEFAULT 'miniqmt' COMMENT '数据来源',
    quality_flag  UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1,
    INDEX idx_symbol symbol TYPE set(10000) GRANULARITY 4,
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "l2_tick"
DATABASE = "c1_market"
CATEGORY_ID = "market_l2_tick"
CALC_MODE = "replay"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(market_type, symbol, trade_date, timestamp, price)"

# 列清单（fetch_l2_tick 写入的 9 列，其余列由 DEFAULT 填充）
# 对齐 miniqmt_provider.fetch_l2_tick columns 定义
INSERT_COLUMNS = "(trade_date, timestamp, symbol, price, volume, amount, bid_price, ask_price, data_source)"
