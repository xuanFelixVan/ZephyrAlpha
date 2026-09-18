# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_cftc_positioning
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] scripts.ch.apply_cross_asset_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] cftc_positioning 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 scripts/ch/apply_cross_asset_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_cross_asset_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_cross_asset_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""cftc_positioning（CFTC 持仓报告 COT，长表化）DDL-as-Code（category_id: market_cftc_positioning）.

D5 跨资产·H7 CFTC 持仓（骨架 01 号文档 D5 族 / altdata_line 09 清单，DS-CAND-024 毕业，
2026-09-18 全流通战役 st-ff-altdataF-20260918 施工）。

源与覆盖（2026-09-18 本机实测，四接口全活）：
    - AKShare macro_usa_cftc_c_holding            = 商品类**非商业**持仓（12 品种）✅ 1935 行
    - AKShare macro_usa_cftc_nc_holding           = 外汇类**非商业**持仓（9 币种）  ✅ 1935 行
    - AKShare macro_usa_cftc_merchant_goods_holding   = 商品类**商业**持仓（12 品种）✅ 1935 行
    - AKShare macro_usa_cftc_merchant_currency_holding= 外汇类**商业**持仓（9 币种） ✅ 1935 行
    区间实测 1986-01-15 ~ 2026-09-08（周频，COT 报告 as-of 周二/发布周五）。
    ⚠ 上游为金十 datacenter（datacenter.jin10.com/reportType/dc_cftc_*）——与 2025-10 停更的
      议息日历（dc_*_calendar 族）**不同报表**：CFTC 族实测仍日新（max=2026-09-08），
      即"金十退役"是**分报表**的而非整站，本表停更检测由哨兵独立承担。

宽转长：源端每接口是「日期 × (品种×多头/空头/净仓位)」宽表（37/28 列），本表按
(trader_class, asset_class, market_name, report_date) 长表化，便于按品种/按交易者类别
切片与因子计算（净持仓 z-score、商业-非商业分歧度）。1935×(12+9)×2 = 81,270 行/全量。

PIT 双轴：report_date=COT as-of 日期（事实时间锚，源端自带"日期"列，非运行日）；
ingest_ts=采集时间。注意 COT 发布滞后 as-of 日 3 个交易日（周五 15:30 ET），消费侧
按 report_date 对齐时须自行加发布滞后，避免前视。

引擎选型：
    ReplacingMergeTree（无版本列），同键重拉幂等替换。
    PARTITION BY toYear(report_date)——40 年长历史（1986-）若按月分区将产生 480+ 分区，
    远超 CH 单表健康分区数；年分区 + ORDER BY 前缀已满足裁剪需求（例外理由留痕）。
"""

from __future__ import annotations

# category_id: market_cftc_positioning
# calc_mode: preload

CFTC_POSITIONING_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.cftc_positioning
(
    report_date     Date                     COMMENT 'COT 报告 as-of 日期(周二,事实时间锚;发布滞后3个交易日)',
    trader_class    LowCardinality(String)   COMMENT '交易者类别(commercial=商业/non_commercial=非商业)',
    asset_class     LowCardinality(String)   COMMENT '资产大类(goods=商品/currency=外汇)',
    market_name     String                   COMMENT '品种中文名(源端口径:纽约原油/黄金/大豆/美元/日元...)',
    long_positions  Nullable(Int64)          COMMENT '多头仓位(合约数)',
    short_positions Nullable(Int64)          COMMENT '空头仓位(合约数)',
    net_positions   Nullable(Int64)          COMMENT '净仓位(多头-空头,合约数)',
    data_source     LowCardinality(String)   DEFAULT 'akshare_alt' COMMENT '数据来源',
    quality_flag    UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYear(report_date)
ORDER BY (trader_class, asset_class, market_name, report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "cftc_positioning"
DATABASE = "c1_market"
CATEGORY_ID = "market_cftc_positioning"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYear(report_date)"
ORDER_BY = "(trader_class, asset_class, market_name, report_date)"

INSERT_COLUMNS = (
    "(report_date, trader_class, asset_class, market_name, "
    "long_positions, short_positions, net_positions, data_source, quality_flag)"
)
