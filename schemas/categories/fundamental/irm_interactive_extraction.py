# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.fundamental.irm_interactive_extraction
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; scripts/ch/irm_extract_batch.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] irm_interactive_extracted 表 DDL 唯一真源；抽取行可由 qa_id 反查 irm_interactive_qa
#              原文与 G 盘快照；review_status='approved' 是下游唯一准许消费态（置信度门）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""irm_interactive_extracted（C6 互动易问答 LLM 抽取产物）DDL-as-Code
（category_id: fund_irm_interactive_extraction）。

D7 文本抽取（altdata_line 09 清单 D7 波3，2026-09-18 夜班施工）。
每行 = 一条问答对（qa_id FK irm_interactive_qa）的 LLM 结构化抽取：
涉及产品 / 供应链关系 / 情绪极性 / 置信度 / 原文证据。

置信度门（复用 pdf_forecast_extracted 先例 + D7 清单硬约束）：
    review_status='approved'   extraction_confidence>=0.7 且校验全过 —— 下游唯一准许消费态
    review_status='manual_pool' confidence<0.7 或校验不过（证据非原文逐字/极性非法/JSON 解析失败）
                               —— 入人工池，不入下游，留档待人工复核
    校验含反幻觉硬检查：evidence 必须是问答原文的逐字子串
    （_EXTRACT_RULES 契约机械化，substring 校验 fail-closed）。

可复现三列：extraction_confidence / model_version / prompt_version。
未回答的提问不抽取（无公司信号，抽了就是问句情绪污染）——只出 raw 层。

引擎：ReplacingMergeTree(extracted_at) 同 qa_id 重抽取幂等覆盖；
PARTITION BY toYYYYMM(pit_date)；ORDER BY (qa_id)。
"""

from __future__ import annotations

# category_id: fund_irm_interactive_extraction
# calc_mode: preload

IRM_INTERACTIVE_EXTRACTION_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.irm_interactive_extracted
(
    qa_id                  String                      COMMENT '互动易条目ID(FK irm_interactive_qa.qa_id)',
    stock_code             String                      COMMENT '股票代码(承自 raw 层)',
    pit_date               Date                        COMMENT 'PIT锚=信号可用时点(有回答=answer_date,否则question_date)',
    involves_product       String                      COMMENT '涉及产品/业务(原文出现的名称, 无=空串)',
    supply_chain_relation  String                      COMMENT '供应链关系(公司×主体×上下游, 无=空串)',
    sentiment              LowCardinality(String)      COMMENT '情绪极性 positive/neutral/negative(对公司口径)',
    extraction_confidence  Float64                     COMMENT '抽取置信度 0-1(LLM 自评, 门=0.7)',
    evidence               String                      COMMENT '证据原文摘录(逐字, 反幻觉 substring 校验)',
    review_status          LowCardinality(String)      COMMENT 'approved=入下游/manual_pool=人工池(含parse_fail)',
    reject_reason          String                      COMMENT '入池原因(低置信/证据非逐字/极性非法/解析失败)',
    model_version          String                      COMMENT '抽取模型(如 qwen3:8b)',
    prompt_version         String                      COMMENT 'prompt 版本号(改 prompt 必 bump)',
    extracted_at           DateTime64(3, 'UTC')        DEFAULT now() COMMENT '抽取时间戳'
)
ENGINE = ReplacingMergeTree(extracted_at)
PARTITION BY toYYYYMM(pit_date)
ORDER BY (qa_id)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "irm_interactive_extracted"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_irm_interactive_extraction"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(pit_date)"
ORDER_BY = "(qa_id)"

INSERT_COLUMNS = (
    "(qa_id, stock_code, pit_date, involves_product, supply_chain_relation, sentiment, "
    "extraction_confidence, evidence, review_status, reject_reason, model_version, prompt_version)"
)
