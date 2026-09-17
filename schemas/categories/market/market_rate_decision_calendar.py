# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_rate_decision_calendar
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] rate_decision_calendar 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rate_decision_calendar（央行议息日历）DDL-as-Code（category_id: market_rate_decision_calendar）.

J5 议息日历（骨架 01 号文档 J 族/altdata_line 09 清单 D1 波1，2026-09-18 夜班施工）。
11 家主要央行利率决议的结构化数据集：决议日期 + 决议利率 + 市场预测值 + 前值。

源：AKShare macro_bank_*_interest_rate 11 接口（金十数据口径，利率单位=年化 %）：
    fed(usa)/ecb(euro)/pboc(china)/boj(japan)/boe(english)/rba(australia)/
    rbi(india)/rbnz(newzealand)/cbr(russia)/snb(switzerland)/bcb(brazil)。
注意：pboc 系列为 2019-10 前贷款基准利率口径（LPR 改革后停更属源端现实，非断供）。

与 c1_market.calendar_event 的关系（查重声明）：
    calendar_event.fomc_meeting 仅手工录入会议日期（无决议值，单央行）；
    本表为 11 央行×决议值的结构化数据集（回测口径不同：数值列+bank 维度），按
    骨架分类学判据 2（回测口径变了→拆）独立成表，不与 calendar_event 双真源。

PIT 双轴：decision_date=事实时间锚（决议公布日，未决议的预约场次为 NULL 值行）；
ingest_ts=采集时间。ReplacingMergeTree 无版本列，重拉幂等去重（值只会被更完整的行替换）。

引擎选型：
    ReplacingMergeTree（无版本列）。
    PARTITION BY toYYYYMM(decision_date)。
    ORDER BY (bank_code, decision_date)。
"""

from __future__ import annotations

# category_id: market_rate_decision_calendar
# calc_mode: preload

RATE_DECISION_CALENDAR_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.rate_decision_calendar
(
    bank_code     LowCardinality(String)      COMMENT '央行代码(fed/ecb/pboc/boj/boe/rba/rbi/rbnz/cbr/snb/bcb)',
    decision_date Date                        COMMENT '决议公布日(事实时间锚;预约场次=会议日)',
    rate_value    Nullable(Decimal(10, 4))    COMMENT '决议利率(年化%;未公布=NULL)',
    rate_forecast Nullable(Decimal(10, 4))    COMMENT '市场预测值(年化%)',
    rate_previous Nullable(Decimal(10, 4))    COMMENT '前值(年化%)',
    data_source   LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag  UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(decision_date)
ORDER BY (bank_code, decision_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "rate_decision_calendar"
DATABASE = "c1_market"
CATEGORY_ID = "market_rate_decision_calendar"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(decision_date)"
ORDER_BY = "(bank_code, decision_date)"

INSERT_COLUMNS = "(bank_code, decision_date, rate_value, rate_forecast, rate_previous, data_source, quality_flag)"
