---
ttl: task_bound
---

> **⚠ 保留依据（防删声明，任何清理会话必读）**：**建议【保留，且已入 git 追踪】**。①本文档是"剩余未施工项"唯一总账与施工波次派单真源（A 类 22 项/B 类 21 项/C 类 10 项/GP1+ 13 项逐项含出处锚点+代码实证），删除即丢失后续施工排期依据；②对齐前端缺口总账同规（2026-08-22-frontend-backend-gap-ledger.md 防删先例）；③根本保护=git 追踪（建成即提交，_working 已有 62+ 份 md 在 git，本账不在 ignore 名单）。
>
> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=register · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-28 · topic=remaining_construction_roadmap · scope=07_trading_decision_architecture + 09_ai_architecture · completes_when=全部 A/B 类项施工闭环或转裁定后归档（归档不删除，保留审计链）。

# 剩余施工项全量清单与施工顺序路线图

> **用途**：2026-08-28 全量审查批（85 篇设计文档 × 代码实证，4 路核查）发现的全部"未施工/施工一部分"项的统一登记、施工必要性裁定与施工顺序派单真源。
> **真源分工**：本文档 = **施工排期真源**；[construction_progress_tracker.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md) = 施工执行/遗留登记真源（其 §六 56 条未闭环项按 Owner 裁定**引用不复制**，见 §三）。
> **关联**：[92_phase2_business_construction_order.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md)（阶段二清单，已结案）、[18_gp0_construction_order.md](../02_enterprise_architecture/09_ai_architecture/implementation_plans/18_gp0_construction_order.md)（GP0 清单，已结案）——本文档是两者的继任派单。
> **Owner 两项裁定（2026-08-28）**：①tracker 56 条引用不复制（防双真源）；②09 域 GP1+ 单列分期区不排当前波次（等 GP0 终审 M0 后单独开 GP1 排期批）。
> **防误删**：本文档建成即入 git 追踪（事故 #49 教训：_working 未追踪文件曾被 reconciler 误删不可恢复）。

## 一、施工必要性裁定总表

> 三分类口径：**A 类** = 需要施工且无外部阻塞，可立即排期；**B 类** = 需要施工但被外部条件阻塞（等数据/等实盘/等 Owner/等外部账户），触发条件达成即转 A 类；**C 类** = 已裁定暂缓/不施工/远期登记，不排期仅登记。

### A 类：可立即排期（22 项）

