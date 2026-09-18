# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_activity_gauge
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_activity_gauge 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_activity_gauge（实体活动宽表：工业增加值/社零/固投/城镇调查失业率）DDL-as-Code
（category_id: macro_activity_gauge）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
中国月度实体经济活动宽表：规模以上工业增加值同比(+累计) / 社会消费品零售总额(当月+同比+
累计) / 固定资产投资(自年初累计+同比) / 城镇调查失业率。

源（东财 datacenter/统计局口径，月度，fresh 实测 2026-08）：
    macro_china_gyzjz               → industrial_va_yoy/industrial_va_cum_yoy（2008- 起）
    macro_china_consumer_goods_retail → retail_sales/retail_sales_yoy/
                                       retail_sales_cum/retail_cum_yoy（2008- 起）
    macro_china_gdzctz              → fai_ytd/fai_yoy（2012- 起；早期月份当月同比可为空）
    macro_china_urban_unemployment  → urban_unemployment_rate（2018- 起，
                                       item=全国城镇调查失业率 单序列提取）

供给缺口留痕：出口交货值/发电量/粗钢/水泥产量无独立 akshare macro_ 接口
（正门=macro_china_nbs_nation 统计局树形 API，已挂账 DS-CAND 候选；
全社会用电量代理见 macro_daily_gauge 兄弟表规划）。
货运量接口 macro_china_society_traffic_volume 实测源端解码坏（rejected 留痕）。

与 c1_market.macro_data 的关系（查重声明）：
    macro_data=generic 长表；本表为宽表结构化数据集，
    按骨架分类学判据 2 独立成表，不构成双真源。

PIT 双轴：report_date=事实时间锚（统计期月末）；ingest_ts=采集时间。
金额单位亿元；同比/失业率单位 %。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(report_date)。
    ORDER BY (report_date)。
"""

from __future__ import annotations

# category_id: macro_activity_gauge
# calc_mode: preload

MACRO_ACTIVITY_GAUGE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_activity_gauge
(
    report_date           Date                        COMMENT '统计期月末(事实时间锚)',
    industrial_va_yoy     Nullable(Decimal(10, 4))    COMMENT '规上工业增加值当月同比(%)',
    industrial_va_cum_yoy Nullable(Decimal(10, 4))    COMMENT '规上工业增加值累计同比(%)',
    retail_sales          Nullable(Decimal(18, 4))    COMMENT '社会消费品零售总额当月(亿元)',
    retail_sales_yoy      Nullable(Decimal(10, 4))    COMMENT '社零当月同比(%)',
    retail_sales_cum      Nullable(Decimal(18, 4))    COMMENT '社零年初累计(亿元)',
    retail_cum_yoy        Nullable(Decimal(10, 4))    COMMENT '社零累计同比(%)',
    fai_ytd               Nullable(Decimal(18, 4))    COMMENT '固定资产投资自年初累计(亿元)',
    fai_yoy               Nullable(Decimal(10, 4))    COMMENT '固定资产投资同比(%)',
    urban_unemployment    Nullable(Decimal(10, 4))    COMMENT '城镇调查失业率(%)',
    data_source           LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag          UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts             DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_activity_gauge"
DATABASE = "c1_market"
CATEGORY_ID = "macro_activity_gauge"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(report_date)"

INSERT_COLUMNS = (
    "(report_date, industrial_va_yoy, industrial_va_cum_yoy, retail_sales, retail_sales_yoy, "
    "retail_sales_cum, retail_cum_yoy, fai_ytd, fai_yoy, urban_unemployment, data_source, quality_flag)"
)
