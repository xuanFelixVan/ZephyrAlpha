---
ttl: permanent
---

# design_memos 审查·分包2（29-37/40-43/50/51 共 15 篇）

> 方法：逐篇读全文 → 识别文档承诺施工内容 → Grep/Glob 在 `src/zephyr`（+`tests/`+注册表 YAML）实证落码 → 结案报告段核验/插入/补正 → 未施工清单逐条裁定。
> 裁定口径：**过度工程**（违 system_charter §2 约束一~六 或 §4 范围边界 B-017~B-020）/ **未来工程-小型**（函数级/配置级/小模块，单批可闭环）/ **未来工程-大型**（多模块/新基础设施级）。
> tracker（construction_progress_tracker.md）只读未改；memo 结案报告段按授权直接改；未 commit；未动 src/。

---

## 29_factor_strategy_extraction（潘潘课程因子策略提炼）

**施工状态实证**：本文档承诺=546 条因子/策略判定入库。实证（2026-08-19 注册表计数）：`factor_registry.yaml` **140** 条（与结案报告"140 条全量重建"一致）；`strategy_registry.yaml` **146** 条（一致）；`risk_limit_registry.yaml` **110** 条（与"48 条 route_risk 62→110"一致）。入库承诺已兑现。

**结案报告动作**：已有 2026-08-16 自含格式结案报告（入库去向总表+判定不入库 29 条逐条理由），与实证**一致，无需改动**（格式非三段式但实质覆盖"实际开发/最终成果/未做+原因"三要素）。

**未施工清单+裁定**：
1. 因子量化落码 candidate→quantized（factor_registry 多数条目 code_path 空、ic 字段全 null，tracker #56 ⏳ 等排期）——**未来工程-大型**（因子落码+experiment_registry 跑批回填 IC/IR，跨多批次+依赖回测跑批基础设施）。
2. 库内算法迭代（algorithm_status/evidence 字段从 pending_backtest 流转）——同上，随批次 1 排期。

---

## 30_multi_strategy_concurrency（多策略并发架构）

**施工状态实证**：承诺=Model A 四模块。实证全部 MATURITY=production：`strategy_book.py`（688 行，`VolatilityInfo`+`_is_vol_anomaly` 4 检查链+`SentimentStageSignal`+`rebalance_to_budget`+`size_positions`）；`firm_risk_aggregator.py`（673 行，pre/post_kelly 两段+LIQUIDITY 20%/10% ADV 裁剪）；`budget_change_handler.py`（548 行，`TierLevel`+防抖+`strategy_type`）；`regime_meta_allocator.py`（586 行，allocate 5 步+CRISIS floor+water-filling）。四测试套件（25/60/33/55）均在位。灾后重建 4 项（测试/capability/depgraph/33 号）全部闭环。

**结案报告动作**：**插入三段式结案报告**（frontmatter 后）；并修 §2.4 施工注记"481 行"→"548 行"（遗留 #36 实证项，2026-08-19 就地更正）。

**未施工清单+裁定**：
1. `cold_start_ratio` 参数+StrategyBook 冷启动状态机（§6.7 施工指导）——全 src 零命中。**未来工程-小型**（首批策略上线前装配）。
2. score→weight 显式转换函数（§2.2 契约③）——设计内延期（留给策略子类）。**未来工程-小型**。
3. §6.2 策略间相关性验证（correlation drop rule）——23 号承载，等 PnL 数据。**未来工程-小型**。
4. §6.9 并存旧体系退役裁定（MOD-PA-003/PA-002/PA-004/pf_core 5 示例）——**等 Owner 裁决**（文档明示需人裁定）。
5. Bayesian/Conformal Kelly、Water-Filling、no-trade 半带、MPC、Relaxed RP——文档已裁 Phase 2/3 远期，**非缺口**。

---

## 31_position_sizing（仓位算法）

**施工状态实证**：承诺=策略层粗仓位+firm 层 Kelly+硬上限裁剪+§2.8 漂移再平衡。实证：`position_sizing_engine.py`（MOD-POS-001，C1-C13 全链）、`strategy_book.py`（σ_i 异常 4 检查链 `_is_vol_anomaly` 在位）、`firm_risk_aggregator.py`（LIQUIDITY_SEVERE/MODERATE 常量+裁剪在位）、`position_limit_enforcer.py` 在位；`test_strategy_book.py`（25 测试）在位。与结案报告一致。

