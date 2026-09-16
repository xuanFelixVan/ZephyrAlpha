# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md | §consensus
# [MODULE] schemas.categories.fundamental.consensus_daily_repaired
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] none（纯常量模块，无入向依赖；被 build_consensus_daily_repaired.py 与
#                 apply_consensus_daily_repaired_ddl.py 按名导入 INSERT_COLUMNS/DDL/provenance 常量）
# [CONSUMERS] build_consensus_daily_repaired.py（重建 CLI）；factor/expectations 值类因子复评（EXP-01/02/03/05）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] consensus_daily_repaired 表 DDL 唯一真源（DDL-as-Code）；与 DS-229 consensus_daily 物理隔离双轨并存
#              （禁读写现表，方案 §L48/§L64-65）；列序=DS-229 二十列 + 两列 provenance，语义逐列对齐现表；
#              每行=PIT 正确快照（只聚合 publish_date<=trade_date，零 embargo）；无覆盖不成行（禁前向填充）；
#              forecast_year 锚定日历年；ReplacingMergeTree(ingest_ts) 同键重建幂等；
#              PARTITION BY toYYYYMM(trade_date) 与 ORDER BY 与现表同构（消费方零改动切换）
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 与 DB 不一致->apply_consensus_daily_repaired_ddl.py --verify 退出码 1
# [TESTS] python scripts/ch/build_consensus_daily_repaired.py --check
# [TTL] permanent
"""consensus_daily_repaired（双轨重建表）DDL-as-Code（category_id: fund_consensus_daily_repaired）。

本文件是 c3_fundamental.consensus_daily_repaired 表结构的唯一真源。
施工依据：docs/_working/2026-09-14-c4-history-repair-plan.md §2-L4/§6（双轨隔离条款）；
污染定性真源：policies/expectation_consumption_design_policy.md §9（DS-229 历史快照=东财源站
"当前快照"回放，值类因子全阻塞）；裁定 #253（值类因子待 C4 修复后复评）。

为什么要这张表（第一性原理）：
    DS-229 的 eps_consensus 族列来自 research_report 的 fy0/fy1/fy2 槽位，而该槽位在源站是
    "页面当前快照"而非"报告发布时点值"——历史区间每一行都是未来函数。PDF 原文是发布时点的
    真历史原件，C4 提取链从中取回 (report_id, forecast_year, eps)，按 DS-229 同口径重聚合，
    即得 PIT 干净的历史一致预期。双轨并存、不覆盖现表，切换权在 Owner（switch_gate）。

数据源与覆盖边界（诚实声明，勿在消费侧假设连续性）：
    segment A  2017-01-02 ~ 2021-12-31  eps_source='pdf_forecast_high'
              = pdf_forecast_extracted confidence='high'（表格几何路径）经量纲守卫后聚合；
              评级/覆盖度统计沿用 research_report（§9.2 定性：publish_date/评级/机构/计数不受值污染）。
    segment B  2026-07-22 ~ 最新快照日  eps_source='analyst_forecast_snapshot'
              = analyst_forecast（同花顺一致预期官方日度快照，§9.2 认定的干净 PIT 源）直接映射，
              不经窗口聚合（该源本身已是聚合值），window_days 列记 1 标记"无窗口"。
    空洞      2022-01-01 ~ 2026-07-21  无任何行。
              该段 PDF 被 EO_Bot 反爬挡住（方案 §1 出界条款，8.6 万份=独立子工程），
              按 PIT 铁律禁前向填充，故不补、不插值。消费方必须按段取数。

provenance 两列的必要性：
    双轨期间任何因子结论都要能回答"这个值来自哪条证据链"，故 eps_source 逐行留痕；
    build_batch 记本次重建批次（守卫参数/源表行数写在 docs/_working/reports/ 台账）。
"""

from __future__ import annotations

# category_id: fund_consensus_daily_repaired
# calc_mode: preload（与 DS-229 同款，回测时预加载到内存）

CONSENSUS_DAILY_REPAIRED_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.consensus_daily_repaired
(
    trade_date        Date                     COMMENT '交易日（快照日）',
    symbol            String                   COMMENT '证券代码（6位）',
    forecast_year     UInt16                   COMMENT '预测目标日历年（非槽位序）',
    eps_consensus     Float64                  COMMENT '窗口内该年 EPS 预测均值（PIT 真值）',
    eps_median        Float64                  COMMENT '窗口内该年 EPS 预测中位数',
    eps_std           Float64                  COMMENT '窗口内该年 EPS 预测总体标准差（n=1 时为 0）',
    eps_min           Float64                  COMMENT '窗口内该年 EPS 预测最小值',
    eps_max           Float64                  COMMENT '窗口内该年 EPS 预测最大值',
    pe_consensus      Nullable(Float64)        COMMENT 'PE 预测均值；segment A 恒 NULL（C4 提取表 pe 列 0/192302 有值，实测），segment B 取 forecast_pe',
    n_reports         UInt16                   COMMENT '窗口内对该年有预测的研报数（A=high 置信提取行数；B=analyst_count）',
    n_orgs            UInt16                   COMMENT '其中不同机构数（A=窗口内全部研报 org_name 去重，沿用 research_report 干净计数列）',
    rating_score_mean Nullable(Float64)        COMMENT '窗口内全部研报评级分均值（买入7/增持5/中性持有3/减持2/卖出1，空值不计入）',
    n_buy             UInt16                   COMMENT '窗口内买入评级研报数',
    n_add             UInt16                   COMMENT '窗口内增持评级研报数',
    n_neutral         UInt16                   COMMENT '窗口内中性/持有评级研报数',
    n_negative        UInt16                   COMMENT '窗口内减持/卖出/回避评级研报数',
    n_unrated         UInt16                   COMMENT '窗口内无评级研报数',
    last_report_date  Date                     COMMENT '窗口内最新研报发布日期',
    window_days       UInt16                   COMMENT '构建窗宽（自然日）；segment B 无窗口聚合记 1',
    data_source       LowCardinality(String)   COMMENT '聚合口径来源标识（沿用 DS-229 列名以零改动切换）',
    eps_source        LowCardinality(String)   COMMENT 'EPS 证据链：pdf_forecast_high / analyst_forecast_snapshot',
    build_batch       String                   COMMENT '重建批次标识（守卫参数与源行数见 docs/_working/reports/ 台账）',
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date, forecast_year)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "consensus_daily_repaired"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_consensus_daily_repaired"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date, forecast_year)"

# 与 DS-229 逐列同名的前 20 列（消费方切换时按列名取数，不依赖位置）
SHARED_COLUMNS = (
    "trade_date, symbol, forecast_year, eps_consensus, eps_median, eps_std, eps_min, eps_max, "
    "pe_consensus, n_reports, n_orgs, rating_score_mean, n_buy, n_add, n_neutral, n_negative, "
    "n_unrated, last_report_date, window_days, data_source"
)

# 列清单（INSERT 显式指定，排除 MATERIALIZED/DEFAULT(now) 列）
INSERT_COLUMNS = f"({SHARED_COLUMNS}, eps_source, build_batch)"

# provenance 取值常量（builder 与验收脚本共用，禁散落字面量）
EPS_SOURCE_PDF_HIGH = "pdf_forecast_high"
EPS_SOURCE_ANALYST_FORECAST = "analyst_forecast_snapshot"
