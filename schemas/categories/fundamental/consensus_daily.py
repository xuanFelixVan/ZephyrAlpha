# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] schemas.categories.fundamental.consensus_daily
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] none
# [CONSUMERS] build_consensus_daily.py（回补/重建）；（C2 起消费）factor/expectations 预期因子族；pit_manager 可选
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] consensus_daily 表 DDL 唯一真源；每行=PIT 正确快照（只聚合 publish_date<=trade_date 的研报，零 embargo）；无覆盖=不成行（禁前向填充）；horizon 锚定日历年（forecast_year），非报告槽位序
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->verify_schema_truth.py 报漂移+build_consensus_daily.py --verify 退出码1
# [TESTS] python scripts/ch/build_consensus_daily.py --check
# [TTL] permanent
"""consensus_daily（一致预期每日快照）DDL-as-Code（category_id: fund_consensus_daily, calc_mode: preload）。

本文件是 c3_fundamental.consensus_daily 表结构的唯一真源（DDL-as-Code 模式）。
施工依据：docs/_working/2026-09-12-expectation-consumption-design.md（消费端设计 C1，Owner 2026-09-12 拍板"现在就开工"）。

本质（第一性原理）：研报明细是事件流，因子回测要"每股每日矩阵"——本表把
c3_fundamental.research_report（事件流）按 (symbol, trade_date, forecast_year) 聚合为
华泰金工系列全部一致预期公式的标准输入（EXP-01~06 预期因子族的地基）。

粒度裁定：
    (symbol, trade_date, forecast_year) —— forecast_year 锚定**日历年**（如 2026），
    非报告槽位序（fy0/fy1/fy2）。每份研报展开为至多 3 行（其 fy0/fy1/fy2 槽位各自的
    日历年 + EPS/PE 预测值），跨年滚动自然对齐：年初窗口内研报的 fy0=当年，年末新研报
    的 fy0=次年（槽位序会跳年，日历年不跳）。

字段语义：
    eps_consensus/median/std/min/max = 窗口（window_days 自然日，默认 90）内对 forecast_year
    有预测值的研报聚合；rating_score_mean/n_buy/n_add/n_neutral/n_negative/n_unrated =
    窗口内**全部**研报（含无预测值者）的评级统计（同 symbol-date 各 forecast_year 行重复，
    反规范化换查询便利）；last_report_date = 窗口内最新 publish_date。
    评级映射：买入=7/增持=5/中性·持有=3/减持·卖出·回避=2/1，空值不计入均值（n_unrated 计数）。

PIT 铁律：
    只聚合 publish_date <= trade_date 的研报（发布即得，零 embargo）；无覆盖不成行，
    禁前向填充（消费方自行决定 as-of 语义）。

引擎选型：
    ReplacingMergeTree(ingest_ts)——同键重建幂等；PARTITION BY toYYYYMM(trade_date)；
    ORDER BY (symbol, trade_date, forecast_year)。审计列对齐 analyst_forecast 先例
    （ingest_ts DateTime64(3,'UTC')+TRAE-082 MATERIALIZED 派生）。
"""

from __future__ import annotations

# category_id: fund_consensus_daily
# calc_mode: preload（回测时预加载到内存）

CONSENSUS_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c3_fundamental.consensus_daily
(
    trade_date        Date                     COMMENT '交易日（快照日）',
    symbol            String                   COMMENT '证券代码（6位）',
    forecast_year     UInt16                   COMMENT '预测目标日历年（非槽位序）',
    eps_consensus     Float64                  COMMENT '窗口内该年 EPS 预测均值',
    eps_median        Float64                  COMMENT '窗口内该年 EPS 预测中位数',
    eps_std           Float64                  COMMENT '窗口内该年 EPS 预测总体标准差（n=1 时为 0）',
    eps_min           Float64                  COMMENT '窗口内该年 EPS 预测最小值',
    eps_max           Float64                  COMMENT '窗口内该年 EPS 预测最大值',
    pe_consensus      Nullable(Float64)        COMMENT '窗口内该年 PE 预测均值（可空）',
    n_reports         UInt16                   COMMENT '窗口内有该年预测的研报数',
    n_orgs            UInt16                   COMMENT '其中不同机构数（org_name 非空去重）',
    rating_score_mean Nullable(Float64)        COMMENT '窗口内全部研报评级分均值（买入7/增持5/中性持有3/减持2/卖出1，空值不计入）',
    n_buy             UInt16                   COMMENT '窗口内买入评级研报数',
    n_add             UInt16                   COMMENT '窗口内增持评级研报数',
    n_neutral         UInt16                   COMMENT '窗口内中性/持有评级研报数',
    n_negative        UInt16                   COMMENT '窗口内减持/卖出/回避评级研报数',
    n_unrated         UInt16                   COMMENT '窗口内无评级研报数',
    last_report_date  Date                     COMMENT '窗口内最新研报发布日期',
    window_days       UInt16                   COMMENT '构建窗宽（自然日，留痕）',
    data_source       LowCardinality(String) DEFAULT 'research_report' COMMENT '数据来源',
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
TABLE_NAME = "consensus_daily"
DATABASE = "c3_fundamental"
CATEGORY_ID = "fund_consensus_daily"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(symbol, trade_date, forecast_year)"

# 列清单（INSERT 显式指定，排除 MATERIALIZED/DEFAULT(now) 列）
INSERT_COLUMNS = (
    "(trade_date, symbol, forecast_year, eps_consensus, eps_median, eps_std, eps_min, eps_max, "
    "pe_consensus, n_reports, n_orgs, rating_score_mean, n_buy, n_add, n_neutral, n_negative, "
    "n_unrated, last_report_date, window_days, data_source)"
)