**结案报告动作**：已有 2026-08-16 三段式，实证**一致，无改动**（遗留 #30 T+1 口径仍 ⏳ 开放，与报告声明一致）。

**未施工清单+裁定**：
1. T+1 可卖持仓口径对齐（#30 ⏳，供数方按 T+1 可卖权重供数）——**未来工程-小型**（供数口径）。
2. C10 偏度/峰度分布感知（§2.3.3，依赖 BM-SEL-13 密度 PDF 高阶矩）——**未来工程-大型**（依赖上游密度预测基础设施）。
3. `sizing_basis` 显式输出（§2.3.4 binding constraint 命名）——**未来工程-小型**（dataclass 补字段）。
4. 单票 8%/5%/5% 三层口径统一（§2.4.1/§5）——**未来工程-小型**（待 G04 首批策略产出后配置统一）。
5. Conformal/Bayesian/Empirical Kelly、HRP-μ、Tepelyan、DCVaR-RNN——文档已裁 Phase 2-4 远期，**非缺口**。

---

## 32_firm_risk_aggregator（firm 层风险聚合）

**施工状态实证**：承诺=求和+三级硬裁剪+冲突净额。实证：`firm_risk_aggregator.py` production，`pre_kelly_aggregate`/`post_kelly_clip`/`aggregate`/`_clip_liquidity`/`_clip_sector` 全在位，A-G 修复项（liquidity_cap 键/contributions 透传/adv_data 参数化）实证在位；`test_firm_risk_aggregator.py`（60 测试）在位。与结案报告一致。

**结案报告动作**：已有 2026-08-16 三段式，实证**一致，无改动**。

**未施工清单+裁定**：
1. 行业偏离 ±10%/±15% 裁剪（Step 2 仅绝对 30% 落码，偏离裁剪需 D-FACTOR 行业基准权重）——**未来工程-小型**（等 D-FACTOR 行业分类模块）。
2. `sector_overlay_active` 预留参数消费——同上，与 1 同批。
3. CVaR 接口对齐（var_calculator → `constraint_checks.tail_risk`，§6 待对齐）——**未来工程-小型**（接口对齐，var_calculator 已 production）。
4. T+1 可卖口径（同 31 号 #30）——**未来工程-小型**。
5. 单票三层口径统一（同 31 号）——**未来工程-小型**。
6. 相关性聚类/拥挤度 HBI-CSAD/华泰风格/PCA/CorrDD/Fassino/MFCCA/Hsieh DRO（§2.10.x）——文档已裁 Phase 3-5 远期，**非缺口**。

---

## 33_budget_change_handler（budget 三级升级）

**施工状态实证**：承诺=三级升级+防抖双层+差异化窗口+收敛三条件。实证：`budget_change_handler.py` production，`TierLevel`/`handle_budget_change`/`check_convergence`/`_retarget_in_convergence`/`strategy_type` 全在位；`test_budget_change_handler.py`（33 测试）在位。

**结案报告动作**：已有三段式，**补"复核注记（2026-08-19）"** 登记 §6/§7 暂缓项的代码实证状态（事件链未接线等），正文其余一致。

**未施工清单+裁定**：
1. BudgetChanged 事件链接线（`handle_budget_change` 全 src 无生产调用方，纯库模块）——**未来工程-小型**（装配级，随 G15→G14 集成）。
2. `on_firm_violation()` firm 违例直触 Tier3 入口（§7-③ 待决策）——**未来工程-小型**（函数级）。
3. TierState 跨日持久化（DB）——文档裁暂缓（重评条件=多进程/跨日常态未达成），**非当前缺口**。
4. E-POS-40/41 事件发射——文档裁暂缓（无消费方），**非当前缺口**。
5. 收敛后显式解冻指令——文档裁暂缓，**非当前缺口**。
6. convergence_window 校准——**等数据**（首批策略实盘换手率）。

---

## 34_regime_meta_allocator（regime 元分配器）

**施工状态实证**：承诺=三因子乘法分配器。实证：`regime_meta_allocator.py` production，`allocate()`/`_compute_shrinkage`（CRISIS floor 0.09→0.05）/`_normalize_and_clip`（water-filling+N=2 无解兜底）/`compute_performance_score`（Sortino n-1 分母修复）全在位；`test_regime_meta_allocator.py`（55 用例重建）在位。与结案报告一致。

**结案报告动作**：已有 2026-08-16 三段式，实证**一致，无改动**。

