# [BLUEPRINT] MOD-L02-001
# [MODULE] schemas.categories.factor_signal
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] apply_*_ddl（建表部署）；zephyr.factor.core.batch_output.buffer（默认写入面 target_table）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] factor_signal 表 DDL 唯一真源；本文件仅供 apply DDL 引用，禁止直接执行建表
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_*_ddl.py --verify退出码1
# [TESTS] tests/factor/test_batch_output.py（TSV 列序契约）
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: schema 真源与 apply 注册脚本 DDL 内容相同但用途不同(SSoT vs apply)
"""factor_signal 表 DDL-as-Code（category_id: factor_signal）。

本文件是 c1_market.factor_signal 表结构的唯一真源（DDL-as-Code 模式）。
2026-10-07 图12/TDM 战役收官总攻批·车道F（st-vm12final-20261007-laneF）建表，
消账 DSC-GAP-FFSIG（config/data_supply_chain_map.yaml waiting_table_gaps）。

字段口径来源（先查后建，三分合一）：
    ① 契约真源=src/zephyr/shared/contracts/factor_signal.py::FactorSignal（CTR-002
      CODEGEN 冻结段）——标量字段全集与语义（as_of_date/factor_id/idempotency_key/
      raw_value/symbol/confidence/normalized_value/rank_pct/is_valid/factor_version/
      schema_version）；
    ② 写入面声明=zephyr.factor.core.batch_output.buffer._SIGNAL_COLUMNS（TSV 列序
      契约，11 列与本文件 INSERT_COLUMNS 同序）——buffer 默认
      target_table=c1_market.factor_signal（DSC-GAP-FFSIG 挂账的"默认落点"）；
    ③ 资产在册=data_asset_registry DS-003/DS-004（CTR-002 FactorSignal 契约级条目：
      factor_id/symbol/as_of_date/raw_value/normalized_value 核心集）。
    治理列（data_source/ingest_ts）与 TRAE-082 MATERIALIZED 派生列（exchange/
    symbol_canonical）对齐同族表 factor_feature_value（schemas/categories/
    factor_feature_value.py）既有惯例。

列设计：
    as_of_date DateTime64(3,'Asia/Shanghai')：截面时点（契约 datetime；converter
    幂等键 date_str 取其日期部分；PIT 铁律=对齐因子计算的数据截面日期，INV-004；
    显式时区合 RULE-SCHEMA-TZ）。
    raw_value/normalized_value/rank_pct Nullable(Float64)：契约 Optional/NaN 语义
    → NULL 不前向填充（与 factor_feature_value.value 同裁）。
    is_valid UInt8：契约 bool→CH UInt8（buffer TSV 写 1/0）。
    confidence Float64 DEFAULT 1.0：契约默认 1.0。
    idempotency_key String：converter 生成 "{prefix}{factor_id}:{symbol}:{date_str}"
    （重放同键；不入排序键——同键重算取最新语义见下）。

引擎/分区/排序（照同族先例 factor_feature_value）：
    ReplacingMergeTree（同 factor+symbol+截面时点 重放取最新，幂等重算；ORDER BY
    不含 idempotency_key/factor_version——重算语义=最新覆盖，prefix/版本漂移不产生
    重复行）；月分区 toYYYYMM(as_of_date)（回算/归档整批 DROP）；ORDER BY
    (factor_id, symbol, as_of_date)（主查询模式=单因子截面/单标的时间序）。
"""

from __future__ import annotations

# category_id: factor_signal
# calc_mode: preload（因子批量输出 buffer flush 直写：盘后批产/盘中增量，非调度器采集）

FACTOR_SIGNAL_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.factor_signal
(
    as_of_date      DateTime64(3, 'Asia/Shanghai') COMMENT '截面时点(对齐因子计算的数据截面日期,PIT,INV-004)',
    symbol          String         COMMENT '证券代码',
    factor_id       LowCardinality(String) COMMENT '因子ID(factor_registry.yaml 条目)',
    idempotency_key String         COMMENT '幂等键(converter生成 prefix+factor_id:symbol:YYYYMMDD,重放同键)',
    raw_value       Nullable(Float64)  COMMENT '原始因子值(预热/无效=NULL不前向填充)',
    confidence      Float64        DEFAULT 1.0 COMMENT '置信度[0,1](契约默认1.0)',
    normalized_value Nullable(Float64)  COMMENT '标准化值(zscore,可空)',
    rank_pct        Nullable(Float64)  COMMENT '截面百分位排名[0,1](可空)',
    is_valid        UInt8          DEFAULT 1  COMMENT '有效性(1=有效 0=异常,契约bool)',
    factor_version  LowCardinality(String) DEFAULT '1.0' COMMENT '因子版本(契约SemVer)',
    schema_version  LowCardinality(String) DEFAULT '1.0' COMMENT '契约schema版本',
    data_source     LowCardinality(String) DEFAULT 'factor_dag' COMMENT '数据来源(固定 factor_dag=本地计算)',
    ingest_ts       DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳',

    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(as_of_date)
ORDER BY (factor_id, symbol, as_of_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "factor_signal"
DATABASE = "c1_market"
CATEGORY_ID = "factor_signal"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(as_of_date)"
ORDER_BY = "(factor_id, symbol, as_of_date)"

# 列清单（INSERT 显式指定；与 buffer._SIGNAL_COLUMNS TSV 列序逐一同序=写入面契约；
# ingest_ts DEFAULT now() 自动填充；data_source 有 DEFAULT；exchange/symbol_canonical
# MATERIALIZED 派生禁显式写入）
INSERT_COLUMNS = (
    "(as_of_date, factor_id, idempotency_key, raw_value, symbol, confidence, "
    "normalized_value, rank_pct, is_valid, factor_version, schema_version)"
)
