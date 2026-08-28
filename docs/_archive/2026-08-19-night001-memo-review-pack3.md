---
ttl: permanent
---

# design_memos 审查·分包3（52/53/54/55/60/61/62/63/64/65/66/68/90/91 共 14 篇）

> 方法：逐篇读全文 → 识别文档承诺施工内容 → Grep/Glob 在 `src/zephyr`（+`scripts/`+注册表 YAML）实证落码 → 结案报告段核验/插入/补正 → 未施工清单逐条裁定。
> 裁定口径：**过度工程**（违 system_charter §2 约束一~六 或 §4 范围边界 B-017~B-020）/ **未来工程-小型**（函数级/配置级/小模块，单批可闭环）/ **未来工程-大型**（多模块/新基础设施级）。
> tracker（construction_progress_tracker.md）只读未改；memo 结案报告段按授权直接改；未 commit；未动 src/。
> 口径适配：90 号=开放式问题文档（本体任务=逐项裁定）、61/65/66/68=治理类（结案报告=机制落地状态）、91=远期愿景文档（无施工承诺）。

---

## 逐篇一行结论总览

| 篇 | 结案报告动作 | 结论 | 未施工条数 | 裁定分布（过度工程/未来小/未来大/待Owner） |
|---|---|---|---|---|
| 52_backtest_framework_docking | **插入** | 框架全 production 实证，本篇为 why 回填零新施工；未施工=§6 暂缓项+DSR 两项+零单测 | 8 项（2 条合并计） | 1 / 6 / 1 / 1（DSR 统编等裁定） |
| 53_simulation_live_path | 核验一致无改动 | 五态降级机+state_store+耦合点全实证；未施工=执行侧接线+排队引擎+远期算法 | 7 | 2 / 4 / 1 / 0 |
| 54_reconciliation_attribution | 核验一致无改动 | 16/18 环节 production 实证；未做=REC-02-B/03-D+横向缺口（调度/DB/渠道/双实现裁定） | 9 | 2 / 6 / 1 / 2（双实现裁定） |
| 55_monitoring_review | **补正**（Panel Tab 注记） | 三件套+33 阈值+统读闭环全实证；未做=§6 四暂缓（均带重评条件） | 5 | 0 / 5 / 0 / 0 |
| 60_cross_cutting_cleanup | 核验一致无改动 | conflict_matrix 实证 3 条+CAND-PFALLOC-002 rejected；无未施工项 | 0 | 0 / 0 / 0 / 0 |
| 61_lifecycle_multi_ai | **插入**（治理口径） | 交接纪律/退役判据执行体已承载；mSPRT/DriftObservatory/退役工作流未落码；⚠️MLflow 引用漂移 | 7 | 1（合并计） / 4 / 2 / 0 |
| 62_business_registry_construction | 核验一致无改动 | 18 注册表全在位；因子 ic 全 null 实证（回填未做一致） | 3 | 0 / 2 / 1 / 0 |
| 63_data_utilization_audit | **插入** | 审查本体完工；三波补文档未执行（实证 35/37/10/24 零引用）；注册表已由 62 号闭环 | 5 | 1 / 3 / 0 / 1（Q1/Q8 等） |
| 64_data_source_download_spec | **补正**（§16.2 漏核 4 项） | 规范定稿+巡检健康；但裁定施工 14 项中 Q8/Q16/Q17/Q18 未施工（Q18=P0 实证） | 4 | 0 / 4 / 0 / 0 |
| 65_git_safety_governance | **补正**（漏 #69） | 多层防护全实证生产运行；未做=#72+#69 两小治理债 | 2 | 0 / 2 / 0 / 0 |
| 66_commit_queue_serialization | 核验一致无改动 | 两层防护+task_board+PG 韧性实证；commit_queue 本体零施工痕迹 | 2 | 0 / 0 / 2 / 0 |
| 68_code_algorithm_review_pipeline | **插入**（治理口径） | 审查线首批五路全 merge 实证，机制常态化；未做=节奏/存量/场景库三观察项+两待 Owner | 5 | 1 / 3 / 0 / 1 |
| 90_methodology_open_questions | **插入**（开放问题口径） | 21 项裁定闭环；Phase 1/2 施工承诺实证全未施工（CST-T0/benchmark/BHY/LVaR/做T配置等零命中） | 6（合并计） | 2（合并计） / 3（P1 三项+P2 合并+C-030） / 0 / 1（P-1~P-5） |
| 91_density_prediction | **插入**（远期愿景口径） | 无施工承诺，维持规划态；仓内仅 feedback_loop 简易 CP 骨架，其余零命中一致 | 5 | 3 / 0 / 2 / 0 |

