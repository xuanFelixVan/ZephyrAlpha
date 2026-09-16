# [BLUEPRINT] MOD-PA-040 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] schemas.categories.alloc_budget_daily
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.pf_alloc.allocation_persistence(写); scripts/backtest/sim_paper_ledger(读钱包额度); 分配对账/归因(读)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code）；只增不改（重跑=新 run_id 追加，同 regime_snapshot_history 口径）；
#   一行=某 run 某交易日某策略的分配结果（allocation Σ=1.0 / effective_budget=allocation×shrinkage×cold_start）；
#   金额单位=元；allocated_capital=组合总资金×effective_budget（分配链驱动实际下注规模的落点）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/pf_alloc/test_pf_alloc_schemas.py
# [A_module] module_id=MOD-PA-040 | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] alloc-budget-daily-mod-pa-040-20260916
"""alloc_budget_daily 表 DDL-as-Code——组合分配链的逐策略预算落地表（车道 D / PFA-2 后端缺口治本）。

真源：docs/_working/full-auto-chain/S11_assembled_backtest/nodes/pf_alloc_consumer_mining.md
  PFA-1（MOD-PA-007 链零生产调用方）+ PFA-2（全 CH 无 alloc/budget/shrinkage 表，分配结果从未落库）
  + 六向挖矿 ⑥"sim_pocket_daily 缺 budget/allocation_source 溯源列（接线后可对账）"。

定位：MOD-PA-007 RegimeMetaAllocator 每个分配周期（事件触发，非 cron）对每个策略产出一行——
先验权重/绩效分/相对占比/全局节流/冷启动比例/实收预算/裁决终值/钱包额度，全部同表可归因。

设计决策：
1. MergeTree 只增不改——同 trade_date 重跑以新 run_id 追加（对齐 regime_snapshot_history 先例，
   禁 ReplacingMergeTree 静默覆盖历史分配，归因链断不可丢）。
2. 库归属 c1_backtest（分配链首个消费端=模拟盘账本，与 sim_pocket_daily 同库便于对账；
   实盘侧接入后按 52 号库属主裁定另议迁库，登记见施工报告）。
3. PARTITION BY toYYYYMM(trade_date) + ORDER BY (trade_date, run_id, strategy_id)——
   主读模式=按日取最近 run 的全策略切片。
4. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：ingest_ts=DateTime64(3,'UTC') DEFAULT now64(3)
   ——入库时刻由 DB 侧生成，写侧生成器禁用 datetime.now()/time.time()（run_id 由业务日+uuid 构造）。
5. final_weight/adjudication_id 列 = MOD-POS-024 裁决中心最保守收敛结果回写，
   使"预算→裁决→下注规模"三段在一行内可对账（PFA-1 断点的可观测面）。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.alloc_budget_daily"
DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.alloc_budget_daily
(
    ingest_ts             DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,DB侧生成)',
    run_id                String               COMMENT '分配 run 标识 alloc-<trade_date>-<uuid6>(重跑=新 run_id 追加)',
    trade_date            Date                 COMMENT '业务交易日(分配 as-of 日)',
    strategy_id           String               COMMENT '策略钱包键(STR-xxx)',
    strategy_type         LowCardinality(String) COMMENT '策略类型(打板/多因子/事件驱动，收敛窗口查询键)',
    base_weight           Float64              COMMENT '先验权重(PP-001 sleeve 或等权补齐后)',
    base_weight_source    LowCardinality(String) COMMENT '先验来源:pp001_sleeve|pp001_mean_prior_fill|equal_weight',
    perf_score            Float64              COMMENT 'PerformanceScore∈[0.5,1.5](MOD-PA-007 规范映射)',
    perf_sample_days      Int32                COMMENT '绩效样本天数(<30 冷启动，Score 强制中性 1.0)',
    allocation            Float64              COMMENT '相对占比(floor5%~cap40%，同 run 内 Σ=1.0)',
    global_shrinkage      Float64              COMMENT '全局风险节流因子∈[0.05,1.0](只减不增，同 run 共用)',
    cold_start_ratio      Float64              COMMENT '冷启动执行比例∈(0,1](30号§6.7 三段式)',
    effective_budget      Float64              COMMENT '实收预算占比=allocation×shrinkage×cold_start_ratio',
    previous_budget       Float64              COMMENT '上期 effective_budget(MOD-POS-022 防抖对照，首次=同值)',
    allocated_capital     Float64              COMMENT '钱包额度(元)=组合总资金×effective_budget',
    final_weight          Float64              COMMENT 'MOD-POS-024 四层裁决终值权重(拒绝=0)',
    adjudication_id       String               COMMENT '裁决令牌(sha256 前16hex，下单链凭证)',
    budget_action         String               COMMENT 'MOD-POS-022 裁决动作(NO_ACTION/DEBOUNCE/TIER1+TIER2/RETARGET/CONVERGED/TIER3)',
    current_tier          LowCardinality(String) COMMENT '三级升级状态 idle/tier_1_lock/tier_2_rebalance/tier_3_force_trim/converged',
    batch_plan_json       String               COMMENT 'MOD-PA-006 分批建仓计划 JSON(批次比例+触发条件+降级标记)',
    note                  String               COMMENT '备注/溯源说明',
    schema_version        LowCardinality(String) COMMENT '行契约版本',
    INDEX idx_sid strategy_id TYPE set(100) GRANULARITY 2
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id, strategy_id)
COMMENT '组合分配链逐策略预算落地表（车道 D 实盘接线，2026-09-16）'
"""