**未施工清单+裁定**：
1. 分配参数值校准（Base 权重/PerformanceScore 映射/四档阈值/floor·cap）——**等数据**（首批策略 3-6 月 PnL，设计内状态）。
2. D1 ±20% 敏感性网格（11 号 §0.5.7 待完成项）——**未来工程-小型**（回测跑批）。
3. 外部信号交叉验证（5 档水温/板块轮动，§3.2.7）——文档裁远期辅助印证，等数据管线，**非当前缺口**。
4. CHMM-t/Sticky HMM/JM/Hybrid Poisson/HSMM/GAS/BOCPD——归 10 号 regime 检测器远期候选，**非本档缺口**。
5. bootstrap CI（stationary block）/James-Stein 收缩防护升级——文档已登记远期，**非缺口**。

---

## 35_drawdown_protocol_impl（回撤 Protocol）

**施工状态实证**：承诺=三层防御+Kill Switch 链路+Ghost 检测+生产接线。实证：`stop_loss.py`（`trigger_kill_switch`/`execute_kill_switch_liquidation` 15 笔秒分片/`detect_ghost_positions`）；`state_store.py`（JsonStateStore+AppendOnlyDedupSet）+`state_store_redis.py`（RedisStateStore 双后端）；`risk_layer_orchestrator.py`（MOD-L06-001，evaluate_intraday+_engage_kill_switch+LiquidityRecoveryState）；`drawdown_tracker`/`capital_curve_manager`/`drawdown_controller`/`daily_auditor` 全 production。与结案报告两波施工一致。

**结案报告动作**：**补正**——原"Redis 后端未做"已过时，标记 ✅ 已闭环（2026-08-17 AI-REDIS-001，merge e9d49313），并点名其余未做项按 §6 优先级属设计内延期。

**未施工清单+裁定**：
1. DrawdownStateMachine 持久化状态机+§3.20 hysteresis 完整算法+毕业准则（§6.6 P1）——**未来工程-小型**（单模块+持久化+测试，单批可闭环；state_store 原语已就位）。
2. Kill Switch 4 层 L2/L3（§6.11）：L2 broker 端 bracket——**外部依赖**（miniQMT 能力待确认）；L3 看门狗独立进程——**未来工程-大型**（新基础设施）。
3. 盘前初始化+盘后持久化配对编排（§3.15/§3.18，含 entry_var 持久化/mark_persistable）——**未来工程-小型**（编排层函数级，state_store 已有）。
4. RiskOrchestrator 日度编排+§3.10 校准动作接入（与 36 号同项）——**未来工程-小型**（接线）。
5. 回撤类型诊断+归因自动化（§6.7/§6.13，复用 daily_auditor AttributionBias）——**未来工程-小型**。
6. 连续 5 天亏损降仓 50%（§6.2）——**未来工程-小型**。
7. 强制休息 5 天自动计时（§6.1）——**未来工程-小型**（配置级）。
8. 全清超时告警+撤单率预检（§6.14）——**未来工程-小型**。
9. static 破产底线触发源（§6.15）——**未来工程-小型**。
10. 前端回撤/Kill Switch 面板——**未来工程-小型~中**（前端组件）。
11. §7 ㉓ 15% EMERGENCY 是否触发 Kill Switch——**等 Owner 裁决**（跨 4 真源口径统一）。
12. §6.16-§6.37 远期登记（MPC/趋势跟踪/CDaR/BOCD/Conformal/RWC/MFCCA/RRP 等）——文档已裁 P2-P5，**非缺口**。
13. ~~周/月两级亏损限额~~——**实证已落**（`ashare_stop_loss_engine.py` weekly 5%/monthly 10% 配置+检查在 L528/L535；非 memo 设想的 trading_kill_switch 扩展路径，但实质等效，登记备查）。

---

## 36_var_es_monitoring（VaR/ES 监控）

**施工状态实证**：承诺=VaR/ES 计算+触发+回测+校准。实证：`var_calculator.py`（conservative_max+`method='lower'`+nan_dropped Fail-Closed）；`tail_risk_monitor.py`（ES method='lower'+`pot_fallback_historical`+`PotFailureCounter` 跨日持久化，AI-POT-001 已落）；`var_backtester.py`（4 法 full_report）；`fhs_engine.py`（MOD-RK-26）；`drawdown_controller.py`（5 级单调修正后）；`daily_auditor.py`（production v0.1.0，但**无 §3.11 声称的四方法**）；`risk_layer_orchestrator.py` 在位。

