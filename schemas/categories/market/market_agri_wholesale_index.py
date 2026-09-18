# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_agri_wholesale_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] agri_wholesale_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""agri_wholesale_index（农业农村部批发价格 200 指数）DDL-as-Code（category_id: market_agri_wholesale_index）.

F13 肉蛋菜批发价（骨架 01 号文档 F 族/altdata_line 09 清单 D4 波2，2026-09-18 夜班施工）。
农业农村部「全国农产品批发市场价格信息系统」两条日度指数：
农产品批发价格 200 指数（AJC200）+ 菜篮子产品批发价格 200 指数（CLZ200），2005-09 起。
06 传导链引擎 N5 食品节点挂价消费（N0→N5 3-6 月化肥/运输联动先验）。

源与覆盖（2026-09-18 夜班实测，分品种接口证据留痕）：
    - AKShare macro_china_agricultural_product（=农产品批发价格 200 指数日度）✅
    - AKShare macro_china_vegetable_basket（=菜篮子产品批发价格 200 指数日度）✅
    - 分品种（猪肉/鸡蛋/蔬菜细分）日均价：官方系统 pfsc.agri.cn API 实测坏
      （pageList 404 / getVarietyMajorCategories 业务 500「服务故障」），rejected 留痕；
      指数层先行（挂价铁律：指数即可观测序列），分品种待源端恢复后扩列。

PIT 双轴：trade_date=指数日期（事实时间锚）；ingest_ts=采集时间。基点：2015 年=100（源端口径）。

引擎选型：
    ReplacingMergeTree（无版本列），同键 (index_code, trade_date) 重拉幂等替换。
    PARTITION BY toYYYYMM(trade_date)。
"""

from __future__ import annotations

# category_id: market_agri_wholesale_index
# calc_mode: preload

AGRI_WHOLESALE_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.agri_wholesale_index
(
    index_code   LowCardinality(String)   COMMENT '指数代码(AJC200=农产品批发价格200/CLZ200=菜篮子产品批发价格200)',
    trade_date   Date                     COMMENT '指数日期(事实时间锚)',
    index_name   String                   COMMENT '指数中文名',
    index_value  Decimal(18, 4)           COMMENT '指数点位(基点 2015 年=100,源端口径)',
    change_pct   Nullable(Decimal(10, 4)) COMMENT '日环比涨跌幅(%)',
    data_source  LowCardinality(String)   DEFAULT 'akshare_alt' COMMENT '数据来源',
    quality_flag UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts    DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (index_code, trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "agri_wholesale_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_agri_wholesale_index"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(index_code, trade_date)"

INSERT_COLUMNS = "(index_code, trade_date, index_name, index_value, change_pct, data_source, quality_flag)"