# 表元数据（静态清单由本文件承载，禁散落硬编码）
DATABASE = "c1_backtest"
CATEGORY_ID = "alloc_budget_daily"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, run_id, strategy_id)"

INSERT_COLUMNS = (
    "(run_id, trade_date, strategy_id, strategy_type, base_weight, base_weight_source,"
    " perf_score, perf_sample_days, allocation, global_shrinkage, cold_start_ratio,"
    " effective_budget, previous_budget, allocated_capital, final_weight, adjudication_id,"
    " budget_action, current_tier, batch_plan_json, note, schema_version)"
)

# 读侧查询模板（SQL 单一真源，禁散落在业务代码里拼裸 SQL）。
# 占位符约定：{table} 由本模块常量填充；{date} 由调用方填入 **已通过 _DATE_RE 校验** 的
# 'YYYY-MM-DD' 字面量（ClickHouse 字符串日期字面量即 Date 可解析），未校验值不得入 SQL。
#
# "最近一次 run" 的判据=DB 侧 ingest_ts，**不能用 run_id 排序**：alloc run_id 形如
# alloc-<date>-<uuid6>，后缀是随机 uuid，同日重跑的字典序与时间序无关（用 argMax(x, run_id)
# 会静默取到旧 run 的预算 → MOD-POS-022 防抖对照失真）。
# 对比：regime_snapshot_history 的 run_id（VAL-P0-YYYYMMDD-HHMMSS）字典序=时间序，
# 那边按 run_id 排是安全的，本表不是。
SQL_LATEST_EFFECTIVE_BUDGETS = (
    "SELECT strategy_id, argMax(effective_budget, (trade_date, ingest_ts)) AS eb "
    "FROM {table} WHERE trade_date < '{date}' GROUP BY strategy_id"
)
# 上期"计划暴露"（final_weight 口径，MOD-POS-022 Tier2→Tier3 收敛回检的输入）
SQL_LATEST_PLANNED_EXPOSURE = (
    "SELECT strategy_id, argMax(final_weight, (trade_date, ingest_ts)) AS planned_exposure "
    "FROM {table} WHERE trade_date < '{date}' GROUP BY strategy_id"
)
SQL_DAY_SLICE = (
    "SELECT strategy_id, run_id, allocation, global_shrinkage, effective_budget, "
    "allocated_capital, final_weight, budget_action, current_tier "
    "FROM {table} WHERE trade_date = '{date}' "
    "ORDER BY ingest_ts DESC LIMIT 1 BY strategy_id"
)
