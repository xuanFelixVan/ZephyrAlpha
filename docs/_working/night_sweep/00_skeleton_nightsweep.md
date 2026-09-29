---
asset_id: "DOC:docs/_working/night_sweep/00_skeleton_nightsweep.md"
ttl: "task_bound"
title: "夜战骨架补干册——全流通 132 环节状态总表与开口项映射（2026-09-29）"
session: st-nightsweep-sw1-20260929
completes_when: "开口环节全部翻绿或登记 Owner 门位后本册归档"
---

# 夜战骨架补干册——全流通 132 环节状态总表

> **一句话**：总纲 §一"补干挖矿"的环节总表交付件——132 环节 × 状态轴[已通/开口/等Owner] × 开口项(审计卡号/接线缺口) × 处方指针，一行不缺。
> **真源四件**（本表全部机判可复跑，禁手改数字）：①`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122 状态列，built 81/partial 30/design 5/missing 6）②`docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增 10 环，合计 132）③`docs/_working/wiring_gap_inventory_20260927.md`（四层未接线：59 零引用表/13 无环节域/41 未接线环节/38 TDM null）④`.runtime/tmp/st-legacy-audit-20260929/canonical.json`（审计 534 卡：DONE 218/UNDONE 108/PARTIAL 84/OWNER_GATE 75/ABSORBED 29/OBSOLETE 11/UNVERIFIABLE 9）。
> **状态轴判定规则（机械，可复核）**：有 OWNER_GATE 卡或明确 Owner 判定项（F95 31 项/F121 M0 待裁）→ 等Owner；基态 partial/design/missing（总册自报）或有 UNDONE/PARTIAL 卡或在接线清单 §1.4 名单或为 F123-F132 新环 → 开口；其余 → 已通。
> **开口环节补挖规则**：按总纲 §一，对开口环节逐个补挖矿卡（六向台账快照+自审闸三态+处方），落本目录；谁挖干谁先开工，不等总筹点头。处方指针=fullconnect 战役 per-F 卷（若该件仍在暂存/untracked 以 git show :path 读）。

## 环节总表（132 行）