| # | 缺口 | 出处文档 | 缺口内容 | 代码实证 | 建议波次 |
|---|---|---|---|---|---|
| ◐ A1 | B4 S2 翻 true 收尾重验（校准专项施工中） | [13号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/13_regime_phase3_engineering_plan.md) / [14号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md) | ⚠️ 2026-08-28 重验 0/3（三层致死根因调查落盘 reports/2026-08-28-s2-calibration-investigation.md）→ **2026-08-29 治本施工（AI-WAVE4-001，Owner 四裁定）**：①capitulation 参数化四层（base_mode A1分位/A2平静窗 × wick_mode B1/B2 × vol_filter × agg_mode C1衰减峰值/C3簇计数，默认 legacy 不破坏现状，126 用例绿）；②three_yang v2_index（d5 30%→15% 指数口径+删 d4 误抄维+分级重构）；③路 A index_valuation_daily 管道四件套（中证主源+真 CAPE+接线降级路 B）。残余=walk-forward 选型验证（§4.4 六层栈）→dump_s2_scores 复跑→B4 design_match 翻 true（须 Owner 确认） | overlay_features.py 五函数+keys_or_gte 已在位 | 校准专项（波 4 已施工，验证待跑） |
| ~~A2~~ | ~~打板三符号+PIT 注入~~ ✅ 已完工（2026-08-28 波 2a，AI-WAVE2A-001，commit 待统筹统一提交） | [24号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/24_daban_strategy_detail.md) | ~~DabanExecutionAlgorithm / DabanTimingDecision / DynamicCapacityCalculator 三符号零命中；DabanPITBacktestFramework 骨架态未注入~~ → 三符号落码 `ex_core/daban_execution.py`（23 用例）；`from_db_session` 真依赖注入（+5 用例）；两轮全绿零回归 | ex_core/daban_*.py 七文件在位 | ~~波 2~~ 已闭环 |
| ~~A3~~ | ~~板块资金性质聚合+多周期动量~~ ✅ 已完工（2026-08-28 波 2b，AI-WAVE2B-001，D1 查重命中——前序 fff6ea6bfc 已落码，零新增源码） | [22号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md) | ~~零命中~~ → 既有实证：sector_breadth.py（aggregate_capital_nature_to_sector+capital_nature_multiplier，37 用例）+sector_momentum.py（multi_tf_momentum 0.4×q20+0.3×q5+0.3×q3，15 用例，已被 sector_report_builder 消费）；本波=实证核验 2 轮 52+2395 全绿+治理补登（4 token+4 中文名）+22 号 v1.9.9 纠偏 | 同上 | ~~波 2~~ 已闭环 |
| ~~A4~~ | ~~回测四核心模块零单测~~ ✅ 已完工（2026-08-28 波 2c，AI-WAVE2C-001） | [52号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/52_backtest_framework_docking.md) | ~~零直接单测~~ → tests/backtest/ 新建 4 文件 118 用例（engine_base 14/matching_logic 41 黄金数/portfolio 31 含 T+1 锁定/metrics 32），纯内存合成夹具；两轮 118 passed+全套件 952 零回归 | 同上 | ~~波 2~~ 已闭环 |
| ~~A5~~ | ~~事件漏斗 BM-SEL-19~~ ✅ 已完工（2026-08-28 波 3，AI-WAVE3A-001） | [26号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md) | ~~零命中~~ → intelligence/event_funnel.py 新建（MOD-INT_EVENT_FUNNEL：候选池合并去重→四重门控→评分降序→容量截断，评分全委托 compute_event_score 零重造）；33 用例三轮全绿+614 零回归。**重要发现**：MOD-SIG-049（signal_ashare/event_driven_screener.py）已存在——21 号 A 股域骨架与 26 号漏斗平行承载 BM-SEL-19，归并裁定转架构议题（遗留登记） | 同上 | ~~波 3~~ 已闭环 |
| A6 | GAP-2 常驻服务化 | [57号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/57_daily_cycle_sop.md) | ◐ 部分闭环（2026-08-28 波 3b，AI-WAVE3B-001，commit 待统筹统一提交）：LiveStrategyAdapter 库级件已落码 `ex_core/live_strategy_adapter.py`（多 slot 承载/异常隔离/biz 心跳/退避重启熔断，19 用例两轮全绿）——残余=CLI/调度接线（assemble_session 包 slot 常驻）+deadman_switch 第四路扩展（后续批/Owner 窗口） | start_paper_session.py 已在位 | 波 3 |
| ◐ A7 | 日历扩展消费点注入改造 | [94号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md) | ◐ 首批已注入（2026-08-29 波 4，AI-WAVE4-001，commit fd792ddb）：backfill_checker/tick_subscriber/daban_pit_safety/event_score/intraday_main + policies.yaml 改走 data/calendar 包；**残余**：清单复核收尾（代理回报丢失，待盘点注入覆盖率） | data/calendar/ 包已在位；消费点清单 docs/_working/reports/2026-08-26-calendar-consumers-inventory.md | 波 4 首批已闭环，残余盘点 |
| ~~A8~~ | ~~盘中实时操纵检测~~ ✅ 已完工（2026-08-28 波 3，AI-WAVE3C-001） | [43号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/43_compliance_discipline.md) | ~~实时流驱动未接~~ → MOD-CMP-018 manipulation_realtime_monitor 落地：OrderManager 委托/成交事件流挂接+RedisTickMarketProvider tick 流供给+4 类检测（Spoofing/Layering/WashTrade/拉抬打压）+告警冻结分发+C-002 第三道闸抛转；31 新用例+1503 两轮全绿 | 同上 | ~~波 3~~ 已闭环 |
| ◐ A9 | 绩效归因全链+元级迭代 | [54号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/54_reconciliation_attribution.md) | ✅ BM-REC-02-B 已闭环（2026-08-29 波 4，AI-WAVE4-001，commit c5628ff6）：MOD-RPT-036 归因计算（Brinson/Carino/T+1）+ MOD-RPT-037 落库查询（34 用例+728 关联域绿）；**残余**：BM-REC-03-D 元级迭代（依赖 A10 mSPRT 通道）+ 双实现收敛裁定（54号 §6，Owner 窗口） | SettlementReconciler/PositionReconciler/DailyAuditor 已在位 | 波 4 已闭环（02-B 部分） |
| ◐ A10 | 生命周期治理编排层 | [61号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) | ◐ 编排层已落码（2026-08-29 波 4，AI-WAVE4-001，commit c9d0b346）：drift_observatory_orchestrator（四层编排）+ msprt_promotion_channel + factor_promotion_wiring（[MATURITY] testing，B-007 新件封顶）；**残余**：production 启用待 Owner 审批（同 B5/B6 通道） | lifecycle_governance 五件 production 已在位 | 波 4 已闭环（落码），启用待批 |
| ◐ A11 | Panel 作战室前端页（P1 已完工，P2/P3 占位） | [45号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/45_warroom_playbook.md) | ✅ P1（2026-08-29 波 4，AI-WAVE4-001）：作战室 Tab 居首位（13→14）——前日预案区/实时走势分析区/今日→明日惯性区/IDX-02 四指数卡（B21 搭车）+缺口⑥~⑩ P2/P3 折叠占位；components/warroom.py 新建 15 用例；残余=P2（9格概率完整版/批量边界/相关性净额/禁做清单）+P3 辩论实例化 | daily_warroom_pipeline 已随 B5 转 production +dashboard_feeds W5 已在位 | ~~波 4~~ P1 已闭环 |
| A12 | 回撤延期项清偿 | [35号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md) | §6 P0-P4 登记延期：DrawdownStateMachine 持久化 / L2·L3 兜底 / 回撤归因自动化 | drawdown_tracker/controller 已在位 | 波 5 |
| A13 | BudgetChange 接线尾巴 | [33号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/33_budget_change_handler.md) | TierState 跨日持久化 / E-POS-40/41 事件 / 生产调用方接线（sync_from_allocator 适配器已备） | budget_change_handler.py 已在位 | 波 5 |
| A14 | 执行层 Phase 2 项 | [40号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/40_execution_broker.md) | 拒单分类实际动作 Saga 接管 / 盘后全量对账 Phase 2 / 盘后固定价格交易 | order_manager/saga/cancel_rate_guard 已在位 | 波 5 |
| A15 | 监控暂缓项复评 | [55号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/55_monitoring_review.md) | Email/WeChat sender 实发 / miniQMT 链路探针 / 偏离归因分解 H-A~D / 模板引擎固化（暂缓带重评条件，先复评再定施工面） | MOD-RK-23/MOD-RPT-009/threshold_loader 已在位 | 波 5 |
| A16 | CPCV+PBO 过拟合增强 | [52号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/52_backtest_framework_docking.md) | CPCV+PBO 设计内延期（过拟合检测增强） | deflated_sharpe/overfitting_adjudicator 已在位 | 波 5 |
| ~~A17~~ | ~~Q8 parts>100 告警~~ ✅ 已完工（2026-08-28 波 0，AI-WAVE0-001） | [64号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/64_data_source_download_spec.md) | ~~零命中~~ → 实证监控主体 ch_parts_monitor.py 已于 08-20 在位，真尾巴=阈值 100 硬编码；本波=THD-HEALTH-005 入注册表（v1.3.0）+fail-closed 统读接线+4 新用例+一致性守卫 35→36，两轮 102 passed | 同上 | ~~波 0~~ 已闭环 |
| ~~A18~~ | ~~8 态预测口径回切~~ ✅ 已完工（2026-08-28 波 0，AI-WAVE0-001） | [90号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md) | ~~口径矛盾~~ → 90 号 v2.1.0 六处回切：预测模块（MOD-SIG-037 只出概率分布）登记为既有模块，暂缓对象收敛为 8 态→决策消费链，历史裁定原文全保留 | 同上 | ~~波 0~~ 已闭环 |
| ~~A19~~ | ~~CAND-CRYPTO-007 翻 promoted~~ ✅ 已完工（2026-08-28 波 0 实证已闭环，零改动） | [94号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md) | ~~仍 candidate~~ → 实证条目已 promoted（promoted_to 指向三件套，2026-08-28 已落），任务背景为旧快照 | 同上 | ~~波 0~~ 已闭环 |
| ~~A20~~ | ~~回测历史回灌评估~~ ✅ 已完工（2026-08-28 波 0，AI-WAVE0-001） | [50号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/50_backtest_observability_workplan.md) | ~~小遗留~~ → 评估落盘 docs/_working/reports/2026-08-28-backfill-evaluation.md，结论=**按需回灌（当前不回灌）**：唯一候选源知识已由 md 承载、无批量积压、与 51 号口径一致；附触发条件与实现要点 | 同上 | ~~波 0~~ 已闭环 |
| ~~A21~~ | ~~task_board 死信标签联动~~ ✅ 已完工（2026-08-28 波 0，AI-WAVE0-001） | [66号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md) | ~~P1~~ → tag_dead_letter 函数抽出+commit_queue 死信分支接入（meta.task_id 存在时打标，不存在/不可达宁漏不阻断）+5 新用例，两轮 108 passed；66 号回填闭环标注 | 同上 | ~~波 0~~ 已闭环 |
| A22 | 期指 tick 采集+A50 数据源评估 | [44号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md) | 期货分钟/tick 采集 symbols 未配置（配置即施工）；A50 通道数据源评估落地（日韩已裁定砍） | 期指日频/ES/NQ 通道已在位 | 波 3 |

