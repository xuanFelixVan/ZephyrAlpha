# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.fundamental.ir_activity_record
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.irm_provider; scripts/ch/irm_extract_batch.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] ir_activity_record 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ir_activity_record（C9 投资者关系活动记录表·原文层）DDL-as-Code
（category_id: fund_ir_activity_record）。

D7 文本抽取（altdata_line 09 清单 D7 波3，2026-09-18 夜班施工）。
每行 = 一份投资者关系活动记录表（调研纪要）的元数据行——官方接口
irm.cninfo.com.cn/newircs/index/search（searchTypes=4），匿名公开；
正文在 PDF（attachmentUrl → static.cninfo.com.cn），PDF 原件即快照落 G 盘冷库
（G:\\zephyr_cold\\30_corpus\\web_snapshots\\<批次>_irm_ir_records\\），
本表 snapshot_path 列可反查 PDF 快照（冷库 SOP：快照类=原文不动）。

抽取物走 c3_fundamental.ir_activity_extracted（LLM 管道读 PDF 文本），本表不动。
置信度门语义同 irm_interactive_extracted：<0.7 或校验不过=manual_pool。

PIT 双轴：publish_date=事实时间锚（记录表披露时点）；ingest_ts=采集时间。

引擎：ReplacingMergeTree(ingest_ts) 同 record_id 重爬幂等覆盖；
PARTITION BY toYYYYMM(publish_date)；ORDER BY (record_id)。
"""

from __future__ import annotations

# category_id: fund_ir_activity_record
# calc_mode: preload

IR_ACTIVITY_RECORD_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.ir_activity_record
(
    record_id        String                      COMMENT '记录表唯一ID(源 attachedId/indexId)',
    stock_code       String                      COMMENT '股票代码(6位裸码)',
    company_name     String                      COMMENT '公司简称(源 companyShortName)',
    title            String                      COMMENT '记录表标题(mainContent)',
    publish_date     Date                        COMMENT '披露日期(源 pubDate 毫秒时戳转日期, 事实时间锚)',
    pdf_url          String                      COMMENT 'PDF 相对路径(源 attachmentUrl, 静态域=static.cninfo.com.cn)',
    pdf_size_kb      UInt32                      DEFAULT 0 COMMENT 'PDF 大小 KB',
    snapshot_path    String                      COMMENT 'G盘 PDF 快照绝对路径(可反查原件)',
    data_source      LowCardinality(String)      DEFAULT 'irm_cninfo' COMMENT '数据来源',
    ingest_ts        DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(stock_code,1,1) IN ('6','9'), 'SH', substring(stock_code,1,2) IN ('43','83','87','92'), 'BJ', 'SZ') COMMENT '交易所码(深所平台为主, 沪/北码按前缀推导)',
    symbol_canonical String MATERIALIZED if(position(stock_code, '.') > 0, stock_code, concat(stock_code, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(publish_date)
ORDER BY (record_id)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "ir_activity_record"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_ir_activity_record"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(publish_date)"
ORDER_BY = "(record_id)"

INSERT_COLUMNS = (
    "(record_id, stock_code, company_name, title, publish_date, pdf_url, "
    "pdf_size_kb, snapshot_path, data_source)"
)