| 环节 | 名称(基态/优先) | 状态轴 | 开口项(卡号/接线缺口) | 处方指针 |
|---|---|---|---|---|
| F001 | 多源采集调度（built/P1） | 开口 | 卡:C192,C252,C253 | docs/_working/fullconnect_campaign/a_data_foundation/01_f01_multi_source_ingest.md |
| F002 | 数据源接入生命周期（partial/P0） | 开口 | 卡:C226 | docs/_working/fullconnect_campaign/a_data_foundation/02_f02_source_onboarding_lifecycle.md |
| F003 | Provider 实现与源路由（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/03_f03_provider_routing.md |
| F004 | 清洗校验与坏数修复（partial/P0） | 等Owner | 卡:C46; Owner卡:C66 | docs/_working/fullconnect_campaign/a_data_foundation/04_f04_cleaning_validation.md |
| F005 | 判重与数据审计（built/P2） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/a_data_foundation/05_f05_dedup_audit.md |
| F006 | CH 热库落库（built/P1） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/a_data_foundation/06_f06_ch_hot_warehouse.md |
| F007 | PG 架构库（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/07_f07_pg_arch_db.md |
| F008 | 冷库归档运维（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/08_f08_cold_archive.md |
| F009 | 备份 3-2-1 双链（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/09_f09_backup_chain.md |
| F010 | 行情订阅分发（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/10_f10_quote_subscribe.md |
| F011 | TDM 交叉轴挂接（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/11_f11_tdm_crossaxis.md |
| F012 | 产业链图谱（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/a_data_foundation/12_f12_industry_chain_graph.md |
| F013 | E0 算力调度心跳（partial/P1） | 开口 | 卡:C252,C74 | docs/_working/fullconnect_campaign/b_factory_inbound/01_f13_e0_compute_gate.md |
| F014 | E1 想法进货编排（partial/P1） | 开口 | 卡:C253 | docs/_working/fullconnect_campaign/b_factory_inbound/02_f14_e1_intake_orchestration.md |
| F015 | 车道A·社区货源（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/b_factory_inbound/03_f15_lane_a_community.md |
| F016 | 车道B·AI 生成（partial/P1） | 开口 | 卡:C252 | docs/_working/fullconnect_campaign/b_factory_inbound/04_f16_lane_b_ai_gen.md |
| F017 | 车道C·公式挖掘机（partial/P1） | 开口 | 卡:C235 | docs/_working/fullconnect_campaign/b_factory_inbound/05_f17_lane_c_formula_mining.md |
| F018 | 车道D·产业链三高（partial/P1） | 开口 | 卡:C242 | docs/_working/fullconnect_campaign/b_factory_inbound/06_f18_lane_d_three_high.md |
| F019 | 车道E·模型基线（partial/P2） | 开口 | — | docs/_working/fullconnect_campaign/b_factory_inbound/07_f19_lane_e_model_baseline.md |
| F020 | 车道G·全网搜索进货（partial/P1） | 开口 | 卡:C251 | docs/_working/fullconnect_campaign/b_factory_inbound/08_f20_lane_g_stomach_intake.md |
| F021 | E2 假说预审逻辑门（partial/P1） | 开口 | 卡:C252,C253 | docs/_working/fullconnect_campaign/b_factory_inbound/09_f21_e2_hypothesis_precheck.md |
| F022 | E3 构造与翻译（partial/P1） | 开口 | 卡:C251 | docs/_working/fullconnect_campaign/b_factory_inbound/10_f22_e3_construct_translate.md |
| F023 | E4 考试咽喉（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/c_exam_pipeline/01_f23_e4_exam.md |
| F024 | E5 协同去重（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/c_exam_pipeline/02_f24_e5_synergy_dedup.md |
| F025 | E6 入库监控（built/P1） | 开口 | 卡:C74 | docs/_working/fullconnect_campaign/c_exam_pipeline/03_f25_e6_intake_monitor.md |
| F026 | E7 模拟盘前哨（missing/P0） | 开口 | 卡:C376; missing§1.4 | docs/_working/fullconnect_campaign/c_exam_pipeline/04_f26_e7_paper_outpost.md |
| F027 | E8 组装与资金分配（partial/P0） | 开口 | — | docs/_working/fullconnect_campaign/c_exam_pipeline/05_f27_e8_assembly_allocation.md |
| F028 | E9 实盘归因（partial/P0） | 开口 | — | docs/_working/fullconnect_campaign/c_exam_pipeline/06_f28_e9_live_attribution.md |
| F029 | 工厂进货台账与出生证（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/c_exam_pipeline/07_f29_factory_ledger_birth_cert.md |
| F030 | L9 源线·行情基本面族（missing/P1） | 开口 | 卡:C46; missing§1.4 | docs/_working/fullconnect_campaign/d_l9_knowledge/01_f30_源线行情基本面.md |
| F031 | L9 源线·另类数据族（missing/P2） | 开口 | missing§1.4 | docs/_working/fullconnect_campaign/d_l9_knowledge/02_f31_源线另类.md |
| F032 | L9 图谱谱系（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/d_l9_knowledge/03_f32_图谱谱系.md |
| F033 | L9 状态变量快照（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/d_l9_knowledge/04_f33_状态变量快照.md |
| F034 | L9 知识供给汇聚（missing/P0） | 等Owner | 卡:C41; Owner卡:C67; missing§1.4 | docs/_working/fullconnect_campaign/d_l9_knowledge/05_f34_知识汇聚.md |
| F035 | L9 决策假设与一问一考（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/d_l9_knowledge/06_f35_一问一考.md |
| F036 | L9 治理横切（partial/P2） | 开口 | — | docs/_working/fullconnect_campaign/d_l9_knowledge/07_f36_治理横切.md |
| F037 | L0 盘前作战计划（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/e_decision_chain/01_f37_l0_premarket_plan.md |
| F038 | L1 大盘总闸+六传感器（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/e_decision_chain/02_f38_l1_market_gate.md |
| F039 | L2 板块选择（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/e_decision_chain/03_f39_l2_sector_selection.md |
| F040 | L3 个股选择（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/e_decision_chain/04_f40_l3_stock_selection.md |
| F041 | L4 买卖点与执行（built/P0） | 开口 | 卡:C202 | docs/_working/fullconnect_campaign/e_decision_chain/05_f41_l4_execution.md |
| F042 | P1 持仓体检（built/P1） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md |
| F043 | P2 做T与加减仓（built/P1） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/e_decision_chain/07_f43_p2_t_trade_rebalance.md |
| F044 | P3 加仓决策（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/e_decision_chain/08_f44_p3_pyramiding.md |
| F045 | S1 卖出信号收集评分（built/P0） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/e_decision_chain/09_f45_s1_sell_signal.md |
| F046 | S2 离场执行（built/P0） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/f_exec_risk/01_f46_s2_exit_execution.md |
| F047 | R1 应急保命（built/P0） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/f_exec_risk/02_f47_r1_emergency_lifeline.md |
| F048 | C1 预算切分（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/03_f48_c1_capital_budget_split.md |
| F049 | C2 组合聚合（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/04_f49_c2_portfolio_aggregation.md |
| F050 | C3 绩效归因反馈（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/05_f50_c3_attribution_feedback.md |
| F051 | 币圈决策骨架（missing/P2） | 开口 | 卡:C267; missing§1.4 | docs/_working/fullconnect_campaign/f_exec_risk/06_f51_crypto_decision_skeleton.md |
| F052 | 验证方法学与决策算法库（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/07_f52_validation_methodology_dal.md |
| F053 | 订单生命周期与预检（built/P0） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/f_exec_risk/08_f53_order_lifecycle_precheck.md |
| F054 | 打板执行族（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/09_f54_daban_execution_family.md |
| F055 | 执行算法路由 SOR（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/f_exec_risk/10_f55_sor_algo_routing.md |
| F056 | QMT/miniQMT 桥（built/P0） | 等Owner | 卡:C46; Owner卡:C42,C63 | docs/_working/fullconnect_campaign/f_exec_risk/11_f56_qmt_broker_bridge.md |
| F057 | 结算对账与三方核对（built/P0） | 开口 | 卡:C107 | docs/_working/fullconnect_campaign/f_exec_risk/12_f57_settlement_reconciliation.md |
| F058 | 执行成本反馈（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/01_f58_execution_cost_feedback.md |
| F059 | 风控限额与止损引擎（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/02_f59_risk_limit_stoploss.md |
| F060 | 回撤状态机与熔断（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/03_f60_drawdown_state_machine.md |
| F061 | KillSwitch 三实例族（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/04_f61_killswitch_instances.md |
| F062 | 合规门与程序化交易报告（built/P0） | 等Owner | 卡:C268,C41; Owner卡:C287,C521 | docs/_working/fullconnect_campaign/g_backtest_gpu/05_f62_compliance_report_gate.md |
| F063 | 仓位管理与对账（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/06_f63_position_reconciliation.md |
| F064 | 回测三件套（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/07_f64_backtest_triad_registries.md |
| F065 | 回测引擎族（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/08_f65_backtest_engine_family.md |
| F066 | 回测预注册与七步循环（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/09_f66_backtest_prereg_loop.md |
| F067 | 实验登记与档案（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/10_f67_experiment_registry.md |
| F068 | GPU 矩阵/工厂格子（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/11_f68_gpu_matrix_grid.md |
| F069 | T0/成本门/IBT（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/g_backtest_gpu/12_f69_t0_cost_gate_ibt.md |
| F070 | 模拟撮合与偏差检测（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/01_f70_sim_matching_bias.md |
| F071 | AutoRuntime Core（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/02_f71_auto_runtime_core.md |
| F072 | 模拟盘日跑四件（partial/P0） | 开口 | — | docs/_working/fullconnect_campaign/h_sched_recovery/03_f72_paper_four_pieces.md |
| F073 | A/B 联赛与分仓（design/P0） | 开口 | 卡:C46; design§1.4 | docs/_working/fullconnect_campaign/h_sched_recovery/04_f73_ab_league.md |
| F074 | 转正建议书汇总器（missing/P0） | 开口 | 卡:C46; missing§1.4 | docs/_working/fullconnect_campaign/h_sched_recovery/05_f74_promotion_gate.md |
| F075 | 策略生命周期状态机（partial/P1） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/h_sched_recovery/06_f75_lifecycle_fsm.md |
| F076 | Windows 计划任务群（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/07_f76_windows_schedtasks.md |
| F077 | 数据调度常驻（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/08_f77_data_scheduler.md |
| F078 | belt daemon（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/09_f78_belt_daemon.md |
| F079 | reaper 与水位监控（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/10_f79_reaper_watermark.md |
| F080 | 资源画像与排班（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/11_f80_resource_profile.md |
| F081 | 监控告警（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/h_sched_recovery/12_f81_monitor_alert.md |
| F082 | 订单与结算常驻（partial/P0） | 开口 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/01_f82_order_settlement_resident.md |
| F083 | 自动化班底（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/02_f83_automation_crew.md |
| F084 | 反馈循环 FBL（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/03_f84_feedback_loop_fbl.md |
| F085 | 环境与启动链（partial/P1） | 等Owner | Owner卡:C394 | docs/_working/fullconnect_campaign/i_ai_ops_gov/04_f85_env_startup_chain.md |
| F086 | AI 六族管线（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/05_f86_ai_six_families_pipeline.md |
| F087 | AI 红线（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/06_f87_ai_redline.md |
| F088 | LSG 安全网关（built/P0） | 已通 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/07_f88_lsg_gateway.md |
| F089 | 本地模型与嵌入（built/P1） | 等Owner | Owner卡:C370 | docs/_working/fullconnect_campaign/i_ai_ops_gov/08_f89_local_models_embedding.md |
| F090 | Agent 编排与 A2A（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/09_f90_agent_orchestration_a2a.md |
| F091 | 能力反查渐进披露（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/10_f91_capability_lookup.md |
| F092 | 原问题账本（partial/P2） | 开口 | 卡:C46 | docs/_working/fullconnect_campaign/i_ai_ops_gov/11_f92_meta_question_ledger.md |
| F093 | PG 图书馆（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/i_ai_ops_gov/12_f93_pg_library.md |
| F094 | AI 层七段循环设计面（design/P1） | 开口 | design§1.4 | docs/_working/fullconnect_campaign/j_ai_design_gates/01_f94_ai_seven_segment_design.md |
| F095 | OBJ 四对象线设计面（design/P1） | 开口 | design§1.4 | docs/_working/fullconnect_campaign/j_ai_design_gates/02_f95_obj_four_objects_design.md |
| F096 | 胃·全网搜索消化设备（partial/P1） | 开口 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/03_f96_stomach_intake.md |
| F097 | commit 侧门禁链（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/04_f97_commit_gate_chain_reference.md |
| F098 | GateEngine 运行时门禁（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/05_f98_gate_engine_runtime.md |
| F099 | 漂移检测（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/06_f99_drift_detection.md |
| F100 | 红蓝对抗（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/07_f100_red_blue_adversarial.md |
| F101 | 规则与裁定体系（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/08_f101_rules_and_rulings.md |
| F102 | 审计体系（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/09_f102_audit_system.md |
| F103 | 代码质量与克隆守卫（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/10_f103_code_quality_clone_guard.md |
| F104 | 会话并发治理（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/11_f104_session_concurrency_gov.md |
| F105 | 密钥治理（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/j_ai_design_gates/12_f105_secrets_governance.md |
| F106 | 术语三层翻译体系（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/01_f106_terminology_i18n.md |
| F107 | 回滚恢复（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/02_f107_rollback_recovery.md |
| F108 | 人机门位（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/03_f108_human_gate_risk_tier.md |
| F109 | 注册表族治理（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/04_f109_registry_governance_roor.md |
| F110 | 契约冻结与错误码（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/05_f110_contracts_error_codes.md |
| F111 | Panel 仪表盘（built/P1） | 等Owner | Owner卡:C399 | docs/_working/fullconnect_campaign/k_frontend_docs/06_f111_panel_dashboard.md |
| F112 | API server（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/07_f112_api_server_routes.md |
| F113 | 可视化渲染器（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/08_f113_visual_renderers.md |
| F114 | 通知路由（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/k_frontend_docs/09_f114_notification_router.md |
| F115 | 报告生成（partial/P1） | 开口 | 接线§1.4 | docs/_working/fullconnect_campaign/k_frontend_docs/10_f115_report_generation.md |
| F116 | SOP 方法论族（built/P1） | 已通 | — | docs/_working/fullconnect_campaign/l_methodology_routing/01_f116_sop_methodology_families.md |
| F117 | 文档资产体系（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/l_methodology_routing/02_f117_document_asset_system.md |
| F118 | 四盘存储地图（built/P2） | 已通 | — | docs/_working/fullconnect_campaign/l_methodology_routing/03_f118_four_drive_storage_map.md |
| F119 | 双引擎自动化总计划（built/P2） | 等Owner | Owner卡:C398 | docs/_working/fullconnect_campaign/l_methodology_routing/04_f119_dual_engine_automation_master_plan.md |
| F120 | 业务层四轴+底板骨架（design/P1） | 开口 | design§1.4 | docs/_working/fullconnect_campaign/l_methodology_routing/05_f120_business_fouraxis_skeleton.md |
| F121 | 研究性三域+研究域（design/P2） | 等Owner | M0 待裁挂起不入车道; design§1.4 | docs/_working/fullconnect_campaign/l_methodology_routing/06_f121_research_three_domains.md |
| F122 | 管线路由 M1-M11（partial/P2） | 开口 | 卡:C192; 接线§1.4 | docs/_working/fullconnect_campaign/l_methodology_routing/07_f122_pipeline_routing_boundary.md |
| F123 | DB schema 迁移通道(REG-MIGRATION-001)（new(定版新增)/P0） | 等Owner | 卡:C267,C378,C380,C383,C400,C43; Owner卡:C379; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/a_data_foundation/13_f123_db_schema_migration_channel.md |
| F124 | 状态词表册生命周期(REG-STATE-VOCAB-001)（new(定版新增)/P0） | 开口 | 卡:C383; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/k_frontend_docs/11_f124_state_vocab_lifecycle.md |
| F125 | data_governance 数据治理本体（new(定版新增)/P0） | 开口 | 卡:C383,C43; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/a_data_foundation/14_f125_data_governance_lineage.md |
| F126 | 字段字典(REG-FLD-001, 8280 行 v2.0)（new(定版新增)/P1） | 开口 | 卡:C383; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/a_data_foundation/15_f126_field_dictionary.md |
| F127 | data_eng 数据工程域(16 py)（new(定版新增)/P1） | 开口 | 卡:C383,C43; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/a_data_foundation/16_f127_data_eng_engineering.md |
| F128 | data_security 数据安全域(10 py)（new(定版新增)/P1） | 开口 | 卡:C383,C43; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/k_frontend_docs/12_f128_data_security_masking.md |
| F129 | ml_train 训练线(43 py)（new(定版新增)/P1） | 开口 | 卡:C383; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/b_factory_inbound/11_f129_ml_train_line.md |
| F130 | ml_serve 数值推理线(11 py)（new(定版新增)/P1） | 开口 | 卡:C267,C383,C43; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/j_ai_design_gates/13_f130_ml_serve_adapters.md |
| F131 | nlp 文本情报处理线(7 py)（new(定版新增)/P2） | 开口 | 卡:C383; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/c_exam_pipeline/08_f131_nlp_text_intelligence.md |
| F132 | infra_ops 运维工程域(6 py)（new(定版新增)/P1） | 等Owner | 卡:C267,C383,C400,C43; Owner卡:C377; 新环六向卷待挖(verified§待挖) | docs/_working/fullconnect_campaign/i_ai_ops_gov/13_f132_infra_ops_engineering.md |

