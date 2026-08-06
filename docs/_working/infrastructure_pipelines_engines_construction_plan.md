---
ttl: task_bound
status: draft
version: "1.0.0"
date: 2026-08-05
source: battle_map_panorama.md + src/zephyr 代码核查
---

# 基础设施（管道与引擎）层施工准备方案

> **范围**：作战地图全景图中"AI 可 100% 独立完成、零业务参数输入"的基础设施环节——
> 即"管道与引擎"类模块。机制实现不需要用户提供任何策略/限额/权重/账户参数；
> 机制跑起来后由用户在控制台填业务数值激活。
>
> **真源**：[battle_map_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_panorama.md) 及 12 个分阶段文档 + `src/zephyr/` 代码核查。
>
> **性质**：施工准备方案（草稿区），非架构决策。正式施工须先过 §9 施工前置门禁。

---

## 0. 施工进度追踪（TODO 清单）

> **最后更新**：2026-08-05
> **当前阶段**：P0 验收完成 + P1 核查完成，准备进入 P2 施工
> **缺口总数**：7（G8 已排除）｜ **契约偏差**：2（GAP-01 类型安全 / GAP-02 测试工具，GAP-03 已解决）

### 施工总览

```
串行轨（risk 域）：  G1 告警生成 → G2 流动性监控 → G4 拥挤度检测
并行轨（execution 域）：G7 智能订单路由（独立于 G1/G2/G4，可同时推进）
```

> GAP-03 已解决（`DefaultRiskManagerOrchestrator` 存在），G1/G2/G4 不再被阻塞，可直接接入编排器。

---

### 轨 A：G1 告警生成（串行第 1 位·零外部依赖·先建管道）

> 详见 §6.4 G1。目标：`src/zephyr/risk/core/alert_generator.py`

- [x] **G1-S1** depgraph 设计态登记 ✓（MOD-RK-06, D_RISK, planned, file粒度 + 2条依赖边 + 翻译元数据 + PG备份）
- [x] **G1-S2** 四图对齐 ✓（blueprint.md 创建于 docs/03_modules/_domain_risk/alert_generator/，frontmatter 同步 design/planned；sync_module_panorama: 1模块0失败；align_panoramas: MOD-RK-06 零孤儿/零漂移/零域不一致/零孤立）
- [x] **G1-S3** 写代码 ✓（alert_generator.py 200行: AlertLevel+Alert+AlertGenerator(classify/deduplicate/route/process)+3通道+分层日志）
- [x] **G1-S4** 测试 ✓（27测试全PASS: 8 Mock场景覆盖 RED/ORANGE/YELLOW/clean/mixed + 去重 + 路由 + best-effort + 全流程）
- [x] **G1-S5** depgraph status → production ✓（延迟 max=0.315ms < 1s，余量3174x；build_status: planned→generated→testing→stable；design_maturity: design→production；4图同步0失败）
- [x] **G1-S6** 接入编排器 ✓（DefaultRiskManagerOrchestrator 新增 alert_generator 注入 + aggregate_report() 自动 process() + last_alerts 属性 + best-effort 异常不阻断；88测试全PASS含52现有测试向后兼容）

**依赖**：无（零外部依赖，纯机制）
**预计**：1 天

---

### 轨 A：G2 流动性监控（串行第 2 位·补建 2/3·接入 G1）

> 详见 §6.4 G2。目标：`src/zephyr/risk/core/liquidity_monitor.py`

- [x] **G2-S1** depgraph 登记 ✓（MOD-RK-08, 2条边, translation已补）
- [x] **G2-S2** 四图对齐 ✓（blueprint.md + sync 0失败 + align MOD-RK-08零问题）
- [x] **G2-S3** 写代码 ✓（liquidity_monitor.py 280行: Amihud ILLIQ + 成交量萎缩 + 综合判定 + 批量评估 + RiskCheckResult转换）
- [x] **G2-S4** 测试 ✓（30测试全PASS: 手工验证Amihud + 8计算 + 6萎缩 + 10评估 + 3批量 + 2转换）
- [x] **G2-S5** depgraph status → production ✓（延迟 max=1.477ms < 100ms，余量67x；批量100标的60ms；build_status: planned→generated→testing→stable；design_maturity: design→production；4图同步0失败）
- [x] **G2-S6** 接入编排器 ✓（DefaultRiskManagerOrchestrator 新增 liquidity_monitor 注入 + check_liquidity() 方法 → RiskCheckResult → aggregate_report() → G1 AlertGenerator 自动派发 RED 告警；128测试全PASS含52现有测试零回归）

**依赖**：G1 完成（告警出口）｜ 行情数据（OHLCV + 价差，已有）
**预计**：1 天

---

### 轨 A：G4 因子拥挤度检测（串行第 3 位·依赖 factor 模块·接入 G1）

> 详见 §6.4 G4。目标：`src/zephyr/risk/core/crowding_monitor.py`（对应 MOD-RK-13）

- [x] **G4-S1** depgraph 登记 ✓（MOD-RK-13, 2条边, translation已补）
- [x] **G4-S2** 四图对齐 ✓（blueprint.md + sync 0失败 + align MOD-RK-13零问题）
- [x] **G4-S3** 写代码 ✓（crowding_monitor.py 260行: 持仓重叠度+方向一致性+拥挤评分+批量评估+RiskCheckResult转换）
- [x] **G4-S4** 测试 ✓（25测试全PASS: 手工验证重叠度0.796875 + 手工验证方向一致性 + 拥挤/不拥挤/对冲/单策略/批量）
- [x] **G4-S5** 状态转换 ✓（延迟 max=2.034ms<50ms, 余量24x; build_status→stable; design_maturity→production; 4图同步0失败）
- [x] **G4-S6** 接入编排器 ✓（Orchestrator新增crowding_monitor注入+check_crowding()→HALT→RED告警; 162测试全PASS含52现有零回归）

**依赖**：G1 完成（告警出口）｜ factor 模块（因子成分股/暴露数据）｜ concentration_monitor（HHI 输入）
**预计**：1-2 天

---

### 轨 B：G7 智能订单路由（并行·P1 最高·实盘必需·独立域）

> 详见 §6.2 G7。实现：`src/zephyr/ex_sor/core/algo_trading_engine.py`（MOD-XS-005）

- [x] **G7 模块已建·已接入（2026-08-05 治本）** — `ex_sor/core/algo_trading_engine.py` (MOD-XS-005, 842行, production) 已完整实现 6 种算法: TwapStrategy/VwapStrategy/IcebergStrategy/PovStrategy/ImplementationShortfallStrategy/AggressiveLiquidityTakingStrategy + AlgoStrategy Protocol 基类 + AlgoTradingEngine 引擎 + AlgoParamOptimizer 参数优化器. **`AlgoTradingEngine.generate_plan()` 已接入 `ex_core/execution_engine.py`**——通过依赖注入 `algo_engine` + `market_ctx_provider`（新增 MOD-XS-006 `market_context_provider.py`，从 Redis tick + ClickHouse 日K构造 MarketContext），`_execute_twap`/`_execute_vwap`/`_execute_iceberg` 走真实切片路径（每切片 create_order+submit_order 子订单，守恒校验），未注入时回退占位行为（向后兼容）。25 新测试 + 1181 回归全 PASS。详见 §6.2 G7 接入状态。

**依赖**：EXE-02 执行引擎就绪 ｜ 实时行情 + 历史成交量曲线
**预计**：2-3 天
**注意**：与轨 A 完全独立，可不同会话并行推进

---

### 契约偏差跟踪（P0 遗留）

- [ ] **GAP-01** `pre_trade_check(order: object)` 类型安全——考虑用 `Order` 契约替换 `object`（低优先级，不阻塞施工）
- [x] **GAP-02** `BacktestFill→Fill` 适配器——降级为测试工具，不建 `shared/adapters/` 模块（非生产路径）
- [x] **GAP-03** 风控编排器——**已解决**，`DefaultRiskManagerOrchestrator` 存在（215行，production）

---

### 后续批次（依赖外部模块，暂不排期）

- [ ] G3 AI/Agent 风险监控 — **依赖已就绪·可组装缺口**（详见 §6.2 G3 核查）
- [ ] G5 模型风险审计 — **依赖已就绪·可组装缺口**（详见 §6.2 G5 核查）
- [ ] G6 操作风险审计 — **依赖已就绪·可组装缺口**（详见 §6.2 G6 核查）

