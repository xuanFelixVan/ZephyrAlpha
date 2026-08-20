# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.cross_validation_log
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_schema.py; zephyr.data.cross_source_validator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] cross_validation_log 表 DDL 唯一真源；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [TTL] permanent
"""cross_validation_log 表 DDL-as-Code（P1-4 多源交叉校验）。

存储 QMT 主源 vs TDX 备源的 tick 数据交叉校验结果，
用于检测数据源偏差、缺失标的、价格异常等问题。

设计决策（2026-07-22 P1-4）：
1. MergeTree 引擎（非 ReplacingMergeTree）——校验日志允许重复，每次校验产生新行
2. PARTITION BY toYYYYMM(check_date) 月级分区——与 tick_data 一致
3. ORDER BY (check_date, symbol, metric, check_time)——按日期+标的+指标查询
4. status 使用 LowCardinality——pass/warn/fail 三值枚举
"""

from __future__ import annotations

CROSS_VALIDATION_LOG_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.cross_validation_log
(
    check_time     DateTime64(3, 'UTC')     COMMENT '校验执行时间(系统列,UTC)',
    check_date     Date                    COMMENT '校验数据日期',
    symbol         String                  COMMENT '证券代码',
    metric         LowCardinality(String)  COMMENT '校验指标(price/volume/amount/missing)',
    primary_value  String                  COMMENT '主源值(QMT)',
    backup_value   String                  COMMENT '备源值(TDX)',
    deviation      Decimal(18,6)           COMMENT '偏差(绝对值或百分比)',
    threshold      Decimal(18,6)           COMMENT '偏差阈值',
    status         LowCardinality(String)  COMMENT '校验结果(pass/warn/fail)',
    detail         String                  DEFAULT '' COMMENT '详细信息',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(check_date)
ORDER BY (check_date, symbol, metric, check_time)
"""

# 表元数据
TABLE_NAME = "cross_validation_log"
DATABASE = "c1_market"
CATEGORY_ID = "cross_validation_log"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(check_date)"
ORDER_BY = "(check_date, symbol, metric, check_time)"

# 列清单（用于 INSERT）
INSERT_COLUMNS = (
    "(check_time, check_date, symbol, metric, primary_value, backup_value, deviation, threshold, status, detail)"
)