> 阻塞：无。全部 14 篇处理完毕，未遇不可实证项；53/54/55/60/62/66 六篇既有结案报告经代码实证核验一致（其中 55 补一条 Panel Tab 过时注记，64/65 各补一条漏项注记）。

---

## 52_backtest_framework_docking（回测框架对接）

**施工状态实证**：本篇承诺=BM-BT-01~07 框架 why 回填+策略侧复用裁定，无新施工承诺。实证（2026-08-19）：`backtest/core/` 11 文件全在位（engine_base/vectorized_engine/event_driven_engine/shrinkage_engine/matching_logic/portfolio/walk_forward/pit_manager/overfitting_detector/metrics/decision_gate/tick_replay/data_handler）+ `services/scheduler.py` + `io/` 三件套（result_sink/result_repository/decisiongraph_adapter）；`simulation/deflated_sharpe_calculator.py`（MOD-SIM-024）在位。⚠️ 新发现文档滞后：`services/cache_manager.py`、`services/report_generator.py` 均 MATURITY=production，而 §3.1.1 标"design/不抢先施工"。

**结案报告动作**：**插入三段式结案报告**（frontmatter 后），含上述滞后注记。

**未施工清单+裁定**：
1. CPCV+PBO（§6 暂缓，重评=变体>50 或 DSR 频繁误报）——**未来工程-小型**。
2. Purged K-Fold（BM-BT-04-C，重评=标签重叠窗口策略上线）——**未来工程-小型**。
3. 03-E CRPS 密度预测验证（重评=regime 密度预测上线，91 号路线）——**未来工程-大型**。
4. 回测异常诊断 BM-BT-07-F（重评=故障样本≥10 例）——**未来工程-小型**。
5. 07-H result_deployer——§4 已裁拒绝全自动上线，人工审批承载——**过度工程**（当前阶段）。
6. 策略验证流水线编排入口（§7① 随首批上线）——**未来工程-小型**。
7. DSR 双实现统编（实证 backtest 阈值 0.5 vs simulation 0.95 双轨仍在；tracker #14 ⏳ 等裁定）——**待 Owner 裁定**（裁定后单行收敛）。
8. DSR 接入 DecisionGate 判定链（实证 decision_gate.py 零 dsr 引用）——**未来工程-小型**（随 7 落地）。
9. 四核心模块零单测（walk_forward/decision_gate/overfitting_detector/pit_manager+calculate_dsr，实证 tests/ 无对应文件）——**未来工程-小型**（测试债）。
10. battle_map_03/00_index 同步（越界登记）——**未来工程-小型**（文档治理）。

---

## 53_simulation_live_path（模拟与实盘验证路径）

**施工状态实证**：`rollback_state_machine.py`（MOD-GOV-045）在位；`paper_live_transition.py` `check_promotion_allowed` 耦合点在位（posture!=NORMAL→PermissionError）；`shared/state_store.py`+`state_store_redis.py` 在位（QUANT-002 落地）；`evaluate_rollback` 全 src 无生产调用方（与 §3.8 表"执行侧接线待施工"+tracker #204 一致）；BM-SIM-08 涨跌停排队引擎零命中（与 §2.4"待施工"一致）；`deflated_sharpe_calculator.py`/`slippage_analyzer.py`/`settlement_reconciliation.py`/`position_reconciler.py` 均在位。

**结案报告动作**：已有 2026-08-16+08-17 两段结案报告，与实证**一致，无改动**。

