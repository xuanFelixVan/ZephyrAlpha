# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] schemas.categories.sim_attribution_daily
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] scripts/backtest/sim_attribution_report.py(写); WO-1 四段答案(策略 P&L 分解/
#   成本拖累/基准相对/风险贡献)下游读; E7 前哨 30 笔样本期"钱从哪来"自动应答(读)
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源；变更需经 apply DDL 执行（apply_market_tables_ddl.py 注册归
#   总统筹，本件施工批禁碰——DDL 先落真源，注册由统筹批补）；归因行只增不改
#   （ReplacingMergeTree 按 (strategy_id, trade_date) 去重取最新；重放=新 ingest_ts 覆盖同键，
#   历史行物理保留）；口径锚定 sim_paper_ledger 内联成本常量（BUY_COST/SELL_COST，禁引 config）
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/backtest/test_sim_attribution_report.py
# [A_module] module_id=MOD-BT-216 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_attribution_daily 表 DDL-as-Code——模拟盘收益归因日账（WO-1 长表）。

本文件是 c1_backtest.sim_attribution_daily 表结构的唯一真源（DDL-as-Code 模式，
抄 regime_snapshot_history 先例）。真源工单：docs/_working/residual_construction/
wo1_attribution_workbook.md（pending_items_plan.md WORK-ORDER-1）。

定位：纸面盘组合的例行归因长表——每行 = 某策略某交易日的 P&L 三分（毛/成本/净）+
基准相对 + 风险贡献。与 sim_deviation_report 分工：偏差="当时说 vs 实际走"，
归因="实际走的钱从哪来"。

设计决策：
1. ReplacingMergeTree(ingest_ts) 只增不改——同 (strategy_id, trade_date) 重放/追算
   以新 ingest_ts 覆盖读取视图（FINAL），历史行物理保留（sim_pocket_daily 同款语义）。
2. 库归属 c1_backtest（回测治理产物，防 c1_market 行情库语义污染，同族先例）。
3. PARTITION BY toYYYYMM(trade_date) 月级分区——回放按窗口批量读写。
4. ORDER BY (strategy_id, trade_date)——主读模式=单策略时间轴区间扫描；
   与钱包键（一策略一钱包）对齐。
5. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：ingest_ts 用 DateTime64(3,'UTC')；
   trade_date 业务日期。
6. benchmark_rel 列=主基准（000852 中证1000，组合以中小盘为主）日超额；
   次基准（000300 沪深300）日超额入 detail JSON（benchmark_rel_hs300 键）——
   双基准都出，列只给主基准保 SQL 聚合直观。
7. pnl_cost 口径=账本实际记账（scripts/backtest/sim_paper_ledger.py 内联
   BUY_COST=(2.5+5.0)/1e4、SELL_COST=(2.5+10.0+5.0)/1e4，买入佣金2.5bp+滑点5bp，
   卖出佣金2.5bp+滑点10bp+冲击5bp，无 ¥5 佣金地板——地板是做T config 口径，
   本账本路径未实现）；禁引用 config 默认值（红蓝预登记项）。
8. detail JSON 承载 mode/run_id/signal/equity 链/双基准日收益/成本三元分解/
   事件流水引用/占位标记——展开列只留四段答案主键，防列爆炸。
"""

from __future__ import annotations

SIM_ATTRIBUTION_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.sim_attribution_daily
(
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,ReplacingMergeTree版本)',
    trade_date    Date                    COMMENT '业务交易日',
    strategy_id   String                  COMMENT '策略/钱包键(一策略一钱包,同 sim_pocket_daily)',
    pnl_gross     Float64                 COMMENT '毛收益(元)=pnl_net+pnl_cost(当日市值变动+还原成本)',
    pnl_cost      Float64                 COMMENT '当日交易成本(元,账本口径:买入佣金2.5bp+滑点5bp/卖出佣金2.5bp+滑点10bp+冲击5bp,无地板;非交易日=0)',
    pnl_net       Float64                 COMMENT '净收益(元)=账本 daily_pnl 原值(与 sim_pocket_daily 逐日对平)',
    benchmark_rel Float64                 COMMENT '主基准日超额=策略日收益-000852日收益(基准缺数=NaN,detail 注明)',
    risk_contrib  Float64                 COMMENT '风险贡献占比(单策略期=1.0;多策略期占位=1/N,占位标记入 detail,M-11 升级波动贡献)',
    detail        String                  COMMENT '明细 JSON(mode/run_id/signal/equity链/双基准收益/成本三元分解/事件引用/占位标记)',
    INDEX idx_sid strategy_id TYPE set(100) GRANULARITY 2
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (strategy_id, trade_date)
COMMENT '模拟盘收益归因日账长表(2026-09-18, WO-1 收益归因例行)'
"""

# 表元数据
TABLE_NAME = "sim_attribution_daily"
DATABASE = "c1_backtest"
CATEGORY_ID = "sim_attribution_daily"
CALC_MODE = "batch"
ENGINE = "ReplacingMergeTree(ingest_ts)"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(strategy_id, trade_date)"

# 基准约定（列/JSON 分工见设计决策 6）
BENCHMARK_PRIMARY = "000852"  # 中证1000（主基准，进 benchmark_rel 列）
BENCHMARK_SECONDARY = "000300"  # 沪深300（次基准，进 detail.benchmark_rel_hs300）

# 列清单（用于 INSERT；detail 最后）
INSERT_COLUMNS = (
    "(trade_date, strategy_id, pnl_gross, pnl_cost, pnl_net, benchmark_rel,"
    " risk_contrib, detail)"
)
