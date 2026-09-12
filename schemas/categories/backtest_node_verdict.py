# [BLUEPRINT] MOD-TDMVAL-001
# [MODULE] schemas.categories.backtest_node_verdict
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.trading.validation.runner; zephyr.frontend.dashboard.api_server
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] node_verdict 表 DDL 唯一真源；变更需经 apply DDL 执行；验证态只进台账不进地图 YAML
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/trading/test_node_backtest_governance.py
# [TTL] permanent
"""backtest_node_verdict 表 DDL-as-Code（节点级可回测治理台账，PB-02）。

本文件是 c1_backtest.node_verdict 表结构的唯一真源（DDL-as-Code 模式）。
施工真源：docs/_working/2026-09-09-node-backtest-governance.md §7.1/§8.1（Owner 裁定）。

存储每个 TDM 节点每次验证的"成绩单"行（run 级快照 + 节点级结论），
消费者=验证 runner（写，P1-2）/ api_server /api/tdm/validation（只读）/ 衰减巡检（P2-1）。

设计决策：
1. MergeTree（非 ReplacingMergeTree）——历次验证记录全部保留（抽屉"历次验证记录列表"
   与衰减巡检"对比首次验证"都依赖历史行），每次验证追加新行。
2. 库归属 c1_backtest（新建库）：真源文档 §8.1 暂定名；既有三库 c0_meta/c1_market/c3_fundamental
   按域分库，回测治理产物不入行情库（防 c1_market 语义污染）。
3. PARTITION BY toYYYYMM(window_end) 月级分区——验证按窗口批量写入，巡检按近月裁剪。
4. ORDER BY (node_id, window_end)——按节点拉历次记录是其唯一高频读模式（真源 §8.1 指定）。
5. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：系统列 ingest_ts 用 UTC；
   业务列 window_start/window_end/verdict_at 用 Asia/Shanghai。
6. significance 为轻量土规标记（PB-13 降级裁定）：ok=通过土规 /
   insufficient_samples=触发<30 次不下结论 / oos_decay_suspect=样本外衰减>=50% 判存疑。
7. verdict_reason 为判定原因枚举（G2 结构化裁定，Owner 2026-09-11 R2 认可）：由验证
   runner/衰减巡检代码生成，禁 AI 手填；存量行读默认值 legacy_notes 兼容。
"""

from __future__ import annotations

BACKTEST_NODE_VERDICT_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.node_verdict
(
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC)',
    run_id            String                  COMMENT '验证 run 全局唯一 id',
    snapshot_commit   String                  COMMENT '地图快照 commit 号(git rev-parse --short HEAD,PB-06 轻量快照绑定)',
    window_start      DateTime64(3, 'Asia/Shanghai') COMMENT '验证窗口起(不含 holdout 保密考卷窗口)',
    window_end        DateTime64(3, 'Asia/Shanghai') COMMENT '验证窗口止',
    node_id           String                  COMMENT '交易决策地图节点 id(TDM-*)',
    validation_method LowCardinality(String)  COMMENT '验证方法(sensor_monotonicity/agg_discrimination/exec_quality/exit_counterfactual/portfolio_attribution)',
    triggers          UInt64                  COMMENT '窗口内触发次数(土规:<30 不下结论)',
    hit_ratio         Nullable(Float64)       COMMENT '命中方向占比 0~1(方法相关,无值为 NULL)',
    significance      LowCardinality(String)  DEFAULT '' COMMENT '显著性土规标记(ok/insufficient_samples/oos_decay_suspect,空=不适用)',
    verdict           LowCardinality(String)  COMMENT '结论(valid/noise/pending/untested/decaying)',
    verdict_reason    LowCardinality(String)  DEFAULT 'legacy_notes' COMMENT '判定原因枚举(runner 代码生成禁手填,G2/R2): insufficient_samples/oos_decay_suspect/slip_within_tolerance/slip_marginal/slip_above_tolerance/counterfactual_missing/counterfactual_confirmed/avoided_negative/reference_price_missing/method_not_applicable/discrimination_confirmed/discrimination_below_threshold/discrimination_reversed(P0-001/002 agg_discrimination 扩展,2026-09-12); 存量=legacy_notes',
    verdict_at        DateTime64(3, 'Asia/Shanghai') COMMENT '结论时间',
    notes             String                  DEFAULT '' COMMENT '一句话结论备注(AI/人可读)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(window_end)
ORDER BY (node_id, window_end)
"""

# 表元数据
TABLE_NAME = "node_verdict"
DATABASE = "c1_backtest"
CATEGORY_ID = "backtest_node_verdict"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(window_end)"
ORDER_BY = "(node_id, window_end)"

# 列清单（用于 INSERT）
INSERT_COLUMNS = (
    "(run_id, snapshot_commit, window_start, window_end, node_id, validation_method,"
    " triggers, hit_ratio, significance, verdict, verdict_reason, verdict_at, notes)"
)