### B 类：外部条件阻塞（触发即转 A 类，21 项）

| # | 缺口 | 出处文档 | 阻塞条件 |
|---|---|---|---|
| B1 | 策略级相关矩阵 pipeline/Neff/情绪分层/CUSUM-PSI 漂移监控 | [23号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/23_strategy_correlation_validation.md) | **首批策略回测序列**（回测跑批产出 PnL 序列后转 A） |
| B2 | G04 参数校准（42 号 ATR/止损/熔断 N=2/3 + 24 号时间止损口径统一 + convergence_window + 34 号 RegimeMetaAllocator 参数） | [20号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/20_first_batch_strategies.md) / 42/24/34 号 | **首批策略实盘 PnL（3-6 个月 track record）** |
| B3 | 因子 IC 实证回填（factor_registry ic: null） | [62号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/62_business_registry_construction.md) | 回测跑批产出 IC |
| B4 | 第二批次策略（价值反转/动量趋势） | [27号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/27_second_batch_strategies.md) | 首批 track record ≥3 个月（主动暂缓，非烂尾） |
| B5 | 44 号 M1/M2/M3 模块群 production 启用 | [44号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md) | **Owner 审批**（宪章 B-007 testing 封顶分期） |
| B6 | recon_runner production 启用 | [56号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/56_backtest_vs_sim_reconciliation_plan.md) | **Owner 审批** |
| B7 | RUN-05 真实断网断电断点恢复演练 | [57号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/57_daily_cycle_sop.md) | **Owner 窗口**（真实演练需在场） |
| B8 | CAND-CRYPTO-003 情绪面板/010 宏观面板 | [94号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md) | 外部账户与信源（Cloudflare 账户等）；注：004/008/009 骨架 2026-08-28 已在飞落码（AI-CAL-001 持有，594dfe9f/f55e4193/12345a31），004 实现继续推进中 |
| B9 | 47 项功能裁定清单全量迁移 | [43号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/43_compliance_discipline.md) | 源文档（合规架构.md §10 等不在仓内，**Owner 补供**） |
| B10 | P-1~P-5 五项待人拍板 | [90号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md) | **Owner 裁定** |
| B11 | Q1/Q3/Q4/Q6/Q8 待人决策 | [63号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/63_data_utilization_audit.md) | **Owner 裁定** |
| B12 | RWC 变体/conformal 五变体栈收敛 | [91号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md) | 90 号 P-2 裁定（挂 B10） |
| B13 | 机构级 regime 维度（credit_spread/COT/IV/Margin Debt/CAPE 路 A/PageRank） | [10号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) | 数据源（daily_valuation 管道等） |
| B14 | 选股 6 维权重 IC 校准 | [21号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md) | 实盘数据 |
| B15 | 情绪周期定位器准确率评估 | [28号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md) | 实盘数据 |
| B16 | 外部 Feed 事件因子（dReport/Jump on PEAD） | [26号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md) | 外部 Feed 接入（iFind 已裁定不续费，源待选） |
| B17 | 三套自治等级标尺统一（09 域 Q3） | [15号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md) | **Owner 裁定**（GP 排期联动） |
| B18 | 模块工厂 Phase 0→1 / U7 业务 Agent 细化（09 域 Q1/Q2） | [13号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/13_module_factory.md) / [14号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md) | **Owner 裁定**（前置已就绪，转 GP 排期） |
| B19 | 灰度+影子部署 BM-MT-02-A/B | [61号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) | 策略上线后 |
| B20 | recon_runner L3 期初持仓快照数据源 | [56号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/56_backtest_vs_sim_reconciliation_plan.md) | 57 号文窗口项（日循环跑通后定） |
| B21 | IDX-02 前端接入（架构审查尾巴） | [架构审查](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/architecture_review_2026_08_module_upgrade_audit.md) | 已移交前端会话（D6 裁定有主），随 A11 前端批一并排 |

