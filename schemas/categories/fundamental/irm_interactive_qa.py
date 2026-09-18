# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.fundamental.irm_interactive_qa
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.irm_provider; scripts/ch/irm_extract_batch.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] irm_interactive_qa 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""irm_interactive_qa（C6 深交所互动易问答对·原文层）DDL-as-Code
（category_id: fund_irm_interactive_qa）。

D7 文本抽取（altdata_line 09 清单 D7 波3，2026-09-18 夜班施工）。
每行 = 互动易平台一条投资者提问（含公司回答，若已答）——官方接口
irm.cninfo.com.cn/newircs/index/search（searchTypes=11），匿名公开。

原文快照先行：抓取时整页 API 响应 JSON 落 G 盘冷库
（G:\\zephyr_cold\\30_corpus\\web_snapshots\\<批次>_irm_interactive\\），
本表 snapshot_path 列可反查快照文件（冷库 SOP §3：快照目录即时间戳）。
注意：CH 写侧 tsv_escape 统一空白归一（\n\t\r→空格，平台约定），文本逐字
比对以 G 盘快照为准（抽检口径=空白归一化后全等，2026-09-18 500/500 通过）。

抽取物走 c3_fundamental.irm_interactive_extracted（LLM 管道），本表不动。
置信度门语义：<0.7 或校验不过的抽取行 review_status='manual_pool'，
下游只准消费 review_status='approved'（见 extracted 表 docstring）。

PIT 双轴：question_date=事实时间锚（提问公开时点）；answer_date=公司回答
公开时点（情绪/供应链信号的可用时点）；ingest_ts=采集时间。

引擎：ReplacingMergeTree(ingest_ts) 同 qa_id 重爬幂等覆盖；
PARTITION BY toYYYYMM(question_date)；ORDER BY (qa_id)。
"""

from __future__ import annotations

# category_id: fund_irm_interactive_qa
# calc_mode: preload

IRM_INTERACTIVE_QA_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.irm_interactive_qa
(
    qa_id            String                      COMMENT '互动易条目唯一ID(源 esId, 形如 11_<indexId>)',
    stock_code       String                      COMMENT '股票代码(6位裸码)',
    company_name     String                      COMMENT '公司简称(源 companyShortName)',
    question_text    String                      COMMENT '投资者提问原文(mainContent)',
    question_date    Date                        COMMENT '提问日期(源 pubDate 毫秒时戳转日期, 事实时间锚)',
    answer_text      String                      COMMENT '公司回答原文(attachedContent, 未回答=空串)',
    answer_date      Nullable(Date)              COMMENT '回答日期(源 attachedPubDate, 未回答=NULL)',
    industry         String                      COMMENT '所属行业(源 trade 数组首元素)',
    praise_count     UInt32                      DEFAULT 0 COMMENT '提问点赞数(提问热度代理)',
    qa_status        UInt8                       DEFAULT 0 COMMENT '源 qaStatus 原值',
    snapshot_path    String                      COMMENT 'G盘原文快照路径(整页API响应JSON, 可反查)',
    data_source      LowCardinality(String)      DEFAULT 'irm_cninfo' COMMENT '数据来源',
    ingest_ts        DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(stock_code,1,1) IN ('6','9'), 'SH', substring(stock_code,1,2) IN ('43','83','87','92'), 'BJ', 'SZ') COMMENT '交易所码(互动易=深所平台为主, 沪/北码按前缀推导)',
    symbol_canonical String MATERIALIZED if(position(stock_code, '.') > 0, stock_code, concat(stock_code, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(question_date)
ORDER BY (qa_id)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "irm_interactive_qa"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_irm_interactive_qa"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(question_date)"
ORDER_BY = "(qa_id)"

INSERT_COLUMNS = (
    "(qa_id, stock_code, company_name, question_text, question_date, answer_text, "
    "answer_date, industry, praise_count, qa_status, snapshot_path, data_source)"
)