**未施工清单+裁定**：
1. BM-SIM-08 Paper Matching 涨跌停排队引擎（SHADOW 前置）——**未来工程-小型**。
2. 五态降级机执行侧动作接线（撤单/阻断/减仓/平仓入交易运行时，tracker #112 ⏳ 待 SHADOW 阶段）——**未来工程-大型**（生产接线批）。
3. BM-BT-05-H 四因子归因（待实盘数据）——**未来工程-小型**。
4. 概率型 kill switch BOCPD（≥200 笔 PnL 先验校准）——**未来工程-大型**。
5. MPC 智能调速器（远期）——**过度工程**（自判暂缓，重评条件未达）。
6. RMATS typed message 协调（4 LLM agent+递归协议，自判简化借鉴 v3.0）——**过度工程**（当前阶段）。
7. propagator 传播子滑点模型（需逐笔订单流+L2 接入）——**未来工程-大型**。
8. EvoMarket T+1 native 模拟器（自判 MVP 不引入，远期验证基准）——**过度工程**。
9. citrusquant volume-aware 形式（v2.0 候选）——**未来工程-小型**。
10. 门禁阈值/观察期/灰度顺序校准+miniQMT 执行对账落地（待 SHADOW 数据）——**未来工程-小型**。
11. 00_index 漂移同步（不越界改，登记）——**未来工程-小型**（文档治理）。

---

## 54_reconciliation_attribution（对账归因）

**施工状态实证**：`SettlementReconciler`（MOD-TRADING-003）/`PositionReconciler`（MOD-EX-056）/`PnlCalculator`/`DailyAuditor` 均在位；`reporting/default_attribution_engine.py` 实证仍全桩（三方法 return 0.0）；`pf_core/core/performance_attribution_engine.py`（真实 BHB 实现）在位——双实现冲突未收敛实证一致；MOD-RPT-015 全 src 零命中；StrategyBook 实证仅消费外部注入 `strategy_pnl_history` 不核算 PnL（一致）。

**结案报告动作**：已有 2026-08-16 结案报告（RCAN 批次=文档收敛无新增代码），与实证**一致，无改动**。

**未施工清单+裁定**：
1. 归因引擎双实现收敛（§6 置顶，须 owner 裁定基底/canonical/契约接线）——**待 Owner 裁定**（裁定后收敛施工=未来工程-小型）。
2. MOD-RPT-015 绩效归因报告生成器（planned，登记缺口先补 ARCH）——**未来工程-小型**。
3. StrategyBook 独立 PnL 核算（#ARCH-REG-005 proposed）——**未来工程-小型**。
4. 盘后 15:30 调度接线（APScheduler/work_dag 均无任务）——**未来工程-小型**。
5. 对账/归因 DB 持久化 schema（audit_trail/差异表/归因结果表无 DDL）——**未来工程-小型**。
6. ReportPublisher WEBHOOK/EMAIL 实发（仅 PENDING）——**未来工程-小型**。
7. CTR-P1-007 产出逻辑（GAP-L06-003 P0，BM-REC-02-B 上游）——**未来工程-小型**。
8. 资金对账+transaction_cost_drag TCA IS 四组件（实盘后）——**未来工程-小型**。
9. PositionReconciler/公司行为双实现口径裁定——**待 Owner 裁定**。
10. regime-conditional/Shapley/MCR-CCR 归因（Phase 2/2.5）——**未来工程-大型**（Shapley 为小型）。
11. Barra 因子风险归因（自判拒绝，AUM 机构化重评）——**过度工程**。
12. Merkle/VCP v1.2 审计轨迹升级（远期）——**未来工程-大型**。
13. AI 驱动对账（自判暂缓，日成交>1000 笔重评）——**过度工程**。
14. 微信入站指令解析（归 buy_flow 域，出站实发后评估）——**未来工程-大型**。

---

## 55_monitoring_review（监控告警与复盘）