### C 类：已裁定暂缓/不施工/远期登记（10 项，不排期）

| # | 项 | 出处文档 | 裁定依据 |
|---|---|---|---|
| C1 | 量子神经网络（quantum QNN） | [91号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md) | Owner 裁定过度工程不施工（注意：分位数 QNN qnn_two_stage.py 已 production，是另一物） |
| C2 | 晋级迁移 FSM | [53号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md) | Owner 裁定方案 C 不做（只做降级机不做晋级机） |
| C3 | 轨 A/轨 B 合流 | [15号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/15_data_feature_layer_spec.md) | 既定裁定不做 |
| C4 | 信号工厂九子阶段+聚合器 | [21号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md) | 裁定远期不施工 |
| C5 | regime §9 备查升级路径（HSMM/Student-t 等） | [10号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md) | 维持不施工裁定 |
| C6 | lead-lag network/ML 转折点 | [22号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md) | 远期登记 |
| C7 | 打板 Phase 5 / 多因子 Phase 4.x / 事件 Hawkes/Janus-Q ML 栈 | 24/25/26 号 | 远期登记 |
| C8 | 回测前置检查器 BM-BT-02-D | [15号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/15_data_feature_layer_spec.md) | 暂缓条件未触发 |
| C9 | 南向季度快照 | [19号](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/19_northbound_hold_snapshot.md) | §8/§9 裁定不采集 |
| C10 | 举报人机制 | [16号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/16_ai_security_ops.md) | 远期 P4 |

