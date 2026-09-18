# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_road_freight_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] road_freight_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""road_freight_index（中国公路物流运价指数）DDL-as-Code（category_id: market_road_freight_index）.

油价链三件之二（骨架 01 号文档 E 族/altdata_line 09 清单 D4 波2，2026-09-18 夜班施工）。
中物联（中国物流与采购联合会）×林安物流联合发布的**中国公路物流运价周指数**结构化数据集：
总指数 + 整车 + 零担轻货 + 零担重货 四序列长表。06 传导链引擎 N1b 运价节点挂价消费
（N0→N1b 1-2 周时滞先验）。

源（2026-09-18 夜班实测）：
    - akshare index_price_cflp 坏：底层站 index.0256.cn（林安指数站）超时不可达
      （ReadTimeout 30s×3 实测），rejected 留痕。
    - 正门=中物联官网 chinawuliu.com.cn「学术研究/统计数据」频道的
      「中国公路物流运价周指数报告」文章序列（2015-09 起）——网页类源，
      **爬时原文快照进 G 盘冷库** 30_corpus/web_snapshots/20260918_chinawuliu_roadfreight/
      （data_source_onboarding_sop §12/§13 + 10_g_drive_cold_storage_sop），
      manifest drawers.jsonl 登记一行。

PIT 双轴：trade_date=周指数报告期截止日（周五，标题日期=发布日通常同日或次周初）；
ingest_ts=采集时间。指数基点：2015 年起定基（源端口径），点数。

引擎选型：
    ReplacingMergeTree（无版本列），同键 (index_code, trade_date) 重拉幂等替换。
    PARTITION BY toYYYYMM(trade_date)。
"""

from __future__ import annotations

# category_id: market_road_freight_index
# calc_mode: preload

ROAD_FREIGHT_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.road_freight_index
(
    index_code   LowCardinality(String)   COMMENT '指数代码(CFLP_ROAD_TOTAL/CFLP_ROAD_FTL/CFLP_ROAD_LTL_LIGHT/CFLP_ROAD_LTL_HEAVY)',
    trade_date   Date                     COMMENT '周指数报告期截止日(周五,事实时间锚)',
    index_name   String                   COMMENT '指数中文名',
    index_value  Decimal(18, 4)           COMMENT '指数点位(点,定基)',
    change_pct   Nullable(Decimal(10, 4)) COMMENT '环比涨跌幅(%)',
    source_url   String                   DEFAULT '' COMMENT '原文快照来源 URL(溯源锚)',
    data_source  LowCardinality(String)   DEFAULT 'chinawuliu_web' COMMENT '数据来源',
    quality_flag UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts    DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (index_code, trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "road_freight_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_road_freight_index"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(index_code, trade_date)"

INSERT_COLUMNS = "(index_code, trade_date, index_name, index_value, change_pct, source_url, data_source, quality_flag)"
