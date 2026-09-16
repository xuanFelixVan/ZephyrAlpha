# [BLUEPRINT] MOD-PA-042 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] schemas.categories.alloc_budget_change_log
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.pf_alloc.allocation_persistence(写); zephyr.pf_alloc.allocation_orchestrator(读：昨日态续用/收敛对账);
#   分配链对账器（事件触发，非 cron）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code）；只增不改（重跑=新 run_id 追加）；
#   一行=BudgetChangeHandler（MOD-POS-022）一次 E-POS-40 BudgetChangeHandled /
#   E-POS-41 TierEscalation 领域事件的落地事实；
#   本表是"进程内事件 → 可持久审计面"的唯一出口（事件在内存分发即散，无此表则升级链不可对账）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/pf_alloc/test_pf_alloc_schemas.py
# [A_module] module_id=MOD-PA-042 | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] alloc-budget-change-log-mod-pa-042-20260916
"""alloc_budget_change_log 表 DDL-as-Code——budget 变动裁决与三级升级事件流水表。

真源：pf_alloc_consumer_mining PFA-1（五模块链零生产调用方，E-POS-40/41 从未在产线发出）
+ PFA-2（CH 零 alloc/budget 表→无对账面）。

定位：MOD-POS-022 BudgetChangeHandler 的领域事件（E-POS-40 BudgetChangeHandled /
E-POS-41 TierEscalation）与三级升级指令（Tier1 FreezeNewPositions / Tier2 RebalanceRequest /
Tier3 ForcedTrim）的落地面。handler 的 persist_path JSON 快照是"恢复态"（进程内状态机续用），
本表是"审计态"（谁在何时被从多少改到多少、走到了哪一级、下了什么指令）。

设计决策：
1. grain=(trade_date, run_id, strategy_id, seq)——同一 run 同一策略可先发 Handled 再发
   Escalation（多级流转），seq 保序，不做去重（流水语义，非状态语义）。
2. action 列显式登记 handler 的四种裁决口径（no_change/debounced/new_target/escalated…），
   使"防抖 5%/10% 挡掉了多少次抖动"可对账——防抖是 handler 唯一的日频可用性前提。
3. trim_ratio / freeze_new_positions 独立成列（不是只塞 payload_json）：Tier3 强制裁剪与
   Tier1 封锁新仓是**实际下单语义**，必须能直接 SQL 判"今天这个策略被允许开新仓吗"。
4. payload_json 全量冗余：handler 原始事件 payload 字典 JSON，供归因重放（展开列不足以还原）。
5. 时区铁律：ingest_ts=DateTime64(3,'UTC') DEFAULT now64(3)（DB 侧生成，写侧生成器禁 datetime.now()）。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.alloc_budget_change_log"

DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.alloc_budget_change_log
(
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,DB侧生成)',
    run_id              String               COMMENT '分配 run 标识(与 alloc_budget_daily 同 run_id 对账)',
    trade_date          Date                 COMMENT '业务交易日',
    strategy_id         String               COMMENT '策略钱包键',
    seq                 UInt32               COMMENT '同 run 同策略内的流水序号(0 起,保序)',
    event_id            LowCardinality(String) COMMENT '领域事件 id：E-POS-40 / E-POS-41',
    event_name          LowCardinality(String) COMMENT 'BudgetChangeHandled / TierEscalation',
    old_budget          Float64              COMMENT '变动前 budget(0=新策略首见)',
    target_budget       Float64              COMMENT '变动后 budget(本轮裁决目标)',
    delta_pct           Float64              COMMENT '相对变动幅度=(target-old)/old(old≠0)',
    current_tier        LowCardinality(String) COMMENT 'idle|tier_1_lock|tier_2_rebalance|tier_3_force_trim|converged',
    action              LowCardinality(String) COMMENT '裁决口径:no_change|debounced|accepted|escalated|converged|firm_violation|orphan_released',
    debounce_pct        Float64              COMMENT '生效的防抖阈值(日频 0.10 / 日内 0.05)',
    freeze_new_positions UInt8               COMMENT 'Tier1+ 封锁新仓(1=本日禁开新仓)',
    trim_ratio          Float64              COMMENT 'Tier3 保留比例(仓位×该值);无裁剪=NaN',
    reason              String               COMMENT '触发/裁决原因(人读)',
    payload_json        String               COMMENT 'handler 原始事件 payload JSON(归因重放)',
    schema_version      LowCardinality(String) COMMENT '行契约版本'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id, strategy_id, seq)
COMMENT '组合分配链 budget 变动裁决与三级升级事件流水表（车道 D 实盘接线，2026-09-16）'
"""

DATABASE = "c1_backtest"
CATEGORY_ID = "alloc_budget_change_log"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, run_id, strategy_id, seq)"

INSERT_COLUMNS = (
    "(run_id, trade_date, strategy_id, seq, event_id, event_name, old_budget, target_budget,"
    " delta_pct, current_tier, action, debounce_pct, freeze_new_positions, trim_ratio,"
    " reason, payload_json, schema_version)"
)

# 读侧查询模板（{table}/{date} 占位符约定同 alloc_budget_daily：
# {table} 由表名真源注入，{date} 必须是已校验的 YYYY-MM-DD 字面量，禁裸串拼接用户输入）
# 时序判据=ingest_ts（DB 侧）：run_id 后缀是随机 uuid，同日重跑按 run_id 排序=随机挑一个 run
# 的裁决结论，故禁；seq 只在同一 run 内表达事件先后（E-POS-41 升级 → E-POS-40 收尾）。
SQL_DAY_SLICE = (
    "SELECT * FROM {table} WHERE trade_date = '{date}' ORDER BY ingest_ts DESC, strategy_id, seq"
)
SQL_LATEST_FREEZE_STATE = (
    "SELECT strategy_id, event_id, event_name, old_budget, target_budget, current_tier, action,"
    " freeze_new_positions, trim_ratio, reason "
    "FROM {table} WHERE trade_date <= '{date}' "
    "ORDER BY trade_date DESC, ingest_ts DESC, seq DESC "
    "LIMIT 1 BY strategy_id"
)