**结案报告动作**：**补正两处**——①FHS 引擎已施工（接线仍远期 #147）/RFIX-001 已 merge f8a14cf7；②**新发现文档漂移**：§3.11"daily_auditor v0.2.0 run_var_backtest+3 审计方法 ✅ 已施工"不实（全 src+tests+git 历史 grep 零命中，docs-only 声明）——已就地勘正 §3.11 与组件状态表，并把该未落码项补进结案报告未做清单。

**未施工清单+裁定**：
1. **§3.11 daily_auditor 集成包装层**（`run_var_backtest`→PASS/RECALIBRATE/REBUILD + `log_entry_var`/`log_baseline`/`log_recalibration`）——本次复核新发现，文档原标已施工不实。**未来工程-小型**（var_backtester 已有 full_report，包装+3 日志方法，单批可闭环）。
2. VarBreachStateMachine 落码（§3.15 设计契约，×0.8/×0.9 乘性折扣接入 evaluate()）——**未来工程-小型**（状态机+接线，随 state_store 持久化批）。
3. §3.10 校准动作执行者接入编排层（`update_config`/`enable`/`force_static_mode` 调用点）——**未来工程-小型**（接线）。
4. §3.12 盘中重算函数（`intraday_var_recalc_trigger`/`intraday_var_recalc`）——全 src 零命中，**未来工程-小型**（与 35 §3.13 同 tick 联动，随盘中编排批）。
5. backtest_store 持久化+clean/dirty P&L 双轨（§3.13/§3.18）——**未来工程-小型**。
6. entry_var 持久化链路（§3.4，随 35 §3.15/§3.18 配对施工）——**未来工程-小型**。
7. FHS 编排层接线（三触发+冷却期，tracker #147）——**未来工程-小型**。
8. 远期 9 法回测/QbSD/conformal 族/MCS/深度学习族——文档已裁 Phase 2-5，**非缺口**。

---

## 37_liquidity_crisis_protocol（流动性危机）

**施工状态实证**：承诺=检测+响应+恢复+涨跌停+IPO 预警+LEVEL_3 接线。实证：`liquidity_crisis_manager.py`（MOD-RK-21 六算法全在位）；`risk_layer_orchestrator.py` LEVEL_3 接线（systemic_detector 注入+`build_escape_directive`→`_engage_kill_switch`+降级机 check_recovery）；`akshare_provider.py` `ipo_calendar` capability（巨潮 `stock_new_ipo_cninfo`，DS-105）；`ashare_systemic_risk_detector.py`/`liquidity_monitor.py` production。与结案报告（含 v1.2.0/v1.2.1 闭环行）一致。

**结案报告动作**：已有三段式且已由 LVL3/IPO 批次更新，实证**一致，无改动**。

**未施工清单+裁定**：
1. §3.7.x 前瞻算法群（Hawkes/SaR/Latent build-up/ExsdHawkes/Cascade/Multiplex/Weng/Zhou/LRISK/欧洲 ML/AdjPIN/Kyle λ/尾部大单）——文档已裁 Phase 1.5-3 储备+重评条件，**非缺口**（激活条件未达成）。
2. 阈值实盘校准（spread 0.5%/卖压 0.65/恢复半阈值/min_hold）——**等数据**（3 个月实盘）。
3. 流动性指标接策略层（is_illiquid 反馈选股/权重）——Phase 1.5，**等实盘**。
4. BM-RC-12-B 跨市场传导模型——文档裁"登记远期+激活条件"，等跨市场数据管道，**非当前缺口**。

---

## 40_execution_broker（执行层）

**施工状态实证**：承诺=19 项决策全链。实证：§1.4 表 22 模块全部在位（MiniQmtBroker/BrokerInterface/OrderManager/FillHandler/AlgoTradingEngine/TransactionCostOptimizer/SlippageAnalyzer/OrderExecutionSaga/TradingSession/DefaultTcaEngine/PositionReconciler/MatchingLogic/OpenOrderResolver/CancelRateGuard/PricingPolicy/price_cage/AsyncFillDispatcher/TradingHaltResolver/CorporateActionAdjuster/board_lot/ProgrammaticTradingGuard/shared_xtquant_conn）；`RejectionAction`/`classify_rejection` 在 order_manager.py。与结案报告一致。

