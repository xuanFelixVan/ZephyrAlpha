# [BLUEPRINT] MOD-BT-031 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.regime_snapshot_history
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] scripts/backtest/print_regime_history.py(写); P0-001 L1-AGG 回放(读); P0-002 总闸回放(读)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 表 DDL 唯一真源；变更需经 apply DDL 执行；概率行只增不改（重印=新 run_id 追加）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/backtest/test_regime_snapshot_history.py
# [A_module] module_id=MOD-BT-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""regime_snapshot_history 表 DDL-as-Code（P0 印教材——RegimeSnapshot 历史逐日落库）。

本文件是 c1_backtest.regime_snapshot_history 表结构的唯一真源（DDL-as-Code 模式）。
施工真源：docs/_working/2026-09-11-backtest-evidence-log-discussion.md §3.4 同族 +
SOP-A Step A0（P0-001 L1-AGG / P0-002 L1 总闸回测的输入重建层）。

定位：判定器（MOD-REGIME-001）的 walk-forward 历史输出快照——"教材"。
每行 = 某印教材 run 中某交易日的 7 维灰度概率 + Shrinkage 三元组。
消费者 = P0-001（L1-AGG 六段映射回放）/ P0-002（总闸谨慎度回放）/ 衰减巡检对照。

设计决策：
1. MergeTree 只增不改——重印（参数/窗口变更）以新 run_id 追加，历史行不动（SOP-D 三原则）。
2. 库归属 c1_backtest（回测治理产物，防 c1_market 行情库语义污染，同 node_verdict 先例）。
3. PARTITION BY toYYYYMM(trade_date) 月级分区——按窗口批量读写。
4. ORDER BY (trade_date, run_id)——主读模式=时间轴区间扫描（回放），同日多 run 版本并存。
5. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：ingest_ts 用 UTC；trade_date 业务日期。
6. 概率 7 列展开 + probs_json 全量冗余：展开列供 SQL 直接聚合（区分度检验），
   JSON 保留 hmm/overlay 归因明细（RegimeProbabilities.hmm_probabilities/overlay_probabilities）。
7. G07 教训防复发（docs/_working/2026-09-11-g07-sentiment-validation.md §4）：
   RegimeDetector 无链式先验/无兜底强制保守分支，但印教材 QA 必须报告各态占比与
   最长连续同态天数，防"长期锁死单一态"类路径依赖（state_health 检查在脚本侧）。
"""

from __future__ import annotations

REGIME_SNAPSHOT_HISTORY_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.regime_snapshot_history
(
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC)',
    run_id            String                  COMMENT '印教材 run 全局唯一 id(VAL-P0-*)',
    snapshot_commit   String                  COMMENT '地图快照 commit 号(git rev-parse --short HEAD,PB-06)',
    trade_date        Date                    COMMENT '业务交易日(概率 as-of 语义: detect(t) 只用 ≤t-1 特征,PIT)',
    p_r1              Float64                 COMMENT 'HMM 态1 低波震荡 概率',
    p_r2              Float64                 COMMENT 'HMM 态2 中波震荡 概率',
    p_r3              Float64                 COMMENT 'HMM 态3 牛市趋势 概率',
    p_r4              Float64                 COMMENT 'HMM 态4 熊市阴跌 概率',
    p_r10             Float64                 COMMENT 'overlay CRISIS 概率',
    p_r11             Float64                 COMMENT 'overlay RECOVERY 概率',
    p_r12             Float64                 COMMENT 'overlay BREAKOUT 概率',
    dominant          LowCardinality(String)  COMMENT 'max(P) 对应态(r1..r4,r10..r12)',
    confidence        Float64                 COMMENT 'max(P) 即 ConfidenceSignal 输入',
    confidence_signal Float64                 COMMENT 'ConfidenceSignal 四档映射+稀有态折扣后值',
    risk_signal       Float64                 COMMENT 'RiskSignal 13参数聚合值',
    shrinkage         Float64                 COMMENT '最终 Shrinkage ≤1.0(只减不增)',
    probs_json        String                  COMMENT '完整分布 JSON(含 hmm/overlay 归因明细,schema_version)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id)
"""

# 表元数据
TABLE_NAME = "regime_snapshot_history"
DATABASE = "c1_backtest"
CATEGORY_ID = "regime_snapshot_history"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, run_id)"

# 列清单（用于 INSERT；probs_json 最后）
INSERT_COLUMNS = (
    "(run_id, snapshot_commit, trade_date, p_r1, p_r2, p_r3, p_r4, p_r10, p_r11, p_r12,"
    " dominant, confidence, confidence_signal, risk_signal, shrinkage, probs_json)"
)
