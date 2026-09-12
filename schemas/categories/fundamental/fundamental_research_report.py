# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental.fundamental_research_report
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_research_report_ddl.py; backfill_research_report_full.py; (待接线) zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] research_report 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply 脚本执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+apply_research_report_ddl.py --verify 退出码1
# [TESTS] python scripts/ch/apply_research_report_ddl.py --verify（建表后）+ python scripts/ch/verify_schema_truth.py --table research_report
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""research_report（券商研报明细）DDL-as-Code（category_id: fundamental_research_report, calc_mode: preload）。

本文件是 c3_fundamental.research_report 表结构的唯一真源（DDL-as-Code 模式）。
施工依据：docs/_working/2026-09-12-research-report-data-plan.md（研报+分析师预测数据侧施工方案，
Owner 2026-09-12 拍板"先搞定数据"）。

背景（2026-09-12 数据分层体检结论）：
    现有 research_report_incremental 任务（tasks.yaml:1242）把研报元数据塞进 c3_fundamental.news_data
    共表，丢失全部高价值字段——盈利预测数值（EPS/PE）、个股代码（news_data 无 symbol 列）、
    评级变动、PDF 正文。本表承接全字段研报明细，作为：
    1. 研报元数据真源（机构/评级/行业/标题/日期/PDF链接）
    2. 一致预期历史的原料——每份研报自带预测期 0/1/2 的 EPS/PE 预测值 + publish_date，
       按 (symbol, as-of 日期) 聚合即 PIT 正确的一致预期（对标朝阳永续原理，免付费数据商）。
    实测深度：东财研报接口按个股可回溯至 2017-08（茅台 771 条实证；
    接口 beginTime 参数 2000-01-01，实际覆盖以返回为准）。

字段设计：
    fy0/fy1/fy2 = 预测期 0/1/2（按 EPS 列年份升序映射；akshare 动态年份列
    "{YYYY}-盈利预测-收益/市盈率" 在 provider 侧展开为固定列+年份值，防年份滚动漂移）。
    body_status/body_ref 为 PDF 全文二期预留（本阶段只存链接，不做批量下载）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——同 (symbol, publish_date, report_id) 重复行保留最新。
    PARTITION BY toYYYYMM(publish_date)——按发布日期月分区。
    ORDER BY (symbol, publish_date, report_id)——单股时序点查友好，report_id 兜底防同日同股重名。

审计列（audit 1.7 #ARCH-CH-022 对齐 analyst_forecast 先例）：
    ingest_ts DateTime64(3,'UTC') DEFAULT now()；exchange/symbol_canonical MATERIALIZED
    派生（TRAE-082 universal，表达式与 fundamental_analyst_forecast.py 完全一致）。
"""

from __future__ import annotations

# category_id: fundamental_research_report
# calc_mode: preload（回测时预加载到内存）

RESEARCH_REPORT_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.research_report
(
    report_id      String                   COMMENT '东财研报唯一ID（infoCode，自PDF链接 H3_{code}_1.pdf 提取，缺失时MD5(symbol+title+date)兜底）',
    symbol         String                   COMMENT '证券代码（6位）',
    title          String                   COMMENT '报告标题',
    org_name       String            DEFAULT '' COMMENT '研报机构',
    rating         LowCardinality(String) DEFAULT '' COMMENT '东财评级（买入/增持/中性/减持/卖出等）',
    rating_change  LowCardinality(String) DEFAULT '' COMMENT '评级变动（接口返回时填写：上调/下调/维持/首次）',
    industry       String            DEFAULT '' COMMENT '所属行业（接口返回口径）',
    researchers    String            DEFAULT '' COMMENT '研究员（多人分号分隔）',
    publish_date   Date                     COMMENT '发布日期',
    fy0_year       UInt16            DEFAULT 0 COMMENT '预测期0年份（当前年度）',
    eps_fy0        Nullable(Float64)        COMMENT '预测期0 每股收益预测',
    pe_fy0         Nullable(Float64)        COMMENT '预测期0 市盈率预测',
    fy1_year       UInt16            DEFAULT 0 COMMENT '预测期1年份（次年）',
    eps_fy1        Nullable(Float64)        COMMENT '预测期1 每股收益预测',
    pe_fy1         Nullable(Float64)        COMMENT '预测期1 市盈率预测',
    fy2_year       UInt16            DEFAULT 0 COMMENT '预测期2年份（后年）',
    eps_fy2        Nullable(Float64)        COMMENT '预测期2 每股收益预测',
    pe_fy2         Nullable(Float64)        COMMENT '预测期2 市盈率预测',
    source_url     String            DEFAULT '' COMMENT '研报PDF链接（pdf.dfcfw.com 直链）',
    body_status    UInt8             DEFAULT 0 COMMENT 'PDF下载状态：0未下载/1已存（二期批量下载用）',
    body_ref       String            DEFAULT '' COMMENT 'PDF本地路径（二期）',
    data_source    LowCardinality(String) DEFAULT 'akshare_research_report_em' COMMENT '数据来源',
    ingest_ts      DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(publish_date)
ORDER BY (symbol, publish_date, report_id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "research_report"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fundamental_research_report"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(publish_date)"
ORDER_BY = "(symbol, publish_date, report_id)"

# 列清单（用于 INSERT 时显式指定，排除 MATERIALIZED/DEFAULT(now) 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(report_id, symbol, title, org_name, rating, rating_change, industry, researchers, "
    "publish_date, fy0_year, eps_fy0, pe_fy0, fy1_year, eps_fy1, pe_fy1, fy2_year, eps_fy2, pe_fy2, "
    "source_url, body_status, body_ref, data_source)"
)
