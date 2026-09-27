# [BLUEPRINT] MOD-L04-STOCK-POOL | docs/_working/decision_map_campaign/links/L04_stock_wire/SKEL.md §3（M-41/D22 落地）
# [MODULE] schemas.categories.market.market_stock_candidate_pool
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_ashare.core.candidate_pool_snapshot（产出侧，ch_writer 正门落表）; zephyr.strategy_pipeline.daily_gate_snapshot（LK-04 通电侧带，盘后日循环触发）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] stock_candidate_pool 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；列集=producer POOL_INSERT_COLUMNS 16 列 + exchange/symbol_canonical MATERIALIZED 派生 + ingest_ts DEFAULT 列，不按想象加字段；ReplacingMergeTree (trade_date,stage,symbol) 同键重放幂等（池聚合器同 symbol 去重，一日一 stage 一 symbol 一行）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TESTS] tests/signal_ashare/test_candidate_pool_snapshot.py
# [A_module] module_id=MOD-L04-STOCK-POOL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] stock-candidate-pool-ddl-l04c01-20260925
"""stock_candidate_pool 表 DDL-as-Code（category_id: market_stock_candidate_pool, calc_mode: lazy）。

本文件是 c1_market.stock_candidate_pool 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

背景（L04-C01 · M-41/D22 候选池持久化载体落地）：
    TDM-E-L3 全家族十五节点主链现状"纯内存/回测内存话，无持久化"（L04 作业簿 W2③/W7②）：
    最终候选池（10-20 只，带 sleeve 标签+顺位分+否决标记）只在回测内存里活一瞬，
    L4 买卖/P2-02 做T调度/P1 体检/BM-BUY-03/整装回测全部吃不到真值全史。本表是
    "当日候选池快照"的持久化载体——日批逐交易日落一行/池内 symbol，回放任一历史日
    可取当日池快照（C01 验收口径）。

字段口径（producer 契约，见 candidate_pool_snapshot.pool_to_rows）：
    - sleeve —— 主标签=聚合器 FinalPoolEntry.best_sleeve（顺位最优来源的 sleeve）；
      sleeves=JSON 数组合流 sleeve 全集（跨束同 symbol 异 sleeve 合流去重留痕）。
    - rank_score —— 顺位分原值透传（上游分数体系不一，z_score/0-100 分/权重均可，
      口径统一由调用方负责，本表不做二次归一——禁拍假值冒充）。
    - pool_rank —— 池内最终顺位（1-based）：未否决在前按顺位分降序、vetoed 沉底留痕
      （聚合器最终排序序，喂 L4 只取未否决顺位前段的重放依据）。
    - vetoed/veto_reasons —— 否决只标记不剔除（一票否决裁决在上游 negative_veto
      MOD-SIG-137，本表留痕不重复裁决）；veto_reasons=JSON 数组全量披露命中原因。
    - tier_slot —— Tier 槽位预留（分层归 TDM-E-L3-09 pool_tier_maintenance，接线后
      回填；未接线恒 NULL，不硬凑）。
    - conduction_adj —— 板块传导调节分乘数（W0 两字段，接线后回填；缺=None 显式缺省，
      禁拍 1.0 冒充中性）。
    - score_components —— JSON 评分明细逐成分（含各成分 status，对齐 sector_state
      草案 components 逐成分留痕口径；v1 由调用方注入，缺省={}）。
    - snapshot_meta —— JSON 快照元数据：容量/actual_size/truncated_out/vetoed_symbols/
      notes/环境开关六段×四开关（L3-06 来源标尺）/两市成交额代理/regime dominant——
      单表回放自足（免 join 复原当日快照上下文）。
    - version —— 语义化版本（口径变更必升版）；data_source —— 来源标尺。

引擎选型说明：
    日频批产物（trade_date×stage×symbol 快照宽表），ReplacingMergeTree 按
    (trade_date, stage, symbol) 同键静默替换——同日重跑/版本升级重推导幂等。
    池聚合器同 symbol 去重（顺位最优保留），一日一 stage 一 symbol 恰一行。

PIT 消费契约（决策日 T 只读 trade_date < T）：
    本表 trade_date = 池产出日（盘后日批，收盘后才知池成员与顺位）。决策日 T 取
    max(trade_date) < T 的分区（shift(1) 口径防未来函数，对齐 daban_engine_load 先例）。
"""

from __future__ import annotations

from typing import Final

# category_id: market_stock_candidate_pool
# calc_mode: lazy

STOCK_CANDIDATE_POOL_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.stock_candidate_pool
(
    trade_date             Date                          COMMENT '池产出交易日(盘后日批;决策日 T PIT 只读 <T 分区)',
    stage                  LowCardinality(String)        COMMENT '快照时点(close_final 盘后定稿;pre_open/intraday_vN 预留)',
    symbol                 String                        COMMENT '证券代码(6位裸码)',
    exchange               LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生)',
    symbol_canonical       String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal)',
    sleeve                 LowCardinality(String)        COMMENT '主标签=顺位最优来源 sleeve(short_term/swing/daban/multifactor/event_driven)',
    sleeves                String                        COMMENT 'JSON数组 合流sleeve全集(跨束同symbol异sleeve合流留痕)',
    rank_score             Float64                       COMMENT '顺位分原值透传(口径统一归调用方,禁二次归一拍假值)',
    source_rank            Nullable(Int32)               COMMENT '上游内部名次(None=上游未给)',
    pool_rank              UInt16                        COMMENT '池内最终顺位1-based(未否决在前按顺位分降序,vetoed沉底)',
    vetoed                 UInt8 DEFAULT 0               COMMENT '否决标记(只标记不剔除,裁决在上游negative_veto)',
    veto_reasons           String                        COMMENT 'JSON数组 否决原因全集(可审计全量披露)',
    tier_slot              Nullable(Int16)               COMMENT 'Tier槽位(L3-09 pool_tier_maintenance接线后回填,未接线NULL)',
    conduction_adj         Nullable(Float64)             COMMENT '板块传导调节分乘数(W0两字段接线后回填,缺=None禁拍1.0)',
    score_components       String                        COMMENT 'JSON 评分明细逐成分(含status,对齐sector_state草案components口径)',
    snapshot_meta          String                        COMMENT 'JSON 快照元(容量/actual_size/truncated_out/否决清单/环境开关六段x四开关/成交额代理/dominant 单表回放自足)',
    version                LowCardinality(String) DEFAULT 'v1' COMMENT '语义化版本(口径变更必升版)',
    data_source            LowCardinality(String) DEFAULT 'candidate_pool_aggregator' COMMENT '来源标尺',
    ingest_ts              DateTime64(3, 'Asia/Shanghai') DEFAULT now() COMMENT '入库时间戳(DateTime64(3)+显式时区 RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "stock_candidate_pool"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_stock_candidate_pool"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, stage, symbol)"

# 列清单（INSERT 显式列，排除 exchange/symbol_canonical MATERIALIZED 与 ingest_ts DEFAULT）
# 与 candidate_pool_snapshot.POOL_INSERT_COLUMNS 16 列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, stage, symbol, sleeve, sleeves, rank_score, source_rank, "
    "pool_rank, vetoed, veto_reasons, tier_slot, conduction_adj, "
    "score_components, snapshot_meta, version, data_source)"
)