**施工状态实证**：`strategy_deviation_monitor.py`（MOD-RK-23）/`review_orchestrator.py`（MOD-RPT-009）/`strategy_retirement_evaluator.py`/`shared/alerts/threshold_loader.py` 全在位；`alert_threshold_registry.yaml` 33 条 active 实证；THD-RETIRE-001/002/003+THD-DEVIATION-003 四条 active 转正实证。

**结案报告动作**：已有 2026-08-16 结案报告与实证一致；**补一条 2026-08-19 复核补正**：§7 新发现 3（Panel 实验历史 Tab 未施工）已过时（51 号工作流 B 已建成 `_tab_experiment_history`）。

**未施工清单+裁定**：
1. Email/WeChat sender 实发（no-op 占位；首批上线前必须注入）——**未来工程-小型**。
2. miniQMT 下单链路探针（随 40 号缺口清单）——**未来工程-小型**。
3. 偏离度量归因分解 H-A~D 四因子（首次真实触发后）——**未来工程-小型**。
4. 复盘模板引擎固化（周复盘跑满 12 期后）——**未来工程-小型**。
5. shared/alerts 全组无测试（工程 backlog）——**未来工程-小型**（测试债）。
6. BM-RC-08-E 操作风险审计 / BM-RC-08-D 模型风险审计（设计态，重评=首批上线+3 月 track record）——**未来工程-小型**（编排复用既有资产）。

---

## 60_cross_cutting_cleanup（冲突矩阵清理与事件总线）

**施工状态实证**：`module_translation_registry.yaml` conflict_matrix 实证收敛为 3 条 firm-level 硬上限（31→3）；`sell_conflict_arbitrator.py`（MOD-SELL-008）/`shared/event_bus.py`（MOD-INF-016）均在位；CAND-PFALLOC-002 实证 status=rejected（2026-08-15 AI-XCUT-001 留痕）。

**结案报告动作**：已有 2026-08-16 结案报告，与实证**一致，无改动**。

**未施工清单+裁定**：无本科目未做项（§6 待裁定=sync 重生成自动闭合验证/盘中多信号源/热更新，均远期或派生验证项）。

---

## 61_lifecycle_multi_ai（策略生命周期与多 AI 协作）

**施工状态实证**（机制落地口径）：交接纪律/并发冲突纪律已由 Gateway+worktree+lock_files 承载；退役判据执行体 `strategy_retirement_evaluator.py` 在位（55 号落码）；mSPRT/drift_observatory/retirement_workflow 全 src 零命中；strategy_archive/ 目录不存在；**mlflow 全 src 零命中**（51 号已卸载）——本篇 MLflow alias 载体引用（§3.3/§3.9）需重裁定落地载体，已在结案报告注记。

**结案报告动作**：**插入三段式结案报告**（治理类口径），含 MLflow 漂移注记。

**未施工清单+裁定**：
1. Champion-Challenger mSPRT 晋升通道（§3.3 纪律 1）——**未来工程-大型**（需先裁定 MLflow 退役后的载体）。
2. Drift Observatory 四层编排（§3.3 纪律 4）——**未来工程-大型**（随首批上线后监控批）。
3. 退役 5 步工作流（§3.9）——**未来工程-小型**（判据已由 55 承载，编排待首个退役触发）。
4. strategy_archive/ 目录——**未来工程-小型**（触发时施工）。
5. BM-MT-02-A/B 灰度+影子+对抗鲁棒性——**未来工程-大型**（MLOps Level 2 批）。
6. AI 行为基线+异常告警（BM-RC-04-F）——**未来工程-小型**。
7. 冷启动 T0/T1/T2 渐进建仓（§3.1）——**未来工程-小型**（随 53 号迁移路径承载）。
8. LLM alpha 挖掘远期候选/独立 Lifecycle Manager/KFP 编排/多 Agent 编排——**过度工程**（本篇已逐项裁定 Phase 5+/暂缓/拒绝）。

---

## 62_business_registry_construction（业务资产注册表体系）