> **核查订正（2026-08-05）**：原记"G3/G5/G6 依赖 autonomy_core/ml_serve/ex_core 审计日志未就绪"**不准确**。
> 三者依赖均已存在且 production：autonomy_core（230 文件，含 agent_observability）、
> 漂移检测基础设施（intelligence/model_drift_detector + gov_drift/ + factor/analysis/ic_decay）、
> ex_core/audit_journal/auditor.py（MOD-EX-003，ExecutionAuditReport 含 by_event_type 含 ORDER_REJECTED）。
> 三者**非 G7 式纯误判**（无完整 production 实现坐落 risk/core/），但**亦非被阻塞**——
> 检测能力散落于相邻域，G3/G5 组装进 risk/core/ 的 ai_agent_monitor/model_risk_audit 即可；G6 已作为 `compute_operational_risk_stats` 方法落地于 MOD-EX-003（见 §6.2 G6），不新建 risk/core/ 模块。

---

## 1. 执行摘要

### 1.1 核心发现

经 battle_map 6 件套"③参数"字段逐环节核对 + `src/zephyr/` 代码结构核查，得出：

| 维度 | 数量 | 说明 |
|---|---|---|
| AI 可独立造的基础设施环节总数 | **66** | 第一类(零参数机制 31) + 第二类(纯技术/公开规则管道 35) |
| 其中 ✓ 代码已实现 | **38** | 实现度 ≈ 58%，代码库已相当成熟 |
| 其中 ◐ 代码存在但待核查完整度 | **20** | 有对应文件，但子能力可能不全，需核查 |
| 其中 ✗ 缺口/待施工 | **8** | 真正需要从零补全的模块 |

**结论**：本方案性质不是"从零建造 66 个模块"，而是 **"实现度核查 + 少数缺口补全"**。
真正需要写新代码的只有 **8 个缺口项**（见 §6），其余 58 项是验收确认或轻量补全。

### 1.2 施工三阶段

| 阶段 | 任务 | 工作量 | 依赖 |
|---|---|---|---|
| **P0 验收确认** | 38 个已实现项跑通冒烟测试，确认契约完整 | 轻量 | 无 |
| **P1 完整度核查** | 20 个待核查项逐个核对子能力，补缺失分支 | 中等 | P0 |
| **P2 缺口补全** | 8 个缺口项从零施工 | 重 | P1（部分） |

### 1.3 关键铁律提醒

施工前 MUST 遵守三条治本规则（详见 §9）：
1. **依赖关系先行**：写第 1 行业务代码前，MUST 先用 `apply_depgraph.py --add-design-node` 登记依赖（status=planned）
2. **四图对齐**：`sync_panorama_module.py` 派生 + `align_panoramas.py` 验证干净后再施工
3. **备份先行**：`apply_depgraph` 内置 `backup_pg_architecture()` + oneoff 脚本运行前 git commit

---

## 2. 背景与目标

### 2.1 背景

用户问："作战地图全景图里，哪些基础设施是不需要我参与、给策略就能独立完成的？"
进一步澄清："哪些是不需要给策略、AI 能独立完成、是基础设施、完全可以自己做、不需要我给出任何参数的？"

经两轮分析，锁定判定标准为环节 6 件套中的 **"③参数"字段**：
- 参数为 **"—"（空）** → 纯机制，零外部参数
- 参数为 **纯技术 SLA / A 股公开规则 / 行业标准方法** → AI 可用行业默认值独立造
- 参数为 **业务数值（权重/限额/AUM/账户）** → 需用户给，排除

### 2.2 目标

为"马上施工"做准备，输出：
1. 66 个 AI 可独立造的基础设施环节完整清单 + 代码现状对照
2. 真正缺口的施工规格（接口/输入输出/技术要点）
3. 施工分期与依赖顺序
4. 施工前置门禁与验收标准

### 2.3 不在范围内

- 需用户业务参数的环节（风控限额数值、仓位上限、策略权重、账户配置等）—— 见 §7 排除清单
- 设计态/候选态未建环节（BM-RC-10 风险否决权、BM-RC-11 独立风险管道、横切层 CC_01~16 等 107 项）
- 策略/因子/选股决策层（BM-SEL-02~25、BM-BUY-01~08、BM-SELL-01~06 等）

---

## 3. 判定标准与方法论

### 3.1 "AI 可独立造"的二元判定

| 判定维度 | 是（可独立造）| 否（需用户参与）|
|---|---|---|
| ③参数字段 | "—" 或纯技术/公开规则/行业标准 | 含业务数值 |
| 知识来源 | A 股公开规则 / 行业标准方法 / 纯技术 SLA | 用户业务决策 |
| 示例 | T+1 结算、万三佣金、Sharpe 计算、VWAP 算法 | 仓位上限 0.8、策略权重 A30% |

### 3.2 数据采集方法

1. 从 [battle_map_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_panorama.md) 提取全部 220 个生产态环节
2. 逐环节核对分阶段文档的"③参数"字段
3. 对 `src/zephyr/` 代码结构核查，定位每个环节的代码文件
4. 交叉比对 battle_map "代码当前"标注 vs 实际文件存在性

### 3.3 代码现状三态标记

- **✓ 已实现**：代码文件存在，且 battle_map 标注 implemented/production
- **◐ 待核查**：代码文件存在，但子能力完整性未确认（可能内嵌或部分实现）
- **✗ 缺口**：未找到对应代码文件，需从零施工

---

## 4. 代码现状盘点（按模块域）

### 4.1 风控域 `src/zephyr/risk/`

| 子目录 | 文件 | 对应环节 |
|---|---|---|
| 顶层 | risk_manager.py, risk_limits.py, risk_manager_base.py, risk_validator.py, stop_loss.py | RC-01, RC-02, RC-05 |
| core/ | var_calculator.py, drawdown_tracker.py, concentration_monitor.py, tail_risk_monitor.py, ashare_stop_loss_engine.py, ashare_systemic_risk_detector.py, risk_budget_allocator.py, risk_decomposition.py, stress_test_engine.py, daily_auditor.py | RC-04, RC-05, RC-06, RC-07, RC-08 |
| implementations/ | default_position_limit_checker.py, default_risk_limits_calculator.py, default_risk_manager_orchestrator.py, default_risk_validator.py, default_stop_loss_engine.py | RC-01, RC-02, RC-05 |

**缺口**：告警生成、流动性风险监控、AI/Agent 风险监控、拥挤度检测、模型风险审计、操作风险审计（6 项）

### 4.2 回测域 `src/zephyr/backtest/`

| 子目录 | 文件 | 对应环节 |
|---|---|---|
| core/ | engine_base.py, matching_engine.py, matching_logic.py, metrics.py, overfitting_detector.py, pit_manager.py, portfolio.py, tick_replay.py, walk_forward.py, decision_gate.py, data_handler.py | BT-01, BT-02, BT-03, BT-04, BT-05, BT-06, BT-07 |
| implementations/ | vectorized_engine.py, event_driven_engine.py | BT-01-B, BT-03-C |
| services/ | cache_manager.py, data_quality_checker.py, decay_monitor.py, nan_processor.py, param_analyzer.py, report_generator.py, result_comparator.py, scheduler.py, anomaly_diagnoser.py | BT-01-E, BT-02-C/D, BT-03-D, BT-05-D/E |
| io/ | backtest_result_sink.py, decisiongraph_adapter.py, result_repository.py | BT-07 持久化 |

**状态**：回测域实现最完整，几乎全覆盖 BT-01~07。

### 4.3 数据接入域 `src/zephyr/market_data/`

| 子目录 | 文件 | 对应环节 |
|---|---|---|
| 顶层 | vendor_registry.py, vendor_base.py, autoload.py | SEL-01-A, SEL-01-D |
| connectors/ | manager.py, base.py | SEL-01-B |
| failover/ | manager.py | SEL-01-C |

**待核查**：原始数据缓存（SEL-01-E）、标准化行情产出（SEL-01-F）—— 可能在 `data_eng/` 或 `data/` 下。

### 4.4 执行域 `src/zephyr/ex_core/` + `ex_sor/`

| 文件 | 对应环节 |
|---|---|
| execution_engine.py, trading_session.py | EXE-02 |
| fill_handler.py, order_manager.py, order_execution_saga.py | EXE-06 |
| position_reconciler.py | 持仓对账 |
| ex_sor/services/transaction_cost_optimizer.py | EXE-03 TCA / EXE-05 部分 |

