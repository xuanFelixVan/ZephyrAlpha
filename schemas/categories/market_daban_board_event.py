# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_daban_board_event
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.daban_board_event_deriver(产出侧,STR-DABAN-022 打板 sleeve 回测数据腿)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] daban_board_event 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；列集=deriver INSERT_COLUMNS 21 列+ingest_ts DEFAULT 列，不按想象加字段
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""daban_board_event 表 DDL-as-Code（category_id: market_daban_board_event, calc_mode: lazy）。

本文件是 c1_market.daban_board_event 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一；STR-DABAN-022 / ee174053bf）：
    打板事件推导器 zephyr.data.implementations.daban_board_event_deriver
    （MOD-DAT-daban_board_event_derive）docstring DDL 草稿转正——deriver
    INSERT_COLUMNS 21 列与本表列序一一对应（ingest_ts 为 DEFAULT 列不入列）。
    事件由库内数据推导（kline_daily 全史 + kline_1min 分钟 2021-09 起 +
    tick_data 盘口 2026-07 起 + stk_limit 三级解析链），逐行 limit_src 留痕。

推导口径（deriver 契约留痕）：
    - 触板 touched：当日 high ≥ limit_up − 0.001；封住 close_sealed：close 同判；
      一字 is_one_word：low 同判；连板 consec_limit：封住日链式计数。
    - first_touch_time：kline_1min 首个 high ≥ 涨停价 的分钟（HH:MM:SS 分钟级代理，
      无分钟数据 None 如实空缺）。
    - open_board_count：分钟 walk 封→开转换计数（下限口径，分钟内快开快合漏计）。
    - seal_bid_volume/seal_amount_proxy：tick 尾盘最后一笔 bid_price ≥ 涨停价 的
      买一档（手/元；2026-07 前无盘口量 → None 如实空缺不硬造）。

引擎选型说明：
    日频批推导产物（触板 symbol-day 事件，未触板日不出行），ReplacingMergeTree
    按 (trade_date, symbol) 同键静默替换——同一窗口重跑/derive_version 升级
    重推导幂等（§7.3 幂等首选）。

与草稿的唯一偏差（施工裁定，2026-08-26）：
    open 由草稿 Decimal(18,4) 升级为 Nullable(Decimal(18,4))——deriver 代码契约
    DabanBoardEvent.open 为 float | None（derive_daily_events 仅保证 high/low/close
    非空，open 可为 None），Nullable 与代码契约对齐防 INSERT 炸列。
"""

from __future__ import annotations

from typing import Final

# category_id: market_daban_board_event
# calc_mode: lazy

MARKET_DABAN_BOARD_EVENT_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.daban_board_event
(
    trade_date        Date                        COMMENT '交易日期',
    symbol            String                      COMMENT '证券代码(6位裸码)',
    board             LowCardinality(String)      COMMENT '板块(sh_main/sz_main/star/chinext/bj)',
    st_flag           UInt8                       COMMENT 'ST标记(库内stk_limit源直给;其余源按有效幅度推断)',
    pre_close         Nullable(Decimal(18, 4))    COMMENT '昨收(kline昨收链,原始价口径除权日不复权)',
    limit_up_price    Decimal(18, 4)              COMMENT '涨停价(三级解析链:ch_stk_limit/tushare/rule_derived)',
    open              Nullable(Decimal(18, 4))    COMMENT '开盘价(可为None,对齐deriver代码契约)',
    high              Decimal(18, 4)              COMMENT '最高价',
    low               Decimal(18, 4)              COMMENT '最低价',
    close             Decimal(18, 4)              COMMENT '收盘价',
    touched           UInt8                       COMMENT '盘中触板(high>=limit-0.001)',
    close_sealed      UInt8                       COMMENT '收盘封住(close>=limit-0.001)',
    is_one_word       UInt8                       COMMENT '一字板(low>=limit-0.001)',
    first_touch_time  Nullable(String)            COMMENT '首次触板时刻HH:MM:SS(kline_1min分钟级代理;无分钟数据None)',
    open_board_count  Nullable(UInt16)            COMMENT '开板次数(分钟级下限口径,分钟内快开快合漏计)',
    seal_bid_volume   Nullable(UInt64)            COMMENT '尾盘买一封单(手,tick代理2026-07起,否则None)',
    seal_amount_proxy Nullable(Decimal(20, 2))    COMMENT '封单金额代理(元)=bid_volume*100*bid_price',
    consec_limit      UInt16                      COMMENT '连板数(封住日链;未封住=0)',
    limit_src         LowCardinality(String)      COMMENT '涨停价来源(ch_stk_limit/tushare_stk_limit/rule_derived)',
    data_source       LowCardinality(String)      DEFAULT 'derived_kline' COMMENT '数据来源',
    derive_version    LowCardinality(String)      DEFAULT 'v1' COMMENT '推导口径版本',
    ingest_ts         DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "daban_board_event"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_daban_board_event"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, symbol)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 与 daban_board_event_deriver.INSERT_COLUMNS 21 列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, symbol, board, st_flag, pre_close, limit_up_price, open, high, "
    "low, close, touched, close_sealed, is_one_word, first_touch_time, "
    "open_board_count, seal_bid_volume, seal_amount_proxy, consec_limit, "
    "limit_src, data_source, derive_version)"
)
