---
module_id: MOD-TRADING-012
title: "EOD Processor 日终处理器蓝图 — 收盘价格快照 + NAV/PnL 确认 + 日终风险重估"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_trading
layer_name: trading
functional_domain: trading
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
design_maturity: design
build_status: testing
responsibility_domain: 
---

# MOD-TRADING-012 EOD Processor — 日终处理器 蓝图

> **module_id**: MOD-TRADING-012 | **域**: D_TRADING | **层**: 交易运营层增量
> **优先级**: P1 | **来源**: CAND-TRD-005（B10-02208，D-TRADING-04 §30.2.5，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-TRADING-012
> **铸号备注**: 初铸 MOD-TRADING-010 与 W-P1-23 并行会话 settlement_record_aggregate 撞号，
> 本方退让改铸 MOD-TRADING-012（对方节点先登先落码，本方节点 10631552 已 set-blueprint-id 改号）。

## 0. 查重裁定与 canonical 声明（RULE-EIGHT 探查结论）

候选 spec：价格快照 + NAV/P&L 确认 + 风险重估，挂 post_settlement_pipeline 15:30 链；
依赖前置 settlement_reconciliation（已有）/ risk 重估（已有）。业界对标：日终处理 =
NAV/P&L 确认 + 风险重估，qlib/vnpy 均以 EOD job 落地。

场内既有件逐一探查：

- post_settlement_pipeline（MOD-TRADING-003 族）：15:30 对账 + 日终审计**调度接线入口**
  ——只串联 SettlementReconciler/DailyAuditor 回调，**无 NAV/价格快照判定核心**（TSV 原
  文"NAV/价格快照缺"）；
- settlement_reconciliation（MOD-TRADING-003）：交易级对账（Fill vs 券商结算单容差比对）
  ——对账面，非日终估值；
- pnl_calculator（MOD-TRADING-002）：单笔/组合盈亏计算（Fill 驱动，含费率）——计算器，
  无"日终快照 → NAV 确认 → 风险重估"三步编排；
- recon_runner（MOD-TRADING-007）：盘中券商快照资金/持仓 gap 巡检（nav=cash+市值
  仅作 gap 分母）——盘中对账循环，非日终确认裁决；
- daily_auditor（MOD-RK-20）：日终风险指标报告（风险重估**被委托方**，已有）。

**裁定：独立缺口成立，按补充层施工（判定核心纯函数 + 回调委托）。canonical 声明：
本模块为 "D-TRADING-04 EOD Processor 日终处理器" 唯一真源；W-P1-23 同名候选
CAND-TRD-007（B14-04718，spec 同名撞车）后到时应归并本件（本波先建先登）。**

## 1. 定位

交易运营层日终判定核心：每个交易日收盘后（15:30 链）执行三步——
① 收盘价格快照（逐持仓 symbol 取日终价，缺失如实披露不臆造）；
② NAV/P&L 确认（NAV=cash+Σ(qty×eod_price)，未实现盈亏=Σ((eod−cost)×qty)，
   对期望 NAV 容差比对 → CONFIRMED/DRIFT）；
③ 日终风险重估（委托既有 risk 件回调，异常落状态不逃逸）。
纯函数无 IO；价格/风险真源一律探针注入；DRIFT/异常经 alert_sink + audit_sink 留痕。

不做什么：不实际挂 APScheduler 生产任务（build_eod_job_spec 只产调度规格，与
post_settlement_pipeline 同 15:30 窗口串联由调度层注册）；不做交易级对账（归
MOD-TRADING-003）；不做费率/单笔盈亏（归 MOD-TRADING-002）；风险重估判定不内嵌
（委托 MOD-RK-20 族回调）。

## 2. 输入 / 输出

- 输入：trade_date（YYYY-MM-DD）+ positions（EodPosition: symbol/quantity/avg_cost，
  Decimal）+ cash（Decimal）；探针注入：price_probe(symbol→Decimal 日终价)、
  risk_reassess_fn(trade_date, nav→对象，可选)、expected_nav（可选基准）+
  nav_tolerance（默认 1.00 元）；alert_sink/audit_sink（可选）。
- 输出：EodReport（frozen）：trade_date/nav/cash/market_value/unrealized_pnl/
  priced_symbols/unpriced_symbols/snapshot_status(OK/INCOMPLETE/ERROR)/
  nav_status(CONFIRMED/DRIFT/SKIPPED)/risk_status(OK/ERROR/SKIPPED)/errors/
  captured_at。

## 3. 核心规则（MVP）

1. 输入校验：trade_date 非空；positions quantity/avg_cost、cash、探针取价均 Decimal
   且有限——非法抛 InvalidEodInputError（Fail-Closed，占位未登码）。
2. 价格快照：逐 symbol 调 price_probe；探针异常/返回非正 → 该 symbol 记 unpriced
   （市价与盈亏按 0 计并如实披露，不臆造价格）；全部缺失 → snapshot_status=ERROR。
3. NAV/P&L：market_value=Σ(qty×price)（未定价按 0）；nav=cash+market_value；
   unrealized_pnl=Σ((price−avg_cost)×qty)（未定价按 0）。expected_nav 提供时
   |nav−expected|>nav_tolerance → DRIFT + alert + audit；未提供 → SKIPPED。
4. 风险重估：risk_reassess_fn 注入则调用（trade_date, nav）；异常捕获 → ERROR +
   alert + errors 落状态（盘后任务异常不逃逸调度器，对齐 post_settlement_pipeline
   口径）；未注入 → SKIPPED。
5. 不变量：Decimal-only 金额；EodReport/EodPosition frozen 不可变；探针异常不阻断
   主链（收敛为状态字段）；alert_sink/audit_sink 异常吞没不阻断主链路。

## 4. 依赖与委托

- 同链编排：post_settlement_pipeline（15:30 盘后链规格同窗口，build_eod_job_spec 对齐）。
- 对账面：settlement_reconciliation（MOD-TRADING-003，日终链前序）。
- 盈亏语义：pnl_calculator（MOD-TRADING-002，未实现盈亏口径对齐，委托不重造）。
- 风险重估：daily_auditor（MOD-RK-20 族，risk_reassess_fn 生产接线目标）。
- 审计：D_GOV_AUDIT writer（audit_sink 委托）。

## 5. 测试锚点

tests/trading/test_eod_processor.py：快照全/缺/异常三态、NAV 与未实现盈亏算数、
CONFIRMED/DRIFT/SKIPPED、风险重估 OK/ERROR/SKIPPED、alert/audit 委托、输入校验、
调度规格（cron=30 15 * * * + trading_day_only + entrypoint 指向本模块）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TRADING-012`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TRADING-012` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-TRADING-012` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TRADING-012 | MOD-TRADING-012 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