**已实现**：智能订单路由与拆单（EXE-05）= `ex_sor/core/algo_trading_engine.py`（MOD-XS-005，6 种算法 production）。

### 4.5 对账清算域 `src/zephyr/trading/` + `reporting/`

| 文件 | 对应环节 |
|---|---|
| trading/settlement_reconciliation.py | REC-01-A |
| trading/corporate_action_processor.py | REC-01-B |
| risk/core/daily_auditor.py | REC-01-C / RC-08-A |
| reporting/default_tca_engine.py | EXE-03 / REC-02-A |
| reporting/default_attribution_engine.py | REC-02-B |
| reporting/risk_report_engine.py | REC-02-E |
| reporting/regulatory_report_generator.py | REC-02-F |
| reporting/report_publisher.py | REC-02-D |

**状态**：对账清算域实现完整。

### 4.6 仓位域 `src/zephyr/position/`

| 文件 | 对应环节 |
|---|---|
| position/core/sell_position_link.py | POS-09 |
| position/core/cash_manager.py | POS-06 |

**待核查**：再平衡执行（POS-07）、日历仓位约束（POS-08）、仓位审计追溯（POS-10）—— 可能在 `pf_alloc/` 下。

---

## 5. 基础设施清单（66 环节 + 代码现状对照）

### 5.1 第一类：零参数纯机制层（31 项，③参数="—"）

