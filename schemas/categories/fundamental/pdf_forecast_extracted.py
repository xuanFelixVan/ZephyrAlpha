# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.fundamental.pdf_forecast_extracted
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; scripts/ch/c4_extract_batch.py（C4 历史修复批处理）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] pdf_forecast_extracted 表 DDL 唯一真源；变更需经 apply 基建执行；
#              原表 research_report 不动（数据保存者），本表=提取产物，可整体废弃重建；
#              同键（report_id, forecast_year）重提取幂等覆盖
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致->apply 基建 --verify 报漂移
# [TTL] permanent
"""pdf_forecast_extracted（C4 历史修复：研报 PDF 盈利预测提取产物）DDL-as-Code
（category_id: fund_pdf_forecast_extracted, calc_mode: lazy）。

使命：research_report 的预测槽位是源站当前快照语义（历史无 PIT，档案=
docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §9）；
本表承载从 PDF 原文（发布时点冻结件）提取的**真历史预测值**——
每行 = 一份研报 PDF 里抠出的一个 (预测年份, EPS, PE) 三元组 + 置信度与证据。

置信度语义：
    high = 启发式数值紧邻年度表头（标准表格式）；mid = 启发式跨行推断 / LLM 高自评分；
    low = LLM 低自评分或证据残缺（low 不入重建聚合，仅留档审计）。

引擎：ReplacingMergeTree(ingest_ts) 同键重提取幂等覆盖；
PARTITION BY toYYYYMM(publish_date)；ORDER BY (report_id, forecast_year)。
"""

from __future__ import annotations

# category_id: fund_pdf_forecast_extracted
CATEGORY_ID = "fund_pdf_forecast_extracted"
TABLE_NAME = "pdf_forecast_extracted"
DATABASE = "c3_fundamental"
CALC_MODE = "lazy"

PDF_FORECAST_EXTRACTED_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.pdf_forecast_extracted
(
    report_id      String                   COMMENT '研报编号（=infoCode，FK research_report）',
    symbol         String                   COMMENT '标的（承自 research_report）',
    publish_date   Date                     COMMENT '研报发布日期（PDF 冻结时点）',
    forecast_year  Int32                    COMMENT '预测目标日历年（PDF 原文字样归一）',
    eps            Nullable(Float64)        COMMENT '预测 EPS（元）',
    pe             Nullable(Float64)        COMMENT '预测 PE',
    confidence     LowCardinality(String)   COMMENT '置信度 high/mid/low（low 不入重建聚合）',
    method         LowCardinality(String)   COMMENT '提取法 heuristic/llm',
    snippet        String                   COMMENT '证据片段（PDF 原文上下文，审计用）',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(publish_date)
ORDER BY (report_id, forecast_year)
"""

INSERT_COLUMNS = (
    "(report_id, symbol, publish_date, forecast_year, eps, pe, confidence, method, snippet)"
)