**施工状态实证**：18 个业务注册表全部在位（catalogs/ 实证 factor/strategy/risk_limit/technical_indicator/execution_algo/data_asset/chart_pattern/field_dictionary/experiment/universe/benchmark/cost_model/seat/regime_cycle/model/event_calendar/macro_indicator/portfolio_model）；`factor_registry.yaml` 实证 140 条 `ic: null`、无非空 ic 值——"因子 IC 实证回填未做"与结案报告一致。

**结案报告动作**：已有 2026-08-16 结案报告，与实证**一致，无改动**。

**未施工清单+裁定**：
1. 因子 IC 实证回填（140+ 条 ic 全 null；tracker #56 ⏳ 等排期裁定）——**未来工程-大型**（依赖回测跑批基础设施）。
2. chart_pattern used_by_factors 回填（tracker #32，形态因子施工后）——**未来工程-小型**。
3. YAML→DB 迁移（MIGRATE_REGISTRY 算法，远期）——**未来工程-大型**。
4. experiment_registry attribution_result 字段回填（依赖 54 号归因施工）——**未来工程-小型**。
5. §6/§7 节标题"P1/P2 待施工" vs §3 全部已施工——文档节标题滞后，随下一文档治理批顺手（非施工项）。

---

## 63_data_utilization_audit（业务数据资产利用率审查）

**施工状态实证**：审查本体完工（v2.1.0 全量重扫）；批次 A 补文档**未执行**实证——35/37/10/24 号文档对 restricted_shares/share_unlock/etf_nav/edb_data/block_trade_detail 全部零引用；`scripts/audit_data_utilization.ps1` 不存在；`data_asset_registry.yaml` 在位约 199 条（§7.4 补齐计划已由 62 号施工线超额闭环）。

**结案报告动作**：**插入三段式结案报告**。

**未施工清单+裁定**：
1. 第一波批次 A 9 张风险表消费文档（→35/37/10/24 号）——**未来工程-小型**（纯文档施工）。
2. 第二波批次 B+C 25 张（→26/22/15 号）——**未来工程-小型**。
3. 第三波批次 D 记录+归档决策——**未来工程-小型**。
4. scripts/audit_data_utilization.ps1 + docs/_audit/ 快照——**未来工程-小型**（持续校验前置）。
5. Leiden/Temporal Coupling/SPC/状态指纹四脚本（运维期机制，触发条件未到）——**过度工程**（当前阶段）。
6. Q1/Q8/Q3/Q4/Q6 待人决策项——**待 Owner**（默认建议在档）。
7. §9 全表"不做什么"——已逐项裁定拒绝，**非缺口**。

---

## 64_data_source_download_spec（数据源与下载体系规范）

**施工状态实证**：规范本体定稿+巡检健康（一致）；但 §16.2 裁定施工 14 项执行态：Q5 北向/Q6 冷归档/Q13 ARCH-SPECIAL-DAYS 登记/Q14 死 fallback 清理（tasks.yaml 实证无 qmt/exchange/bdpan，local_valuation 保留 1 处）——4 项已闭环；**Q8 parts 告警（无实现）/Q16 fetch_perf（scheduler 零写入）/Q17 自动熔断（零命中）/Q18 create_provider internal 接线（实证 else→None，`hk_trade_calendar_refresh` source: internal 当前失败）——4 项未施工，Q18 为 P0**。

**结案报告动作**：**补一条 2026-08-19 复核补正**（原报告漏核 §16.2 执行态）。

**未施工清单+裁定**：
1. Q18 internal 接线（P0：一行 elif+docstring 虚标修正+港股日历缺口评估）——**未来工程-小型**（建议优先排期）。
2. Q17 per-source 自动熔断器（P1：连续失败 N 次熔断 M 分钟+半开探针）——**未来工程-小型**。
3. Q8 data parts>100 告警（P1：防 CH parts 爆炸重演）——**未来工程-小型**。
4. Q16 fetch_perf scheduler 被动记录（P2：为 Q11/Q17 提供数据基础）——**未来工程-小型**。
5. §16.3 十九项暂缓/维持/不做（含 edb_data 替代源、东方财富爬虫、SLA 监控等）——本篇已逐项裁定，**非缺口**（L2/iFind 费用两项待人拍板，默认建议暂不）。