**结案报告动作**：**补正**——原"无本科目未做项"补充 §6.1 三项按既定 Phase 暂缓的实证状态（gap 4 日志态/gap 10 Phase 2/gap 16 Phase 1.5）。

**未施工清单+裁定**：
1. gap 4 拒单分类 RETRY_ONCE/ALERT_FREEZE/ALERT_RECONCILE 实际动作（待 OrderExecutionSaga 接管）——**未来工程-小型**。
2. gap 10 盘后全量对账（券商对账单三方核对，Phase 2）——**未来工程-小型~中**。
3. gap 16 盘后固定价格交易通道（Phase 1.5 可选）——**未来工程-小型**。
4. Phase 1.5/2 候选（TWAP 随机化/VWAP 在线纠偏/POV 补偿/IS 完整 AC QP/delay cost 分桶/OBI/regime-aware 选算法/冲击分离/集合竞价/RL/MPC/限价单三件套）——文档已裁 Phase+触发条件，**非缺口**。
5. §6.2 "9 模块 depgraph 未登记"——2026-08-19 AI-NIGHT-001 阶段0 已全量刷新 depgraph（964 模块），**推断已闭环**（建议统筹核验后销项）。

---

## 41_buy_flow（买入流）

**施工状态实证**：承诺=分批建仓+突破失败+时序+锚定+资金协同+T+1+扳机清单+明日预案。实证：`batched_position_builder.py`（MOD-PA-006 六算法+`gate_batch_order` 纪律闸接线）；`trigger_registry.py`（MOD-TRIG-001，`TriggerEntry`+15 条 MVP 清单含 RISK_KILL_SWITCH/BUY_BATCH2_RELEASE）；`plan_engine/`（MOD-PLAN-001/002/003，TomorrowBoundary/ConstraintState/BoundedActionAdvice）。与结案报告一致。

**结案报告动作**：已有 2026-08-16 三段式（含 REGF-001 两项闭环行），实证**一致，无改动**。

**未施工清单+裁定**：
1. BM-BUY-01 多情景对策生成——文档裁暂缓（8 态预测被 90 §7 暂缓连带），**等触发条件**。
2. BM-BUY-02-B 数据驱动轨——文档裁暂缓（信号工厂未建），**等触发条件**。
3. 独立 DO 决策编排器——文档裁**不建**（TriggerList+硬边界承载），**非缺口**。
4. BM-BUY-02-A-2 因子直通裁决——文档裁**不建设**（架构冲突），**非缺口**。
5. 首仓比例/执行时点/Make-or-Take 超时/窗口阈值校准——**等数据**（G04 策略定稿+实盘）。
6. 阶段 4-7（盘中实时分散/TWAP-VWAP 拆单/ML 加仓/执行 RL/MPC）——文档已裁远期，**非缺口**。

---

## 42_sell_flow（卖出流）

**施工状态实证**：承诺=MVP 四族（止损/止盈/破位/猎杀防护）+执行编排。实证：`position_triage.py`（MOD-SELL-000）、`stop_loss_strategy.py`（MOD-SELL-005，compute_stop_loss+check_time_stop）、`take_profit_strategy.py`（MOD-SELL-004）、`sell_execution_planner.py`（MOD-SELL-019，schedule_sell_order+rank_limit_down+rank_kill_switch）全在位；7 个既有生产模块（003/001/007/009/008/015/006）在位。MOD-SELL-014/017 无实现文件（与结案报告"MVP 不施工"一致）。

**结案报告动作**：已有 2026-08-16 三段式，实证**一致，无改动**。

**未施工清单+裁定**：
1. MOD-SELL-014 策略止损范式——CAND-SELL-001 已登记（触发=G04 校准+连续小亏证据），**未来工程-小型**。
2. MOD-SELL-017 分批退出——同登记（`simple_scaling_out` 三步法可作 80/20 过渡），**未来工程-小型**。
3. TradeLevelCircuitBreaker 交易级熔断——Phase 2 候选（~30 行类），**未来工程-小型**。
4. G04 参数校准（ATR 倍数/移动止损/时间止损差异化）——**等数据**。
5. 密度感知止损/止盈——**未来工程-大型**（依赖 BM-SEL-13 密度 PDF）。
6. 退潮信号 L2-B 注入权重——**等 28 号**（数据/参数）。
7. BM-SELL-09 卖出闭环优化（E-SELL-04 反馈，挂 55 号复盘编排）——**未来工程-小型~中**。
8. Watch 秒级扫描——**等实时风控**。
9. MOD-SELL-008 deprecated 三方分裂真源裁决——**等 Owner 裁定**。
10. risk 域 default_stop_loss_engine 替换/并存关系——**未来工程-小型**（倾向并存，施工时确认）。

