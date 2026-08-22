---
ttl: permanent
doc_type: architecture_view
title: 交易决策架构主题全集（总索引）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.11.13"
date: 2026-08-21
topic: trading_decision_index
scope: 07_trading_decision_architecture
---

# 交易决策架构主题全集（总索引）

> 本文档是 `07_trading_decision_architecture` 下所有"待讨论/已定稿"主题的**总索引与路线图**。
> 性质：永久态路线图，可随项目演进而修订（修订升版本号，见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §5.3）。
> 用途：用户将开启多个 AI，每个 AI 认领一个主题组 → 讨论 → 落盘 discussion/design_memo → 施工。本文档是分工的"作战地图"。
> 关联：[30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md)（多策略并发架构，已定稿 v2.5.0）｜ [10_regime_detector_spec](10_regime_detector_spec.md)（regime 完整 spec，已定稿 v1.5.1）｜ [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（regime 验证，已定稿 v1.5.2，C1 已通过 commit 852457e9）

## 0. 现有文档总目录（54 篇·按段位编号）

> 段位语义：**0x**=meta（规范与索引）｜**1x**=地基层（regime/数据特征）｜**2x**=Alpha 策略层｜**3x**=组合仓位与风控层｜**4x**=交易执行层｜**5x**=验证与可观测性层｜**6x**=跨切治理层｜**9x**=开放问题与远期愿景。
> 命名规则见 §8；新旧名对照见 §10；占用登记见 §7.3。
> **状态图例**：`active`=已定稿/已落地｜`draft`=草案/待讨论｜**骨架**=已建占位文档（frontmatter status=draft，仅含主题组信息与讨论要点清单，§2-§6 待填空；讨论定型后升 active）。
> ⚠️ **2026-08-11 git 灾难影响标注**（v2.9.0 取证确认 + v2.9.1 重建联动更新）：15/16×2/28/33/52/55/60 号曾被本索引标记为 active 高版本，但 git 历史证明高版本内容**从未提交**（未提交内容被 `git clean -fd`/`git reset --hard` 清除）——其中 **7 篇已于 2026-08-12 04:32 重建**（commit 6a4f5392：33/55/52/15/16catalog/16build_plan→active v1.0.0、27号→draft v0.2.0，依 production 代码回建）；**28号已于 2026-08-12 从 commit a3750b90d1 恢复 v1.2.0（commit 16f119bd）；60号经核查 HEAD 已是 active v1.0.0 完整版（129行，8da7513309 提交，原"骨架"标注过时）**；另 34号 测试套件（55 用例）丢失待重建。详见 §9 开放问题 #D1/#D2。本表"状态"列对齐 2026-08-12 工作树实际 frontmatter（当前有 22 路并发审查 session 正在更新各文档，版本可能再次漂移，下轮审查时重新核对）。
> 注：`AI_review_instructions.md`（22 路并发 AI 审查回填指令集，active v2.1.0）为审查操作手册，非设计备忘，不入本目录编号。
> 注：`construction_progress_tracker.md`（施工进度总跟踪表）+ `handoff_construction_coordinator.md`（统筹交接包）为施工统筹协调文件，非设计备忘，不入本目录编号（2026-08-14 自 docs/_working 迁入，防 reconciler 误删——事故 #49）。

| 文件 | 内容一句话 | 状态 |
|---|---|---|
| [00_index_trading_decision.md](00_index_trading_decision.md) | 本文档：总目录 + G01-G29 主题组路线图 + 多 AI 分工认领 | active v2.9.0 |
| [01_design_memo_management_spec.md](01_design_memo_management_spec.md) | 设计备忘管理规范（三层分治 / 命名 / 防飘移机制） | active v1.2.0 |
| [02_construction_workflow_sop.md](../../../01_policies_and_standards/sop/construction_workflow_sop.md) | 07 域施工流程 SOP——端到端 15 步施工闭环（编排层，整合 18+15 盲点+附录 A 长清单审查 12 节+附录 B 验证脚本索引+附录 C 40+ reconciler 清单）**→ 2026-08-13 迁至 docs/01_policies_and_standards/sop/construction_workflow_sop.md（SOP 属永久规则，与施工图纸临时区分离）** | active v1.4.0（已迁出本目录） |
| [10_regime_detector_spec.md](10_regime_detector_spec.md) | regime 检测器完整 spec（12 态设计真源；实现态 4 态 HMM + 3 特殊态 overlay） | active v1.5.1 |
| [11_regime_backtest_validation_plan.md](11_regime_backtest_validation_plan.md) | regime 回测验证方案（Phase 1-5 验收指南；C1 四项全通过） | active v1.5.2 |
| [12_regime_phase2_validation.md](12_regime_phase2_validation.md) | Phase 2 模型质量验证（A1/A2/B1/B4 四验证器） | active v0.2.2 |
| [13_regime_phase3_engineering_plan.md](13_regime_phase3_engineering_plan.md) | Phase 3 工程规划（降态+校准+NLP+S2/T3） | draft v0.3.2 |
| [14_regime_s2_diagnosis.md](14_regime_s2_diagnosis.md) | S2 算法错配诊断报告 | draft v0.4.5 |
| [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md) | G01 数据与特征层规范 | active v1.0.0（2026-08-12 重建 6a4f5392） |
| [16_technical_indicator_build_plan.md](16_technical_indicator_build_plan.md) | 技术指标施工计划（9周期覆盖+增量/全量调度） | active v1.0.0（2026-08-12 重建） |
| [16_technical_indicator_catalog.md](16_technical_indicator_catalog.md) | 技术指标目录（5大类指标规范：trend/momentum/volatility/volume/reversal，对齐代码真源） | active v1.0.0（2026-08-12 重建） |
| [17_special_trading_days_data_assets.md](17_special_trading_days_data_assets.md) | A股特殊交易日数据资产全景与治理（完整清单+已施工盘点+hk_trade_calendar修复#ARCH-DATA-001+治本方案#ARCH-DATA-002） | active v1.0.0 |
| [18_cold_archive_build_plan.md](18_cold_archive_build_plan.md) | 冷归档施工计划 | active v0.2.0 |
| [19_northbound_hold_snapshot.md](19_northbound_hold_snapshot.md) | 北向资金季度持仓快照 fetcher 施工计划（日频断档替代方案，tushare hk_hold 已验证） | draft v0.1.0 |
| [20_first_batch_strategies.md](20_first_batch_strategies.md) | 首批 3 策略定义（打板+多因子+事件驱动） | active v1.2.4 |
| [21_stock_selection_engine.md](21_stock_selection_engine.md) | G05 选股引擎架构 | active v1.1.18 |
| [22_sector_rotation_spec.md](22_sector_rotation_spec.md) | G06 板块轮动 spec | active v1.9.8（2026-08-21 电风扇速度计升独立因子跨文档登记，44 号 M1-⑩） |
| [23_strategy_correlation_validation.md](23_strategy_correlation_validation.md) | G07 策略间相关性验证 | active v1.7.0 |
| [24_daban_strategy_detail.md](24_daban_strategy_detail.md) | G08 打板策略细节 | active v1.10.4 |
| [25_multifactor_strategy_detail.md](25_multifactor_strategy_detail.md) | G09 多因子策略细节 | active v1.12.11 |
| [26_event_driven_strategy_detail.md](26_event_driven_strategy_detail.md) | G10 事件驱动策略细节 | active v1.8.0 |
| [27_second_batch_strategies.md](27_second_batch_strategies.md) | G11 第二批次策略（价值反转/动量趋势，暂缓） | draft v0.2.0（暂缓说明已补） |
| [28_sentiment_cycle_trading.md](28_sentiment_cycle_trading.md) | G21 情绪周期×交易决策（五阶段+定位器+regime分工+策略部署+隐形驱动验证） | active v1.2.0（2026-08-12 从 a3750b90d1 恢复，16f119bd） |
| [29_factor_strategy_extraction.md](29_factor_strategy_extraction.md) | 潘潘直播课程因子与策略提炼知识库（546 条：F1-F8 因子+S9-S16 策略，二十一轮审查收敛，factor/strategy/risk_limit 三注册表 doc_ref 真源） | active v1.0.0（2026-08-14 从 _working/潘潘直播课程 迁入） |
| [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) | 多策略并发架构总纲（Model A：独立账本+firm聚合） | active v2.5.0 |
| [31_position_sizing.md](31_position_sizing.md) | 仓位算法 spec（策略层粗仓位+firm层Kelly精裁决） | active v1.25.0 |
| [32_firm_risk_aggregator.md](32_firm_risk_aggregator.md) | G13 FirmRiskAggregator 逻辑 | active v1.0.22 |
| [33_budget_change_handler.md](33_budget_change_handler.md) | G14 BudgetChangeHandler 三级升级 | active v1.1.0（2026-08-14 AI-BGT-001 行号漂移修正+§7 四项闭环，1b8a774ad5） |
| [34_regime_meta_allocator.md](34_regime_meta_allocator.md) | G15 RegimeMetaAllocator 参数（框架 active + 代码 production v1.0.0；C1 已通过；参数待首批策略 PnL 校准） | active v2.8.1 |
| [35_drawdown_protocol_impl.md](35_drawdown_protocol_impl.md) | G16 回撤 Protocol 落地 | active v1.39.0 |
| [36_var_es_monitoring.md](36_var_es_monitoring.md) | G17 VaR/ES 与波动率监控 | active v1.11.2 |
| [37_liquidity_crisis_protocol.md](37_liquidity_crisis_protocol.md) | G18 流动性危机处理 | active v1.2.0（2026-08-17 AI-LVL3-001 LEVEL_3 生产接线完工，检测→逃生指令→Kill Switch 清算全链+降级机阶梯，c37b4b6f merge） |
| [40_execution_broker.md](40_execution_broker.md) | 执行层下单对接（19项决策+代码已施工；§2.8 盘前检查链+订单层熔断两级） | active v2.10.1 |
| [41_buy_flow.md](41_buy_flow.md) | G19 买入流 spec（含明日预案双层架构+上游四轨裁定） | active v1.7.0 |
| [42_sell_flow.md](42_sell_flow.md) | G20 卖出流 spec（MVP 已施工：Triage/止损/止盈/执行编排 4 模块） | active v1.7.1 |
| [43_compliance_discipline.md](43_compliance_discipline.md) | G30 合规与交易纪律体系（四项必做/四项严禁/信息合规/硬边界裁定/交易合规检测，D_COMPLIANCE 域设计真源） | active v1.1.0（2026-08-15 施工落地 AI-COMP-001 + 运行时装配 AI-ASM-001） |
| [44_premarket_intraday_decision_upgrade.md](44_premarket_intraday_decision_upgrade.md) | 盘前与盘中决策支持升级（M1 情绪实时分析 10 增量/M2 盘中次日预案边界修正/M3 盘前综合预判 9 增量含 LLM 盘后分析，28+41+90 号升级备忘；§9 施工算法十四件；§11 五项裁定 Owner 已批准；§12 附录 M4 日志体系+短板复核+开源评估+Tito 提取；CAND 登记因并发纪律缓办） | active v1.2.0（2026-08-21 五项裁定全批+Owner 四问批次，施工按分期排 P0 之后） |
| [45_warroom_playbook.md](45_warroom_playbook.md) | 作战手册体系（作战室）施工设计——预案/验证/执行跟踪三位一体（第一性原理五则+机构实践对标[quantamental 定位]+W0-W6+W2b 区块规格+数据契约映射+缺口⑥~⑩分期；前端改版 L15 落地件，HTML 原型 14 项自检全绿） | active v1.0.0（2026-08-22 Owner 裁定新增页） |
| [50_backtest_observability_workplan.md](50_backtest_observability_workplan.md) | 回测可观测性工作计划（六零件日志+MLflow方案调研） | draft v1.0.2 |
| [51_panel_experiment_history_mlflow_retirement.md](51_panel_experiment_history_mlflow_retirement.md) | Panel 实验历史 Tab + MLflow 退役施工计划 | active v1.2.6 |
| [52_backtest_framework_docking.md](52_backtest_framework_docking.md) | G23 回测框架对接 | active v1.0.0（2026-08-12 重建） |
| [53_simulation_live_path.md](53_simulation_live_path.md) | G24 模拟与实盘验证路径（5 态 FSM 已落码 AI-DGR-001，MOD-GOV-045 production） | active v1.7.9 |
| [54_reconciliation_attribution.md](54_reconciliation_attribution.md) | G25 对账归因 | active v1.14.0 |
| [55_monitoring_review.md](55_monitoring_review.md) | G26 监控告警与复盘 | active v1.2.0（2026-08-17 AI-THD-001 存量 9 模块阈值统读完工） |
| [56_backtest_vs_sim_reconciliation_plan.md](56_backtest_vs_sim_reconciliation_plan.md) | 回测 vs 模拟盘对账方案（P0-1②：不变量 I1-I4+三层 diff 复用+归因三分类+10 项对照清单；G1/G6 转 Owner 窗口） | active v1.0.0（2026-08-21 P0 批） |
| [57_daily_cycle_sop.md](57_daily_cycle_sop.md) | 交易日模拟盘+收盘后回测 日循环 SOP（P0-5：六环节命令清单+开盘前 QMT 人工确认项+缺口 GAP1-5+首跑彩排记录） | active v1.0.0（2026-08-21 P0 批，首跑彩排已过） |
| [60_cross_cutting_cleanup.md](60_cross_cutting_cleanup.md) | G27 冲突矩阵清理与事件总线（31条仲裁→3条firm硬上限+任务系统总线+三档节奏） | active v1.1.0 |
| [61_lifecycle_multi_ai.md](61_lifecycle_multi_ai.md) | G28 策略生命周期与多 AI 协作 | active v2.10.0 |
| [62_business_registry_construction.md](62_business_registry_construction.md) | 18业务注册表施工（registry_of_registries） | active v1.32.0 |
| [63_data_utilization_audit.md](63_data_utilization_audit.md) | 数据利用审计 | draft v2.0.0 |
| [64_data_source_download_spec.md](64_data_source_download_spec.md) | 数据源与下载体系规范（15 源/130+任务/11档调度/落库/韧性全面盘点+升级讨论载体） | active v1.4.0 |
| [65_git_safety_governance.md](65_git_safety_governance.md) | Git 安全治理体系（alias 失效修复+多层防护施工总案，Trae IDE 专用；#ARCH-AICOLLAB-001 三件套方案落 §12；wipe 治本 S1-S6+task_board 已 merge 回 dev，四证首次真实清理走通；**Phase 1 wrapper 层 7 项已全部施工**，merge 后跑安装脚本激活） | active v2.3.1 |
| [66_commit_queue_serialization.md](66_commit_queue_serialization.md) | 提交队列串行化（跨切治理层·集成基建；commit queue 三层防护方案，MVP 待排期；§2.4 #9 task_board 已按其 schema 重建 production 并 merge 回 dev） | active v1.1.0 |
| [67_merge_conflict_resolution_sop.md](../../../01_policies_and_standards/sop/merge_conflict_resolution_sop.md) | Merge 冲突处理 SOP——冲突三分法（叠加型合并/迭代型取新/互斥型升级裁定）+标准 7 步流程+5 红线，全项目冲突处理唯一真源 **→ 2026-08-13 迁至 docs/01_policies_and_standards/sop/merge_conflict_resolution_sop.md** | active v1.0.1（已迁出本目录） |
| [68_code_algorithm_review_pipeline.md](68_code_algorithm_review_pipeline.md) | 代码与算法多模型审查流水线（跨切治理层；施工后审查线——5+5 路并发：施工 5 对话+审查修复 5 对话复用 audit 20 域每路 4 域，Kimi-K3/GLM-5.3/Qwen3.8-Max 多模型轮流交叉审查已 merge 模块代码/算法/运行情况，全自动化零打扰自主治本修复，冲突防护五机制，统一统筹调度；执行蓝本 docs/audit_prompts_20_ai.md；模型池已定 Kimi-K3/GLM-5.3/Qwen3.8-Max（Trae CN 切换）+轮换矩阵+调度卡一键复制指令模板库） | draft v1.2.0 |
| [90_methodology_open_questions.md](90_methodology_open_questions.md) | 方法论遗留提案 21 项（全部待讨论） | draft v1.18.1 |
| [91_density_prediction.md](91_density_prediction.md) | 密度预测与 QNN 远期愿景（待讨论） | draft v0.1.2 |

## 1. 文档定位

### 1.1 为什么有这份文档
- 30_multi_strategy_concurrency 已锁定多策略并发架构（Model A：独立账本 + firm 聚合 + regime 风险节流），但**只覆盖了"组合层"的 why**
- 10_regime_detector_spec/002 覆盖了 regime 检测器（**地基层**的 why + 验证）
- **选股、板块、仓位细节、风控落地、买入卖出、执行、对账、运营的 why 层全是空白**
- 这些空白需要逐个讨论定型，且数量众多（20+ 主题组），需要一份路线图统一调度

### 1.2 本文不做什么
- **不写 what is 的细节**（当前状态由作战地图 + depgraph 维护，本文只引用稳定 path）
- **不做裁定**（每个主题的裁定落在各自的 discussion/design_memo 里，本文只列"要讨论什么"）
- **不锁死顺序**（标注依赖与推荐顺序，但可根据人力/AI 资源灵活认领）

## 2. 三层现状快照

> 三层分治见 [management_spec §2](01_design_memo_management_spec.md)。本表标注每个作战地图阶段的"why 层"覆盖状态。

| 作战地图 | 阶段 | why 层（备忘/讨论） | depgraph 模块 | 施工方 | 状态 |
|---|---|---|---|---|---|
| 01 | 研究孵化 | ✅ G28 策略生命周期（61号 active v2.13.1：知识流水线拍板+研究环境否定式裁定+远期候选登记）+ 51号实验体系 | — | — | **已覆盖**（2026-08-12 全覆盖补丁） |
| 02 | 模型训练 | ✅ G28（61号 v2.13.1 含 MT-01-B/C 裁定） | — | — | **已覆盖**（2026-08-12 全覆盖补丁） |
| 03 | 回测验证 | ✅ regime 验证（11号 active v1.5.2，C1 四项全通过）+ G23（52号 active v1.0.3 含辅助组件契约与映射锚定）+ 15/23/51/53 映射补强 | 🟧 shrinkage/c1_comparator | 另一AI | **已覆盖**（2026-08-12 全覆盖补丁） |
| 04 | 模拟验证 | ✅ G24（53号 active v1.7.4，含 §3.9 仿真域 why 层回填 + BM-SIM-08 锚定） | 🟧 5 态 FSM 代码待落地（#ARCH-QUANT-003） | — | **已覆盖**（why 层已补齐，代码待落） |
| 05 | 选股 | ✅ G04-G10 全部定稿（20-26号 active）；G11 暂缓骨架；21/24/25/22/15 环节映射已锚定 | 🟧 BM-SEL-02/22-25 | — | **已覆盖**（7 主题组定稿+环节级锚定） |
| 06 | 买入流 | ✅ G19（41号 active v1.6.0，含明日预案双层架构+上游四轨裁定）+ G30（43号 active v1.1.0 合规纪律） | ✅ 43 号 7 模块已施工（AI-COMP-001：必做清单/四项严禁+熔断/授权审计/功能门禁/合规检测+报告门禁，78 测试全绿）+ 运行时装配（AI-ASM-001：C-004/C-002/MOD-PA-006 接线+日申报笔数硬计数器） | — | **已覆盖** |
| 07 | 卖出流 | ✅ G20（42号 active v1.7.0，含 §3.11 卖出闭环优化+双向反馈契约） | ✅ MVP 4 模块已施工（AI-SELL-001：Triage/止损/止盈/执行编排，65 测试全绿） | — | **已覆盖** |
| 08 | 仓位管理 | ✅ 30号 §2.1 + G12/G13/G15（31/32/34号 active）+ G14（33号 active v1.0.0，2026-08-12 重建）+ 31号 v1.24.2 漂移再平衡小节 | ✅ MOD-POS-020/021/022 + MOD-PA-007 全部 production | — | 框架已定+代码 production+文档齐 |
| 09 | 风控 | ✅ 30号 §2.5 + G16-G18（35/36/37号 active）+ 62号 v1.34.2 限额注册表 why 层 + 61号运行时风险治理 + 55号操作/模型风险审计 | ✅ drawdown/var/kill_switch 已 production | — | **已覆盖** |
| 10 | 执行 | ✅ 40_execution_broker active v2.10.1（§2.8 盘前检查链+订单层熔断两级） | ✅ 代码已施工（10 项 P0 gap 待落 #ARCH-EXEC-001） | G22-AI | ✅ 已定稿+代码已施工 |
| 11 | 对账 | ✅ G25（54号 active v1.15.5，含压力测试/仓位审计/模型层反馈小节） | 🟧 3 项待落码 | — | **已覆盖** |
| 12 | 跨切 | 🟧 G27（60号 active v1.1.0）+ G29（64号 draft v1.3.1）+ 62/63/65/90/91号（90号 v2.0.1 补 5 条远期开放问题） | — | — | **已覆盖** |

**结论**（2026-08-12 全覆盖补丁后更新）：12 个阶段的 why 层**全部覆盖**——2026-08-12 作战地图全覆盖工程以 PG `battle_map_steps` 340 环节为真源逐环节核对（19 弃用除外），321 个活跃环节全部在设计备忘中有载体（语义覆盖）且**逐编号显式锚定**（正文可检索 BM-XXX 编号至承载小节）：新建 43号（G30 合规与交易纪律），41/61/21/24/25/52/15/51/53/54/55/35/31/32/36/37/42/17/62/64/90/91/40/10/20/34/23 共 26 篇补环节设计或裁定，否定式裁定（不建设/暂缓+重评条件）与建设契约四要素齐全。git 灾难丢失的 8 篇设计文档**全部就绪**（7 篇 04:32 重建 + 28号 v1.2.0 已从 a3750b90d1 恢复（16f119bd）+ 60号 active v1.0.0 已在 HEAD），仅剩 34号 测试套件（代码非文档）待重建。遗留：battle_map 真源 3 处成熟度口径修正（BM-MT-01-B 标 production 实为 design、BM-SIM-03/06 production 标注 vs code_mapping planned、BM-BUY-02-A-1-c 待回写 90 §7 暂缓标注）已分别登记在 61 §7.5 / 52 §7，待治理流程回写 DB。

## 3. 主题组全集（G01–G30）

> 按"决策架构层次"组织（对标机构量化 pipeline：地基→alpha→组合→风控→交易→执行→验证→运营→治理）。
> 每个主题组是一个**可独立认领的讨论单元**，组内含若干子项。
> **正交性**列：是否与另一 AI 的 regime 施工正交（✅ 正交可并行 / ⚠️ 有依赖需协调）。

---

### L0·地基层

#### G01 数据与特征层规范
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 01/02 + 跨切 |
| 依赖 | 无（地基） |
| 讨论要点 | ① ClickHouse schema 规范（日K/分钟/Tick/板块/期权）② miniQMT tick 接入契约 ③ PIT 铁律（AS OF JOIN + Embargo）④ 特征仓库架构（计算/缓存/版本）⑤ 因子工程总纲（因子库/IC 评估/衰减监控/过拟合监控）⑥ 数据质量门控 |
| 产出物 | `15_data_feature_layer_spec_data_feature_layer.md` |
| 对标 | WorldQuant Alpha 工厂 / Numerai 数据管线 / qstobody 因子工程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.0.0（2026-08-12 依已施工能力重建，6a4f5392） |
| 优先级 | P0（地基，但可后置——策略定义不阻塞） |

#### G02 regime 检测器 spec ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [10_regime_detector_spec](10_regime_detector_spec.md) v1.5.1 |
| 状态 | ✅ 已定稿 v1.5.1；代码已施工 production，C1 已通过（commit 852457e9） |
| 正交性 | — 本身就是 regime |

#### G03 regime 回测验证方案 ✅已定稿
| 项 | 内容 |
|---|---|
| 产出物 | [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) v1.5.2 |
| 状态 | ✅ 已定稿 v1.5.2；Phase 0-2 完成（C1 四项全通过），Phase 3-4 部分（D1 敏感性网格未跑），Phase 5 未启动 |

---

### L1·Alpha 选股层

#### G04 首批 3 策略定义 ⭐推荐起点
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 + 30_multi_strategy_concurrency §6.1 |
| 依赖 | 无（alpha 地基） |
| 讨论要点 | ① 确认首批 3 策略（候选：打板 + 多因子 + 事件驱动）② 每策略 alpha 信号来源 ③ 换手率特征（高/中/低）④ 容量上限（打板几万~几十万）⑤ 选股池范围 ⑥ 持仓周期 ⑦ 与 regime 的关系（正交，regime 只节流不选股） |
| 产出物 | `20_first_batch_strategies_first_batch_strategies.md` |
| 对标 | Citadel pod 模型（每 pod 独立 alpha + 独立 book）/ Morwane 双 sleeve |
| 正交性 | ✅ 与 regime 正交（30_multi_strategy_concurrency §2.2 明确） |
| 状态 | ✅ 已定稿 v1.2.4（打板+多因子+事件驱动；主升龙头并入打板） |
| 优先级 | **P0**（一切 alpha/组合/风控下游的地基） |
| 校准跟踪 | ⚠️ **G04 参数校准未产出**（2026-08-14 登记，tracker #48）：定稿≠校准——按策略类型的参数校准（42 §7 卖出侧 ATR 倍数/移动止损回撤/时间止损差异化 + §3.10 熔断 N=2/3 + 20 号 convergence_window/RegimeMetaAllocator 参数）依赖首批策略回测/实盘 track record。**下游挂载**：42 号 §5.2 阶段 5b（MOD-SELL-014）/§6 止盈差异化/§3.10 熔断（CAND-SELL-001）+ 24 号 §3.13#1 时间止损口径统一（跨文档校准项）。**责任**：统筹跟踪项，首批策略回测/实盘启动时触发 |

#### G05 选股引擎架构
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① 双引擎融合（BM-SEL-25，30_multi_strategy_concurrency 定位为"打板策略内部融合"，非跨策略层）② L0→L1→L2-C 分层 ③ 量化强度评级 ④ 选股 pipeline 标准接口（输入信号→输出 target_portfolio）⑤ 候选池生成→过滤→排序→输出 ⑥ 与 StrategyBook 的对接契约 |
| 产出物 | `21_stock_selection_engine_stock_selection_engine.md` |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.1.18 |
| 优先级 | P1 |

#### G06 板块轮动 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-08/09） |
| 依赖 | G04（板块是选股的输入特征，非独立层） |
| 讨论要点 | ① 板块强度算法（BM-SEL-08，460 板块 880xxx K线）② 回踩质量等级 A/B/C 判定 ③ 调整周期追踪（BM-SEL-09，进度≥80% 激活分批）④ 轮动序列追踪 ⑤ 虹吸态识别（30_multi_strategy_concurrency §1.3 提到情绪周期隐形驱动）⑥ 板块资金流 ⑦ 板块→个股的传导映射 |
| 产出物 | `22_sector_rotation_spec.md` |
| 对标 | AQR sector momentum / 华泰板块轮动研报 / 申万行业轮动 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.8.0 |
| 优先级 | P1 |

#### G07 策略间相关性验证
| 项 | 内容 |
|---|---|
| 所属 | 30_multi_strategy_concurrency §6.2（施工前必做） |
| 依赖 | G04（需策略定义才能算相关） |
| 讨论要点 | ① 5 候选策略两两相关矩阵 ② 按情绪周期分层看相关性 ③ 若各阶段相关性 >0.6 则"多策略实为情绪 beta 穿多件衣服"→ 重新审视 ④ 验证数据区间 ⑤ 验证报告模板 |
| 产出物 | `23_strategy_correlation_validation_strategy_correlation_validation.md` |
| 对标 | Morwane block-bootstrap 相关性验证 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.7.0 |
| 优先级 | P1（G04 后立即） |

#### G08 打板策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05（BM-SEL-22~25）+ 30_multi_strategy_concurrency §4.3 |
| 依赖 | G04、G05、G06 |
| 讨论要点 | ① 连板梯队识别 ② 情绪周期定位器（BM-SEL-23-B，30_multi_strategy_concurrency §6.3 待评估准确率）③ 主升龙头识别 ④ 打板容量极小（单票几万~几十万）→ 必须小账本 ⑤ 双引擎融合在此策略内部（BM-SEL-25）⑥ 打板专用风控参数 ⑦ T+1 约束下的打板时序 ⑧ 助攻梯队权重真源裁定 |
| 产出物 | `24_daban_strategy_detail.md`（active v1.9.7：8 项讨论要点全对齐+§3.13/§3.14 施工算法 12 项补全+2026-08 arXiv 最新研究整合） |
| 对标 | 游资打板体系（龙虎榜/连板梯队/情绪周期）/ 量化社区连板策略 / 华安涨停板Alpha 2026-03 / caifuhao 连板复盘 2026-08 |
| 正交性 | ✅ 与 regime 正交（打板读情绪周期不读 regime） |
| 状态 | ✅ active v1.9.7（8 项讨论要点全对齐+施工算法 12 项补全） |
| 优先级 | P1（高换手、小容量、高频 alpha） |

#### G09 多因子策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05、G01（因子工程） |
| 讨论要点 | ① 因子组合方式（打分/IC加权/正交化）② 行业中性化 ③ 因子衰减监控 ④ 多因子换手率（低，3-5 天 convergence）⑤ 多因子容量（较大，可承载主资金）⑥ 与打板策略的相关性 |
| 产出物 | `25_multifactor_strategy_detail.md`（active v1.12.11：6 项讨论要点全对齐+§3.7 施工算法 8 项补全+Phase 4.1-4.20 远期候选栈+2026-08 arXiv 最新研究整合） |
| 对标 | WorldQuant / Numerai 多因子 / 华泰金工多因子 / BigQuant ICIR 2026-07 |
| 正交性 | ✅ 与 regime 正交（纯横截面选股） |
| 状态 | ✅ active v1.12.11（6 项讨论要点全对齐+施工算法 8 项补全） |
| 优先级 | P2（承载主力资金的低频基石） |

#### G10 事件驱动策略细节
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 05 |
| 依赖 | G04、G05 |
| 讨论要点 | ① 事件源（公告/新闻/龙虎榜/异动）② 事件分类（业绩/并购/政策/突发事件）③ 事件冲击衰减曲线 ④ 事件信号→选股映射 ⑤ 事件驱动换手率（中，2-3 天）⑥ news_data 多源情绪接入 |
| 产出物 | `26_event_driven_strategy_detail_event_driven_strategy_detail.md` |
| 对标 | RavenPack 事件驱动 / 彭博事件策略 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.8.0 |
| 优先级 | P2 |

#### G11 第二批次策略（价值反转 / 动量趋势）
| 项 | 内容 |
|---|---|
| 所属 | 30_multi_strategy_concurrency §1.1（5 候选策略后 2 个） |
| 依赖 | G04 先跑 3 个月有 track record |
| 讨论要点 | ① 价值反转 alpha 信号 ② 动量趋势 alpha 信号 ③ 与首批 3 策略相关性 ④ 上线时机（首批 track record 后） |
| 产出物 | `27_second_batch_strategies_second_batch_strategies.md` |
| 对标 | AQR 价值/动量 / Fama-French |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 暂缓（首批上线 3 个月后再讨论）·骨架 v0.1.0 |
| 优先级 | P4（远期） |

---

### L2·组合仓位层

#### G12 仓位算法 spec（落地分层裁定）
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.1 |
| 依赖 | G04（选股结果）+ G05 |
| 讨论要点 | ① 策略层粗仓位（等权 / risk parity，**不用 Kelly**）② 组合层 Kelly 精裁决（MOD-POS-001）③ Kelly 参数（预期收益/方差估计来源）④ risk parity 具体公式（inverse-vol / Morwane 范式）⑤ 单票硬上限 8% 裁剪逻辑 ⑥ 现金管理 ⑦ 分层裁定的接口契约（StrategyBook 输出粗仓位→firm 层 Kelly 精裁决） |
| 产出物 | `31_position_sizing.md` |
| 对标 | Morwane inverse-vol risk parity / Kelly criterion 实证 / Morwane sleeve(alpha)+risk-parity-throttle(firm) 分层 |
| 正交性 | ✅ 与 regime 正交（regime 只缩 budget，不调仓位算法） |
| 状态 | ✅ 已定稿 v1.23.0（[31_position_sizing](31_position_sizing.md)） |
| 优先级 | P1（spec 层可先动） |

#### G13 FirmRiskAggregator 逻辑
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | G12（仓位算法） |
| 讨论要点 | ① 按标的求和（自然叠加，30_multi_strategy_concurrency §2.3）② 单票硬上限裁剪（>8% 按比例削）③ 行业/总仓位硬约束 ④ 冲突标的处理（一策略买一策略卖→净额 or 优先级）⑤ **不做 MVO，不做协方差估计**（30_multi_strategy_concurrency §3.1 拒绝）⑥ 输出 firm_target_portfolio 契约 ⑦ O(N) 复杂度保证 |
| 产出物 | `32_firm_risk_aggregator_firm_risk_aggregator.md` |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.0.20；代码 MOD-POS-021 已 production（54 测试） |
| 优先级 | P2 |

#### G14 BudgetChangeHandler 三级升级
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.4 |
| 依赖 | G12、G13 |
| 讨论要点 | ① Tier 1 封锁新仓（瞬时）② Tier 2 rebalance_to_budget 信号（策略自选砍仓）③ Tier 3 按比例强裁（firm 层兜底）④ convergence_window 按换手率差异化（30_multi_strategy_concurrency §6.4：打板 1-2 天/多因子 3-5 天/事件 2-3 天）⑤ rebalance_to_budget 接口契约（策略不能说"我不卖"）⑥ 每级独立 log/复盘 |
| 产出物 | `33_budget_change_handler_budget_change_handler.md` |
| 对标 | 机构级 budget rebalance 协议 |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 状态 | ✅ active v1.0.0（2026-08-12 依 MOD-POS-022 production 代码重建，6a4f5392；含 §3.2 三级升级 + §3.3 防抖双层） |
| 优先级 | P2 |

#### G15 RegimeMetaAllocator 参数
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | ✅ C1 验证已通过（commit 852457e9，Shrinkage 有效）；⚠️ G04 PerformanceScore 需首批策略 PnL（未就绪） |
| 讨论要点 | ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` ② Base_i 先验权重 ③ PerformanceScore 60 日 Sortino 映射 [0.5,1.5]（34号 v1.2.0 起 Sharpe→Sortino 已切换）④ Shrinkage 置信度→风险节流映射（30_multi_strategy_concurrency §2.2 四档）⑤ floor≥5% / cap≤40% ⑥ 稀有态差异化收缩 ⑦ 第二阶段上线时机 |
| 产出物 | `34_regime_meta_allocator_regime_meta_allocator.md` |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（30_multi_strategy_concurrency §2.2） |
| 正交性 | ⚠️ 本身就是 regime 节流的消费者；C1 已通过，参数待策略 track record 后校准 |
| 状态 | ✅ 框架已定稿 v2.8.1（C1 已通过 commit 852457e9）；代码 MOD-PA-007 production v1.0.0（测试套件丢失待重建）；参数待首批策略 PnL 校准 |
| 优先级 | P3（第二阶段，等策略 track record） |

---

### L3·风控层

#### G16 回撤 Protocol 落地
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5 |
| 依赖 | G12（仓位）—— 但框架已有，可并行 |
| 讨论要点 | ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec ② 单策略 vs 组合层面分层（§2.5.3）③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）④ Kill Switch 触发条件与执行路径（§2.5.5）⑤ 日度熔断（组合 -4%/单策略 -5%）⑥ Kill Switch 不可覆盖原则 ⑦ 回撤基准净值计算口径 ⑧ 与 regime Shrinkage 的协同（drawdown 是账户风险，regime 是市场风险，§2.5 定位） |
| 产出物 | `35_drawdown_protocol_impl.md` |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（§2.5 已引） |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 状态 | ✅ active v1.39.0 |
| 优先级 | P2（与 G12 并行） |

#### G17 VaR/ES 与波动率监控
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.4 |
| 依赖 | G16 |
| 讨论要点 | ① VaR_95 计算（历史模拟/参数法）② ES_95 计算 ③ 入场 VaR/ES 基准 ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）⑤ 30 日波动率调整（每增10%→仓位减20%）⑥ 数据窗口 ⑦ 与回撤 Protocol 的协同 |
| 产出物 | `36_var_es_monitoring.md` |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.10.2 |
| 优先级 | P3 |

#### G18 流动性危机处理
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.5 |
| 依赖 | G16 |
| 讨论要点 | ① 买卖价差监控（>正常 5x 触发）② 流动性危机→立即停止开仓仅允许平仓 ③ 流动性指标定义（换手率/成交额/盘口深度）④ 与 Kill Switch 的关系 ⑤ A 股涨跌停流动性失效处理 |
| 产出物 | `37_liquidity_crisis_protocol.md` |
| 对标 | tradingwyckoff Kill Switch / 机构流动性风控 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.0.16 |
| 优先级 | P3 |

---

### L4·交易流层

#### G19 买入流 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位）、G16（风控） |
| 讨论要点 | ① 分批建仓（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）② 突破失败降级 ③ 买入时序（盘中/盘后/集合竞价）④ 买入价格锚定 ⑤ 资金分配到多标的 ⑥ 与 budget 的协同 ⑦ T+1 约束 |
| 产出物 | `41_buy_flow_buy_flow.md` |
| 对标 | 机构分批建仓 / Wyckoff 吸筹时序 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.5.1（5 算法伪代码已定型待落码） |
| 优先级 | P3 |

#### G20 卖出流 spec
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 07 |
| 依赖 | G19 |
| 讨论要点 | ① 卖出时序（止损/止盈/时间止损）② 止损触发（固定%/移动/ATR）③ 止盈逻辑 ④ 情绪退潮卖出（与 regime CRISIS/RECOVERY 协同）⑤ 破位卖出 ⑥ 分批卖出 ⑦ T+1 卖出约束 ⑧ 与回撤 Protocol 的联动 |
| 产出物 | `42_sell_flow_sell_flow.md` |
| 对标 | 机构卖出纪律 / O'Neil 卖出法则 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（但 regime 只给 Shrinkage，卖出逻辑在策略内） |
| 状态 | ✅ 已定稿 v1.5.2（5 算法伪代码已定型待落码） |
| 优先级 | P3 |

#### G21 情绪周期×交易决策
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04、G08（打板最依赖情绪周期） |
| 讨论要点 | ① 5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律 ② 情绪周期定位器准确率评估（30_multi_strategy_concurrency §6.3）③ 情绪周期与 regime 12 态的映射关系 ④ 各策略在不同情绪阶段的部署策略 ⑤ 情绪周期是"隐形驱动"（30_multi_strategy_concurrency §1.3）→ 策略间相关性来源 |
| 产出物 | `28_sentiment_cycle_trading_sentiment_cycle_trading.md` |
| 对标 | 游资情绪周期体系 / 龙虎榜情绪 / 涨跌停情绪温度 |
| 正交性 | ⚠️ 与 regime 部分重叠（regime 12 态含情绪维度），需明确分工 |
| 状态 | ⚠️ 骨架 v0.1.0（内容 2026-08-11 git 灾难丢失待重建，v1.2.0 可从 commit a3750b90d1 恢复） |
| 优先级 | P2（打板策略前置） |

#### G30 合规与交易纪律体系
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 06/09/10（跨段，D_COMPLIANCE 域） |
| 依赖 | G19（41号行为命名与拦截定位）、G22（40号撤单率/价格笼子/限频 production 基座）、G08（24号 §3.7 程序化新规约束） |
| 讨论要点 | ① 四项必做清单自动化检测（BM-BUY-08-A，盘前/盘中/盘后/晚间 4 时点）② 四项严禁阈值与检测算法（BM-BUY-08-B 追高/补仓/骄傲/报复 + Kill Switch 轻量版）③ 信息合规（BM-BUY-09 数据源授权条款合规登记+使用审计）④ 硬边界裁定（BM-BUY-12 功能二元裁定清单+上线门禁流程）⑤ 交易合规检测补强（BM-BUY-15 操纵 4 类检测+程序化报告 6 项义务） |
| 产出物 | [43_compliance_discipline](43_compliance_discipline.md) |
| 对标 | 2026 程序化新规 / 机构合规检查清单 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已落盘 draft v0.1.0（2026-08-12 作战地图全覆盖补丁新建，5 环节裁定齐全） |
| 优先级 | P2（实盘前置合规底线） |

---

### L5·执行层

#### G22 下单对接与撮合
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 10 |
| 依赖 | G19/G20（买卖信号） |
| 讨论要点 | ① miniQMT 下单接口对接 ② 撮合算法（TWAP/VWAP/拆单/被动成交）③ 滑点模型 ④ 交易成本模型（佣金/印花税/过户费）⑤ 订单状态机 ⑥ 失败重试 ⑦ 执行风控（订单层熔断）⑧ 集合竞价处理 |
| 产出物 | [40_execution_broker](40_execution_broker.md) |
| 对标 | miniQMT 文档 / 机构执行算法（TWAP/VWAP/IS） |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v2.9.2 + 代码已施工（commit 015826ae，2026-08-08，G22-AI） |
| 优先级 | P4 |

---

### L6·验证层

#### G23 回测框架对接
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义） |
| 讨论要点 | ① BM-BT-01~07 环节在策略验证中的用法（regime 验证已映射，见 11_regime_backtest_validation_plan §2.1）② 策略回测 vs regime 回测的差异 ③ 策略上线门控 IS→WFA→OOS（BM-BT-07）④ 过拟合检测三维度（BM-BT-05）⑤ Deflated Sharpe（BM-BT-05-G） |
| 产出物 | `52_backtest_framework_docking_backtest_framework_docking.md` |
| 对标 | 11_regime_backtest_validation_plan 已建立的对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 状态 | ✅ active v1.0.0（2026-08-12 重建，6a4f5392；regime 侧对接已在 11号 落地，策略侧待补） |
| 优先级 | P2（G04 后） |

#### G24 模拟与实盘验证路径
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 04 |
| 依赖 | G23（回测通过） |
| 讨论要点 | ① 模拟验证（paper trading）环境 ② 模拟时长 ③ 实盘小资金验证路径 ④ 实盘→模拟差异监控 ⑤ 上线决策门控 ⑥ 灰度上线（单策略先上） |
| 产出物 | `53_simulation_live_path_simulation_live_path.md` |
| 对标 | 机构 paper trading → 小资金 → 全量 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ 已定稿 v1.6.6（5 态 FSM 代码待落地 #ARCH-QUANT-003） |
| 优先级 | P4 |

---

### L7·运营层

#### G25 对账归因
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 11 |
| 依赖 | G22（执行）+ G04（策略） |
| 讨论要点 | ① PnL 归因（策略贡献分解）② 每日对账（成交 vs 持仓 vs 资金）③ 归因维度（策略/标的/因子/时段）④ 与 StrategyBook 独立 PnL 归因的对接（30_multi_strategy_concurrency §2.2）⑤ 异常交易检测 ⑥ 报表生成 |
| 产出物 | `54_reconciliation_attribution.md` |
| 对标 | 机构中后台对账 / Barra 归因 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.14.0 |
| 优先级 | P5 |

#### G26 监控告警与复盘
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 |
| 依赖 | G25 |
| 讨论要点 | ① 系统健康监控（数据/引擎/下单链路）② 策略偏离监控（实盘 vs 回测）③ 告警阈值与通知 ④ 每日/每周/每月复盘机制 ⑤ 策略退役标准（连续跑输/逻辑失效）⑥ 复盘文档模板 |
| 产出物 | `55_monitoring_review.md` |
| 对标 | 机构 PM 周报 / 风控周报 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v1.1.0（2026-08-15 三件套+阈值注册表施工，AI-MON-001） |
| 优先级 | P5 |

---

### L8·跨切与治理层

#### G27 冲突矩阵清理与事件总线
| 项 | 内容 |
|---|---|
| 所属 | 作战地图 12 |
| 依赖 | G04-G13（架构定型后才能清理冲突） |
| 讨论要点 | ① battle_map_12 §16 的 31 条跨策略冲突仲裁→大部分因 A 模型消失（30_multi_strategy_concurrency §7.3）② 仅留 firm-level 硬上限 ③ 事件总线/信号注入机制 ④ 实时计算节奏（盘中 vs 盘后）⑤ 配置驱动（参数热更新/AB 测试）⑥ 多策略投票降级（BM-SEL-20 已 rejected，§7.3） |
| 产出物 | `60_cross_cutting_cleanup.md` |
| 对标 | 机构事件总线 / 微服务信号路由 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ⚠️ 骨架 v0.1.0（内容 2026-08-11 git 灾难丢失待重建） |
| 优先级 | P3（架构定型后） |

#### G28 策略生命周期与多 AI 协作
| 项 | 内容 |
|---|---|
| 所属 | 跨作战地图 01/02/03/04 |
| 依赖 | 全局 |
| 讨论要点 | ① 策略生命周期（孵化→训练→回测→模拟→实盘→退役，对应作战地图 01-04/11）② 研究孵化阶段（BM-RES）规范 ③ 模型训练阶段（BM-MOD）规范 ④ 多 AI 协作分工规范（另一 AI 做 regime，本边做选股，交接点）⑤ 文档治理（design_memo 编号体系，本文档建立）⑥ creation_token / depgraph 登记流程 |
| 产出物 | `61_lifecycle_multi_ai.md` |
| 对标 | MLOps 生命周期 / 机构策略研发流程 |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | ✅ active v2.10.0 |
| 优先级 | P3（治理类，可后置） |

#### G29 数据源与下载体系
| 项 | 内容 |
|---|---|
| 所属 | 跨切治理层（6x 段位）+ 作战地图 01 数据源保障 |
| 依赖 | 无（数据地基治理） |
| 讨论要点 | ① 15 数据源/130+ 下载任务/11 档调度全面盘点 ② 落库 schema 与韧性（断点续传/失败重试/降级）③ 数据源升级讨论载体（64号 §12 含 12 项待裁定+12 开放问题） |
| 产出物 | [64_data_source_download_spec.md](64_data_source_download_spec.md) |
| 对标 | 机构数据供应链治理 / tushare-akshare-miniqmt 多源 failover |
| 正交性 | ✅ 与 regime 正交 |
| 状态 | 待讨论（64号 draft v1.2.1 已落盘，与 63号 数据利用审计配套：63 审"用得怎么样"、64 审"下得怎么样"） |
| 优先级 | P1（数据供应链地基） |

## 4. 依赖关系图

```
                    [G01 数据特征层] ─────────────────────────┐
                         │（地基，可后置）                      │
                         ↓                                    │
[L0地基]  G02 regime spec ✅ ──→ G03 regime验证 ✅ ──→ (C1验证通过 852457e9)
                                    │                          │
                                    │ ✅ G15 RegimeMetaAllocator│
                                    │   C1已通过，等策略PnL+D1   │
                                    ↓                          ↓
[L1 Alpha] G04 首批3策略⭐ ──→ G05 选股引擎 ──→ G06 板块轮动 ──→ G07 相关性验证
                │              │                                │
                ├──→ G08 打板细节 ←── G21 情绪周期×交易          │
                ├──→ G09 多因子细节 ←── G01 因子工程              │
                ├──→ G10 事件驱动细节                            │
                └──→ G11 第二批次（远期 P4）                      │
                │                                              │
                ↓                                              │
[L2 组合] G12 仓位算法 ──→ G13 FirmRiskAggregator ──→ G14 BudgetChangeHandler
                │              │
                │              └──→ G15 RegimeMetaAllocator（C1已通过，等策略PnL）
                ↓
[L3 风控] G16 回撤Protocol落地 ──→ G17 VaR/ES ──→ G18 流动性危机
                │（与G12并行）
                ↓
[L4 交易] G19 买入流 ──→ G20 卖出流 ──→ G21 情绪周期×交易
                │
                ↓
[L5 执行] G22 下单对接撮合
                │
                ↓
[L6 验证] G23 回测框架对接 ──→ G24 模拟实盘验证
                │
                ↓
[L7 运营] G25 对账归因 ──→ G26 监控告警复盘
                │
                ↓
[L8 治理] G27 冲突矩阵清理 + G28 生命周期与多AI协作 + G29 数据源下载体系
```

## 5. 推荐认领顺序（3 条并行轨道）

> 另一 AI 持续做 regime（G02/G03 + C1 验证）。本边开启多 AI，每条轨道一个 AI，**3 条轨道并行**。

> **⚠️ 2026-08-14 用户裁定·治理插队**：第 1-3 批业务施工（G12-G14/G16-G20/G22 等 18 会话）全部完工 merge 后，**git/并发协作基础设施专项治理（65/66/67 号，AI-GIT-001）插队为最高优先级**，先于第 4/5 批（34/60/43/53/54/55）。依据：三次事故（git clean 灾难/tracker 丢失/worktree wipe）四层根因（R1 删除原语零拦截/R2 隔离君子协定/R3 删除无审计/R4 清理无 SOP）从未治本，裁定书=docs/02_enterprise_architecture/04_architecture_principles_decisions/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md（2026-08-14 自 _working 临时区迁入 04 永久区）。

### 轨道 A：Alpha 链（核心关键路径）
```
G04 首批3策略⭐ → G05 选股引擎 → G06 板块轮动 → G07 相关性验证
                                    ↓
                    G08 打板 / G09 多因子 / G10 事件驱动（3个可并行）
```
- **理由**：策略定义是一切 alpha/组合/风控下游的地基，且与 regime 正交，可立即开工
- **认领建议**：1 个 AI 串行 G04→G05→G06→G07，再分 3 个 AI 并行 G08/G09/G10

### 轨道 B：组合风控链（spec 层先动）
```
G12 仓位算法spec → G13 FirmRiskAggregator → G14 BudgetChangeHandler
        ↓（并行）
G16 回撤Protocol落地 → G17 VaR/ES → G18 流动性危机
```
- **理由**：仓位/风控框架已定（30_multi_strategy_concurrency §2.1/§2.5），spec 层可不等选股细节先动；待 G04 产出后接口对齐
- **认领建议**：1 个 AI 串行 G12→G13→G14，另 1 个 AI 并行 G16→G17→G18

### 轨道 C：执行运营链（下游，可延后）
```
G22 下单对接 → G19 买入流 → G20 卖出流 → G23 回测对接 → G25 对账 → G26 监控复盘
```
- **理由**：执行/运营依赖上游信号定型，但 G22（miniQMT 对接）和 G23（回测对接）可独立预研
- **认领建议**：1 个 AI 串行，待轨道 A/B 产出后接口对齐

### 三条轨道的交汇点
- **G04 产出后**：轨道 B 的 G12 接口对齐、轨道 C 的 G23 策略载体就绪
- **C1 已通过**（2026-08-08，commit 852457e9）：G15 剩余门槛 = 首批策略 3-6 月实盘 PnL + D1 敏感性网格（[11号](11_regime_backtest_validation_plan.md) §0.5.7）
- **G08/G09/G10 产出后**：G27 冲突矩阵清理（架构全定型）

## 6. 与 regime 施工的正交性说明

> 30_multi_strategy_concurrency §2.2 核心裁定：**regime 只做风险节流（Shrinkage），不做 alpha 择时；不参与选股，只参与 budget 缩放。**

| 主题组 | 与 regime 关系 | 说明 |
|---|---|---|
| G04-G11（Alpha 全部） | ✅ 完全正交 | regime 不管选股，策略 alpha 独立 |
| G12-G14（组合仓位） | ✅ 正交 | regime 只缩 budget 数值，不调仓位算法 |
| G15（RegimeMetaAllocator） | ⚠️ 消费者 | C1 已通过（852457e9）；等策略 PnL + D1 校准，第二阶段 |
| G16-G18（风控） | ✅ 正交 | drawdown 是账户级，regime 是市场级（§2.5 定位） |
| G19-G22（交易执行） | ✅ 正交 | |
| G21（情绪周期） | ⚠️ 部分重叠 | regime 12 态含情绪维度，分工边界已定（28号 v1.2.0 §2.2/§3：情绪周期=sleeve内alpha择时 vs regime=市场级风险节流） |
| G23-G29（验证运营治理） | ✅ 正交 | |

**结论**（2026-08-12 更新）：G15 的 C1 门槛已解除（剩策略 PnL + D1），G21 分工边界已定（28号 v1.2.0 §2.2/§3）；其余主题组全部可与 regime 并行。

## 7. 多 AI 分工认领指南

### 7.1 认领流程
1. 用户为每个主题组开启一个 AI 对话
2. 该 AI 首读本文档 + 30_multi_strategy_concurrency + 相关作战地图
3. AI 按本主题组的"讨论要点"逐项讨论，与用户对齐
4. 讨论定型后落盘产出物（discussion_NNN / design_memo_NNN）
5. 涉及模块施工的，按 management_spec §2.2 流程登记 depgraph

### 7.2 交接点纪律
- **AI 间不直接通信**，通过产出物（discussion/design_memo）+ depgraph path 交接
- 认领 G05 的 AI 必须先读 G04 的产出物 `20_first_batch_strategies`
- 认领 G12 的 AI 必须先读 30_multi_strategy_concurrency §2.1 分层裁定
- 所有 AI 必读：30_multi_strategy_concurrency（架构总纲）+ 本文档（路线图）

### 7.3 编号占用表（避免冲突）

> ⚠️ 2026-08-09 起改段位编号制，下表已同步更新为新名。2026-08-12 v2.9.0 第三轮版本同步：全部对齐工作树实际 frontmatter，幻影版本已更正（§0 头部 ⚠️ 标注 + §9 #D1）。新文档按 §8 段位规则命名，不再使用此表分配编号；本表转为**历史认领记录**，实时状态以 §0 目录为准。

> 认领时在此登记，避免产出物编号冲突。

| 产出物编号 | 主题组 | 认领方 | 状态 |
|---|---|---|---|
| 10_regime_detector_spec | G02 regime spec | 另一AI | ✅ v1.5.1 |
| 11_regime_backtest_validation_plan | G03 regime 验证 | 另一AI | ✅ v1.5.2（C1 已通过） |
| 20_first_batch_strategies | G04 首批3策略 | G04-AI | ✅ v1.2.4 |
| discussion_004 | ⚠️ 编号冲突已澄清：代码误用此号指代 13 号文档（Phase 3 降维裁定）；G06 板块轮动实际产出物为 `22_sector_rotation_spec.md` | — | 已澄清 |
| 15_data_feature_layer_spec | G01 数据特征层 | ✅ 已定稿 | active v1.0.0（2026-08-12 重建） |
| 21_stock_selection_engine | G05 选股引擎 | ✅ 已定稿 | active v1.1.18 |
| 22_sector_rotation_spec | G06 板块轮动 | ✅ 已定稿 | active v1.8.0 |
| 23_strategy_correlation_validation | G07 相关性验证 | ✅ 已定稿 | active v1.7.0 |
| 24_daban_strategy_detail | G08 打板细节 | ✅ 已定稿 | active v1.9.7（8 要点+12 施工算法） |
| 25_multifactor_strategy_detail | G09 多因子细节 | ✅ 已定稿 | active v1.12.11（6 要点+8 施工算法+Phase 4 栈） |
| 26_event_driven_strategy_detail | G10 事件驱动 | ✅ 已定稿 | active v1.8.0 |
| 27_second_batch_strategies | G11 第二批次 | （待认领） | draft v0.2.0（暂缓讨论，说明已补） |
| 35_drawdown_protocol_impl | G16 回撤落地 | ✅ 已定稿 | active v1.39.0 |
| 36_var_es_monitoring | G17 VaR/ES | ✅ 已定稿 | active v1.11.2 |
| 37_liquidity_crisis_protocol | G18 流动性危机 | ✅ 已定稿 | active v1.2.0（2026-08-17 AI-LVL3-001 LEVEL_3 生产接线完工，检测→逃生指令→Kill Switch 清算全链） |
| 28_sentiment_cycle_trading | G21 情绪周期 | （待重建） | 骨架 v0.1.0 ⚠️内容丢失（v1.2.0 可从 a3750b90d1 恢复） |
| 29_factor_strategy_extraction | 潘潘课程因子策略提炼知识库（工程文档，非G主题） | 已落盘 | active v1.0.0（2026-08-14 用户裁定从 _working 迁入，原名 因子与策略提炼.md） |
| 52_backtest_framework_docking | G23 回测对接 | ✅ 已定稿 | active v1.0.0（2026-08-12 重建） |
| 53_simulation_live_path | G24 模拟实盘 | ✅ 已定稿 | active v1.7.9 |
| 55_monitoring_review | G26 监控复盘 | ✅ 已定稿 | active v1.2.0（2026-08-17 AI-THD-001 阈值统读完工） |
| 12_regime_phase2_validation | Phase 2 模型质量验证（工程文档，非G主题） | 已落地 | ✅ v0.2.2 |
| 50_backtest_observability_workplan | 回测可观测性工作计划（工程文档，非G主题） | 已提议 | draft v1.0.2 |
| 13_regime_phase3_engineering_plan | Phase 3 工程规划（工程文档，非G主题） | 已提议 | draft v0.3.2 |
| 14_regime_s2_diagnosis | S2 算法错配诊断（工程文档，非G主题） | 已提议 | draft v0.4.5 |
| 16_technical_indicator_build_plan | 技术指标施工计划（数据地基层子项） | ✅ 已定稿 | active v1.0.0（2026-08-12 重建） |
| 16_technical_indicator_catalog | 技术指标目录（数据地基层子项） | ✅ 已定稿 | active v1.0.0（2026-08-12 重建） |
| 17_special_trading_days_data_assets | 特殊交易日数据资产（数据地基层子项） | ✅ 已定稿 | active v1.0.0 |
| 18_cold_archive_build_plan | 冷归档施工计划（数据地基层子项） | 已提议 | active v0.2.0 |
| 62_business_registry_construction | 18 业务注册表施工（跨切治理层） | ✅ 已定稿 | active v1.32.0 |
| 63_data_utilization_audit | 数据利用审计（跨切治理层） | 已提议 | draft v2.0.0 |
| 65_git_safety_governance | Git 安全治理体系（跨切治理层） | ✅ 已定稿（Phase 1 wrapper 层已施工，待激活） | active v2.3.1 |
| 66_commit_queue_serialization | 提交队列串行化（跨切治理层·集成基建） | ✅ 已定稿（MVP 待排期） | active v1.1.0 |
| 90_methodology_open_questions | 方法论遗留提案（工程文档，非G主题） | 已提议 | draft v1.18.1 |
| 91_density_prediction | 密度预测远期愿景（工程文档，非G主题） | 已提议 | draft v0.1.2 |
| 51_panel_experiment_history_mlflow_retirement | Panel 实验历史 Tab + mlflow 退役施工计划（工程文档，非G主题，50_backtest_observability_workplan M2 下游） | ✅ 已定稿 | active v1.2.6 |
| 30_multi_strategy_concurrency | 多策略并发架构 | ✅ 已定稿 | active v2.5.0 |
| 31_position_sizing | G12 仓位算法 | ✅ 已定稿 | active v1.25.0 |
| 32_firm_risk_aggregator | G13 FirmRiskAggregator | ✅ 已定稿 | active v1.0.22 |
| 33_budget_change_handler | G14 BudgetChangeHandler | ✅ 已定稿 | active v1.1.0（2026-08-14 AI-BGT-001 行号漂移修正+§7 四项闭环，1b8a774ad5） |
| 34_regime_meta_allocator | G15 RegimeMetaAllocator | ✅ 已定稿 | active v2.8.1（C1 已通过；参数待策略 PnL 校准） |
| 41_buy_flow | G19 买入流 | ✅ 已定稿 | active v1.7.0 |
| 42_sell_flow | G20 卖出流 | ✅ 已定稿 | active v1.7.1 |
| 43_compliance_discipline | G30 合规与交易纪律体系（交易流层子项，D_COMPLIANCE 域） | ✅ 已施工 | active v1.1.0（2026-08-15 AI-COMP-001 落地 7 模块 + AI-ASM-001 运行时装配：C-004/C-002/MOD-PA-006 接线+日申报笔数硬计数器，213 测试全绿） |
| 40_execution_broker | G22 下单对接 | G22-AI | ✅ v2.10.1 + 代码已施工 |
| 54_reconciliation_attribution | G25 对账归因 | ✅ 已定稿 | active v1.14.0 |
| 60_cross_cutting_cleanup | G27 冲突矩阵清理 | ✅ 已定稿 | active v1.1.0（2026-08-15 AI-XCUT-001 实证非骨架：v1.0.2 内容完整；施工=§7⑦ 闭环+CAND-PFALLOC-002 标 rejected+battle_map §16 真源收敛 31→3） |
| 61_lifecycle_multi_ai | G28 生命周期多AI | ✅ 已定稿 | active v2.10.0 |
| 19_northbound_hold_snapshot | 北向季度快照 fetcher（数据地基层子项） | 待施工 | draft v0.1.0 |
| 64_data_source_download_spec | G29 数据源与下载体系（跨切治理层·6x 段位） | ✅ 已定稿 | active v1.4.0 |
| 44_premarket_intraday_decision_upgrade | 盘前与盘中决策支持升级（28/41/90 号升级备忘，4x 交易流层） | ✅ Owner 五项裁定全批（2026-08-21） | active v1.2.0 |

## 8. 产出物命名规范

遵循 [management_spec §4.1](01_design_memo_management_spec.md)：
- 全部文档：`<段位号>_<topic>.md`（topic 为 snake_case 主题）
- 段位语义：**0x** meta｜**1x** 地基（regime/数据特征）｜**2x** Alpha 策略｜**3x** 组合仓位与风控｜**4x** 交易执行｜**5x** 验证与可观测性｜**6x** 跨切治理｜**9x** 开放问题与远期
- 新文档按业务域入段，段内取下一个空号；不预留坑位
- 全部 snake_case，遵循项目命名铁律
- status 枚举：`active`（已定稿/已落地）/ `draft`（草案/待讨论/待施工）/ `deprecated`（废弃）

**历史**：2026-08-09 前使用 `discussion_NNN` / `design_memo_NNN` 双前缀制，因前缀与内容性质错位、编号断档严重而废止。新旧名对照见 §10。
## 9. 待人决策的开放问题汇总

> 以下问题需用户拍板，散落在各主题组内，集中索引便于追踪。

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| 首批 3 策略确认（打板+多因子+事件驱动） | 30_multi_strategy_concurrency §6.1 / G04 | ✅ 已定 v1.2.4（20_first_batch_strategies；主升龙头并入打板，多因子新增） |
| convergence_window 按换手率定（打板1-2/多因子3-5/事件2-3天） | 30_multi_strategy_concurrency §6.4 / G14 | 待首批策略定后校准 |
| 情绪周期定位器准确率评估 | 30_multi_strategy_concurrency §6.3 / G21 | 待评估（28号 v1.2.0 已恢复，可重启评估） |
| regime 检测器业务规则 spec | 30_multi_strategy_concurrency §6.6 / 10_regime_detector_spec | ✅ 已定 v1.5.1 |
| 12 态×N 策略样本量 | 30_multi_strategy_concurrency §6.5 | ✅ 已决策（灰度+软分配） |
| 第二批次策略上线时机 | G11 | 暂缓（首批 track record 后） |
| G15 RegimeMetaAllocator 上线 | G15 | ✅ C1 已通过（852457e9）；待首批策略 3-6 月 PnL + D1 敏感性网格（11号 §0.5.7） |
| **#D1 8 篇设计文档幻影版本事件（15/16×2/28/33/52/55/60号）——全部就绪** | 00号 v2.9.0 git 取证（2026-08-12）+ v2.9.1/v2.9.2 重建联动 | ✅ 闭环：git 历史证明这些文档的"active 高版本"内容**从未提交**（2026-08-11 `git clean -fd`/`git reset --hard` 清除未提交内容；或 v2.5.0 同步时幻觉登记）。**7 篇已于 2026-08-12 04:32 重建**（commit 6a4f5392：33/55/52/15/16catalog/16build_plan→active v1.0.0、27号→draft v0.2.0，依 production 代码回建）；**28号已从 commit a3750b90d1 恢复 v1.2.0（16f119bd）；60号经核查 HEAD 已是 active v1.0.0 完整版（8da7513309，原"骨架"标注过时）** |
| **#D2 34号 测试套件丢失（55 用例）** | 34号 §3.5 已施工设施盘点 / §6 待裁定 | ⚠️ 待用户裁定重建时机（建议首批策略上线前闭环）：`tests/pf_alloc/test_regime_meta_allocator.py` 从未提交、被 git clean 删除不可恢复，须按 34号 §3.4 伪代码 + MOD-PA-007 代码本体重建；重建后立即 git add + commit |
| **#D3 30号 §2.2 对 34号 的引用过时** | 30号 §2.2（2026-08-10 快照） | ⚠️ 待 30号 维护方更新：30号称"34号 框架已 active v1.0.0、代码仍骨架（design 态）"，实际 34号 已 v2.8.1 + 代码 MOD-PA-007 production v1.0.0（含 CRISIS floor 降级 + water-filling 投影，55 测试待重建） |

### 9.1 2026-08-11 第一性原理调研发现的 35 项缺失议题（全部 status=proposed）

> 来源：客观架构师对标专业机构 + 量化社区 + 氛围编程社区的差距分析报告。
> 决策依据：5 条第一性原理（P1 资金安全 / P2 回测可复现 / P3 状态确定性 / P4 决策可追溯 / P5 风险不可累积）。
> 替代机制：项目已有 `ruling_registry.yaml`（裁定#NNN 含 `superseded_by` 链，可推翻）替代 ADR（ADR 不可推翻，对个人项目是过度工程），故不引入 ADR。
> 完整议题内容见 [architecture_issue_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 末尾 35 条新增条目。

#### AI 治理类（10 项，#ARCH-AIGOV-001~010）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-AIGOV-001 | PATH-shim git wrapper 补充拦截 git commit --no-verify（65 号 §7.1 扩展） | P0 致命 | proposed |
| #ARCH-AIGOV-002 | Secret 双层扫描（pre-commit detect-secrets + post-push GitGuardian） | P0 致命 | proposed |
| #ARCH-AIGOV-003 | Library Hallucination 检测（Mypy + Pyright + 包名验证） | P0 致命 | proposed |
| #ARCH-AIGOV-004 | Revertability git 四步纪律（push before risky run） | P0 致命 | proposed |
| #ARCH-AIGOV-005 | 对抗式多 agent（生成/审查/测试分离，禁止单 agent 自审） | P1 高 | proposed |
| #ARCH-AIGOV-006 | AGENTS.md 嵌套就近优先（拆分 327KB 根文件） | P2 中 | proposed |
| #ARCH-AIGOV-007 | 静态分析反馈环（Bandit+Pylint+CodeQL→AI 修复迭代） | P1 高 | proposed |
| #ARCH-AIGOV-008 | 多层 Guardrails（pre/post-input/tool-call/output） | P1 高 | proposed |
| #ARCH-AIGOV-009 | Patchwork Problem 图不变量验证框架 | P2 中 | proposed |
| #ARCH-AIGOV-010 | OWASP Agentic Top 10 安全扫描（agent-audit CI 集成） | P1 高 | proposed |

#### AI 协作类（1 项，#ARCH-AICOLLAB-001，方案已写入 65 号 §12）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-AICOLLAB-001 | Git Worktree + File Lock(TTL) + Task Board 三件套（26 路协调层） | P1 高 | proposed（方案已落 65 号 §12，另一 AI 正施工） |

#### 机构风控类（5 项，#ARCH-RISK-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-RISK-001 | Kill Switch 经纪商侧硬止损（miniQMT 平台崩溃托底） | P0 致命 | proposed |
| #ARCH-RISK-002 | 7-Trigger 熔断器（补"系统错误频发"触发） | P0 致命 | proposed |
| #ARCH-RISK-003 | 14-Check 事前风控（A 股特化） | P0 致命 | proposed |
| #ARCH-RISK-004 | 单笔风控 L1（0.5-1% risk / 最小 R:R 2:1） | P0 致命 | proposed |
| #ARCH-RISK-005 | 3-Tier 回撤协议（Green/Amber/Red 中间态减仓） | P1 高 | proposed |

#### 量化架构类（5 项，#ARCH-QUANT-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-QUANT-001 | 回测-模拟-实盘同一内核（NautilusKernel 式抽象） | P1 高 | proposed |
| #ARCH-QUANT-002 | Crash-only 设计 + 状态外部化（Redis） | P1 高 | proposed |
| #ARCH-QUANT-003 | 53_simulation_live_path 5 态 FSM 状态机代码落地 | P1 高 | proposed |
| #ARCH-QUANT-004 | pf_core / pf_alloc / ex_sor 三个 stub 落地 | P1 高 | proposed |
| #ARCH-QUANT-005 | VaR → ES 范式迁移（ES 进决策层） | P2 中 | proposed |

#### 治理/注册表类（5 项，#ARCH-REG-001~005）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-REG-001 | factor_registry schema + provenance | P1 高 | proposed |
| #ARCH-REG-002 | strategy_registry 退役状态机 | P1 高 | proposed |
| #ARCH-REG-003 | 策略衰减检测（30 天滚动 + 20% 退化阈值） | P1 高 | proposed |
| #ARCH-REG-004 | MLOps 四支柱简化版（无 model card） | P2 中 | proposed（用户已裁定不引入 model card） |
| #ARCH-REG-005 | 多策略独立 sub-book + 归因到"框架决策 vs override" | P2 中 | proposed |

#### A 股特化类（2 项，#ARCH-ASHARE-001~002）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-ASHARE-001 | 北向资金配置型/交易型双结构信号 + regime 信号源 | P1 高 | proposed |
| #ARCH-ASHARE-002 | 情绪周期 6 阶段标准化 + 4 盘面指标自动检测 | P1 高 | proposed |

#### 合规类（1 项，#ARCH-COMPLIANCE-001，P0-5 与 P2-8 合并）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-COMPLIANCE-001 | 2026-06-08 程序化交易新规模块（5000 笔预警 + 撤单率 80% + 存档 20 年） | P0 致命 | proposed |

#### SDD / 审计 / drift / 执行 / CI / 注册表治本（6 项）

| # | 议题 | 优先级 | 决策状态 |
|---|---|---|---|
| #ARCH-SDD-001 | GitHub Spec Kit / AWS Kiro SDD 四阶段闭环 | P2 中 | proposed |
| #ARCH-AUDIT-001 | 简化版 IETF AAT audit trail（SHA-256 + action classification + tamper-evident，砍个体归属） | P1 高 | proposed（用户已裁定简化） |
| #ARCH-DRIFT-002 | Spec drift detection CI job（design_memo 与代码漂移自动检测） | P1 高 | proposed |
| #ARCH-EXEC-001 | 40_execution_broker 10 项 P0 gap 落地 | P0 致命 | proposed |
| #ARCH-CI-001 | CI 真正运行（首次 push origin/dev + 后续自动触发） | P0 致命 | proposed（循环审查第 1 轮追加） |
| #ARCH-REGCAN-001 | ROOR entry_count 自动同步 reconciler（治本元数据漂移） | P1 高 | proposed（循环审查第 1 轮追加） |

#### 已排除项（用户裁定不引入）

| 项 | 不引入理由 |
|---|---|
| P1-10 ADR supersede 链 | 项目已有 `ruling_registry.yaml`（裁定#NNN 含 `superseded_by` 链，可推翻）完美替代 ADR；ADR 不可推翻对个人项目是过度工程 |
| P2-5 model card 部分 | 用户裁定不引入 model card（量化策略不是 ML 模型，无需伦理考虑），保留 MLOps 其他三支柱 |
| 测试覆盖率监控 | 用户裁定不引入（个人项目 158 处 TODO/stub，强制阈值太严；靠对抗式多 agent + 静态分析反馈环已够） |
| 部署运维（Docker 真用） | 用户裁定不引入（65 号 §4.1 已确认 Trae IDE + Windows 本地环境，纯本地开发，Docker 是过度工程） |

#### 状态汇总

- **登记总数**：35 项（全部 `status=proposed`，铁律#9 决策类议题待用户确认）
- **优先级分布**：P0 致命 11 项 / P1 高 17 项 / P2 中 7 项
- **域分布**：AI 治理 10 / AI 协作 1 / 机构风控 5 / 量化架构 5 / 治理注册表 5 / A 股特化 2 / 合规 1 / SDD 1 / 审计 1 / drift 1 / 执行 1 / CI 1 / 注册表治本 1
- **第一性原理覆盖**：P1 资金安全 ✓ / P2 回测可复现 ✓ / P3 状态确定性 ✓ / P4 决策可追溯 ✓ / P5 风险不可累积 ✓
- **用户裁定记录**：Git Worktree 三件套全部加入（写入 65 号 §12）/ SDD 全部加入 / IETF AAT 简化版 / model card 不引入 / 测试覆盖率不引入 / Docker 部署不引入

## 10. 改名对照表（2026-08-09 文档体系重排）

| 旧名 | 新名 |
|---|---|
| discussion_000_discussion_framework.md | 00_index_trading_decision.md |
| design_memo_management_spec.md | 01_design_memo_management_spec.md |
| discussion_001_regime_detector_spec.md | 10_regime_detector_spec.md |
| discussion_002_regime_backtest_validation_plan.md | 11_regime_backtest_validation_plan.md |
| discussion_017_phase2_model_quality_validation.md | 12_regime_phase2_validation.md |
| discussion_019_phase3_engineering_plan.md | 13_regime_phase3_engineering_plan.md |
| discussion_023_s2_algorithm_misalignment_diagnosis.md | 14_regime_s2_diagnosis.md |
| discussion_003_first_batch_strategies.md | 20_first_batch_strategies.md |
| design_memo_001_multi_strategy_concurrency.md | 30_multi_strategy_concurrency.md |
| design_memo_004_position_sizing.md | 31_position_sizing.md |
| design_memo_010_execution_broker.md | 40_execution_broker.md |
| discussion_018_backtest_observability_workplan.md | 50_backtest_observability_workplan.md |
| discussion_022_panel_experiment_history_tab_and_mlflow_retirement.md | 51_panel_experiment_history_mlflow_retirement.md |
| discussion_020_methodology_open_questions.md | 90_methodology_open_questions.md |
| discussion_021_density_prediction.md | 91_density_prediction.md |

> 旧"编号占用表"预定坑位（design_memo_002/003/005-009/011-013、discussion_004-016）同步废止，未来文档按 §8 段位规则命名。
> ✅ 已修正（2026-08-09）：discussion_004 §2.1/§2.2 全仓统一替换为 13_regime_phase3_engineering_plan §2.1/§2.2——13 号文档即代码所引用内容，章节号完全对应，无需补落盘。

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-06 | 1.0.0 | 初稿 | 建立 28 个主题组（G01-G28）的讨论框架路线图，供多 AI 分工认领；梳理依赖关系与 3 条并行轨道；建立产出物编号占用表 |
| 2026-08-07 | 1.1.0 | §7.3 标记 G04/G12/G22 认领状态为已分配 | 三主题组分配给并行 AI 开工，避免后续编号撞车 |
| 2026-08-08 | 1.2.0 | 20_first_batch_strategies 占用状态更新为 ✅ v1.0.0；§9 首批3策略开放问题标记已定 | G04-AI 落盘 20_first_batch_strategies（首批3策略=打板+多因子+事件驱动；主升龙头并入打板，多因子新增；§1.4 对齐 charter §3 裁定 Model A 非 Citadel pod） |
| 2026-08-08 | 1.3.0 | 20_first_batch_strategies 占用状态同步至 ✅ v1.2.0（补施工流程+灰度判据）；G22 40_execution_broker 状态更新为"代码已施工" | 20_first_batch_strategies 经多轮审查迭代至 v1.2.0（补施工环节流程算法+2026灰度判据）；G22-AI 完成 40_execution_broker 代码施工（commit 015826ae） |
| 2026-08-08 | 1.4.0 | 51_panel_experiment_history_mlflow_retirement 落盘登记 | Panel 实验历史 Tab + mlflow 退役施工计划定稿（50_backtest_observability_workplan M2 下游），补 §七 10 项施工算法补遗 + §八 4 项后续增强登记 |
| 2026-08-09 | 2.1.0 | §3 G06 产出物改为 `22_sector_rotation_spec.md`；§7.3 discussion_004 占用行澄清为编号冲突；全仓 `discussion_004`→`13_regime_phase3_engineering_plan`（保留 §2.1/§2.2 章节号） | `discussion_004` 从未落盘，代码/11号文档误用此号引用 13 号文档（Phase 3 降维 §2.1 + 校准器 §2.2）；G06 板块轮动与 regime 降维无关 |
| 2026-08-09 | 2.2.0 | §0 目录 14_regime_s2_diagnosis 状态 active→draft、51_panel 状态 draft→active 对齐各文档 frontmatter；补登 12/13/14/50/90/91 六篇改名修订记录 | 00_index §0 目录与各文档 frontmatter status 一致性；上一轮改名工程遗漏的六篇修订记录补齐 |
| 2026-08-09 | 2.3.0 | §0 目录 15→38 篇（新增 23 篇骨架文档行 + 状态图例）；§7.3 占用表 23 项状态更新为"骨架已建 v0.1.0"，补登 22_sector_rotation_spec（G06）占用行 | 施工图骨架先行：G01-G28 全部待讨论主题组的产出物骨架一次性落盘（frontmatter status=draft，仅含主题组信息+讨论要点清单，§2-§6 待填空），统一结构后再逐篇讨论填空；22 号此前仅有 discussion_004 澄清行、无独立占用行 |
| 2026-08-09 | 2.3.1 | 关联行+§3/§5/G22 产出物行修复 7 处重复后缀断链（`_name_name.md`→`_name.md`，涉及 30/10/11/31/40 号） | 改名工程遗留：段位前缀重复拼接产生断链，全量断链扫描发现并修复 |
| 2026-08-09 | 2.4.0 | 15 篇有内容文档文档头统一登记：frontmatter 字段集/顺序统一（补齐 title/owner/language/topic/scope，12/13/14 的 doc_id/priority/depends_on 等扩展字段保留），H1 去前缀与 title 对齐（废止"讨论框架·/讨论文档·/讨论·/设计备忘·/讨论稿：/NN_filename —"六种混用风格），修订记录各补一行（14 号补建修订记录章节）；00 自身同步 | 骨架体系收尾：结构统一只动文档头元数据与标题行，章节编号与正文内容零变更、零遗漏风险；规范真源见 01_design_memo_management_spec §4.2/§4.3（v1.1.1 同步） |
| 2026-08-10 | 2.4.1 | 40号 v2.9.0→v2.9.1 版本同步：§2.12通道平权行补2026-07-31正式关闭局域网行情通道事件 | 40号§2.12监管约束表"通道平权"行从"已推进"更新为完整事件描述——2026-07-31交易所正式关闭局域网行情通道，微秒级延迟→毫秒级，量化从拼速度转向拼深度，与项目中低频+因子驱动定位一致 |
| 2026-08-10 | 2.5.0 | 系统性版本同步+61号arXiv:2608.01789整合 | ①批量frontmatter核对发现21个文档已升级为active但00_index仍标注"骨架v0.1.0"（15/21-23/25-26/28/32-37/41-42/52-55/60-61），§0目录表+§7.3占用表共40处版本引用更新为实际frontmatter版本；②61号§3.2补arXiv:2608.01789自主Alpha发现综述六组件统一框架作为理论参照（八篇候选统一分类视角，Memory组件覆盖最薄弱印证FactorMiner独特价值）|
| 2026-08-10 | 2.6.0 | 系统性版本同步第二轮+缺失文档补登+61号漂移检测体系增强 | ①§0目录补登5篇缺失文档（16号×2/18号/62号/63号）；②§0目录+§7.3批量版本同步：36号v1.0.0→v1.2.0/55号骨架→v1.21.0/54号骨架→v1.13.0/60号骨架→v1.8.0/61号骨架→v2.9.1/30号v1.3.0→v2.5.0/31号v1.2.0→v1.23.0/G02 v1.3.1→v1.9.25/G03 v1.0.0→v1.10.0；③G09状态从"骨架v0.1.0"更正为"active v1.12.6"（重大状态失同步修复）；④G16/G17/G18/G25/G26/G27/G28状态从"待讨论/框架已定"更新为对应active版本号+修复6处重复后缀断链；⑤61号§3.3漂移检测体系补Modular CP via Residual Decomposition（arXiv:2510.04406阶段级归因）+SA-BCP（arXiv:2605.00432时空解耦CP），漂移归因从"特征级→资产级"扩展为"特征级→阶段级→资产级"三级体系 |
| 2026-08-10 | 2.7.0 | §0目录+§7.3补登19号 | 北向日频断档后实测 akshare 三接口失效/tushare hk_hold 季度末可行，新建 19_northbound_hold_snapshot 施工计划（fetcher+落表+外资行为方法论），1x段位新占19号 |
| 2026-08-10 | 2.7.1 | §0目录+§3+§7.3+§9 第三轮系统性版本同步 | 持续改进：用户要求"再次审查文档所有内容+施工环节流程算法有缺失+选项之外更好的答案算法+全网搜 2026年8月今天最新研究+文档结构顺序内容调整+持续改进不要停下来询问"。frontmatter 批量核对发现 4 篇文档版本失同步：①10号 v1.3.1→v1.9.31（§0目录/§3 G02/§7.3/§9 开放问题 4 处）；②25号 v1.12.6→v1.12.11（§0目录/§3 G09/§7.3 3 处+施工算法数 6→8）；③35号 v1.30.6→v1.32.0（§0目录/§3 G16/§7.3 3 处）；④36号 v1.2.0→v1.6.0（§0目录/§3 G17/§7.3 3 处）。本轮同步为版本号对齐，无文档结构调整 |
| 2026-08-10 | 2.8.0 | §0目录补登 64 号+§7.3 占用表补登 64 号 | 用户要求新建专门聊"数据集成下载/数据下载/数据源"的设计备忘录，把项目里所有已施工落盘的数据源/下载相关内容全面写入作为讨论升级载体。64_data_source_download_spec.md 落盘（6x 段位 64 号·跨切治理层，1x 地基层 10-19 已满；与 63 号数据利用审计配套——63 审"用得怎么样"64 审"下得怎么样"）。spec 工程详设类，§3-§10 按数据获取管线 8 对象分节，§12 缺口与升级方向含 12 项待裁定+12 个开放问题。§0 目录 43→44 篇 |
| 2026-08-10 | 2.8.1 | §0目录+§3 G16+§7.3 35号版本同步 | 35_drawdown_protocol_impl frontmatter 已升级至 v1.34.0，00_index 三处版本引用仍标 v1.32.0（§0目录第56行/§3 G16状态行第310行/§7.3占用表第603行），本次同步为 v1.32.0→v1.34.0 版本对齐，无文档结构调整 |
| 2026-08-10 | 2.8.2 | §0目录+§3+§7.3+§9 第三轮版本同步 | 第三轮版本同步——10号 v1.9.31→v1.9.37、24号 v1.9.4→v1.9.7、40号 v2.9.1→v2.9.2，三处 frontmatter 版本漂移修复 |
| 2026-08-12 | 2.9.0 | **AI-12 审查轮：git 灾难取证 + 幻影版本更正 + 65号补登 + C1 状态全面刷新**——① **git 取证确认 8 篇幻影版本**（15/16×2/28/33/52/55/60号）：`git log --all -S` 证明其"active 高版本"内容从未在任何提交存在，2026-08-11 git 灾难（`git clean -fd`/`git reset --hard` 清除未提交内容）后当前均为骨架 v0.1.0，§0/§3/§7.3 三处同步更正并标"待重建"（28号 v1.2.0 可从 commit a3750b90d1 恢复；33/52/55/60号 代码均已 production 可依代码回建）；② **65_git_safety_governance 补登** §0 目录（44→47 篇）+ §7.3 + §0 头部注记 AI_review_instructions.md 为操作手册不入编号；③ **全表版本对齐 2026-08-12 工作树 frontmatter**（10号 v1.9.37→v1.5.1 / 11号 v1.10.0→v1.5.2 / 20号 v1.2.4 / 35号 v1.37.0 / 36号 v1.10.0 / 61号 v2.10.0 / 62号 v1.32.0 / 63号 v2.0.0 / 64号 v1.2.1 / 18号 active v0.2.0 等 20+ 处）；④ **§2 三层快照刷新**（8 阶段 why 已覆盖 / 4 部分覆盖 / 0 全空白）；⑤ **G15 全部"等 C1"标注更新**为"C1 已通过（852457e9），参数待策略 PnL + D1 校准"（§0/§3/§4/§5/§6/§7.3/§9 共 8 处）；⑥ **§3 标题 G01-G23→G01-G29 + 新增 G29**（64号 数据源下载体系，补全 §7.3 既有登记对应的主题组定义）；⑦ **§9.1 architecture_issue_registry.yaml 断链修复**（`../../../../` 多一级 → `../../../`）；⑧ **§9 新增 3 项待裁定**：#D1 文档丢失事件 / #D2 34号 测试套件丢失（55 用例未提交被删）/ #D3 30号 §2.2 对 34号 引用过时；⑨ **G15 讨论要点③"60 日 Sharpe"修正为"60 日 Sortino"**（对齐 34号 v1.2.0 起真源口径）；⑩ **§7.3 补登缺失行**（14/16×2/17/18/62/63/65号）+ 表头注明转为历史认领记录。frontmatter v2.8.2→v2.9.0 | AI-12 任务驱动审查（34/00号 双文档）：发现 v2.5.0 起多轮"版本同步"登记的 8 篇高版本为幻影（从未提交 git），C1 已于 08-08 通过但全索引 8 处仍标"等 C1"，65号（§9.1 已引用）未入目录，G15 讨论要点③仍写 Sharpe 与 34号 Sortino 真源矛盾，§9.1 注册表链接断裂。本轮为索引准确性大修，无主题组增删决策（G29 为 §7.3 既有登记的定义补全） |
| 2026-08-12 | 2.9.1 | **7 篇骨架重建联动修正（循环审查第 2 轮新发现）**——另一 AI 会话于 04:32 提交 commit 6a4f5392 重建 7 篇骨架文档（33/55/52/15/16catalog/16build_plan→active v1.0.0、27号→draft v0.2.0，依 production 代码回建），本索引 v2.9.0 的"骨架待重建"标注随之部分过时。本轮同步：§0 目录 7 行（15/16×2/27/33/52/55号）+ §0 头部 ⚠️ 标注（7 篇已重建/仅剩 28+60号）+ §2 快照（03/08 行 + 结论）+ §3 状态（G01/G14/G15 v2.8.1/G23/G26）+ §7.3 同 7 行 + §9 #D1 改"部分闭环"（仍待裁定：28号恢复/60号重建）+ #D3 34号版本引用更新。**未变**：28号（可从 a3750b90d1 恢复 v1.2.0）与 60号（骨架）待重建、34号 测试套件（55 用例）丢失待重建。frontmatter v2.9.0→v2.9.1 | 循环审查自检发现：v2.9.0 提交准备期间，7 篇骨架已被另一 AI 重建提交（6a4f5392），索引须联动保持准确——本轮为重建联动修正，无新主题组/决策变更 |
| 2026-08-12 | 2.10.0 | **作战地图全覆盖工程（BM 339 环节逐环节核对闭合）**——以 PG `battle_map_steps` 为真源全量核对 design_memos 覆盖：① **新建 43号**（G30 合规与交易纪律体系，draft v0.1.0，承载 BM-BUY-08-A/08-B/09/12/15）；② **26 篇补环节设计/裁定**：41号 v1.6.0（明日预案双层架构 BM-PLAN-01/02/03 + 上游四轨裁定）、61号 v2.13.1（研究知识流水线拍板+研究环境否定式裁定+运行时风险治理 BM-RC-09/04-F）、40号 v2.10.1（§2.8 盘前检查链 BM-RC-02/02-C）、53号 v1.7.3（§3.9 仿真域 why 回填 BM-SIM-03/04/06/07）、52号 v1.0.3（辅助组件契约+暂缓裁定）、42号 v1.6.2（§3.11 卖出闭环优化）、31号 v1.24.2（§2.8 持仓漂移与再平衡）、32号 v1.0.22（组合优化口径裁定）、35号 v1.38.2（否决执行引擎 BM-RC-10/10-A）、36/37/54/55/62/15/51/17/64/90/91/21/24/25/20/34/23/10 号同步补丁；③ **环节级锚定**：全部活跃环节（320/339，19 弃用除外）正文显式标注 BM 编号至承载小节，可检索可追溯；④ §0 目录 47→48 篇 + G30 主题组登记 + §2 快照 12 阶段全部"已覆盖"（60号 骨架待重建除外）+ §7.3 补登 43号。否定式裁定（不建设/暂缓+重评条件）经用户 2026-08-12 裁定认可。遗留：battle_map 真源 3 处成熟度口径修正登记在 61 §7.5 / 52 §7 待治理流程回写 DB | 用户裁定驱动：design_memos 须包含作战全景图全部环节流程供后续完整开发；四路语义审计（221 环节）发现 GAP 32 项+PARTIAL 72 项，按"能合并不新建"偏好仅新建 43 号一篇，其余全部并入现有备忘 |
| 2026-08-12 | 2.10.1 | **全覆盖复核补锚 3 活跃环节 + 28/60号状态回归修正**——① PG `battle_map_steps` 复核（340 环节/19 deprecated/321 活跃，BM-SIM-08 新入库 +1）：发现 3 个活跃环节未逐编号锚定，补锚 24号 v1.10.4（BM-SEL-23-C 情绪周期策略映射→§3.5 门控切换/§3.6 仓位上限 5 档、BM-SEL-25-B 情绪周期自适应权重→§3.5 `determine_adaptive_weights`）+ 53号 v1.7.4（BM-SIM-08 Paper Matching 涨跌停排队引擎→§3.2 Step②/公式②），321 活跃环节恢复 0 缺口；② §2 快照口径更新 339→340 环节、320→321 活跃；③ 修正 v2.10.0 合并回归——28号/60号 状态误回退为"骨架待重建"，实际 28号 v1.2.0 已恢复（16f119bd）、60号 active v1.0.0 已在 HEAD（8da7513309），重放 v2.9.2 更正至 §0 头部注记/§0 目录×2/§2 快照行 12+结论/§6 G21 行+结论/§9 定位器评估行/#D1 闭环共 8 处；④ §0 目录版本对齐 24号 v1.10.4 / 53号 v1.7.4 | 全覆盖工程收口复核：以 DB 当前真源（340 环节）重扫发现 BM-SIM-08 等 3 个活跃环节漏锚（语义早已覆盖、编号未显式）；同时发现 v2.10.0 合并时 28/60号状态文本覆盖了 v2.9.2 的已恢复标注，一并修正 |
| 2026-08-14 | 2.11.0 | **29号补登（潘潘课程因子策略提炼知识库迁入）**——§0 目录 48→49 篇 + §7.3 占用表补登 29 号；29_factor_strategy_extraction.md（原 docs/_working/潘潘直播课程/因子与策略提炼.md，546 条 F1-F8 因子+S9-S16 策略，二十一轮审查收敛）经用户裁定迁入 design_memos 落位 2x Alpha 策略层，frontmatter 按 01 号规范 §4.2 规范化（ttl→permanent），factor/strategy/risk_limit 三注册表 doc_ref 同步更名；capability_canonical_file_registry token 沿用（auto-panpan-factor-extraction-20260810） | 用户裁定驱动：提炼知识库作为三注册表 doc_ref 真源应落位永久区而非 _working 临时区（task_bound 易被 TTL/wipe 类进程误删，已实证两次）；迁入后命名合规（段位号+snake_case） |
| 2026-08-17 | 2.11.1 | **68 号补登（代码与算法多模型审查流水线）**——§0 目录 49→50 篇（标题篇数由 48 同步修正为 50，29 号 v2.11.0 补登时标题滞后一并修正）；68_code_algorithm_review_pipeline.md 落位 6x 跨切治理层（67 号已占用迁出，取下一空号 68），draft v1.0.0 待用户裁定（待定问题 4 项：模型版本渠道/首审批次/token 预算/周审查窗口） | 用户指令驱动：建立施工后审查线——多模型轮流审查已 merge 模块代码/算法/运行情况，与前方施工线双线并行，统一由统筹会话调度；与 AI_review_instructions（审文档 why 层）、55 号（监控基建）、pre-commit 门禁（L1 机械检查）互补不重叠 |
| 2026-08-17 | 2.11.2 | 68 号描述同步更新（§0 目录 68 号一句话）：v1.0.0→v1.1.0——只读纪律推翻→自主治本修复，双线并行→5+5 并发制，新增冲突防护五机制+止损降级线+全自动化零打扰两个打扰例外，执行蓝本补登 audit_prompts_20_ai.md；§5 待裁定重排（删报告存放、增模型-域绑定表与提示词落盘形态） | 用户裁定驱动：68 号 v1.0.0 初稿设计（审查线只登记+双线串行）被用户推翻，按用户"并发执行且审查与自我循环修复全自动化尽量不问用户"裁定修订为 v1.1.0；索引描述随之同步更新 |
| 2026-08-17 | 2.11.3 | 68 号描述同步更新（§0 目录 68 号一句话）：v1.1.0→v1.2.0——模型池确认（Kimi-K3/GLM-5.3/Qwen3.8-Max，Trae CN 选择器手动切换）+§2.3 轮换矩阵落地+新增决策十一调度卡协议（切模型/执行任务/一键复制指令三要素）+§8 附录指令模板库（初审修复/复审/红队/调度卡示例），待裁定 #4/#5 与待定问题 #1 闭环 | 用户裁定驱动：三模型版本与 Trae CN 切换工作方式确认（每对话完成须输出下一步切模型+任务+一键复制指令），68 号 v1.2.0 落地调度卡任务链机制，索引描述同步 |
| 2026-08-21 | 2.11.4 | **44 号补登（盘前与盘中决策支持升级，28/41/90 号升级备忘）**——§0 目录 50→51 篇 + §7.3 占用表补登 44 号；44_premarket_intraday_decision_upgrade.md 落位 4x 交易流层（40-43 已占用，取下一空号 44），draft v0.1.0 待 Owner 裁定（登记三缺口：M1 大盘情绪实时分析增量/M2 盘中次日预案边界修正/M3 盘前综合预判；CAND 登记因 candidate_module_registry.yaml 正被残余四项专项批写入，按并发纪律缓办） | Owner 三问核查驱动：实证 MOD-SIG-025 缺加速度/板块属性映射/剩余走势推演三增量、BM-SEL-04 暂缓裁定下 T+1 走边界修正替代路线、MOD-PLAN-002 缺盘前修正器——新建升级备忘与 28/41/90 号互引，不产生第二真源 |
| 2026-08-21 | 2.11.5 | 44 号 v0.1.0→v0.2.0 版本同步（§0 目录+§7.3 两处）：全网调研+审查升级——M1 扩容 4→7 增量、M3 扩容 4→5 增量、新增 §2.1 因子定性裁定（6 条 FCT-sentiment 登记清单）+§6 数据源盘点+§9 施工算法七件（9.1-9.7），描述同步更新 | Owner 指令驱动：审查施工算法缺失+选项外更优算法+2026-08 最新研究整合（护盘实证/权重掩护三特征/开盘啦情绪五维/外盘四通道+龙虎榜溢价） |
| 2026-08-21 | 2.11.6 | 44 号 v0.2.0→v0.3.0 版本同步（§0 目录+§7.3 两处）：新增 M1-⑧ 期指基差+M3-⑥ 期指三时点通道、§11 四项建议裁定（三缺口认可/CAND 前缀/日韩用途/期指通道）、§9.8 期指算法、§6 竞价采集口径更正（auction_book 已有） | Owner 第四问驱动（股指期货+白天美股期指盘中影响）：实证项目期货地基（kline_futures 311 万行/futures_position L1 轮询/index_quote 现货腿，唯一缺口=tick 采集 symbols 未配置） |
| 2026-08-21 | 2.11.7 | 44 号 v0.3.0→v1.0.0 翻正 active（§0 目录+§7.3 两处）：§11 四项建议裁定 Owner 全批+追加裁定五（ES/NQ 盘中实时下载+实时分析，主源新浪 hf_ES/hf_NQ 秒级延时+L1 调度族 1 分钟轮询），§9.8 通道3 升级完整规则，状态 draft→active | Owner 批准驱动+机构实践核实：跨市场台亚洲时段必看美股期指/量化社区免费实时方案=akshare futures_foreign_commodity_realtime（新浪） |
| 2026-08-21 | 2.11.8 | 44 号 v1.0.0→v1.1.0 版本同步（§0 目录+§7.3 两处）：华泰机构范式整合——新增 M1-⑨ 期权情绪三件套（PCR+IV Rank+Skew）/M3-⑦ 盘后资金面四件套（两融/主力/大宗/ETF 申赎）/M3-⑧ 事件日历联动+竞价三细节+M2 修正有效期，§9 算法 8→12 件，FCT 清单 8→10 条 | Owner 持续改进指令驱动：华泰证券 2026-03-17 A 股情绪指数研究（PCR+IV 两衍生品/融资+ETF 申购+CDS 三资金/非对称买卖夏普 1.07）+期权实战口径（2026-08-14）整合；实证两融/大宗/money_flow/option_iv/calendar_event 均已在库 |
| 2026-08-21 | 2.11.9 | 44 号 v1.1.0→v1.1.1 版本同步（§0 目录+§7.3 两处）：§9.12 补 A50 期货交割日规则（每月倒数第 2 个工作日，新交所，交割前夜外资调仓→次日跳空；敏感度升半档+A50 通道权重上调 0.45），§6 事件日历行更正（写入任务未注册=P0-4② 挂账，A50 交割为第 13 类 event_type 候选） | Owner 指令驱动：特殊交易日盘点核查（17 号台账实证 calendar_event_refresh 未注册），A50 交割日 17 号 §2.4 已登记待评估且与 44 号 A50 通道直接联动 |
| 2026-08-21 | 2.11.10 | 44 号 v1.1.1→v1.1.2 版本同步（§0 目录+§7.3 两处）：新增 M1-⑩ 板块分歧度与轮动速度计（消费 22 号 5 状态/虹吸态+新增电风扇速度计/个股分歧度两因子）+§9.13 算法+§9.5 降档触发补两条，FCT 清单 10→12 条 | Owner 板块分歧核查驱动："电风扇无主线→混沌中继/板块分歧→见顶/个股分歧→见顶中继"三命题规则化；实证 22 号体系已完整（sector_rotation_state/sector_siphon 已落码），真实缺口=消费接入断裂+两因子未独立 |
| 2026-08-21 | 2.11.11 | 22 号 v1.8.0→v1.9.8 版本同步（§0 目录一处，顺带修正 v1.8.0→v1.9.7 历史漂移）：22 号 §2.4 补"电风扇速度计已升级为独立因子"跨文档登记（44 号 M1-⑩/§9.13，rotation_velocity+top3_overlap+lead_streak 无主线判定→M2 降档），22 号 §2.3/§2.4 为其设计真源锚点 | Owner 指令驱动：把"电风扇行情口径有未落成独立因子"的升级状态写入文档——44 号因子设计+22 号锚点登记双向互引闭环 |
| 2026-08-21 | 2.11.12 | 44 号 v1.1.2→v1.2.0 版本同步（§0 目录+§7.3 两处）：Owner 四问批次——新增 M3-⑨ LLM 盘后分析（DeepSeek-V4-Flash+PIT 回填四铁律+llm_daily_analysis 新表）+§9.14+§12 附录（M4 日志体系 4 缺口/外部短板复核 5 条全有主/开源评估 15 项/Tito 提取 2 因子+MA10 gate） | Owner 四问驱动（短板复核/日志体系/开源评估/LLM 数据源+Tito）：DeepSeek 官方定价实证、TradingAgents v0.3.0 决策日志同构借鉴、optuna/Numba 候选引入 |
| 2026-08-21 | 2.11.13 | **56/57 号补登（P0 批两件）**——§0 目录 51→53 篇：56_backtest_vs_sim_reconciliation_plan.md（P0-1② 回测 vs 模拟盘对账方案，不变量 I1-I4+三层 diff+归因三分类+对照清单，G1/G6 转 Owner 窗口）+57_daily_cycle_sop.md（P0-5 日循环 SOP，六环节命令清单+开盘前 QMT 人工确认项+缺口 GAP1-5 登记+首跑彩排记录已过），均 active v1.0.0 | P0 批施工驱动：到期前目标态（交易日模拟盘+收盘后回测对账）的两件承载文档落位 5x 验证与可观测性层 |