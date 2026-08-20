# [BLUEPRINT] MOD-L04-002
# [MODULE] schemas.categories.factor_feature_value
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] apply_*_ddl（Owner 窗口执行）；zephyr.factor.feature_store_writer
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] factor_feature_value 表 DDL 唯一真源；本文件仅供 apply DDL 引用，禁止直接执行建表
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_*_ddl.py --verify退出码1
# [TESTS] tests/factor/test_feature_store_writer.py（列序契约）
# [TTL] permanent
"""factor_feature_value 表 DDL-as-Code（category_id: factor_feature_value）。

本文件是 c1_market.factor_feature_value 表结构的唯一真源（DDL-as-Code 模式）。
**状态：设计态（design）——未执行 apply DDL**（DDL 执行属 Owner 窗口；
15_data_feature_layer_spec §3.4 要点④特征仓库存储层，AI-NIGHT-001 包N 施工）。

架构选型（15 号 §3.4 轻量三层之存储层）：
    特征值落 ClickHouse 单表——仿 technical_indicator 表"单表 + 维度列"模式
    （该模式已验证可行：单表加维度过滤，避免 N 张分表的 schema 演进改 N 处）。
    technical_indicator 用 period 列区分 9 周期；本表用 factor_id 列区分因子。
    注：memo 原文"宽表"落地为单表+factor_id 维度列而非一因子一列的物理宽表——
    因子集合动态演进（factor_registry 111 条目生老病死），物理宽表每新增因子
    都要 ALTER TABLE，维度列模式演进成本为零（与 technical_indicator 同构裁定）。

列设计：
    factor_version LowCardinality(String)：因子 SemVer 版本（62 号 §4 原则 9：
    Semantic Versioning + git commit 充 immutable，不建独立特征版本服务）。
    value Nullable(Float64)：预热期无值为 NULL（不前向填充，PIT 铁律在
    特征层的落实，15 号 §3.4 FactorSignal NaN 填充裁定）。
    治理列对齐 internal 计算表惯例（technical_indicator 同）：data_source
    （固定 'factor_dag'）+ ingest_ts（UTC 入库审计）+ TRAE-082 MATERIALIZED
    派生列 exchange/symbol_canonical（跨表 JOIN 身份统一）。

引擎/分区/排序：
    ReplacingMergeTree（同 factor+symbol+date 重复计算取最新，幂等重算）；
    月分区 toYYYYMM(trade_date)（回算/归档可整批 DROP，18 号对齐）；
    ORDER BY (factor_id, symbol, trade_date)（主查询模式=单因子截面/单标的时间序）。

登记说明（待办，不属本批施工）：
    ① business_data_categories.yaml 新增 category_id=factor_feature_value
      （三库注册链 SSoT，随 Owner 窗口 apply DDL 同批登记）；
    ② data_asset_registry.yaml 数据资产登记——62 号 P1 载体（15 号 §3.4 既定）；
    ③ 本文件 [AI_AUTONOMY] human_only：后续结构变更走 schema-change 守卫。
"""

from __future__ import annotations

# category_id: factor_feature_value
# calc_mode: preload（盘后预计算入表，盘中实时调用 compute() 不入表）

FACTOR_FEATURE_VALUE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.factor_feature_value
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '证券代码',
    factor_id    LowCardinality(String) COMMENT '因子ID(factor_registry.yaml 条目)',
    factor_version LowCardinality(String) DEFAULT '0.0.0' COMMENT '因子SemVer版本(62号版本层)',
    value        Nullable(Float64)  COMMENT '特征值(预热期NULL不前向填充,PIT)',
    data_source  LowCardinality(String) COMMENT '数据来源(固定 factor_dag=本地计算)',
    ingest_ts    DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳',

    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (factor_id, symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "factor_feature_value"
DATABASE = "c1_market"
CATEGORY_ID = "factor_feature_value"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(factor_id, symbol, trade_date)"

# 列清单（INSERT 显式指定；ingest_ts DEFAULT now() 自动填充；exchange/symbol_canonical
# MATERIALIZED 派生；factor_version 有 DEFAULT 但写入侧始终显式携带版本）
INSERT_COLUMNS = "(trade_date, symbol, factor_id, factor_version, value, data_source)"