## 二、09 域 GP1+ 分期区（Owner 裁定：单列，不排当前波次）

> 触发条件：**GP0 终审 M0 后单独开 GP1 排期批**（M0 已宣布 Owner 终审通过，GP1 进入条件 I1-1~I1-3 见 [17号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/17_phase_roadmap.md) §4.3）。其中 Q1/Q3 待人裁项先走 Owner 窗口（已列入 B17/B18）。

| # | 项 | 出处文档 | 内容 |
|---|---|---|---|
| G1 | AutoRuntime 容量升级 12 项 GAP + boot watchdog NoneType（#255） | [04号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/04_autoruntime_core_build.md) | 触发式施工 |
| G2 | intelligence_governance __init__.py 入口腐烂修复 | [05号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/05_intelligence_governance_consolidation.md) | Q1 待裁（16 个不存在名字+漏列 5 个实存模块） |
| G3 | 画像→考试→护照→门控端到端自动闭环 | [06号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/06_model_profiling_pipeline.md) | 手动链路已 5/5 PASS，自动化属 GP1 |
| G4 | inject 生产空段/llm_summary 压缩档/InProcessContextEngine | [07号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/07_context_engine_build.md) | CE 收口已完成，生产接线属 GP1 |
| G5 | commit_queue dead 40+ 死信积压清理 | [08号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/08_multi_ai_concurrency_governance.md) | 运维观察项（可随时清，不等 GP1） |
| G6 | LSG 层内 20%（L3B 沙箱/Threat Intel/PerformanceGuard/CI workflow）+ v2.0.0 signal_bus | [09号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/09_llm_security_integration.md) | GP1+/蓝图侧 |
| G7 | 预算硬门/路由级联/MCP 动态发现/模型注册 SSoT 裁定 | [10号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/10_llm_infrastructure.md) | GP1 |
| G8 | 技能库自动生成（AutoSkill+Voyager）/模型路由编排器 | [11号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md) | GP1+ |
| G9 | L2/L3 反思/PreFlect 消费接线/涌现告警介入/投票壳消费 | [12号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md) | GP1+ |
| G10 | 模块工厂自动分类器/映射引擎/受控生成通道/自动化采集 | [13号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/13_module_factory.md) | Phase 1+，挂 B18 裁定 |
| G11 | 执行层 Phase 1 接 11/12/13 正式接口/U7 业务 Agent 细化 | [14号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md) | GP1+，挂 B18 裁定 |
| G12 | Agentic Drift 行为基线/ARS 双轨/自治标尺统一 | [15号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md) | GP1+，Q3 挂 B17 裁定 |
| G13 | 自愈统一管线/修复策略库落盘/A-L0~A-L4 成熟度代码 | [16号(09)](../02_enterprise_architecture/09_ai_architecture/implementation_plans/16_ai_security_ops.md) | GP1+ |