---

## 43_compliance_discipline（合规纪律）

**施工状态实证**：承诺=五环节+运行时装配。实证：7 模块全在位（discipline_must_do_checker/discipline_prohibition_checker/license_usage_auditor/hard_boundary_adjudicator/trading_compliance_detector/compliance_report_registry/compliance_log）；装配实证——`trading_session._validate_and_submit` 四道合规闸（MOD-CMP-001/002/007 注入+成对注入 fail-fast）；`order_manager._check_compliance_gates`（ReportGate+日申报读数检查，`ComplianceGateBlockError`）；`batched_position_builder.gate_batch_order`；`cancel_rate_guard` 日申报硬计数器（5000 预警/10000 阻断，报单+撤单双计）。与结案报告一致。

**结案报告动作**：已有 2026-08-16 三段式，实证**一致，无改动**。

**未施工清单+裁定**：
1. 47 项功能裁定清单全量迁移——源文档不在仓（#77），**阻塞：等用户补供源文档**（当前 19 条有据种子已登记）。
2. Spoofing/Layering/WashTrade 盘中实时检测——detector 已建，需盘中实时流驱动，**未来工程-小型~中**（接实时流批次）。
3. MVP 阈值实盘校准（追高 +2%/骄傲 5 笔×1.5）——**等数据**（C1 实盘误拦截率）。
4. 单日申报笔数填报值 2000 笔/日校准——**等数据**（实盘首月统计）。

---

## 50_backtest_observability_workplan（回测可观测性）

**施工状态实证**：承诺=M1 包+C1 接入（✅）+ M2 Panel Tab+mlflow 退役（✅ 经 51 号）。实证：`experiment_tracking` 包 8 文件在位；`c1_runner.py` lazy import `track_c1_result` 接线在位；全 src `import mlflow|_MLflowBackend` 零命中；app_panel 11 Tab；`download_artifact`/`download_artifact_text` 在位；`test_experiment_history.py` 在位。

**结案报告动作**：**插入三段式结案报告**（frontmatter 后）。

**未施工清单+裁定**：
1. §3 ⑥ 其余五零件接入（regime_detector/feature_builder/vectorized_engine/StrategyRunner/C2C3+lineage）——`adapters/` 仅 c1_adapter 一个（实证）。**未来工程-小型**（逐零件 adapter，预估 ~1.5 天，单批可闭环）。
2. §3 ⑤ 历史结果回灌评估——**未来工程-小型**（评估动作，随 51 号收口一并）。
3. §3 ⑦ 治理登记收尾（07_d_infra_telemetry.md 措辞同步/creation_token/blueprint 单一 JSON 后端同步）——**未来工程-小型**（文档级，随治理批顺手）。

---

## 51_panel_experiment_history_mlflow_retirement（Panel Tab+MLflow 退役）

**施工状态实证**：承诺=A/B/C 三工作流。实证全部兑现（见 50 号实证）；另头部"状态：待施工"行已同步更正为"已施工"。

**结案报告动作**：**插入三段式结案报告**（frontmatter 后）+ 修正头部状态行（待施工→已施工）。

**未施工清单+裁定**：
1. PNG 退役（`_render_nav_png` 仍在 c1_adapter.py L132/L190）——§七.P2-10 条件 3 用户确认未达成，**等 Owner 确认后删除**（函数级）。
2. 前端 C4 Container Diagram 登记（第 11 个 Container）——**未来工程-小型**（文档级）。
3. §九 BM-RES-02-B 可复现性契约（repro_manifest.json）/BM-RES-02-C 实验异常检测（PSI+CUSUM+阈值表）——2026-08-12 补登设计裁定，**未来工程-小型**（契约级，重评=日均 run≥50）。
4. §八 后续增强（DTW/PBO 九门禁/curve_smoothness/DuckDB/Panel Live Server/社区 HoloViz MCP）——文档已裁"登记不做/MVP 不做"+触发条件，**非缺口**。

---

## 汇总

### 15 篇一行结论