> 集中在风控域。参数字段为空 = 纯机制实现，跑起来读用户配置的限额数值。

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 1 | BM-RC-01-A | 风控策略 CRUD 与版本管理 | [risk_manager.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_manager.py) + [default_risk_manager_orchestrator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_manager_orchestrator.py) | ✓ |
| 2 | BM-RC-01-B | 九种限额类型与消耗追踪 | [risk_limits.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_limits.py) + [default_risk_limits_calculator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_limits_calculator.py) | ✓ |
| 3 | BM-RC-01-C | 预警分级与审批流 | [risk_manager.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_manager.py)（内嵌）| ◐ |
| 4 | BM-RC-02-A | 仓位限额检查 | [default_position_limit_checker.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_position_limit_checker.py) | ✓ |
| 5 | BM-RC-02-B | 行业集中度检查 | [concentration_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/concentration_monitor.py) | ✓ |
| 6 | BM-RC-02-C | 杠杆率检查 | [default_risk_validator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_validator.py) | ◐ |
| 7 | BM-RC-02-D | 合规规则检查 | [default_risk_validator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_validator.py) | ◐ |
| 8 | BM-RC-02-E | Kill Switch 状态检查 | [trading_kill_switch.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py) | ✓ |
| 9 | BM-RC-03-A | 触发条件判定 | [trading_kill_switch.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py) | ✓ |
| 10 | BM-RC-03-B | 状态机与冷却期 | [trading_kill_switch.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py) | ◐ |
| 11 | BM-RC-03-C | Owner 确认重置与多域通知 | [trading_kill_switch.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py) | ◐ |
| 12 | BM-RC-04-A | VaR 实时计算 | [var_calculator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/var_calculator.py) | ✓ |
| 13 | BM-RC-04-B | 回撤实时追踪 | [drawdown_tracker.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/drawdown_tracker.py) | ✓ |
| 14 | BM-RC-04-C | 因子暴露与相关性矩阵 | [concentration_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/concentration_monitor.py) | ✓ |
| 15 | BM-RC-04-D | 告警生成 | 未找到独立文件 | ✗ |
| 16 | BM-RC-04-E | 流动性风险监控 | 未找到独立文件 | ✗ |
| 17 | BM-RC-04-F | AI/Agent 风险监控 | 未找到独立文件 | ✗ |
| 18 | BM-RC-05-A | 六种 A 股止损模式 | [ashare_stop_loss_engine.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/ashare_stop_loss_engine.py) | ✓ |
| 19 | BM-RC-05-B | 通用止损引擎 | [default_stop_loss_engine.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_stop_loss_engine.py) + [stop_loss.py](file:///d:/ZephyrAlpha/src/zephyr/risk/stop_loss.py) | ✓ |
| 20 | BM-RC-05-C | 亏损限额强制停盘 | [risk_limits.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_limits.py) | ◐ |
| 21 | BM-RC-06-A | 五大信号扫描 | [ashare_systemic_risk_detector.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/ashare_systemic_risk_detector.py) | ✓ |
| 22 | BM-RC-06-B | 尾部风险监控 | [tail_risk_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/tail_risk_monitor.py) | ✓ |
| 23 | BM-RC-06-C | 三级警报与清仓执行 | [ashare_systemic_risk_detector.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/ashare_systemic_risk_detector.py)（内嵌）| ◐ |
| 24 | BM-RC-06-D | 拥挤度检测 | 未找到独立文件 | ✗ |
| 25 | BM-RC-07-A | VaR 三阶段演进 | [var_calculator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/var_calculator.py) | ✓ |
| 26 | BM-RC-07-B | 风险预算优化求解 | [risk_budget_allocator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/risk_budget_allocator.py) | ✓ |
| 27 | BM-RC-07-C | 风险贡献与再平衡 | [risk_decomposition.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/risk_decomposition.py) | ✓ |
| 28 | BM-RC-08-A | 日终 PnL 对账与合规报告 | [daily_auditor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/daily_auditor.py) | ✓ |
| 29 | BM-RC-08-B | 风险归因分解 | [risk_decomposition.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/risk_decomposition.py) | ✓ |
| 30 | BM-RC-08-C | 压力测试 | [stress_test_engine.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/stress_test_engine.py) | ✓ |
| 31 | BM-RC-08-D | 模型风险审计 | 未找到独立文件 | ✗ |
| 32 | BM-RC-08-E | 操作风险审计 | 未找到独立文件 | ✗ |

> 第一类统计：✓ 已实现 19 ｜ ◐ 待核查 7 ｜ ✗ 缺口 6

### 5.2 第二类：纯技术 / A 股公开规则管道层（35 项）

> 参数全是技术 SLA、A 股公开规则或行业标准方法。AI 掌握全部知识，可用行业默认值独立造。

#### 5.2.1 数据接入管道（6 项）

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 33 | BM-SEL-01-A | 供应商注册与适配器 | [vendor_registry.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/vendor_registry.py) + [vendor_base.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/vendor_base.py) | ✓ |
| 34 | BM-SEL-01-B | 行情连接器管理 | [connectors/manager.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/connectors/manager.py) + [base.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/connectors/base.py) | ✓ |
| 35 | BM-SEL-01-C | 故障切换与 Failover | [failover/manager.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/failover/manager.py) | ✓ |
| 36 | BM-SEL-01-D | 自动加载与热切换 | [autoload.py](file:///d:/ZephyrAlpha/src/zephyr/market_data/autoload.py) | ✓ |
| 37 | BM-SEL-01-E | 原始数据缓存 | 待核查（可能在 data_eng/） | ◐ |
| 38 | BM-SEL-01-F | 标准化行情产出 | 待核查 | ◐ |

#### 5.2.2 回测引擎（18 项，`backtest/`）

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 39 | BM-BT-01-A | 引擎基座与契约 | [core/engine_base.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/engine_base.py) | ✓ |
| 40 | BM-BT-01-B | 向量化回测引擎 | [implementations/vectorized_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/vectorized_engine.py) | ✓ |
| 41 | BM-BT-01-C | 撮合引擎 | [core/matching_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_engine.py) + [matching_logic.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_logic.py) | ✓ |
| 42 | BM-BT-01-D | A 股交易约束 | [matching_logic.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_logic.py)（内嵌）| ◐ |
| 43 | BM-BT-01-E | 自动回测调度器 | [services/scheduler.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/services/scheduler.py) | ✓ |
| 44 | BM-BT-01-F | 回测加速架构 | 待核查（scheduler/vectorized 内）| ◐ |
| 45 | BM-BT-02-A | 持仓组合管理 | [core/portfolio.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/portfolio.py) | ✓ |
| 46 | BM-BT-02-B | 多源数据接入 | [core/data_handler.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/data_handler.py) | ✓ |
| 47 | BM-BT-02-C | 回测缓存管理器 | [services/cache_manager.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/services/cache_manager.py) | ✓ |
| 48 | BM-BT-02-D | 回测数据质量检查器 | [services/data_quality_checker.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/services/data_quality_checker.py) | ✓ |
| 49 | BM-BT-02-E | 幸存者偏差防护 | 待核查（data_handler 内）| ◐ |
| 50 | BM-BT-03-A | 绩效指标计算 | [core/metrics.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/metrics.py) | ✓ |
| 51 | BM-BT-03-B | Tick 回放引擎 | [core/tick_replay.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/tick_replay.py) | ✓ |
| 52 | BM-BT-03-C | 事件驱动回测 | [implementations/event_driven_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/event_driven_engine.py) | ✓ |
| 53 | BM-BT-03-D | 指标 NaN 处理器 | [services/nan_processor.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/services/nan_processor.py) | ✓ |
| 54 | BM-BT-04-A | PIT 三公理与 AS OF JOIN | [core/pit_manager.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/pit_manager.py) | ✓ |
| 55 | BM-BT-04-B | Embargo 期管理 | [pit_manager.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/pit_manager.py)（内嵌）| ◐ |
| 56 | BM-BT-04-C | Purged K-Fold 交叉验证 | 待核查 | ◐ |

#### 5.2.3 对账清算（3 项）

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 57 | BM-REC-01-A | 结算对账 | [settlement_reconciliation.py](file:///d:/ZephyrAlpha/src/zephyr/trading/settlement_reconciliation.py) | ✓ |
| 58 | BM-REC-01-B | 公司行为与费率 | [corporate_action_processor.py](file:///d:/ZephyrAlpha/src/zephyr/trading/corporate_action_processor.py) | ✓ |
| 59 | BM-REC-01-C | PnL 计算 | [daily_auditor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/daily_auditor.py) + reporting/ | ✓ |

#### 5.2.4 执行管道（5 项）

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 60 | BM-EXE-02 | 交易执行 | [execution_engine.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/execution_engine.py) + [trading_session.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/trading_session.py) | ✓ |
| 61 | BM-EXE-03 | 执行质量 TCA | [default_tca_engine.py](file:///d:/ZephyrAlpha/src/zephyr/reporting/default_tca_engine.py) | ✓ |
| 62 | BM-EXE-04 | Pre-Trade 合规检查 | 待核查（compliance/）| ◐ |
| 63 | BM-EXE-05 | 智能订单路由与拆单 | [transaction_cost_optimizer.py](file:///d:/ZephyrAlpha/src/zephyr/ex_sor/services/transaction_cost_optimizer.py)（splitter 待实现）| ✗ |
| 64 | BM-EXE-06 | 成交回报处理与持仓更新 | [fill_handler.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/fill_handler.py) + [order_manager.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) | ✓ |

#### 5.2.5 仓位硬规则（4 项）

| # | 环节 ID | 名称 | 代码位置 | 现状 |
|---|---|---|---|---|
| 65 | BM-POS-07 | 再平衡执行 | 待核查（pf_alloc/）| ◐ |
| 66 | BM-POS-08 | 日历仓位约束 | 待核查 | ◐ |
| 67 | BM-POS-09 | 卖出仓位反馈链路 | [sell_position_link.py](file:///d:/ZephyrAlpha/src/zephyr/position/core/sell_position_link.py) | ✓ |
| 68 | BM-POS-10 | 仓位审计追溯 | 待核查 | ◐ |

> 第二类统计：✓ 已实现 19 ｜ ◐ 待核查 13 ｜ ✗ 缺口 2
>
> **全表统计（67 行，含编号重叠校正）**：✓ 已实现 **38** ｜ ◐ 待核查 **20** ｜ ✗ 缺口 **7**（G8 经核查移除）

---

## 6. 真正缺口聚焦（7 项待施工）

> 这是本方案的核心施工对象——真正需要从零写代码的模块。
> G8（原始数据缓存+标准化）经 P1 核查确认为"已实现·非缺口"，已于 2026-08-05 移除。

### 6.1 缺口清单

| # | 环节 | 缺口描述 | 优先级 | 依赖 |
|---|---|---|---|---|
| G1 | BM-RC-04-D 告警生成 | 风控告警统一生成器（黄/橙/红三级 → 多通道推送）| P2 高 | RC-04-A~C 监控数据 |
| G2 | BM-RC-04-E 流动性风险监控 | Amihud 非流动性 + 买卖价差 + 成交量萎缩监控 | P2 高 | 行情数据 |
| G3 | BM-RC-04-F AI/Agent 风险监控 | Agent 行为越界检测（ASI/AST/MCP 隐性串谋）| P3 中 | autonomy_core |
| G4 | BM-RC-06-D 拥挤度检测 | 因子/策略拥挤度计算 + 阈值预警 | P3 中 | factor 模块 |
| G5 | BM-RC-08-D 模型风险审计 | 模型漂移/衰退/偏差审计 | P3 中 | ml_serve |
| G6 | BM-RC-08-E 操作风险审计 | 操作事件审计 + 失败订单分析 | P3 中 | ex_core 审计日志 |
| G7 | BM-EXE-05 智能订单路由与拆单 | TWAP/VWAP/ICEBERG/POV/IS 拆单算法实现 | P1 最高 | EXE-02 执行引擎 |
| ~~G8~~ | ~~BM-SEL-01-E/F 原始数据缓存 + 标准化产出~~ | **已实现·非缺口**（2026-08-05 P1 核查确认：`data/tick_redis_cache.py` + `data/symbol_normalizer/`，`data_eng/` 为空壳脚手架）| — | — |

### 6.2 缺口施工规格

#### G7：BM-EXE-05 智能订单路由与拆单（最高优先级）

- **真源**：[execution.md:142](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_10_execution.md#L142)
- **实现路径**：`src/zephyr/ex_sor/core/algo_trading_engine.py`（MOD-XS-005，已 production）
- **③参数**（纯技术/A股公开）：算法=TWAP/VWAP/ICEBERG/POV/IS/ALT ｜ 参与率≤15% 分钟成交量（时变）｜ 执行时间窗口=开盘前5min/收盘前10min/均匀分布 ｜ Almgren-Chriss 最优轨迹 E[cost]+λ×Var[cost]
- **输入**：目标订单（标的/方向/数量/算法选择）、实时行情、历史成交量曲线
- **输出**：子订单序列（时间戳/数量/价格/算法标签）
- **接口契约**（实际实现）：
  ```python
  class AlgoTradingEngine:
      def generate_plan(self, order: Order, params: AlgoParams, ctx: MarketContext) -> AlgoExecutionPlan: ...
  ```
- **算法实现要点**：
  - TWAP：按时间窗口均匀切片
  - VWAP：按历史成交量分布加权切片
  - ICEBERG：大单拆小单，隐藏真实量
  - POV：保持参与率恒定，动态调整
  - IS（Implementation Shortfall）：Almgren-Chriss 最优轨迹求解
- **A股约束**：miniQMT 下单速率 10 笔/秒、同标的间隔≥500ms（已在 EXE-02 实现）
- **验收**：拆单后实际参与率≤15%、滑点优于全量市价单基准
- **接入状态（2026-08-05 治本完成）**：`ex_sor/core/algo_trading_engine.py`（MOD-XS-005）作为独立模块已 production（6 算法 + 71 测试），**已接入 `ex_core/execution_engine.py` 执行路径**。
  - 现状：`execution_engine.py` 通过依赖注入 `algo_engine: AlgoTradingEngine` + `market_ctx_provider: MarketContextProvider`（新增 MOD-XS-006 `ex_sor/core/market_context_provider.py`），`_execute_twap`/`_execute_vwap`/`_execute_iceberg` 调用 `generate_plan()` 生成 `AlgoExecutionPlan`，每切片经 `OrderManager.create_order`+`submit_order` 下发子订单（母子订单关联记录于 `algo_orders`，守恒校验由 `AlgoExecutionPlan.__post_init__` 保证）。`MarketContext` 由 `RedisKlineMarketContextProvider` 从 Redis `tick:{symbol}:latest`（last/bid/ask）+ ClickHouse 日K（ADV）真实构造，tick 缺失降级到 K线 close。`OrderTooLargeError`（>15% ADV §13.1）包装为 `ValueError` 供上游统一处理。未注入时回退占位整笔提交（向后兼容）。25 新测试 + 1181 回归全 PASS。
  - 后续可选：接入 XS-04 Execution Scheduler 做时间窗口调度（当前同步提交所有切片，适合模拟/回测；实盘需 `send_at` 时序循环）。

#### G1：BM-RC-04-D 告警生成

- **真源**：[risk_control.md:876](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L876)
- **实现路径**：`src/zephyr/risk/core/alert_generator.py`（MOD-RK-06，已 production）
- **③参数**："—"（零参数纯机制）
- **输入**：RC-04-A~C/E/F 各监控器的越限信号
- **输出**：三级告警（黄提醒/橙警告/红紧急）+ 多通道推送（日志/微信/邮件）
- **接口契约**：
  ```python
  class AlertGenerator:
      def generate(self, breach: RiskBreach) -> Alert: ...
      def route(self, alert: Alert) -> None: ...  # 按级别路由通道
  ```
- **验收**：告警延迟<1s、级别判定正确率100%、通道可达

#### G2：BM-RC-04-E 流动性风险监控

- **真源**：[risk_control.md:907](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L907)
- **实现路径**：`src/zephyr/risk/core/liquidity_monitor.py`（MOD-RK-08，已 production）
- **③参数**："—"（零参数纯机制）
- **输入**：实时行情（买卖价差/盘口深度）、成交数据
- **输出**：Amihud 非流动性指标、买卖价差、成交量萎缩率、出场滑点估计
- **算法**：Amihud(2002) 非流动性 = |收益率|/成交额；每 Tick 3 秒计算，<1 秒延迟
- **验收**：Amihud 计算正确、萎缩率检出延迟<5s

#### G3：BM-RC-04-F AI/Agent 风险监控

- **真源**：[risk_control.md:938](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L938)
- **目标路径**：risk/core/ 下新建 `ai_agent_monitor.py`（G3 组装缺口，待建）
- **③参数**："—"（零参数纯机制）
- **输入**：Agent 行为日志（autonomy_core 产出）
- **输出**：越界检测（ASI/AST/MCP 隐性串谋）、自治边界违反告警
- **依赖**：autonomy_core 模块的行为日志接口
- **验收**：能检出模拟越界场景
- **核查结论（2026-08-05）**：**依赖已就绪·可组装缺口**（非 G7 式纯误判）。
  - 依赖 `autonomy_core` 已存在（230 文件，production），含 [`agent_observability.py`](file:///d:/ZephyrAlpha/src/zephyr/autonomy_core/agent_observability.py)（MOD-INF-019，Agent Trace 全链路可观测）。
  - 行为审计日志已存在：[`security/llm_defense/llm_security/behavior_audit_logger.py`](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/behavior_audit_logger.py)（MOD-LLM_SECURITY，4 类 AI 行为事件 model_call/file_write/rule_trigger/gate_decision，append-only JSONL）。
  - 多 Agent 涌现行为检测已存在：[`feedback_loop/detectors/anomaly/emergent_behavior_detector.py`](file:///d:/ZephyrAlpha/src/zephyr/feedback_loop/detectors/anomaly/emergent_behavior_detector.py)（系统熵/耦合强度/相关维度/级联失效早期信号）+ `feedback_loop/detectors/correlation/agent_trajectory_anomaly_detector.py` + `infrastructure/a2a_protocol/layer3_coordination/a2a_behavior_fingerprint.py`。
  - **缺口本质**：上述检测能力散落于 D_FBL_DETECTORS/D_SECURITY/D_AUTONOMY_CORE，针对 dev-agent/通用 AI 治理；G3 需将其**组装+聚焦**为 risk/core/ 内面向**交易 Agent（ASI/AST/MCP 串谋）**的越界监控。无需从零造轮子。

#### G4：BM-RC-06-D 拥挤度检测

- **真源**：[risk_control.md:1228](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L1228)
- **实现路径**：`src/zephyr/risk/core/crowding_monitor.py`（MOD-RK-13，已 production）
- **③参数**："—"（零参数纯机制）
- **输入**：因子持仓分布、策略持仓集中度
- **输出**：拥挤度评分 + 阈值预警（拥挤→降权）
- **算法**：因子持仓集中度 + 策略相关性 + 换手率异常
- **依赖**：factor 模块的持仓数据
- **验收**：拥挤度评分与历史拥挤事件吻合

#### G5：BM-RC-08-D 模型风险审计

- **真源**：[risk_control.md:1522](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L1522)
- **目标路径**：risk/core/ 下新建 `model_risk_audit.py`（G5 组装缺口，待建）
- **③参数**："—"（零参数纯机制）
- **输入**：模型预测记录、实际表现、漂移检测数据
- **输出**：模型漂移/衰退/偏差审计报告
- **依赖**：ml_serve 的模型预测日志、REC-03-C 模型层反馈
- **验收**：能检出 PSI>0.2 漂移、IC 衰减>50%
- **核查结论（2026-08-05）**：**依赖已就绪·可组装缺口**（非 G7 式纯误判）。
  - 原记"依赖 ml_serve 未就绪"**不准确**：`ml_serve`（14 文件）实为 Agent 技能/自进化基础设施（agent_observability/phase_planner/trigger_router），并非 ML 模型服务/预测日志模块——依赖指向错位。
  - 漂移检测能力已存在：[`intelligence/model_drift_detector.py`](file:///d:/ZephyrAlpha/src/zephyr/intelligence/model_drift_detector.py)（MOD-INF-021，KL/JS 散度漂移检测）+ `gov_drift/` 全套（drift_detector/drift_engine/detector_core/model_drift_monitor）。
  - IC 衰减已存在：[`factor/analysis/ic_decay.py`](file:///d:/ZephyrAlpha/src/zephyr/factor/analysis/ic_decay.py)（MOD-L02-004，IC 衰减曲线 + 半衰期，INV-004 PIT 铁律）。
  - 模型评估/推理已存在：`intelligence/model_evaluation/`（inference_base + default_inference_engine + experiment_tracker）。
  - **缺口本质**：漂移（intelligence/gov_drift，面向 LLM/治理）与 IC 衰减（factor 域）散落各处；G5 需**组装**为 risk/core/ 内统一的"模型风险审计报告"（PSI>0.2 + IC衰减>50% + 偏差），面向交易预测模型。能力齐备，缺组装层。

#### G6：BM-RC-08-E 操作风险审计

- **真源**：[risk_control.md:1554](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L1554)
- **实现路径**：`src/zephyr/ex_core/audit_journal/auditor.py`（MOD-EX-003，作为 `compute_operational_risk_stats` 方法落地，详见下方核查结论）
- **③参数**："—"（零参数纯机制）
- **输入**：ex_core 操作日志、失败订单记录、系统事件日志
- **输出**：操作风险审计报告（失败率/延迟/异常事件统计）
- **依赖**：ex_core 的审计日志接口
- **验收**：能统计失败订单率、检出操作异常
- **核查结论（2026-08-05）**：**依赖已就绪·可组装缺口**（非 G7 式纯误判）。
  - 依赖 `ex_core 审计日志接口`**已满足**：[`ex_core/audit_journal/auditor.py`](file:///d:/ZephyrAlpha/src/zephyr/ex_core/audit_journal/auditor.py)（MOD-EX-003，production，哈希链防篡改审计日志）。记录 8 类执行事件（ORDER_CREATED/SUBMITTED/FILLED/CANCELLED/REJECTED/EXPIRED + FILL_RECEIVED + IDEMPOTENCY_BLOCKED），产出 `ExecutionAuditReport`（含 `by_event_type`/`by_symbol`/`by_source` 统计 + 链完整性校验）。
  - 日终审计已存在：[`risk/core/daily_auditor.py`](file:///d:/ZephyrAlpha/src/zephyr/risk/core/daily_auditor.py)（MOD-RK-20，PnL 对账/归因偏差/合规/检查清单/IssueRecord），但聚焦**财务/PnL 审计**，非操作风险。
  - **缺口本质**：audit_journal 提供**原始事件 + 计数统计**（含 ORDER_REJECTED 计数），但未显式计算**失败率/延迟/操作异常**；G6 需在 audit_journal 之上组装"操作风险审计报告"（失败订单率 = rejected/total、下单→成交延迟分布、IDEMPOTENCY_BLOCKED 异常检出）。数据源就绪，缺统计聚合层。
  - **薄聚合层已落地（2026-08-05）**：✓ 在 MOD-EX-003 实现 `compute_operational_risk_stats(period_start, period_end) → OperationalRiskStats`，聚合失败率（ORDER_REJECTED/ORDER_SUBMITTED，零提交=0.0 不除零）+ 成交延迟（SUBMITTED→FILLED 按 order_id 配对，p50/p95/max/mean ms）。15 单元测试全 PASS（`tests/ex_core/test_operational_risk_stats.py`），原 44 审计测试零回归。**SSoT 决策**：未新建 risk/core/ 模块——depgraph 核查发现 MOD-RK-22 实为 G3（AI/Agent 风险监控，路径 agent_risk_monitor.py），G6 battle_map 真源锚点指向 MOD-INF-023/029（已建 infra），新建 risk 域模块会与真源冲突；失败率/延迟本质是执行审计统计，cohesive 于 MOD-EX-003，作为其内部派生方法落地（无新 depgraph 节点/无四图仪式，符合"不镀金"）。**仍待**：D_RISK 解释层（阈值告警，battle_map→MOD-INF-023/029）+ TCA 质量评分（MOD-EX-012）。

#### ~~G8~~：BM-SEL-01-E/F 原始数据缓存 + 标准化产出 — **已实现·非缺口**

- **核查结论**（2026-08-05 P1）：`data_eng/` 目录为空壳脚手架（6 个子目录仅有 `__init__.py` + `__all__ = []`，零行业务代码，blueprint 标 pending）。实际实现位于 `data/` 目录：
  - 缓存：[`data/tick_redis_cache.py`](file:///d:/ZephyrAlpha/src/zephyr/data/tick_redis_cache.py) — 生产级 Redis 热缓存，PIPELINE 批量写入 + best-effort 降级，有测试
  - 标准化：[`data/symbol_normalizer/normalizer.py`](file:///d:/ZephyrAlpha/src/zephyr/data/symbol_normalizer/normalizer.py) — A股标的代码标准化
- **处置**：从缺口列表移除，缺口数 8→7。`data_eng/` 空壳脚手架建议后续清理或在 depgraph 中标记 deprecated。

### 6.3 P1 核查：risk/ 目录审计 + G1/G2/G4 现状（2026-08-05）

> 对 `src/zephyr/risk/` 全目录核查，确认 GAP-03 状态及 G1/G2/G4 是否已有实现。

#### 6.3.1 risk/ 目录资产盘点

| 类别 | 文件 | 行数 | 状态 | 说明 |
|------|------|------|------|------|
| 编排器 | `implementations/default_risk_manager_orchestrator.py` | 215 | **生产** ✓ | **GAP-03 已解决**——4 个抽象方法全实现，MATURITY=production |
| 验证器 | `implementations/default_risk_validator.py` | 159 | 生产 ✓ | 订单/组合验证 + kill switch |
| 限额计算 | `implementations/default_risk_limits_calculator.py` | 96 | 生产 ✓ | |
| 仓位检查 | `implementations/default_position_limit_checker.py` | 89 | 生产 ✓ | |
| 止损引擎 | `implementations/default_stop_loss_engine.py` | 134 | 生产 ✓ | |
| 核心监控 | `core/concentration_monitor.py` | 347 | 生产 ✓ | HHI/行业暴露/单股权重——**G4 输入数据源** |
| 核心监控 | `core/ashare_systemic_risk_detector.py` | 514 | 生产 ✓ | 含流动性危机检测（买卖价差）——**G2 部分覆盖** |
| 核心监控 | `core/tail_risk_monitor.py` | 446 | 生产 ✓ | ES/POT/跳变检测 |
| 核心监控 | `core/daily_auditor.py` | 941 | 生产 ✓ | 日终审计 |
| 核心监控 | `core/stress_test_engine.py` | 500 | 生产 ✓ | 压力测试 |
| 核心监控 | `core/var_calculator.py` | 323 | 生产 ✓ | VaR 计算 |
| 核心监控 | `core/drawdown_tracker.py` | 262 | 生产 ✓ | 回撤追踪 |
| 核心监控 | `core/risk_budget_allocator.py` | 348 | 生产 ✓ | 风险预算分配 |
| 核心监控 | `core/risk_decomposition.py` | 300 | 生产 ✓ | 风险归因 |
| 止损引擎 | `core/ashare_stop_loss_engine.py` | 560 | 生产 ✓ | A股止损 |

**结论**：risk/ 域基础设施成熟（9 个核心监控模块 + 4 个实现 + 基类），G1/G2/G4 是具体缺口而非空白领域。

#### 6.3.2 GAP-03 复核：已解决

P0 验收时登记 GAP-03 为"风控编排器无生产级具体实现"——**此结论错误**。

[`default_risk_manager_orchestrator.py`](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_manager_orchestrator.py) 已实现全部 4 个抽象方法：
- `pre_trade_check`：调用 `DefaultRiskValidator.validate_order`，HALT 级违规抛 `RiskLimitViolationError`
- `post_trade_check`：成交后检查
- `daily_pnl_check`：日终亏损检查，超限触发 kill switch
- `aggregate_report`：汇总 `RiskReport`（含 failed_checks / active_alerts / kill_switch_active）

**处置**：GAP-03 从契约偏差列表中移除。P0 验收脚本中的 `_MinRiskOrchestrator` 应替换为 `DefaultRiskManagerOrchestrator`。

#### 6.3.3 G1/G2/G4 现状裁定

| 缺口 | 核查结论 | 现有资产 | 仍缺内容 |
|------|----------|----------|----------|
| **G1** 告警生成 | **已实现 (MOD-RK-06, production)** | `risk/core/alert_generator.py`（343 行）——三级分级（黄/橙/红）+ 多通道路由（日志/邮件/微信）+ 同源去重，均已在 §6.3 核查后落地 | — |
| **G2** 流动性监控 | **已实现 (MOD-RK-08, production)** | `risk/core/liquidity_monitor.py`（331 行）——Amihud ILLIQ + 成交量萎缩比率；买卖价差复用 `ashare_systemic_risk_detector` | — |
| **G4** 拥挤度检测 | **已实现 (MOD-RK-13, production)** | `risk/core/crowding_monitor.py`——跨策略拥挤度（持仓重叠度 overlap + 方向一致性 consensus → crowding 评分）；与 `concentration_monitor`（组合内 HHI）互补 | — |

> **关键区分**：`concentration_monitor` 衡量的是"我的组合有多集中"（组合内 HH I）；
> G4 拥挤度衡量的是"全市场有多少人挤在同一个因子/策略上"（跨参与者）。
> 前者是后者的**输入之一**，但不是同一件事。

#### 6.4 G1/G2/G4 实施方案（基于核查结果修订）

> 以下方案已根据 §6.3 核查结果修订——复用现有资产，仅补建缺失部分。

#### G1：告警统一生成器

- **真源**：[risk_control.md:876](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L876)
- **实现路径**：`src/zephyr/risk/core/alert_generator.py`（MOD-RK-06，已 production）
- **③参数**："—"（零参数纯机制）
- **复用资产**：`RiskReport.active_alerts`（各监控器已产出的原始告警 string 列表）
- **输入**：`RiskReport`（来自 `DefaultRiskManagerOrchestrator.aggregate_report()`）
- **输出**：三级告警 `Alert(level, source, message, timestamp)` + 多通道推送
- **接口契约**：
  ```python
  @dataclass(frozen=True)
  class Alert:
      level: AlertLevel  # YELLOW | ORANGE | RED
      source: str         # 来源监控器 (concentration/tail_risk/systemic...)
      message: str
      timestamp: datetime
      idempotency_key: str

  class AlertGenerator:
      def classify(self, report: RiskReport) -> list[Alert]: ...
      def route(self, alert: Alert) -> None: ...  # RED→微信+邮件+日志, ORANGE→邮件+日志, YELLOW→日志
      def deduplicate(self, alerts: list[Alert], window: timedelta) -> list[Alert]: ...
  ```
- **分级规则**（纯机制，零业务参数）：
  - RED：`kill_switch_active=True` 或 `overall_pass=False` 且有 HALT 级违规
  - ORANGE：`failed_checks` 非空但无 HALT
  - YELLOW：`active_alerts` 非空但 `overall_pass=True`
- **通道路由**：RED→微信+邮件+日志 ｜ ORANGE→邮件+日志 ｜ YELLOW→仅日志
- **验收**：告警延迟<1s、级别判定正确率100%、通道可达、5分钟窗口内同源告警去重

#### G2：流动性风险监控（补建 2/3）

- **真源**：[risk_control.md:907](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md#L907)
- **实现路径**：`src/zephyr/risk/core/liquidity_monitor.py`（MOD-RK-08，已 production）
- **③参数**（纯技术/A股公开）：Amihud 窗口=20日 ｜ 价差阈值=0.5%（已在 systemic_risk_detector） ｜ 成交量萎缩阈值=近5日均量<20日均量×60%
- **复用资产**：`ashare_systemic_risk_detector.py` 的买卖价差监控（LIQUIDITY_CRISIS 检测已就绪，不重复造）
- **输入**：行情数据（OHLCV + 买卖价差）、成交量序列
- **输出**：`LiquidityAssessment`（amihud_ratio + spread + volume_shrinkage_flag + 综合流动性评分）
- **接口契约**：
  ```python
  @dataclass(frozen=True)
  class LiquidityAssessment:
      symbol: str
      amihud_illiquidity: float       # |return| / 成交额，20日均值
      bid_ask_spread: float           # 来自 systemic_risk_detector
      volume_shrinkage_ratio: float   # 近5日均量 / 20日均量
      overall_score: float            # 0=极度流动性, 1=极度非流动
      timestamp: datetime

  class LiquidityMonitor:
      def assess(self, symbol: str, ohlcv: pd.DataFrame, spread: float) -> LiquidityAssessment: ...
      def batch_assess(self, market_data: dict[str, pd.DataFrame]) -> list[LiquidityAssessment]: ...
  ```
- **算法实现**：
  - Amihud：`ILLIQ = (1/N) × Σ|daily_return_i| / daily_amount_i`，20日窗口
  - 成交量萎缩：`ratio = mean(vol[-5:]) / mean(vol[-20:])`，<0.6 触发预警
  - 买卖价差：复用 `ashare_systemic_risk_detector` 已有逻辑
- **验收**：Amihud 计算与学术定义一致、萎缩检出率≥95%（合成数据）、与 systemic_risk_detector 无冲突

#### G4：因子/策略拥挤度检测

- **真源**：[risk_control.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md)（BM-RC-06-D）
- **目标路径**：`src/zephyr/risk/core/crowding_monitor.py`（新建，对应 MOD-RK-13）
- **③参数**（纯技术）：HHI 阈值=0.1（集中度过高） ｜ 持仓相关性阈值=0.7 ｜ 拥挤度评分窗口=60日
- **复用资产**：`concentration_monitor.py`（HHI/行业暴露作为输入数据源）
- **输入**：组合持仓 + 全市场因子暴露数据（来自 factor 模块）+ `concentration_monitor` 输出
- **输出**：`CrowdingAssessment`（factor_crowding_score + strategy_crowding_score + 拥挤标的列表）
- **接口契约**：
  ```python
  @dataclass(frozen=True)
  class CrowdingAssessment:
      factor_name: str
      crowding_score: float           # 0~1, >0.7 触发预警
      hhi_of_holders: float           # 持仓集中度（来自 concentration_monitor）
      avg_correlation: float          # 因子成分股近期相关性
      crowded_symbols: list[str]      # 拥挤标的
      timestamp: datetime

  class CrowdingMonitor:
      def assess_factor(self, factor_name: str, holdings: dict, concentration: ConcentrationReport) -> CrowdingAssessment: ...
      def assess_strategy(self, strategy_id: str, positions: dict) -> CrowdingAssessment: ...
  ```
- **算法实现**：
  - 因子拥挤度 = f(HHI_of_holders, avg_correlation, turnover_decay)——三维度加权
  - HHI：复用 `concentration_monitor` 输出
  - 相关性：因子成分股近 60 日收益率相关系数均值
  - 换手衰减：拥挤因子通常伴随换手率下降
- **验收**：能在合成数据上检出拥挤因子、与 concentration_monitor 输出一致、评分单调性正确

#### 6.5 施工顺序修订（基于核查）

> GAP-03 已解决，风控编排器就绪 → G1/G2/G4 有了明确消费者，**不再被阻塞**。

```
原顺序：  [GAP-03 阻塞] → G1/G2/G4 无法接入
修订后：  GAP-03 已解决 ✓ → G1/G2/G4 可直接接入 DefaultRiskManagerOrchestrator
```

| 顺序 | 缺口 | 理由 | 前置门禁 |
|:----:|------|------|----------|
| 1 | **G1** 告警生成 | 零外部依赖，是 G2/G4 输出的统一出口；先建管道再接信号源 | depgraph 登记 + 四图对齐 |
| 2 | **G2** 流动性监控 | 2/3 需补建（Amihud + 成交量萎缩），1/3 已有（价差）；补建后接入 G1 | 同上 |
| 3 | **G4** 拥挤度 | 依赖 factor 模块 + concentration_monitor；接入 G1 | 同上 + factor 模块就绪 |
| — | G7 订单路由 | P1 最高（实盘必需），独立于 G1/G2/G4，可并行 | 同上 + EXE-02 就绪 |

> **建议**：G1→G2→G4 串行（每个 ~1-2 天），G7 可与 G1/G2/G4 并行推进（不同域、不同人/会话）。
> 每个缺口施工前 MUST 执行 §9 三步门禁。

---

## 7. 排除清单（需用户业务参数，不在本方案范围）

明确排除，避免误纳入施工：

| 环节 | 需用户给的业务参数 |
|---|---|
| BM-RC-01 风控策略（父）| 9 种限额的具体数值（仓位/行业/杠杆上限等）|
| BM-POS-01 仓位裁决 | `position_cap` 目标仓位 |
| BM-POS-02 Kelly | 策略预期收益/胜率 |
| BM-POS-04 跨策略硬限制 | 行业偏离、风格暴露阈值 |
| BM-POS-05 回撤缩放 | 总仓位上限 0.80/0.50 |
| BM-POS-06 现金管理 | 最低储备金、机会储备 X% |
| BM-SEL-20 多策略投票 | 策略权重 A30%/B25%/C20% |
| BM-SEL-21 组合优化 | 行业偏离、corr 阈值、Kelly 上限 |
| BM-SEL-22~25 评分卡 | 评分维度、权重、阈值 |
| BM-REC-04 保证金管理 | 预警线、维持担保比例（券商设定）|
| BM-REC-05 多账户分仓 | 账户 AUM、独立风控配置 |
| BM-EXE-01 自适应风控审批 | `max_single_position` |
| BM-BT-02-A 持仓组合 | 初始资金 |

> 这些环节的"机制框架"AI 可造，但跑起来必须等用户填业务数值。本方案只覆盖机制框架中"零参数"的部分。

---

## 8. 施工分期与依赖顺序

### P0 阶段：验收确认（38 项已实现）

**目标**：确认 38 个已实现项契约完整、可独立运行。

**方法**：
1. 对每个 ✓ 项编写冒烟测试（输入标准 fixture → 验证输出契约）
2. 跑通"数据接入 → 回测 → 风控检查 → 对账"最小闭环
3. 记录契约偏差，纳入 P1 修复

**重点验收项**：
- 回测闭环：[engine_base.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/engine_base.py) → [vectorized_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/implementations/vectorized_engine.py) → [metrics.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/metrics.py)
- 风控检查链：[default_risk_validator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_risk_validator.py) → [default_position_limit_checker.py](file:///d:/ZephyrAlpha/src/zephyr/risk/implementations/default_position_limit_checker.py)
- 对账闭环：[settlement_reconciliation.py](file:///d:/ZephyrAlpha/src/zephyr/trading/settlement_reconciliation.py) → [daily_auditor.py](file:///d:/ZephyrAlpha/src/zephyr/risk/core/daily_auditor.py)

**产出**：验收报告 + 契约偏差清单

### P1 阶段：完整度核查（20 项待核查）

**目标**：对 20 个 ◐ 项逐个核对子能力，补缺失分支。

**方法**：
1. 按 battle_map 6 件套逐条对照代码实现
2. 标注"已实现子能力 / 缺失子能力"
3. 缺失子能力补全（轻量施工）

**重点核查项**：

| 环节 | 核查要点 |
|---|---|
| BM-RC-01-C 预警分级 | 三级（黄/橙/红）分级逻辑是否完整 |
| BM-RC-02-C/D 杠杆/合规检查 | 检查规则覆盖度 |
| BM-RC-03-B/C Kill Switch 冷却期+Owner确认 | 30min 冷却期 + Owner 重置流程 |
| BM-RC-05-C 亏损限额强制停盘 | 日2%/周5%/月10% 三级触发 |
| BM-RC-06-C 三级警报与清仓 | 1停/2降30%/≥3清仓 执行链 |
| BM-BT-01-D A股交易约束 | T+1/万三/5元/1bp 是否独立可配 |
| BM-BT-02-E 幸存者偏差 | 退市股纳入回测 |
| BM-BT-04-B/C Embargo+Purged K-Fold | 期长度/K折叠数默认值 |
| BM-EXE-04 Pre-Trade合规 | 报单≥50μs/参与率≤5%/撤单≤15% |
| BM-POS-07/08/10 再平衡/日历/审计 | 待定位代码 |

**产出**：完整度核查表 + 轻量补全 PR

### P2 阶段：缺口补全（8 项待施工）

**目标**：从零实现 8 个缺口模块。

**施工顺序**（按依赖）：

```
第1批（无外部依赖，纯机制）：
  G1 告警生成 → G2 流动性监控 → G4 拥挤度检测
  （三者都消费监控数据产出告警，可并行）

第2批（依赖 ex_core）：
  G7 智能订单路由拆单（最高优先级，实盘必需）
  G6 操作风险审计（消费 ex_core 日志）

第3批（依赖 ml/agent 模块）：
  G3 AI/Agent风险监控（依赖 autonomy_core）
  G5 模型风险审计（依赖 ml_serve）

第4批（已排除）：
  G8 原始数据缓存+标准化 → P1 核查确认已实现于 data/，非缺口，已移除
```

**每个缺口的施工流程**（见 §9 门禁）：
1. depgraph 登记设计态 → 2. 四图对齐 → 3. 写代码 → 4. 测试 → 5. status planned→production

---

## 9. 施工前置门禁（铁律）

> 正式施工前 MUST 完成以下三步，违反即触发幻觉/漂移治本规则。

### 9.1 依赖关系先行铁律（L1，2026-07-02）

任何模块施工前（写第 1 行业务代码前），MUST 先通过 `apply_depgraph.py` 将该模块的依赖关系登记到 depgraph 设计态（status=planned）。

```bash
# 示例：登记 G7 智能订单路由的依赖（施工前 planned → 验证后 production）
python scripts/apply_depgraph.py --add-design-node \
  --path "zephyr.ex_sor.core.algo_trading_engine" \
  --domain D_EX_SOR \
  --build-status planned
python scripts/apply_depgraph.py --add-edge \
  --from "zephyr.ex_core.execution_engine" \
  --to "zephyr.ex_sor.core.algo_trading_engine" \
  --contract "Order→AlgoExecutionPlan"
```

### 9.2 四图对齐铁律（2026-07-22，TRAE-080）

开发任何模块前 MUST 先在四图（depgraph/dataflowgraph/decisiongraph/blueprint.md，以 module_id 对齐）完成设计并对齐：

1. `apply_depgraph.py --add-design-node` 登记 depgraph 设计态（= L1）
2. `sync_panorama_module.py` 自动派生其余 3 图（apply_depgraph 后自动触发）
3. `align_panoramas.py` 验证 4 类对齐问题（孤儿/状态漂移/域不一致/设计态孤立）干净后再施工

### 9.3 备份先行铁律（trae_054 v1.6.0 STEP0，两层）

1. **DB 数据备份**：`apply_depgraph` 内置 `backup_pg_architecture()` 自动 PG 备份（pg_dump + 事务回滚）
2. **脚本代码备份**：oneoff 脚本运行前应 git commit（君子协定，待技术强制）

### 9.4 文件命名规范

- 全项目文件名 snake_case（小写+下划线）
- 新建模块文件：`ai_agent_monitor.py`、`model_risk_audit.py` 等（snake_case；G3/G5 待组装缺口）
- `docs/_working/` 已在 N-16 跳过目录（2026-08-05 已完成豁免），本文件命名不受 N-16 约束

---

## 10. 验收标准

### 10.1 单模块验收（每个缺口项）

| 验收项 | 标准 |
|---|---|
| 代码契约 | 接口实现符合 §6.2 规格 |
| 单元测试 | 覆盖率≥80%，核心路径 100% |
| 冒烟测试 | 标准 fixture 输入 → 预期输出 |
| depgraph 状态 | status 从 planned → production |
| 四图对齐 | `align_panoramas.py` 0 违例 |
| 文档 | battle_map 6 件套"代码当前"字段更新 |

### 10.2 整体验收（66 项基础设施层）

| 验收项 | 标准 |
|---|---|
| 闭环跑通 | 数据接入→回测→风控→执行→对账 最小闭环可运行 |
| 零业务参数 | 66 项机制实现不依赖任何用户业务数值 |
| 缺口清零 | 8 个 ✗ 项全部转 ✓ |
| 完整度核查 | 20 个 ◐ 项全部确认或补全 |

---

## 11. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 待核查项(◐)实际缺口多于预期 | P1 工作量膨胀 | P1 核查时若发现实质缺口，升级为 P2 缺口项单独施工 |
| ~~G8 可能已实现（在 data_eng/）~~ | ~~重复施工~~ | **已核查确认**：实现位于 `data/`（非 `data_eng/`），非缺口，已移除 |
| G3/G5 依赖模块未就绪 | 阻塞施工 | 第3批延后，等 autonomy_core/ml_serve 就绪 |
| depgraph 登记遗漏 | 违反 L1 铁律 | 每个缺口施工前对照 §9.1 清单逐项确认 |
| Kill Switch 冷却期实现不完整 | 实盘安全风险 | P1 重点核查 RC-03-B/C，不完整则升级优先级 |

---

## 12. 附录

### 附录 A：施工对象代码域分布

| 代码域 | 路径 | 缺口数 | 待核查数 |
|---|---|---|---|
| 风控 | `src/zephyr/risk/` | 6 | 7 |
| 执行 | `src/zephyr/ex_sor/` | 1 | 1 |
| 数据接入 | `src/zephyr/market_data/` | 0~2 | 2 |
| 回测 | `src/zephyr/backtest/` | 0 | 6 |
| 对账 | `src/zephyr/trading/` | 0 | 0 |
| 仓位 | `src/zephyr/position/` | 0 | 3 |
| 报告 | `src/zephyr/reporting/` | 0 | 1 |

### 附录 B：真源文件索引

| 文档 | 用途 |
|---|---|
| [battle_map_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_panorama.md) | 全景图真源，330 环节状态分布 |
| [battle_map_09_risk_control.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_09_risk_control.md) | 风控域 6 件套（31 个零参数环节真源）|
| [battle_map_05_stock_selection.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_05_stock_selection.md) | 数据接入 6 件套 |
| [battle_map_03_backtest_validation.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_03_backtest_validation.md) | 回测引擎 6 件套 |
| [battle_map_10_execution.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_10_execution.md) | 执行管道 6 件套 |
| [battle_map_11_reconciliation.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_11_reconciliation.md) | 对账清算 6 件套 |
| [battle_map_08_position_management.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_08_position_management.md) | 仓位硬规则 6 件套 |

### 附录 C：下一步行动清单

> **详细 TODO 追踪见 §0 施工进度追踪**（文档开头）。此处仅保留历史里程碑。

- [x] **已完成**：P0 验收跑通回测→风控→对账最小闭环（2026-08-05，3 阶段全 PASS，登记 3 个契约偏差）
- [x] **已完成**：P1 核查 G8 → 确认已实现于 `data/`（非 `data_eng/`），非缺口，缺口数 8→7
- [x] **已完成**：P1 核查 risk/ 目录 → GAP-03 已解决（`DefaultRiskManagerOrchestrator` 存在），G1=真缺口、G2=半缺口(1/3)、G4=真缺口，实施方案已写入 §6.4
- [ ] **进行中**：见 §0 TODO 清单（G1→G2→G4 串行 + G7 并行）

---

> **本方案状态**：施工准备草稿，保存在 `docs/_working/`（草稿区）。
> 正式施工须先过 §9 施工前置门禁，且每个缺口项的 depgraph 状态从 planned→production 后方可标记完成。