## 三、tracker 未闭环项引用区（Owner 裁定：引用不复制）

> [construction_progress_tracker.md](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md) §六 遗留项登记表现有 **56 条未闭环项**，继续在 tracker 跟踪，本文档不复制。其中与施工排期直接相关的双视角项：
> - **#261 日历扩展消费点** = 本文档 A7（同一事项：tracker 记遗留、本文档排波次）
> - **#253 DeepSeek 402 欠费** = Owner 行动项（充值），影响 44 号 M3-⑨ 主通道恢复（挂 B5 启用的前置）
> - **#112 五态降级机执行侧接线** = 待 SHADOW 阶段（53 号体系内）
> - **#127/#177 ipo_calendar CH 建表** = 待 CH 服务可达时执行（DDL 部署项）
> - **#216/#220/#221/#225/#231③** = 退役裁定/stk_limit 重算/tushare index_weight/depgraph 重生成批次，均 **Owner 窗口**
> - **#263/#264** = f18 环境卡死+tracked-drift 另案（环境治理族）
> - **#71/#75/#81** = 网关防线专项评估（AI-GIT 域）

## 四、施工顺序（波次派单）

> 排序依据：依赖关系 + 冲突面（同文件/同域不并发）+ 见效快慢。每波次内部可并行路数按并发纪律由统筹裁定。

