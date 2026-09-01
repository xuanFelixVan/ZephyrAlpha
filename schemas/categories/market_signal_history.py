# [BLUEPRINT] MOD-L03-001
# [MODULE] schemas.categories.market_signal_history
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] apply_*_ddl（Owner 窗口执行）；zephyr.signal.signal_history_writer；scripts/run_backtest.py；scripts/compute_signals.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] market_signal_history 表 DDL 唯一真源；本文件仅供 apply DDL 引用，禁止直接执行建表
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_*_ddl.py --verify退出码1
# [TESTS] scripts/compute_signals.py --verify（列序契约+落表往返）
# [TTL] permanent
"""market_signal_history 表 DDL-as-Code（category_id: market_signal_history）。

本文件是 c1_market.market_signal_history 表结构的唯一真源（DDL-as-Code 模式）。
**状态：已 apply（2026-09-01 Owner 会话批准，#BT-PIPELINE-001 阶段三）**。

裁定背景（Owner 2026-09-01 批准的调研报告结论）：
    信号落盘选型 C=一张窄表两管道：
    - source='strategy_weight'：BTRUN 回测最新一期权重面板（策略视角：系统想不想持有）
    - source='factor_synth'   ：日频多因子合成截面（个股视角：股票本身强不强）
    未来 signal_ashare 计算器族（92 个）可增量接入同表（pattern_to_signal_mapper
    的 MappedSignal symbol/direction/strength 三字段 1:1 映射）。
    预留名 signal_history（C2 indicator_clickhouse，business_data_architecture.md
    L293）不建库——单用户系统为一张表建第二库属过度工程；本表沿 execution_report
    先例落 c1_market + market_ 前缀，将来若建 C2 可平移（category 登记屏蔽迁移）。

为什么必须 CH 建表（否决 JSON 快照）：
    TRAE-050 灰度门禁（因子信号日变化率<50%）需历史序列；B-016 决策日志 3 年
    留存审计回放；#ARCH-OE-024 信号→成交偏差分析——三者都要 point-in-time 历史。

架构选型（沿 factor_feature_value 同构裁定）：
    维度列模式（source/signal_id 区分来源）而非一来源一表——来源集合动态演进，
    演进成本为零；窄表 9 列 + meta JSON 携带因子分解/血缘（DLG-001）。

引擎/分区/排序：
    ReplacingMergeTree(computed_at)——同 (source,signal_id,symbol,trade_date)
    重复计算取 computed_at 最新，幂等重算；
    月分区 toYYYYMM(trade_date)（回算/归档可整批 DROP）；
    ORDER BY (source, signal_id, symbol, trade_date)——低基数前置（CH 官方
    最佳实践），主查询=按 source+symbol 取最新 / 截面聚合。

治理列对齐 internal 计算表惯例：data_source（生产方标识）+ computed_at
（入库审计）+ TRAE-082 MATERIALIZED 派生列 exchange/symbol_canonical。
"""

from __future__ import annotations

# category_id: market_signal_history
# calc_mode: preload（盘后批计算入表；DEC-INV-002：信号不直连 order，仅展示/审计消费）

MARKET_SIGNAL_HISTORY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_signal_history
(
    trade_date   Date           COMMENT '信号所属交易日(PIT:生产所用数据最后日期)',
    symbol       String         COMMENT '证券代码(纯数字,与kline_daily同口径)',
    source       LowCardinality(String) COMMENT '信号来源: strategy_weight=BTRUN权重面板 | factor_synth=多因子合成',
    signal_id    LowCardinality(String) COMMENT '信号ID: 策略ID或合成器版本(如 topn-momentum / multifactor_v1)',
    direction    LowCardinality(String) COMMENT '方向: buy|sell|hold|neutral(CTR-INJ-003 置信度阈值裁决)',
    score        Float64        COMMENT '合成分(标准化,跨来源可比性由消费方按source分组处理)',
    confidence   Float64        DEFAULT 0 COMMENT '置信度[0,1](CTR-INJ-003)',
    rank_in_universe UInt16     DEFAULT 0 COMMENT '截面排名(1=最强,0=未排名)',
    meta         String         DEFAULT '' COMMENT 'JSON明细: 因子分解/权重/run_id(DLG-001血缘)',
    data_source  LowCardinality(String) COMMENT '生产方: btrun|compute_signals|...',
    computed_at  DateTime64(3, 'UTC')  DEFAULT now() COMMENT '计算时间戳(ReplacingMergeTree版本列)',

    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(computed_at)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (source, signal_id, symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "market_signal_history"
DATABASE = "c1_market"
CATEGORY_ID = "market_signal_history"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(computed_at)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(source, signal_id, symbol, trade_date)"

# 列清单（INSERT 显式指定；computed_at DEFAULT now() 自动填充；
# exchange/symbol_canonical MATERIALIZED 派生）
INSERT_COLUMNS = "(trade_date, symbol, source, signal_id, direction, score, confidence, rank_in_universe, meta, data_source)"