---

## 65_git_safety_governance（Git 安全治理体系）

**施工状态实证**：`git_safety_wrapper.ps1`+`install_git_safety_wrapper.ps1`+`ensure_ai_wrapper_injection.ps1`+`task_board.py`+`lock_files.py`+`git_guard.py` 全在位；git_guard.py 实证 `PLUMBING_BLOCKED_SUBCOMMANDS={read-tree,update-index,write-tree,hash-object}`；wrapper/plumbing/lock_files Mutex+TTL 与结案报告一致。

**结案报告动作**：已有 2026-08-16+08-17 结案报告基本一致；**补一条 2026-08-19 复核补正**：漏登 #69（d6 三 hook pre-commit 传参不兼容 ⏳）。

**未施工清单+裁定**：
1. #72 wrapper `git branch -d` 误报拦截（规则 -d/-D 区分缺陷）——**未来工程-小型**。
2. #69 d6 三 hook pre-commit 传参兼容（argparse 被喂文件名 exit 2）——**未来工程-小型**。
3. §7.31 git 并发操作串行化 P1 保留要点——由 66 号 commit_queue 本体承载（见 66 号，**未来工程-大型**）。
4. §7.11 Trash Redirect（自判远期不施工）+deprecated 17 项——**非缺口**（本篇已裁定）。

---

## 66_commit_queue_serialization（提交队列串行化）

**施工状态实证**：task_board.py（SQLite WAL+CAS）/lock_files.py（TTL+Mutex）/git_guard plumbing 拦截/pg_probe.py（`governance/audit/`）全在位；`.runtime/commit_queue/` 零施工痕迹实证——与结案报告"commit queue 本体未做（遗留 #67 ⏳ 待排期）"一致。

**结案报告动作**：已有 2026-08-16+08-17 结案报告，与实证**一致，无改动**。

**未施工清单+裁定**：
1. commit queue 本体 MVP（队列目录协议+enqueue/status/drain CLI+入队自举排空+专用 worktree 落盘+compaction+`_commit_auto` 改道入队，§10 验收：3 会话 50 提交零丢失/零搭便车/FIFO 序）——**未来工程-大型**（大工程量单项，待排期）。
2. P1 级联标记+死信重入队 CLI+done TTL+worktree 强制升硬联动（61 号 §3.6/65 号 §7.6/ARCH-WORKTREE-GATE-001 口径修订）——**未来工程-大型**（随 MVP 验收后）。
3. P2 监控接入+temp-index 评估+多分支——**未来工程-大型**（评估项，做/不做再裁定）。

---

## 68_code_algorithm_review_pipeline（代码与算法多模型审查流水线）

**施工状态实证**（机制落地口径）：审查线首批五路全部执行并 merge——R1 三批（#150-#162 登记，MERGE_HEAD 盲区等 3 项 P1 治本）、R2 红队（af15018fb2，56 攻击 34PASS/22FAIL，12 治本+26 测试）、R3（#141-144）、R4（8c3bf463a2）、R5（6576445f）；轮换矩阵/调度卡协议首批实证有效。

**结案报告动作**：**插入三段式结案报告**（治理类口径）。

**未施工清单+裁定**：
1. 审查队列节奏裁定（§5 #1，首批 3~5 批完成后）——**未来工程-小型**（运营观察项）。
2. 存量回补审查优先级清单（§5 #2，增量队列清空时）——**未来工程-小型**。
3. 红队场景库物理形态（§5 #3，≥10 条时）——**未来工程-小型**。
4. 周期汇报频率+token 预算（§6 #3）/周审查窗口（§6 #4）——**待 Owner**。
5. 商业 AI 审查服务（§3 已裁暂缓）——**过度工程**（远期选项保留）。

---

## 90_methodology_open_questions（方法论约束遗留提案）