```
波 0（登记尾巴+口径修正，1 会话可清，无代码风险）
  A17 Q8 parts 告警 → A18 8态口径回切 → A19 007 翻 promoted → A20 历史回灌评估 → A21 task_board 死信联动
        │
波 1（纯验证闭环，最快见效——E9 已落码只欠重跑）
  A1 B4 S2 翻 true 重验 + 13 号 draft→active 翻正
        │
波 2（代码施工小中件，三路可并行：ex_core 域 / signal_ashare 域 / tests 域互不重叠）
  A2 打板三符号+PIT 注入 ∥ A3 板块资金性质聚合+q3 动量 ∥ A4 回测四模块测试债
        │
波 3（中件，数据/合规/归因/执行域，两路可并行）
  A5 事件漏斗 ∥ A6 GAP-2 常驻服务 ∥ A7 日历消费点改造（与 crypto 会话协调避让）
  A8 盘中操纵检测实时流 ∥ A9 绩效归因全链 ∥ A22 期指 tick 采集+A50 评估
        │
波 4（大件，前端批可全程并行）
  A10 生命周期治理编排层（Drift Observatory+mSPRT 编排）
  A11 Panel 作战室前端页（前端批，与波 0-5 无文件冲突，可立即开工）
        │
波 5（延期登记项清偿，低优先）
  A12 回撤延期项 → A13 BudgetChange 接线 → A14 执行层 Phase 2 → A15 监控暂缓项复评 → A16 CPCV+PBO
        │
GP1 批（09 域 G1-G13，GP0 终审 M0 后单独开排期批；Q1/Q3 先走 Owner 窗口=B17/B18）
        │
B 类触发链（条件达成自动转 A 类插入对应波次）：
  回测跑批完成 → B1（相关性矩阵）+ B3（因子 IC 回填）
  首批实盘 3-6 月 → B2（G04 校准）→ B4（第二批次）+ B14/B15
  Owner 审批 → B5（44 号启用）+ B6（recon_runner 启用）+ B10/B11
  外部账户就绪 → B8（003/010 面板）
```

**关键依赖说明**：
- A9（BM-REC-03-D）依赖 A10 的 mSPRT 编排层通道——A10 排波 4 但 A9 主体（BM-REC-02-B）可在波 3 先行。
- A7（日历消费点）施工面与 crypto 战线（AI-CAL-001 在飞）有交集，派单前须查冲突登记。
- A11（前端页）与全部后端波次零文件冲突，是唯一可立即开工的大件。
- B5（44 号启用）是 A 类多项的"价值放大器"——M1/M2/M3 模块已落码但未启用，启用后盘前/盘中决策链才真正生产化，建议 Owner 尽早排审批窗口。

**校准专项（2026-08-28 波 1 实证新立项，A1 转入）**：S2 翻 true 双前置——①capitulation 过滤器/衰减参数按 14 号 §4.5 walk-forward 校准（三过滤器联玩过严，A 股暴跌日下影线比≈0 致全程 0 分；非降阈值凑分）；②路 A CAPE 分位管道（daily_valuation）建设+builder 接线。两项达成前 13 号保持 draft。排期建议：随波 3 数据域一并议。

## 五、登记纪律

1. **每推进一项**：复扫本文档更新状态（勾销 + commit hash + 日期），走 GitCommitGateway 提交。
2. **新发现缺口**：先登记进本文档（或 tracker，按 §一 真源分工）再施工，禁止口头派单。
3. **本文档防误删**：建成即入 git 追踪（事故 #49 教训）；任何会话禁止删除（对齐前端缺口总账同规）。
4. **状态流转**：B 类触发条件达成 → 转 A 类并标注转入日期；A 类完工 → 勾销并登 commit；C 类翻案 → 需 Owner 裁定留痕。
5. **复扫节奏**：每波次收尾时全量复扫一遍本文档（防内容-代码漂移，对齐 2026-08-28 审查批实证口径）。

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-28 | 1.0.0 | 初版：85 篇全量审查批产出——A 类 22 项/B 类 21 项/C 类 10 项/GP1+ 13 项全量登记+波次 0-5 派单 | Owner 指令建剩余施工项统一派单真源；两项范围裁定（tracker 引用不复制/GP1+ 单列分期区） |
| 2026-08-28 | 1.1.0 | 波 0 五项全闭环（A17-A21，A19 实证已闭环零改动/A20 结论按需回灌）；波 2a/2b 闭环（A2 三符号落码 44 新用例/A3 查重命中零新增源码）；波 1 重验未通过（0/3）→A1 转校准专项（§四 注记新立项） | 波 0-2 施工回收；波 1 真实验证结论驱动计划修正（capitulation 过严+路 A 未接线，非简单降阈值可解） |
