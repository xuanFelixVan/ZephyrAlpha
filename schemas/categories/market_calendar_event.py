# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_calendar_event
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.internal_compute_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] calendar_event 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""calendar_event（日历事件标记）DDL-as-Code（category_id: market_calendar_event, calc_mode: preload）.

A 股"特殊日子"数据资产——全市场日历事件标记表（2026-08-10 新增）。
每行一个 (event_date, event_type) 组合，记录会引发资金避险/资金流出/价格异常的特殊日子。

事件来源：
    - internal（InternalComputeProvider 规则计算）：
        month_end/quarter_end/half_year_end/year_end  月末/季末/半年末/年末（最后交易日）
        futures_delivery      股指期货交割日（每月第3个周五，非交易日顺延）
        index_option_expiry   股指期权到期日（每月第3个周五）
        etf_option_expiry     ETF期权到期日（每月第4个周三）
        lpr_announcement      LPR公布日（每月20日，遇周末顺延下一工作日）
        hk_connect_closed     港股通休市日（A股开盘但港股休市，北向资金停摆，如圣诞/复活节）
    - manual（手工录入，本批次暂不填充，表结构预留）：
        fomc_meeting          美联储FOMC议息日
        major_meeting         重要会议（两会/中央经济工作会议等）
        stamp_duty_change     印花税调整日

引擎选型：
    ReplacingMergeTree（按 event_date+event_type 去重，全量重算幂等）。
    PARTITION BY toYYYYMM(event_date)——按事件日期月分区。
    ORDER BY (event_date, event_type)——按日期+类型点查友好，便于"某日有哪些事件"查询。

注：本表无 symbol 字段（全市场事件），故不带 TRAE-082 MATERIALIZED exchange/symbol_canonical 派生列。
"""

from __future__ import annotations

# category_id: market_calendar_event
# calc_mode: preload（回测时预加载，作为日级事件特征）

CALENDAR_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.calendar_event
(
    event_date   Date                    COMMENT '事件日期',
    event_type   LowCardinality(String)  COMMENT '事件类型(month_end/quarter_end/half_year_end/year_end/futures_delivery/index_option_expiry/etf_option_expiry/lpr_announcement/hk_connect_closed/fomc_meeting/major_meeting/stamp_duty_change)',
    description  String                  DEFAULT '' COMMENT '事件描述',
    data_source  LowCardinality(String)  DEFAULT 'internal' COMMENT '数据来源(internal=计算派生/manual=手工录入)',
    ingest_ts    DateTime64(3, 'UTC')    DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, event_type)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "calendar_event"
DATABASE = "c1_market"
CATEGORY_ID = "market_calendar_event"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(event_date)"
ORDER_BY = "(event_date, event_type)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
INSERT_COLUMNS = "(event_date, event_type, description, data_source)"