**施工状态实证**：21 项提案 v2.0.0 全量裁定闭环（本体任务完成）；施工优先级表 Phase 1/2 承诺**实证全部未施工**：CST-T0-001（cost_model_registry 零命中）、中证1000/2000/万得全A（benchmark_registry 零命中）、BHY FDR（src 零命中）、liquidity_monitor 压力退出时间/LVaR（零命中）、半衰期样本权重（零命中）、做T 四规则配置（零命中）、algo_execution_selector 默认限价单（未见配置化）。

**结案报告动作**：**插入三段式结案报告**（开放式问题文档口径）。

**未施工清单+裁定**：
1. P1 三项（CST-T0-001+最低佣金确认 / benchmark 三条目增补 / 执行选择器默认限价单+打板路径）——**未来工程-小型**。
2. P2 十一项（BHY FDR / liquidity_monitor 扩展 / 半衰期样本权重 / universe 两维 / 生存线监控 / 单一出口验证 / IM 轻量表 / 指纹库+DTW+持久化 / 做T 四规则 / 泄漏测试自动化 / 族归属治理流程）——**未来工程-小型**（单件 ≤100 行，建议组 1-2 个专项小批清偿）。
3. #7 8 态预测 / #10 密度预测（已裁暂缓/远期）——**过度工程**（当前阶段）。
4. P-1~P-5（Wasserstein/Conformal 栈/Robust HMM/RL 执行/过拟合协议）——**待 Owner**（方向已给，A2 PASS 后 P-1/P-3 紧迫性下调）。
5. §22 五环节：05-D/05-E/06/10 远期 MVP 不建——**过度工程**；26 C-030 溯源链 Phase 2——**未来工程-小型**。

---

## 91_density_prediction（密度预测与 QNN 远期愿景）

**施工状态实证**：无施工承诺（draft 远期愿景，90 号 §10 裁"远期维持 MVP 不建"）；仓内唯一相关实现 `feedback_loop/evolution/conformal_prediction.py` 简易骨架（进化模块自用）实证在位；RWC/LSTM+GMM/MDN/Survival/TCP-RM/QNN 零命中——与裁定一致无漂移。

**结案报告动作**：**插入三段式结案报告**（远期愿景文档口径）。

**未施工清单+裁定**：
1. BM-SEL-14 共形预测 Phase 0（slow unweighted+RWC 变体）——**未来工程-大型**（栈收敛待 90 号 P-2 裁定）。
2. BM-SEL-14-A TCP-RM/DDCI（已裁降级 Phase 2 候选）——**过度工程**（当前阶段）。
3. BM-SEL-15 Survival 止盈止损（AFT，激活=密度预测验证通过）——**未来工程-大型**。
4. BM-BUY-02-A-1-c 8 态 PDF 积分派生（随 90 号 §7 冻结）——**过度工程**（当前阶段）。
5. QNN（可行性未证）——**过度工程**（当前阶段）。

---

## 汇总统计

- **结案报告动作**：插入 6 篇（52/61/63/68/90/91）；补正 3 篇（55 注 Panel Tab、64 注 §16.2 漏核 4 项、65 注漏 #69）；核验一致无改动 5 篇（53/54/60/62/66）。
- **裁定分布**（按条计，含合并项）：过度工程 ≈17 条；未来工程-小型 ≈45 条；未来工程-大型 ≈13 条；待 Owner 裁定 ≈8 条（52 DSR 统编、54 双实现×2、63 Q1/Q8 等、68 两项、90 P-1~P-5、64 费用两项——费用类已给默认建议）。
- **高优先建议**：① 64 号 Q18（P0，internal 接线，影响港股日历月度任务，一行 elif 级小修但裁定 P0）；② 66 号 commit_queue 本体（未来工程-大型单项，待 Owner 排期）；③ 62 号因子 IC 回填（tracker #56 等排期裁定）；④ 90 号 Phase 1/2 施工小批（14 件 ≤100 行登记项组批清偿）。
- **新发现漂移（已注记）**：52 号 §3.1.1 cache_manager/report_generator 标 design 实为 production；55 号 §7 Panel Tab 条目过时；61 号 MLflow 载体引用需随 51 号退役重裁定；64 号结案报告漏核 §16.2（已补正）；65 号结案报告漏 #69（已补正）。