## 统计与复核

- 状态轴分布：已通 64 ｜ 开口 57 ｜ 等Owner 11（合计 132）。
- "已通"=总册 built 基态且无未清审计卡；不代表零缺口（known gaps 见总册各状态列括注）。
- 审计卡号=canonical.json id（C01-C534 区段）；verdict 未清集合=UNDONE/PARTIAL/OWNER_GATE。

### 复跑命令

```bash
# 1. 132 分母
grep -c "^| F" docs/_working/night_sweep/00_skeleton_nightsweep.md
# 2. 总册基态（F01-F122 逐行判）
grep -oE "^\| F[0-9]+ \|" docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md | wc -l   # 122
# 3. F123-F132 定版
sed -n '72p' docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md
# 4. 审计 verdict 分布
python -c "import json;from collections import Counter;d=json.load(open('.runtime/tmp/st-legacy-audit-20260929/canonical.json',encoding='utf-8'));print(Counter(x['verdict'] for x in d))"
# 5. TDM null 38
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' config/trading_decision_map.yaml | wc -l
```

## 遗留与边界声明

- 审计卡↔环节映射按卡内 F 号词边界机判（57/132 环节挂卡）；按名引用未带 F 号的卡未挂（语义映射归各补挖矿卡自认领）。
- UNVERIFIABLE 9 卡不参与状态轴判定（不可证伪），留 Owner 窗口。
- 本册不含处方细节；处方在指针列文档，补挖矿卡落 `docs/_working/night_sweep/`（token 先行）。

