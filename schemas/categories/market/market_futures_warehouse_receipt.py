# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_futures_warehouse_receipt
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] futures_warehouse_receipt 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""futures_warehouse_receipt（交易所仓单日报）DDL-as-Code（category_id: market_futures_warehouse_receipt）.

油价链三件之三（骨架 01 号文档 E 族/altdata_line 09 清单 D4 波2，2026-09-18 夜班施工）。
交易所每日仓单日报结构化数据集：品种 × 交割仓库明细（仓单量/当日增减/有效预报），
长表格式。06 传导链引擎"库存=仓单"可观测序列（节点挂价绑定缺件）消费。

源与覆盖（2026-09-18 夜班实测，接口可用性证据留痕）：
    - CZCE 郑商所：AKShare futures_warehouse_receipt_czce（每日 DFSStaticFiles xls），
      日度增量可用（本任务日更源）。源表两重现实：①"位置续行"语义（仓库列空=承上行
      仓库，换品牌/等级分行），provider 侧 ffill 仓库列；②27 品种列名异构
      （厂库编号/机构编号/提货地点/完税保税分列等），provider 侧 spec 归一——
      非核心列全部进 detail_attrs（k=v| 串）入键，行行唯一键，ReplacingMergeTree
      合并不吞行（2026-09-18 首版漏列实证：等键行 merge 塌缩 72->27 行/品种，已治本）。
      PTA/MA 完税+保税分列品种：receipts=两者合计，原始分列值留 detail_attrs。
    - SHFE 上期所：AKShare futures_shfe_warehouse_receipt（dailydata/*.dat JSON），
      实测仅 serving 归档段（~2014-05-19 起至 2025-11 中旬；2025-12 起源端 404，
      近端改版/WAF 属源端现实）→ 回填任务吃归档段，近端缺口登记 known_data_gaps。
    - DCE 大商所/GFEX 广期所：akshare 接口/源站实测坏（DCE 源站 HTTP 412 WAF），
      本批 rejected 留痕，不接入。
    - 交割仓库层级行 row_type='detail'；CZCE 源端自带"小计"行 row_type='subtotal'
      （仓单量/有效预报合计；增减列合计以 detail 行聚合为准）。

PIT 双轴：trade_date=事实时间锚（交易所仓单日报的自然日）；ingest_ts=采集时间。
单位口径：仓单量单位随品种（SHFE WGHTUNIT/CZCE 自然张或吨），逐品种自洽，跨品种不可比。

引擎选型：
    ReplacingMergeTree（无版本列），同键 (exchange, symbol, trade_date, row_type,
    warehouse_name, region, brand, grade) 重拉幂等替换。
    PARTITION BY toYYYYMM(trade_date)。
"""

from __future__ import annotations

# category_id: market_futures_warehouse_receipt
# calc_mode: preload

FUTURES_WAREHOUSE_RECEIPT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.futures_warehouse_receipt
(
    exchange         LowCardinality(String)   COMMENT '交易所(CZCE/SHFE;DCE/GFEX 源坏未接入)',
    symbol           LowCardinality(String)   COMMENT '品种代码(CZCE=SR/CF...;SHFE=VARID 如 cu/al/sp)',
    trade_date       Date                     COMMENT '仓单日报日期(事实时间锚)',
    row_type         LowCardinality(String)   COMMENT '行类型(detail=仓库明细/subtotal=源端小计行)',
    warehouse_name   String                   COMMENT '交割仓库简称(subtotal 行=TOTAL)',
    region           String                   COMMENT '地区(SHFE REGNAME;CZCE 源端无=空串)',
    detail_attrs     String                   DEFAULT '' COMMENT '明细属性串(k=v|年度/等级/品牌/产地/提货点等非核心列;入键防塌缩)',
    premium_discount Nullable(Decimal(12, 4)) COMMENT '升贴水(CZCE 多品种有;SHFE 无=NULL)',
    receipts         Nullable(Decimal(18, 4)) COMMENT '仓单数量(单位随品种,跨品种不可比)',
    delta            Nullable(Decimal(18, 4)) COMMENT '当日增减(仓单量)',
    valid_forecast   Nullable(Decimal(18, 4)) COMMENT '有效预报(CZCE 口径;SHFE 无=NULL)',
    data_source      LowCardinality(String)   DEFAULT 'akshare_alt' COMMENT '数据来源',
    quality_flag     UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts        DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (exchange, symbol, trade_date, row_type, warehouse_name, region, detail_attrs)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "futures_warehouse_receipt"
DATABASE = "c1_market"
CATEGORY_ID = "market_futures_warehouse_receipt"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(exchange, symbol, trade_date, row_type, warehouse_name, region, detail_attrs)"

INSERT_COLUMNS = "(exchange, symbol, trade_date, row_type, warehouse_name, region, detail_attrs, premium_discount, receipts, delta, valid_forecast, data_source, quality_flag)"
