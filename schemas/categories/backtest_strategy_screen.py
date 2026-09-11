# [BLUEPRINT] MOD-TDMVAL-001
# [MODULE] schemas.categories.backtest_strategy_screen
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] SOP-C C4 快筛批测管道（待施工）; 前端策略档案（后置）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] strategy_screen 表 DDL 唯一真源；变更需经 apply DDL 执行；台账只追加不删改
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] —
# [TTL] permanent
"""backtest_strategy_screen 表 DDL-as-Code（策略快筛台账，SOP-C C4，R3 裁定）。

本文件是 c1_backtest.strategy_screen 表结构的唯一真源（DDL-as-Code 模式）。
施工真源：docs/_working/2026-09-11-backtest-evidence-log-discussion.md §3.4/§八 R3
（Owner 2026-09-11 认可，SOP-C 启动前建好）；漏斗规范见 sop_c_strategy_library_intake.md §4。

存储聚宽 600 条海选的快筛成绩单（一批快筛=一个 SCR-* run，每策略一行），
消费者=SOP-C C4 快筛管道（写，待施工）/ C5 聚类去重（读）/ 前端策略档案（后置）。

设计决策：
1. MergeTree（非 ReplacingMergeTree）——同策略可多次快筛（换参数/换窗口重考），
   历史行全保留（台账"只追加不删改"同构 node_verdict）。
2. 库归属 c1_backtest（与 node_verdict 同库，回测治理产物域）。
3. PARTITION BY toYYYYMM(screened_at) 月级分区；ORDER BY (screen_batch, strategy_id)
   （真源 §3.4 指定——按批拉 scoreboard 是主读模式）。
4. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：系统列 ingest_ts 用 UTC；
   业务列 screened_at 用 Asia/Shanghai。
5. verdict 三值（真源裁定）：screened_in(筛入)/rejected(粗筛或快筛出局)/failed_translate(翻译失败)；
   verdict_reason 由快筛管道代码生成（排除类别/判决原因，禁 AI 手填），对齐 R2 语义。
6. is_sharpe=IS(2019-2023) Sharpe；deflated_sharpe=按试验次数折减后 Sharpe（SOP-C C4 强制，
   600 条海选的多重检验校正）；oos_years_decay=按年外样本衰减率（C4 验收线）。
"""

from __future__ import annotations

BACKTEST_STRATEGY_SCREEN_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.strategy_screen
(
    ingest_ts         DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC)',
    run_id            String                  COMMENT '快筛 run 全局唯一 id(SCR-YYYYMMDD-HHMMSS)',
    screen_batch      String                  COMMENT '快筛批次标识(如 C4-2026W37/试点 pilot)',
    strategy_id       String                  COMMENT '候选策略临时 id(入库后回指 STR-*)',
    source_file       String                  COMMENT '原始源文件溯源路径(盘点归一清单 manifest 行)',
    translated        UInt8                   COMMENT '是否翻译成功 0/1',
    is_sharpe         Nullable(Float64)       COMMENT 'IS 2019-2023 Sharpe(粗口径可 NULL)',
    deflated_sharpe   Nullable(Float64)       COMMENT 'Deflated Sharpe(按试验次数折减,C4 强制)',
    max_drawdown      Nullable(Float64)       COMMENT '最大回撤(0~1)',
    turnover          Nullable(Float64)       COMMENT '年化换手率',
    oos_years_decay   Nullable(Float64)       COMMENT '按年外样本衰减率(0~1,>=0.5 判存疑土规)',
    cluster_id        String                  DEFAULT '' COMMENT 'C5 聚类簇 id(空=未聚类)',
    verdict           LowCardinality(String)  COMMENT '结论(screened_in/rejected/failed_translate)',
    verdict_reason    LowCardinality(String)  DEFAULT '' COMMENT '判决原因枚举(快筛管道代码生成禁手填;粗筛排除类别/判死原因)',
    screened_at       DateTime64(3, 'Asia/Shanghai') COMMENT '快筛结论时间',
    notes             String                  DEFAULT '' COMMENT '一句话备注(AI/人可读)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(screened_at)
ORDER BY (screen_batch, strategy_id)
"""

# 表元数据
TABLE_NAME = "strategy_screen"
DATABASE = "c1_backtest"
CATEGORY_ID = "backtest_strategy_screen"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(screened_at)"
ORDER_BY = "(screen_batch, strategy_id)"

# 列清单（用于 INSERT）
INSERT_COLUMNS = (
    "(run_id, screen_batch, strategy_id, source_file, translated, is_sharpe, deflated_sharpe,"
    " max_drawdown, turnover, oos_years_decay, cluster_id, verdict, verdict_reason, screened_at, notes)"
)
