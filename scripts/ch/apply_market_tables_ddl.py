# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_market_tables_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.local_replay
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: tick_data DDL 真源为 schemas/categories/intraday/market_tick.py; kline_daily DDL 真源为 schemas/categories/kline/market_kline_daily.py; auction_book DDL 真源为 schemas/categories/intraday/market_auction_book.py; sector_snapshot DDL 真源为 schemas/categories/market/market_sector_snapshot.py; apply() 通过 ch_writer.query 执行; verify() 查询 system.tables 验证引擎
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 引擎不匹配->列出差异+退出码1; 全部匹配->退出码0
# [TESTS] none
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: 部署脚本与 schema 文件 DDL 内容相同但用途不同(apply vs SSoT)
"""ClickHouse c1_market 建表 DDL 部署 + 引擎验证脚本（Phase F）。

DDL-as-Code 模式：
    - tick_data DDL 真源为 schemas/categories/intraday/market_tick.py（本脚本导入引用）
    - kline_daily DDL 真源为 schemas/categories/kline/market_kline_daily.py（本脚本导入引用）
    - auction_book DDL 真源为 schemas/categories/intraday/market_auction_book.py（本脚本导入引用）
    - sector_snapshot DDL 真源为 schemas/categories/market/market_sector_snapshot.py（本脚本导入引用）

引擎选型矩阵（设计文档 §5 Phase F，裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F 治本）：
    tick_data        → ReplacingMergeTree（tick 天然唯一）
    kline_daily      → ReplacingMergeTree（日线按交易日去重）
    auction_book     → ReplacingMergeTree（集合竞价高频推送，按 (symbol,trade_date,timestamp) 去重）
    sector_snapshot  → ReplacingMergeTree（板块快照高频推送，按 (sector_code,timestamp) 去重）

用法::

    python scripts/ch/apply_market_tables_ddl.py           # 建表 + 验证
    python scripts/ch/apply_market_tables_ddl.py --verify   # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# 确保 src/ 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
# 仓根入 path（schemas/categories/*.py DDL-as-Code 真源导入前提；
# 此前缺失导致 try/except 内联 fallback 成为事实运行时——真源漂移温床，JOB-077 治本）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from zephyr.data import ch_writer

# ========== DDL 定义 ==========

# tick_data DDL — 真源: schemas/categories/intraday/market_tick.py
try:
    from schemas.categories.intraday.market_tick import TICK_DATA_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    TICK_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_data
(
    trade_date    Date                    COMMENT '交易日期',
    timestamp     DateTime64(3, 'Asia/Shanghai') COMMENT '时间戳(3秒粒度)',
    recorded_time DateTime64(3, 'UTC')  DEFAULT now() COMMENT '录制器本地接收时间(用于延迟分析)',
    symbol        String                  COMMENT '证券代码',
    market_type   LowCardinality(String)  COMMENT '市场类型',
    price         Decimal(18,4)           COMMENT '成交价',
    volume        UInt64                  COMMENT '成交量(股)',
    amount        Decimal(18,2)           COMMENT '成交额(元)',
    direction     LowCardinality(String) DEFAULT '' COMMENT '买卖方向',
    data_source   LowCardinality(String) DEFAULT 'bdpan' COMMENT '数据来源',
    bid_price     Nullable(Decimal(18,4)) COMMENT '买一价',
    ask_price     Nullable(Decimal(18,4)) COMMENT '卖一价',
    bid_volume    Nullable(UInt64)        COMMENT '买一量',
    ask_volume    Nullable(UInt64)        COMMENT '卖一量',
    quality_flag  UInt8          DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# l2_tick DDL — 真源: schemas/categories/intraday/market_l2_tick.py（2026-07-28 建表，#ARCH-DATA-PIPELINE-001）
try:
    from schemas.categories.intraday.market_l2_tick import L2_TICK_DDL
except ImportError:
    L2_TICK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.l2_tick
(
    trade_date    Date,
    timestamp     DateTime64(3, 'Asia/Shanghai'),
    recorded_time DateTime64(3, 'UTC')  DEFAULT now(),
    symbol        String,
    market_type   LowCardinality(String)  DEFAULT '',
    price         Decimal(18,4),
    volume        UInt64,
    amount        Decimal(18,2),
    direction     LowCardinality(String)  DEFAULT '',
    bid_price     Nullable(Decimal(18,4)),
    ask_price     Nullable(Decimal(18,4)),
    bid_volume    Nullable(UInt64),
    ask_volume    Nullable(UInt64),
    data_source   LowCardinality(String)  DEFAULT 'miniqmt',
    quality_flag  UInt8          DEFAULT 1,
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now(),
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1,
    INDEX idx_symbol symbol TYPE set(10000) GRANULARITY 4
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (market_type, symbol, trade_date, timestamp, price)
SETTINGS index_granularity = 8192
"""

# kline_daily DDL — 真源: schemas/categories/kline/market_kline_daily.py
try:
    from schemas.categories.kline.market_kline_daily import KLINE_DAILY_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    KLINE_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_daily
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '证券代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(股)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%)',
    change       Decimal(18,4)  DEFAULT 0 COMMENT '涨跌额(元)',
    turnover     Decimal(18,4)  DEFAULT 0 COMMENT '换手率(%)',
    adj_factor   Decimal(18,8)  DEFAULT 1 COMMENT '复权因子',
    market_type  LowCardinality(String) DEFAULT 'A_share' COMMENT '市场类型',
    data_source  LowCardinality(String)  COMMENT '数据来源',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# kline_etf_daily DDL — 真源: schemas/categories/kline/market_kline_etf_daily.py
try:
    from schemas.categories.kline.market_kline_etf_daily import MARKET_KLINE_ETF_DAILY_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    MARKET_KLINE_ETF_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.kline_etf_daily
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT 'ETF代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(份)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%)',
    data_source  LowCardinality(String) DEFAULT 'miniqmt' COMMENT '数据来源',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