| # | memo | 结论 |
|---|---|---|
| 29 | factor_strategy_extraction | 入库承诺 140/146/110 实证一致；结案报告已有无需动；未施工=因子量化落码（大型） |
| 30 | multi_strategy_concurrency | 四模块全 production 实证一致；插入结案报告+修 481→548；未施工 4 项（3 小+1 等裁定） |
| 31 | position_sizing | 实证一致；结案报告无改动；未施工 4 项（3 小+1 大 C10） |
| 32 | firm_risk_aggregator | 实证一致；结案报告无改动；未施工 5 项（全小型，行业偏离裁剪等 D-FACTOR） |
| 33 | budget_change_handler | 实证一致；补复核注记；未施工 2 项 actionable（事件链接线/on_firm_violation，均小型）+4 项设计内暂缓 |
| 34 | regime_meta_allocator | 实证一致；结案报告无改动；未施工=参数校准（等数据）+D1 网格（小型） |
| 35 | drawdown_protocol_impl | 实证一致；补正 Redis 已闭环；未施工 11 项 actionable（9 小+1 大 L3+1 外部依赖 L2）+1 等裁决 |
| 36 | var_es_monitoring | 实证基本一致；补正 RFIX/FHS+**新发现 §3.11 文档漂移并勘正**；未施工 7 项（全小型） |
| 37 | liquidity_crisis_protocol | 实证一致；结案报告无改动；未施工=前瞻算法储备群（非缺口）+校准（等数据） |
| 40 | execution_broker | 实证一致；补正 §6.1 三项；未施工 3 项（全小型） |
| 41 | buy_flow | 实证一致；结案报告无改动；未施工 2 项等触发+校准等数据 |
| 42 | sell_flow | 实证一致；结案报告无改动；未施工 6 项 actionable（5 小+1 大密度感知）+2 等裁定+校准等数据 |
| 43 | compliance_discipline | 实证一致；结案报告无改动；未施工 2 项 actionable（1 阻塞等源文档+1 小型）+校准等数据 |
| 50 | backtest_observability_workplan | M1/M2 实证兑现；插入结案报告；未施工 3 项（全小型） |
| 51 | panel_experiment_history_mlflow_retirement | 三工作流实证兑现；插入结案报告+修状态行；未施工 3 项（全小型）+PNG 等确认 |

### 未施工内容条数与裁定分布

- **actionable 未施工条目合计 47 条**（不含"等数据/等触发/等裁定/非缺口"标注项）：
  - **未来工程-小型：41 条**（函数级/配置级/小模块/装配接线，单批可闭环）
  - **未来工程-大型：4 条**（29 因子量化落码+IC 回填；31 C10 偏度/峰度（依赖 BM-SEL-13）；42 密度感知止损止盈（依赖 BM-SEL-13）；35 L3 看门狗独立进程）
  - **过度工程：0 条**（各 memo 自身已含过度工程审查，远期项均按 Phase/重评条件登记，无违反 charter §2/§4 的新增承诺）
  - **外部依赖/阻塞：2 条**（43 #77 源文档待用户补供；35 L2 broker bracket 待 miniQMT 能力确认）
- **等 Owner 裁决：5 项**（30 §6.9 旧体系退役；35 §7㉓ 15% EMERGENCY 口径；42 MOD-SELL-008 真源；51 PNG 删除确认；40 §6.2 depgraph 登记建议统筹核验销项）
- **等数据/等触发（非工程缺口）：12 项**（校准类：31/33/34/36/37/40/41/42/43 阈值与窗口校准；41 BM-BUY-01/02-B 触发条件；42 退潮权重/28 号）

### 本次复核新发现（超出既有登记）

1. **36 号 §3.11 文档漂移**（重要）："daily_auditor v0.2.0 `run_var_backtest`+3 审计日志方法 ✅ 已施工"为 docs-only 不实声明——全 src+tests+git 历史 grep 零命中，方法从未存在。已就地勘正 §3.11 标注与组件状态表，并补入结案报告未做清单（裁定=未来工程-小型）。建议统筹登记跟踪（本包不改 tracker）。
2. 30 号 §2.4 "481 行"漂移（遗留 #36 实证项）已就地更正为 548 行。
3. 51 号头部"状态：待施工"行已更正为"已施工"。

### 阻塞

无硬阻塞。两项外部依赖：43 号 47 项裁定源文档待用户补供（#77）；35 号 L2 broker bracket 待 miniQMT 能力确认。