"""

# auction_book DDL — 真源: schemas/categories/intraday/market_auction_book.py
try:
    from schemas.categories.intraday.market_auction_book import AUCTION_BOOK_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    AUCTION_BOOK_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.auction_book
(
    trade_date   Date           COMMENT '交易日期',
    timestamp    DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳(精确到秒)',
    symbol       String         COMMENT '证券代码',
    last_price   Decimal(18,4)  COMMENT '最新成交价',
    volume       UInt64         COMMENT '累计成交量(手)',
    amount       Decimal(18,2)  COMMENT '累计成交额(元)',
    open         Decimal(18,4)  COMMENT '当日开盘价',
    high         Decimal(18,4)  COMMENT '当日最高价',
    low          Decimal(18,4)  COMMENT '当日最低价',
    pre_close    Decimal(18,4)  COMMENT '昨收价',
    upper_limit  Decimal(18,4)  COMMENT '涨停价',
    lower_limit  Decimal(18,4)  COMMENT '跌停价',
    bid_price1   Decimal(18,4)  COMMENT '买一价',
    bid_price2   Decimal(18,4)  COMMENT '买二价',
    bid_price3   Decimal(18,4)  COMMENT '买三价',
    bid_price4   Decimal(18,4)  COMMENT '买四价',
    bid_price5   Decimal(18,4)  COMMENT '买五价',
    bid_volume1  UInt64         COMMENT '买一量(手)',
    bid_volume2  UInt64         COMMENT '买二量(手)',
    bid_volume3  UInt64         COMMENT '买三量(手)',
    bid_volume4  UInt64         COMMENT '买四量(手)',
    bid_volume5  UInt64         COMMENT '买五量(手)',
    ask_price1   Decimal(18,4)  COMMENT '卖一价',
    ask_price2   Decimal(18,4)  COMMENT '卖二价',
    ask_price3   Decimal(18,4)  COMMENT '卖三价',
    ask_price4   Decimal(18,4)  COMMENT '卖四价',
    ask_price5   Decimal(18,4)  COMMENT '卖五价',
    ask_volume1  UInt64         COMMENT '卖一量(手)',
    ask_volume2  UInt64         COMMENT '卖二量(手)',
    ask_volume3  UInt64         COMMENT '卖三量(手)',
    ask_volume4  UInt64         COMMENT '卖四量(手)',
    ask_volume5  UInt64         COMMENT '卖五量(手)',
    data_source  LowCardinality(String) COMMENT '数据来源(miniQMT)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date, timestamp)
SETTINGS index_granularity = 8192
"""

# sector_snapshot DDL — 真源: schemas/categories/market/market_sector_snapshot.py
# 引擎治本迁移（#ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase F）：
# 原 MergeTree（板块快照允许重复）→ ReplacingMergeTree（高频推送按 (sector_code,timestamp) 去重）
# 原因：sector_snapshot 是高频表（30秒轮询+99只推送），MergeTree 写前 DELETE 留 mutations 累积；
# ReplacingMergeTree 直接 INSERT + 后台合并去重，符合 ch_writer.py §7.3 幂等性策略首选。
# Phase 2 治本（2026-07-22）：DDL 从 sector_snapshot_collector.py 内联迁移到独立 schema 文件，
# 消除双真源（本脚本与 collector 共用同一 schema 文件作为 SSoT）。
try:
    from schemas.categories.market.market_sector_snapshot import SECTOR_SNAPSHOT_DDL
except ImportError:
    # fallback: 内联定义（与 schema 文件保持一致）
    SECTOR_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.sector_snapshot
(
    trade_date       Date        COMMENT '交易日',
    timestamp        DateTime64(3, 'Asia/Shanghai') COMMENT '快照时间戳',
    sector_code      String      COMMENT '板块代码 880001.SH',
    market_type      LowCardinality(String) COMMENT 'sector/mkt_index',
    now_price        Decimal(18,4) COMMENT '最新价',
    open_price       Decimal(18,4) COMMENT '开盘价',
    max_price        Decimal(18,4) COMMENT '最高价',
    min_price        Decimal(18,4) COMMENT '最低价',
    last_close       Decimal(18,4) COMMENT '昨收',
    before_5min_now  Decimal(18,4) COMMENT '5分钟前最新价',
    average_price    Decimal(18,4) COMMENT '均价',
    volume           UInt64      COMMENT '成交量(板块恒为0)',
    now_vol          UInt64      COMMENT '现量',
    amount           Decimal(18,2) COMMENT '成交额',
    up_home          UInt32      COMMENT '上涨家数',
    down_home        UInt32      COMMENT '下跌家数',
    inside           UInt32      COMMENT '内盘',
    outside          UInt32      COMMENT '外盘',
    zangsu           Decimal(10,3) COMMENT '涨速',
    data_source      LowCardinality(String) COMMENT 'tqcenter_snapshot/tqcenter_push',
    fetched_at       DateTime64(3, 'UTC') COMMENT '采集时间(UTC)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_code, timestamp)
"""

# cross_validation_log DDL — 真源: schemas/categories/cross_validation_log.py (P1-4)
try:
    from schemas.categories.cross_validation_log import CROSS_VALIDATION_LOG_DDL
except ImportError:
    CROSS_VALIDATION_LOG_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.cross_validation_log
(
    check_time     DateTime64(3, 'UTC')        COMMENT '校验执行时间',
    check_date     Date                    COMMENT '校验数据日期',
    symbol         String                  COMMENT '证券代码',
    metric         LowCardinality(String)  COMMENT '校验指标',
    primary_value  String                  COMMENT '主源值',
    backup_value   String                  COMMENT '备源值',
    deviation      Decimal(18,6)           COMMENT '偏差',
    threshold      Decimal(18,6)           COMMENT '偏差阈值',
    status         LowCardinality(String)  COMMENT '校验结果(pass/warn/fail)',
    detail         String                  DEFAULT '' COMMENT '详细信息'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(check_date)
ORDER BY (check_date, symbol, metric, check_time)
"""

# hog_spot_index DDL — 真源: schemas/categories/market/market_hog_spot_index.py (2026-07-29 生猪价格接入)
try:
    from schemas.categories.market.market_hog_spot_index import HOG_SPOT_INDEX_DDL
except ImportError:
    HOG_SPOT_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_spot_index
(
    trade_date          Date           COMMENT '统计日期(周度)',
    index_value         Decimal(18,4)  COMMENT '生猪现货价格指数',
    ma_4m               Float64        COMMENT '4个月均线',
    ma_6m               Float64        COMMENT '6个月均线',
    ma_12m              Float64        COMMENT '12个月均线',
    presale_avg_price   Decimal(18,4)  COMMENT '预售均价(元/公斤)',
    deal_avg_price      Decimal(18,4)  COMMENT '成交均价(元/公斤)',
    deal_avg_weight     Float64        COMMENT '成交均重(公斤)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# hog_futures_core DDL — 真源: schemas/categories/market/market_hog_futures_core.py
try:
    from schemas.categories.market.market_hog_futures_core import HOG_FUTURES_CORE_DDL
except ImportError:
    HOG_FUTURES_CORE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_futures_core
(
    trade_date    Date           COMMENT '交易日期',
    value         Decimal(18,4)  COMMENT '生猪期货核心价(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

# hog_province_spot DDL — 真源: schemas/categories/market/market_hog_province_spot.py
try:
    from schemas.categories.market.market_hog_province_spot import HOG_PROVINCE_SPOT_DDL
except ImportError:
    HOG_PROVINCE_SPOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.hog_province_spot
(
    trade_date    Date           COMMENT '交易日期(快照日)',
    province      String         COMMENT '省份',
    price         Decimal(18,4)  COMMENT '生猪现价(元/公斤)',
    change        Float64        COMMENT '涨跌幅(元/公斤)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, province)
SETTINGS index_granularity = 8192
"""

# JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15）— 真源: schemas/categories/ 同名文件
# 不内联 fallback：DDL 部署必须 fail-closed（导入失败即报错），防止静默使用漂移副本建错表
# tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）：IPO 日历/募资规模（巨潮新股列表）
# 92号清单 §7.2（2026-08-22）：market_us_futures_intraday=美股期指 ES/NQ + A50 盘中实时快照（44号 §9.8 通道3）
# 92号清单 §8.4（2026-08-22）：market_news_sentiment_window=夜间新闻情绪窗口落库（44号 §4 M3-②，tracker #138 闭环）
# 92号清单 §8.2（2026-08-22）：market_breadth_snapshot=全市场分钟级宽度快照（44号 M1-④ 数据地基，M1-①/③ 消费）
# 2026-08-26 Owner 全批 DDL 三件：limit_up_pool（GAP-F-13 涨停池明细）/ account_nav_daily
# （GAP-F-29 实盘净值）/ reconciliation_differences（T2_closure_review §9.1 #2 / tracker #234 CH 侧）
# 2026-08-26 Owner 全批 DDL 数据层三件：execution_report（CTR-P1-007 契约持久化，P0）/
# sector_fund_flow（D3/GAP-F-16 THS 板块资金流快照）/ daban_board_event（STR-DABAN-022 打板事件推导）
# 2026-08-29 S2 估值路A + A22：index_valuation_daily（指数估值 PE_TTM/CAPE/分位/ERP）/
# a50_futures_daily（富时A50期货日K，44号 §9.6 通道1）
from schemas.categories.market.market_a50_futures_daily import A50_FUTURES_DAILY_DDL
from schemas.categories.market.market_account_nav_daily import MARKET_ACCOUNT_NAV_DAILY_DDL
# 另类数据第 1 批免注册直连（2026-09-12，alt-data-handoff §8-1）：fail-closed 直接导入
from schemas.categories.market.market_alt_shipping_index import ALT_SHIPPING_INDEX_DDL
from schemas.categories.market.market_alt_regime_signal import ALT_REGIME_SIGNAL_DDL
from schemas.categories.market.market_sentiment_panel import SENTIMENT_PANEL_DDL
from schemas.categories.market.market_alt_stock_comment import ALT_STOCK_COMMENT_DDL
# 气象事件层：台风路径（2026-09-14，深圳开放数据平台 appKey 通道）
from schemas.categories.market.market_alt_typhoon_track import ALT_TYPHOON_TRACK_DDL
# 深圳开放数据批量源 ×7（2026-09-14，st-altdata-20260914）：fail-closed 直接导入
from schemas.categories.market.market_alt_sz_stat_monthly import MARKET_ALT_SZ_STAT_MONTHLY_DDL
from schemas.categories.market.market_alt_sz_port_monthly import MARKET_ALT_SZ_PORT_MONTHLY_DDL
from schemas.categories.market.market_alt_sz_house_daily import MARKET_ALT_SZ_HOUSE_DAILY_DDL
from schemas.categories.market.market_alt_sz_weather_warning import MARKET_ALT_SZ_WEATHER_WARNING_DDL
from schemas.categories.market.market_alt_sz_marine_forecast import MARKET_ALT_SZ_MARINE_FORECAST_DDL
# 深圳能见度探测分钟级站点流（2026-09-14，任务 2：服务 1580458478）
from schemas.categories.market.market_alt_sz_visibility import MARKET_ALT_SZ_VISIBILITY_DDL
# 批 2 十一表（2026-09-14 深夜，新钥匙通道 0ecc2b46：环境/水库/楼市/口岸/统计扩展）
from schemas.categories.market.market_alt_sz_air_quality_daily import MARKET_ALT_SZ_AIR_QUALITY_DAILY_DDL
from schemas.categories.market.market_alt_sz_air_quality_region import MARKET_ALT_SZ_AIR_QUALITY_REGION_DDL
from schemas.categories.market.market_alt_sz_reservoir_station import MARKET_ALT_SZ_RESERVOIR_STATION_DDL
from schemas.categories.market.market_alt_sz_reservoir_rain_day import MARKET_ALT_SZ_RESERVOIR_RAIN_DAY_DDL
from schemas.categories.market.market_alt_sz_reservoir_rain_month import MARKET_ALT_SZ_RESERVOIR_RAIN_MONTH_DDL
from schemas.categories.market.market_alt_sz_house_area import MARKET_ALT_SZ_HOUSE_AREA_DDL
from schemas.categories.market.market_alt_sz_house_listing import MARKET_ALT_SZ_HOUSE_LISTING_DDL
from schemas.categories.market.market_alt_sz_house_presale import MARKET_ALT_SZ_HOUSE_PRESALE_DDL
from schemas.categories.market.market_alt_sz_market_subject import MARKET_ALT_SZ_MARKET_SUBJECT_DDL
from schemas.categories.market.market_alt_sz_stat_analysis import MARKET_ALT_SZ_STAT_ANALYSIS_DDL
from schemas.categories.market.market_alt_sz_enterprise_year import MARKET_ALT_SZ_ENTERPRISE_YEAR_DDL
from schemas.categories.market.market_alt_sz_reservoir_level import MARKET_ALT_SZ_RESERVOIR_LEVEL_DDL
from schemas.categories.market.market_alt_sz_env_meteor import MARKET_ALT_SZ_ENV_METEOR_DDL
from schemas.categories.market.market_alt_sz_climate_hist import MARKET_ALT_SZ_CLIMATE_HIST_DDL
from schemas.categories.market.market_alt_sz_ground_obs import MARKET_ALT_SZ_GROUND_OBS_DDL
from schemas.categories.market.market_typhoon_landfall_history import MARKET_TYPHOON_LANDFALL_HISTORY_DDL
from schemas.categories.market.market_typhoon_names import MARKET_TYPHOON_NAMES_DDL
from schemas.categories.market.market_breadth_snapshot import MARKET_BREADTH_SNAPSHOT_DDL
from schemas.categories.market.market_daban_board_event import MARKET_DABAN_BOARD_EVENT_DDL
from schemas.categories.intraday.market_execution_report import MARKET_EXECUTION_REPORT_DDL
from schemas.categories.market.market_index_valuation_daily import MARKET_INDEX_VALUATION_DAILY_DDL
from schemas.categories.market.market_ipo_calendar import IPO_CALENDAR_DDL
from schemas.categories.kline.market_kline_global import KLINE_GLOBAL_DDL
from schemas.categories.market.market_limit_up_pool import MARKET_LIMIT_UP_POOL_DDL
from schemas.categories.market.market_news_sentiment_window import NEWS_SENTIMENT_WINDOW_DDL
from schemas.categories.market.market_reconciliation_differences import (
    MARKET_RECONCILIATION_DIFFERENCES_DDL,
)
from schemas.categories.market.market_sector_fund_flow import MARKET_SECTOR_FUND_FLOW_DDL
from schemas.categories.market.market_stk_limit import STK_LIMIT_DDL
from schemas.categories.market.market_suspend import SUSPEND_DDL
from schemas.categories.market.market_us_futures_intraday import US_FUTURES_INTRADAY_DDL
from schemas.categories.meta_stock_basic import STOCK_BASIC_DDL
from schemas.categories.meta.meta_stock_profile_ths import STOCK_PROFILE_THS_DDL
from schemas.categories.meta.meta_stock_profile_ths import TABLE_NAME as _THS_PROFILE_TABLE

# 所有 DDL（按依赖顺序）
_ALL_DDL: list[tuple[str, str]] = [
    ("c1_market.tick_data", TICK_DATA_DDL),
    ("c1_market.l2_tick", L2_TICK_DDL),
    ("c1_market.kline_daily", KLINE_DAILY_DDL),
    ("c1_market.kline_etf_daily", MARKET_KLINE_ETF_DAILY_DDL),
    ("c1_market.auction_book", AUCTION_BOOK_DDL),
    ("c1_market.sector_snapshot", SECTOR_SNAPSHOT_DDL),
    ("c1_market.cross_validation_log", CROSS_VALIDATION_LOG_DDL),
    ("c1_market.hog_spot_index", HOG_SPOT_INDEX_DDL),
    ("c1_market.hog_futures_core", HOG_FUTURES_CORE_DDL),
    ("c1_market.hog_province_spot", HOG_PROVINCE_SPOT_DDL),
    # 另类数据第 1 批免注册直连（2026-09-12，alt-data-handoff §8-1）
    ("c1_market.alt_stock_comment", ALT_STOCK_COMMENT_DDL),
    ("c1_market.alt_shipping_index", ALT_SHIPPING_INDEX_DDL),
    ("c1_market.sentiment_panel", SENTIMENT_PANEL_DDL),
    ("c1_market.alt_regime_signal", ALT_REGIME_SIGNAL_DDL),
    # 气象事件层：台风路径（2026-09-14）
    ("c1_market.alt_typhoon_track", ALT_TYPHOON_TRACK_DDL),
    # 深圳开放数据批量源 ×7（2026-09-14）
    ("c1_market.alt_sz_stat_monthly", MARKET_ALT_SZ_STAT_MONTHLY_DDL),
    ("c1_market.alt_sz_port_monthly", MARKET_ALT_SZ_PORT_MONTHLY_DDL),
    ("c1_market.alt_sz_house_daily", MARKET_ALT_SZ_HOUSE_DAILY_DDL),
    ("c1_market.alt_sz_weather_warning", MARKET_ALT_SZ_WEATHER_WARNING_DDL),
    ("c1_market.alt_sz_marine_forecast", MARKET_ALT_SZ_MARINE_FORECAST_DDL),
    ("c1_market.alt_sz_visibility", MARKET_ALT_SZ_VISIBILITY_DDL),
    # 批 2 十一表（2026-09-14 深夜）
    ("c1_market.alt_sz_air_quality_daily", MARKET_ALT_SZ_AIR_QUALITY_DAILY_DDL),
    ("c1_market.alt_sz_air_quality_region", MARKET_ALT_SZ_AIR_QUALITY_REGION_DDL),
    ("c1_market.alt_sz_reservoir_station", MARKET_ALT_SZ_RESERVOIR_STATION_DDL),
    ("c1_market.alt_sz_reservoir_rain_day", MARKET_ALT_SZ_RESERVOIR_RAIN_DAY_DDL),
    ("c1_market.alt_sz_reservoir_rain_month", MARKET_ALT_SZ_RESERVOIR_RAIN_MONTH_DDL),
    ("c1_market.alt_sz_house_area", MARKET_ALT_SZ_HOUSE_AREA_DDL),
    ("c1_market.alt_sz_house_listing", MARKET_ALT_SZ_HOUSE_LISTING_DDL),
    ("c1_market.alt_sz_house_presale", MARKET_ALT_SZ_HOUSE_PRESALE_DDL),
    ("c1_market.alt_sz_market_subject", MARKET_ALT_SZ_MARKET_SUBJECT_DDL),
    ("c1_market.alt_sz_stat_analysis", MARKET_ALT_SZ_STAT_ANALYSIS_DDL),
    ("c1_market.alt_sz_enterprise_year", MARKET_ALT_SZ_ENTERPRISE_YEAR_DDL),
    ("c1_market.alt_sz_reservoir_level", MARKET_ALT_SZ_RESERVOIR_LEVEL_DDL),
    ("c1_market.alt_sz_env_meteor", MARKET_ALT_SZ_ENV_METEOR_DDL),
    ("c1_market.alt_sz_climate_hist", MARKET_ALT_SZ_CLIMATE_HIST_DDL),
    ("c1_market.alt_sz_ground_obs", MARKET_ALT_SZ_GROUND_OBS_DDL),
    ("c1_market.alt_typhoon_landfall_history", MARKET_TYPHOON_LANDFALL_HISTORY_DDL),
    ("c1_market.alt_typhoon_names", MARKET_TYPHOON_NAMES_DDL),
    # JOB-077 市场元数据与约束接入（DS-081~083，2026-08-15）
    ("c1_market.stock_basic", STOCK_BASIC_DDL),
    ("c1_market.stk_limit", STK_LIMIT_DDL),
    ("c1_market.suspend", SUSPEND_DDL),
    # tracker #114 / 37号 §3.2a（2026-08-17 AI-IPO-001）
    ("c1_market.ipo_calendar", IPO_CALENDAR_DDL),
    # 92号清单 §7.2（2026-08-22）：美股期指 ES/NQ + A50 盘中实时快照
    ("c1_market.us_futures_intraday", US_FUTURES_INTRADAY_DDL),
    # 92号清单 §8.4（2026-08-22）：夜间新闻情绪窗口落库（tracker #138 闭环）
    ("c1_market.news_sentiment_window", NEWS_SENTIMENT_WINDOW_DDL),
    # 92号清单 §8.2（2026-08-22）：全市场分钟级宽度快照（44号 M1-④ 数据地基）
    ("c1_market.market_breadth_snapshot", MARKET_BREADTH_SNAPSHOT_DDL),
    # 2026-08-26 Owner 全批 DDL 三件
    ("c1_market.limit_up_pool", MARKET_LIMIT_UP_POOL_DDL),
    ("c1_market.account_nav_daily", MARKET_ACCOUNT_NAV_DAILY_DDL),
    ("c1_market.reconciliation_differences", MARKET_RECONCILIATION_DIFFERENCES_DDL),
    # 2026-08-26 Owner 全批 DDL 数据层三件（CTR-P1-007 / D3 GAP-F-16 / STR-DABAN-022）
    ("c1_market.execution_report", MARKET_EXECUTION_REPORT_DDL),
    ("c1_market.sector_fund_flow", MARKET_SECTOR_FUND_FLOW_DDL),
    ("c1_market.daban_board_event", MARKET_DABAN_BOARD_EVENT_DDL),
    # 2026-08-29 S2 估值路A + A22（44号 §9.6 通道1）
    ("c1_market.index_valuation_daily", MARKET_INDEX_VALUATION_DAILY_DDL),
    ("c1_market.a50_futures_daily", A50_FUTURES_DAILY_DDL),
    # 2026-08-30 designmemos 清单 #6 / GAP-F-23：外盘日K线（HSI/N225/KOSPI/CL/GC）
    ("c1_market.kline_global", KLINE_GLOBAL_DDL),
    # 2026-09-09 DS-223：THS 行业/公司简介全市场主数据（细分行业缺口补齐）
    # 表名经 schema 真源 TABLE_NAME 拼接（TABLE-NAME-REGISTRY：全限定名真源=categories YAML）
    ("c1_market." + _THS_PROFILE_TABLE, STOCK_PROFILE_THS_DDL),
]

# 增量迁移（ALTER TABLE ADD COLUMN IF NOT EXISTS）
# 用于已存在的表新增列，CREATE TABLE IF NOT EXISTS 不会修改已存在的表结构
# 每项: (表名, ALTER SQL)
_MIGRATIONS: list[tuple[str, str]] = [
    # P0-1 双时间戳（2026-07-22）: tick_data 新增 recorded_time 列
    (
        "c1_market.tick_data",
        "ALTER TABLE c1_market.tick_data "
        "ADD COLUMN IF NOT EXISTS recorded_time DateTime64(3, 'UTC') DEFAULT now() "
        "COMMENT '录制器本地接收时间(用于延迟分析)' AFTER timestamp",
    ),
    # 2026-09-14 A股标配批+统计族批（st-tilib-20260914）: technical_indicator +14 指标列
    # 趋势+2（DKX）/动量+7（BIAS/PSY/LWR）/统计族+5（CORREL/BETA/LINEARREG/TSF/ROLLVAR）
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS dkx_20 Nullable(Float64) COMMENT '20日多空线', "
        "ADD COLUMN IF NOT EXISTS dkx_ma10 Nullable(Float64) COMMENT '多空线10日移动平均', "
        "ADD COLUMN IF NOT EXISTS bias_6 Nullable(Float64) COMMENT '6日乖离率', "
        "ADD COLUMN IF NOT EXISTS bias_12 Nullable(Float64) COMMENT '12日乖离率', "
        "ADD COLUMN IF NOT EXISTS bias_24 Nullable(Float64) COMMENT '24日乖离率', "
        "ADD COLUMN IF NOT EXISTS psy_12 Nullable(Float64) COMMENT '12日心理线', "
        "ADD COLUMN IF NOT EXISTS psy_ma6 Nullable(Float64) COMMENT '心理线6日移动平均', "
        "ADD COLUMN IF NOT EXISTS lwr_1 Nullable(Float64) COMMENT '慢速威廉LWR1(9,3,3)', "
        "ADD COLUMN IF NOT EXISTS lwr_2 Nullable(Float64) COMMENT '慢速威廉LWR2(9,3,3)', "
        "ADD COLUMN IF NOT EXISTS correl_30 Nullable(Float64) COMMENT '30日close×volume滚动相关系数', "
        "ADD COLUMN IF NOT EXISTS beta_30 Nullable(Float64) COMMENT '30日close对volume滚动beta系数', "
        "ADD COLUMN IF NOT EXISTS linearreg_14 Nullable(Float64) COMMENT '14日线性回归线(当前拟合值)', "
        "ADD COLUMN IF NOT EXISTS tsf_14 Nullable(Float64) COMMENT '14日时间序列预测(一步外推)', "
        "ADD COLUMN IF NOT EXISTS var_20 Nullable(Float64) COMMENT '20日滚动总体方差(ddof=0)'",
    ),
    # 2026-09-14 主流热门批 2a（st-tilib-20260914）: technical_indicator +10 指标列
    # 注意：必须逐列一条 ALTER——多列逗号连发经 ch_writer 双通道失败且假成功（2026-09-14 实证）
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS hma_16 Nullable(Float64) COMMENT '16日Hull均线'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS zlema_21 Nullable(Float64) COMMENT '21日零滞后EMA'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kama_10 Nullable(Float64) COMMENT '10日Kaufman自适应均线'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS vip_14 Nullable(Float64) COMMENT '14日涡旋指标VI+'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS vim_14 Nullable(Float64) COMMENT '14日涡旋指标VI-'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS supertrend_10 Nullable(Float64) COMMENT '超级趋势线(10,3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS supertrend_dir Nullable(Float64) COMMENT '超级趋势方向(1=多,-1=空)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS dpo_20 Nullable(Float64) COMMENT '20日区间震荡'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS natr_14 Nullable(Float64) COMMENT '14日归一化真实波幅(TR/Close×100)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS trange Nullable(Float64) COMMENT '真实波幅原始值(首行=H-L)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS md_14 Nullable(Float64) COMMENT '14日McGinley动态均线'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS tsi Nullable(Float64) COMMENT '真实强度指数(25/13)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS smi Nullable(Float64) COMMENT '随机动量指数(10,3,3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS smi_signal Nullable(Float64) COMMENT 'SMI信号线(EMA3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS fisher_9 Nullable(Float64) COMMENT '费雪变换(9)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS fisher_sig9 Nullable(Float64) COMMENT '费雪变换信号(前值)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kst Nullable(Float64) COMMENT '确知量KST'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kst_signal Nullable(Float64) COMMENT 'KST信号线(SMA9)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS crsi Nullable(Float64) COMMENT 'ConnorsRSI(3,2,100)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS qqe_14 Nullable(Float64) COMMENT 'QQE线(14,5,27)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS qqe_rsi_ma Nullable(Float64) COMMENT 'QQE平滑RSI线(EMA5)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS stc Nullable(Float64) COMMENT 'Schaff趋势周期(23,50,10,3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS rvgi_10 Nullable(Float64) COMMENT '相对活力指数(10)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS rvgi_sig Nullable(Float64) COMMENT 'RVGI信号线(SMA4)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS massi_25 Nullable(Float64) COMMENT '质量指数(9,25)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS vwma_20 Nullable(Float64) COMMENT '20日成交量加权均线'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS adosc Nullable(Float64) COMMENT '蔡金震荡器(3/10)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS eom_14 Nullable(Float64) COMMENT '14日简易波动量'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kvo Nullable(Float64) COMMENT 'Klinger量震荡器(34/55)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kvo_signal Nullable(Float64) COMMENT 'KVO信号线(EMA13)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS nvi Nullable(Float64) COMMENT '负成交量指标'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS pvi Nullable(Float64) COMMENT '正成交量指标'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS tenkan_sen Nullable(Float64) COMMENT '一目均衡转折线(9)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS kijun_sen Nullable(Float64) COMMENT '一目均衡基准线(26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS senkou_span_a Nullable(Float64) COMMENT '一目先行跨度A(显示位移26,PIT安全)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS senkou_span_b Nullable(Float64) COMMENT '一目先行跨度B(52,显示位移26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS chikou_span Nullable(Float64) COMMENT '一目迟行跨度(计算时点收盘值)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_dcperiod Nullable(Float64) COMMENT '希尔伯特主导周期(6-50)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_dcphase Nullable(Float64) COMMENT '主导周期相位(度)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_ip Nullable(Float64) COMMENT '同相分量in_phase'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_qp Nullable(Float64) COMMENT '正交分量quadrature'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_sine Nullable(Float64) COMMENT '主正弦波'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_leadsine Nullable(Float64) COMMENT '超前45度正弦波'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ht_trendmode Nullable(Float64) COMMENT '趋势/循环模式(1趋势,0循环)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS bbi Nullable(Float64) COMMENT '多空指数(MA3/6/12/24均值)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS parkinson_20 Nullable(Float64) COMMENT 'Parkinson波动率(高低极差)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS garman_klass_20 Nullable(Float64) COMMENT 'Garman-Klass波动率(OHLC)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS rogers_satchell_20 Nullable(Float64) COMMENT 'Rogers-Satchell波动率(漂移无关)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS yang_zhang_20 Nullable(Float64) COMMENT 'Yang-Zhang波动率(隔夜跳空+漂移)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS stoch_fastk Nullable(Float64) COMMENT '随机振荡FastK(5)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS stoch_fastd Nullable(Float64) COMMENT '随机振荡FastD(SMA3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS stoch_slowk Nullable(Float64) COMMENT '随机振荡SlowK(SMA3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS stoch_slowd Nullable(Float64) COMMENT '随机振荡SlowD(SMA3)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS aroon_up Nullable(Float64) COMMENT 'Aroon上(14)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS aroon_down Nullable(Float64) COMMENT 'Aroon下(14)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS aroonosc Nullable(Float64) COMMENT 'Aroon震荡器(14)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS bop Nullable(Float64) COMMENT '力量平衡(SMA16)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ppo Nullable(Float64) COMMENT '百分比价格振荡器(12/26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS apo Nullable(Float64) COMMENT '绝对价格振荡器(12/26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS dx_14 Nullable(Float64) COMMENT '动向指数DX(14)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS ar_26 Nullable(Float64) COMMENT '人气指标AR(26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS br_26 Nullable(Float64) COMMENT '意愿指标BR(26)'",
    ),
    (
        "c1_market.technical_indicator",
        "ALTER TABLE c1_market.technical_indicator "
        "ADD COLUMN IF NOT EXISTS cr_26 Nullable(Float64) COMMENT '能量指标CR(26)'",
    ),
]

# 引擎选型矩阵（用于验证）
_EXPECTED_ENGINES: dict[str, str] = {
    "tick_data": "ReplacingMergeTree",
    "l2_tick": "ReplacingMergeTree",
    "kline_daily": "ReplacingMergeTree",
    "kline_etf_daily": "ReplacingMergeTree",
    "auction_book": "ReplacingMergeTree",
    "sector_snapshot": "ReplacingMergeTree",
    "cross_validation_log": "MergeTree",
    "hog_spot_index": "ReplacingMergeTree",
    "hog_futures_core": "ReplacingMergeTree",
    "hog_province_spot": "ReplacingMergeTree",
    # 另类数据第 1 批免注册直连（2026-09-12，alt-data-handoff §8-1）：快照/长表同键替换幂等
    "alt_stock_comment": "ReplacingMergeTree",
    "sentiment_panel": "ReplacingMergeTree",
    "alt_regime_signal": "ReplacingMergeTree",
    "alt_shipping_index": "ReplacingMergeTree",
    # 气象事件层：台风路径（2026-09-14）：KEYID 全局唯一替换幂等
    "alt_typhoon_track": "ReplacingMergeTree",
    # 深圳开放数据批量源 ×7（2026-09-14）：同键替换幂等
    "alt_sz_stat_monthly": "ReplacingMergeTree",
    "alt_sz_port_monthly": "ReplacingMergeTree",
    "alt_sz_house_daily": "ReplacingMergeTree",
    "alt_sz_weather_warning": "ReplacingMergeTree",
    "alt_sz_marine_forecast": "ReplacingMergeTree",
    "alt_sz_visibility": "ReplacingMergeTree",
    "alt_sz_air_quality_daily": "ReplacingMergeTree",
    "alt_sz_air_quality_region": "ReplacingMergeTree",
    "alt_sz_reservoir_station": "ReplacingMergeTree",
    "alt_sz_reservoir_rain_day": "ReplacingMergeTree",
    "alt_sz_reservoir_rain_month": "ReplacingMergeTree",
    "alt_sz_house_area": "ReplacingMergeTree",
    "alt_sz_house_listing": "ReplacingMergeTree",
    "alt_sz_house_presale": "ReplacingMergeTree",
    "alt_sz_market_subject": "ReplacingMergeTree",
    "alt_sz_stat_analysis": "ReplacingMergeTree",
    "alt_sz_enterprise_year": "ReplacingMergeTree",
    "alt_sz_reservoir_level": "ReplacingMergeTree",
    "alt_sz_env_meteor": "ReplacingMergeTree",
    "alt_sz_climate_hist": "ReplacingMergeTree",
    "alt_sz_ground_obs": "ReplacingMergeTree",
    "alt_typhoon_landfall_history": "ReplacingMergeTree",
    "alt_typhoon_names": "ReplacingMergeTree",
    # JOB-077（DS-081~083，2026-08-15）
    "stock_basic": "ReplacingMergeTree",
    "stk_limit": "ReplacingMergeTree",
    "suspend": "ReplacingMergeTree",
    "ipo_calendar": "ReplacingMergeTree",
    # 92号清单 §7.2（2026-08-22）：高频快照，按 (symbol, trade_date, timestamp) 去重
    "us_futures_intraday": "ReplacingMergeTree",
    # 92号清单 §8.4（2026-08-22）：低频窗口写入，按 (scope, symbol, window_type, window_ts) 同键替换幂等
    "news_sentiment_window": "ReplacingMergeTree",
    # 92号清单 §8.2（2026-08-22）：分钟级快照，按 (trade_date, ts) 同分钟重跑幂等替换
    "market_breadth_snapshot": "ReplacingMergeTree",
    # 2026-08-26 Owner 全批 DDL 三件：日频全量重写/重记场景同键替换幂等
    "limit_up_pool": "ReplacingMergeTree",
    "account_nav_daily": "ReplacingMergeTree",
    "reconciliation_differences": "ReplacingMergeTree",
    # 2026-08-26 数据层三件：契约持久化/轮询快照/日频推导同键替换幂等
    "execution_report": "ReplacingMergeTree",
    "sector_fund_flow": "ReplacingMergeTree",
    "daban_board_event": "ReplacingMergeTree",
    # 2026-08-29 S2 估值路A + A22：日频快照按 (symbol, trade_date) 同键替换幂等
    "index_valuation_daily": "ReplacingMergeTree",
    "a50_futures_daily": "ReplacingMergeTree",
    # 2026-08-30 GAP-F-23：日频按 (symbol, trade_date) 同键替换幂等
    "kline_global": "ReplacingMergeTree",
    # 2026-09-09 DS-223：THS 主数据快照按 (trade_date, symbol) 同键替换幂等
    "stock_profile_ths": "ReplacingMergeTree",
}

_DATABASE = "c1_market"


def apply() -> int:
    """执行所有建表 DDL + 增量迁移。"""
    print("=== 创建数据库 ===")
    # #256③ 路线B（2026-08-22）：writer 无 CREATE DATABASE 权限（实证 Code 497），
    # 库由管理员预建（apply_rbac.py）；ensure_database 存在即过、缺失才 CREATE、失败 fail-visible，
    # 替代 ch_writer.query 直发 CREATE 走降级链的旧路径（TCP churn + HTTP 伪报病根）。
    if not ch_writer.ensure_database(_DATABASE):
        print(f"  [ERROR] 数据库 {_DATABASE} 不存在且当前凭据无权创建——需管理员预建（apply_rbac.py）")
        return 2
    print(f"  {_DATABASE} ✓")

    print("\n=== 执行建表 DDL ===")
    for table, ddl in _ALL_DDL:
        print(f"  {table} ...", end=" ")
        ch_writer.query(ddl)
        print("✓")

    print("\n=== 执行增量迁移（ALTER TABLE，子进程隔离+探针） ===")
    # 2026-09-14 治本两层：①探针核实（ch_writer 吞错+无条件 ✓ 曾致多批假成功）
    # ②子进程隔离——主进程大 DDL 触发通道污染（Code 62→TCP 失效→HTTP 500 全军覆没），
    #   迁移在独立干净进程执行+进程内探针
    import subprocess

    migrate_failed = 0
    probe_py = (
        "import re, sys\n"
        "from zephyr.data import ch_reader, ch_writer\n"
        "ch_writer.query(sys.argv[1])\n"
        "m = re.search(r'ADD COLUMN IF NOT EXISTS (\\w+)', sys.argv[1])\n"
        "if not m:\n"
        "    print('OK-noprobe')\n"
        "    sys.exit(0)\n"
        "col = m.group(1)\n"
        "db, tbl = sys.argv[2].split('.', 1)\n"
        "got = ch_reader.query(\n"
        "    f\"SELECT count() FROM system.columns WHERE database='{db}' \"\n"
        "    f\"AND table='{tbl}' AND name='{col}' FORMAT TSV\"\n"
        ").strip()\n"
        "print('OK' if got == '1' else 'MISS')\n"
        "sys.exit(0 if got == '1' else 1)\n"
    )
    repo_root = str(Path(__file__).resolve().parents[2])
    for table, sql in _MIGRATIONS:
        print(f"  {table} ...", end=" ", flush=True)
        r = subprocess.run(
            [sys.executable, "-c", probe_py, sql, table],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=repo_root,
        )
        out_lines = (r.stdout or "").strip().splitlines()
        verdict = out_lines[-1] if out_lines else f"rc={r.returncode}"
        if r.returncode == 0 and "OK" in verdict:
            print(f"✓ (探针核实: {verdict})")
        else:
            err_tail = (r.stderr or "").strip().splitlines()
            err_msg = err_tail[-1][:90] if err_tail else ""
            print(f"✗ 探针未过: {verdict} {err_msg}")
            migrate_failed += 1

    print("\n=== 建表 + 迁移完成 ===")
    if migrate_failed:
        print(f"[FAIL] {migrate_failed} 条迁移探针未通过——ALTER 实际未生效", file=sys.stderr)
        return 3
    return 0


def verify() -> int:
    """查询 CH 表引擎并与预期对比。"""
    sql = f"SELECT name, engine FROM system.tables WHERE database = '{_DATABASE}' ORDER BY name"
    raw = ch_writer.query(sql)

    if not raw.strip():
        print(f"[ERROR] 查询 system.tables 返回空——ClickHouse 可能不可达或库 {_DATABASE} 不存在")
        return 2

    actual: dict[str, str] = {}
    for line in raw.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 2:
            actual[parts[0]] = parts[1]

    print(f"{'表名':<25} {'预期引擎':<25} {'实际引擎':<25} {'is_replacing':<15} {'状态'}")
    print("-" * 100)

    all_match = True
    for table, expected_prefix in _EXPECTED_ENGINES.items():
        engine = actual.get(table, "")
        if not engine:
            print(f"{table:<25} {expected_prefix:<25} {'(不存在)':<25} {'':<15} ❌ 表不存在")
            all_match = False
            continue

        is_replacing = ch_writer.is_replacing_engine(f"{_DATABASE}.{table}")
        matches = engine.startswith(expected_prefix)
        status = "✅ 一致" if matches else "❌ 不一致"
        if not matches:
            all_match = False
        print(f"{table:<25} {expected_prefix:<25} {engine:<25} {is_replacing!s:<15} {status}")

    extra = set(actual.keys()) - set(_EXPECTED_ENGINES.keys())
    for table in sorted(extra):
        engine = actual[table]
        is_replacing = ch_writer.is_replacing_engine(f"{_DATABASE}.{table}")
        print(f"{table:<25} {'(未预期)':<25} {engine:<25} {is_replacing!s:<15} ⚠️ 未在选型矩阵中")

    print("-" * 100)
    if all_match:
        print("[OK] 所有表引擎与设计一致")
        return 0
    print("[FAIL] 存在引擎不一致，请检查")
    return 1


def main() -> int:
    """入口：默认 apply + verify，--verify 仅验证。"""
    if "--verify" in sys.argv:
        return verify()
    rc = apply()
    if rc != 0:
        return rc
    print()
    return verify()


if __name__ == "__main__":
    sys.exit(main())
