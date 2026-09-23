---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_to_derive_candidates.md"
ttl: "task_bound"
---

# 待推导清单（G15-② potential_consumers 增枝前置挖矿·产出三件/三件）

- 班次：st-ulib3b-20260922（增补令 #14③：文档无据、需强模型推导的供数关系）
- 口径：三路摘抄代理一致报告"明文未载"的推断候选；**本册只登记推导方向不做断言**——逐条需回到代码/表实探后方可入 potential_consumers 回填批
- 定稿：st-ulib3b 强模型（增补令 #14"审编定稿必须本班强模型"）

## 一、battle_map 抽象类 → 具体表映射（表级绑定全靠推断）

| # | 推断方向 | 依据 | 推导所需实探 |
|---|---|---|---|
| T1 | BM-SEL-22-C/23-A/24-A 系列消费的"L0 涨停数据"→limit_up_pool（含 industry 列）；"L0 盘口"→tick_depth_5；"L0 集合竞价"→auction_snapshot/auction_book；"L0 资金流向"→money_flow | battle_map_05:2731-3259 用抽象类；data.md 有上述表但从未被点名 | 代码消费面 grep：这些模块实读哪张 CH 表 |
| T2 | 做T 分时因子（量比/CVD/VPIN）的 C-009 管线原料→tick_data/kline_1min/l2_tick 之一或组合 | battle_map_07:487 说消费 C-009 产出，C-009 吃什么全图无载 | C-009 管线代码上游 |
| T3 | "全球市场数据（L0）"（BM-SEL-06 跨市场传导）→kline_global/us_index/hk_kline 子集 | battle_map_05:753 | 模块实读面 |
| T4 | 系统性风险五信号的"融资余额/政策新闻/外围指数"→margin_trading/news_data/us_index | battle_map_09:1214 | 风控模块实读面 |
| T5 | "A 股风险日历（D-DATA）"→calendar_event/ipo_schedule/index_adjustment 候选 | battle_map_08:218 | 日历模块 |

## 二、资产闲置嫌疑（表在库、疑似有用途无人接线）

| # | 推断方向 | 依据 |
|---|---|---|
| T6 | sentiment_panel（25 行无持久化史）疑似 BM-SEL-03-A"市场情绪指标"的断链供表 | battle_map_05:2005 + 情绪线盘点册 :113（币圈恐贪禁顶替 A 股） |
| T7 | c1_backtest.decision_daily/regime_state_anchored/sim_daily_report 与 BM03/BM04 域高度相关但 battle_map 从未点名 | data.md 表目录 vs battle_map 全文 |
| T8 | pipeline.md 任务名暗示链：ZephyrAlpha_TickSubscriber→tick 入库、SectorSnapshot→sector_snapshot、BoardIndexRealtime→board_index_tick、counter_trend_feeder→逆势馈送——任务→表→消费方完整明文链不存在 | docs/library/pipeline.md:20-91 任务名 |
| T9 | 券商结算单（BM-REC-01 消费）与关联账户合并数据（BM-BUY-15 合规）无对应表资产——是缺口还是散落数据待认 | battle_map_11:126 + data.md 322 表反查 |
| T10 | factor_analysis 11 表高密度互引是否构成 factor.value_factor/momentum_20d 的下游消费线 | 63 号 CSV 计数无方向；需查代码 |
| T11 | 63 号 CSV（2026-08-24）与 09-22 实库探针口径差异：zero_ref 的 fundamental 5 表 vs c3_fundamental.daily_valuation/analyst_forecast"在库有货"——命名空间是否同一套 | 两文对读无对齐声明；需一次表名映射核验 |
| T12 | 情绪线 C5 杠杆成分与板块线"杠杆资金分布"共用 margin_trading——两线是否同源共享未见声明 | 两侧台账各自引用同表 |

## 三、推导批处置建议

- T1-T5 为 potential_consumers 首批回填的最大宗来源（battle_map 75 条供给关系里约六成卡在"抽象类→表名"这最后一公里）；建议下一班用"模块实读面 grep"一次跑完，机械可证
- T6-T8 为闲置资产复活线索，回填时标 derived=true + 推导依据路径
- T9-T12 为口径对齐项，宜并入数据面班对账而非本维度

## 四、tags 清道后残留=词表增补候选（st-ulib3c-20260923，Owner 2026-09-23 R4）

- 来路：全仓 catalogs 22 册 tags 非枚举 1197 次经"状态批注摘除"清道后残留 736 次 / 437 distinct；
  已摘除 569 次（TRAE/候选态环节补登/acquisition导入/L1_foundation/layer:X/rejected/deprecated/批N/PN规划/深圳…逐词理由见袋 message 与 `.runtime/tmp/ulib3c_tag_sweep_yaml.py` 头注）。
- 纪律：**禁造词**——下列均为册内既有用词的事实采集，增补与否、并入哪个标准词由馆员/强模型审编定；本班一律未动词表标准词集合（182 词不变，仅按已批 R4 补 3 词条英文别名）。
- 复核命令：`python .runtime/tmp/ulib3c_tag_sweep_yaml.py --plan`（干跑，不写盘）+ `python scripts/governance/generators/check_library_coverage.py`。

### 4.1 建议先裁的一组高频真领域词（出现 ≥3 次）

| 词 | 次 | 涉及册 |
|---|---|---|
| 市场级择时 | 12 | factor_registry |
| 超跌 | 11 | chart_pattern_registry, strategy_registry, technical_indicat |
| 多因子 | 10 | data_asset_registry, model_registry, portfolio_model_registr |
| 江恩 | 10 | chart_pattern_registry, regime_cycle_registry |
| 统计 | 10 | data_asset_registry, technical_indicator_registry |
| 波浪 | 9 | chart_pattern_registry |
| 超买 | 9 | factor_registry, strategy_registry, technical_indicator_regi |
| 循环 | 8 | technical_indicator_registry |
| 扩展 | 7 | candidate_module_registry |
| 量能 | 7 | technical_indicator_registry |
| P0 | 6 | candidate_module_registry |
| P1 | 6 | candidate_module_registry |
| 作战地图审查转入 | 6 | candidate_module_registry |
| PLV | 5 | alert_threshold_registry |
| 上线验证 | 5 | alert_threshold_registry |
| 研报 | 5 | data_asset_registry |
| 退役 | 5 | alert_threshold_registry |
| 防过度设计 | 5 | candidate_module_registry |
| AI层 | 4 | alert_threshold_registry |
| AI模式补全 | 4 | candidate_module_registry |
| L2收集库 | 4 | alert_threshold_registry |
| session_lifecycle | 4 | rule_ai_perception_index |
| 交易 | 4 | alert_threshold_registry |
| 健康 | 4 | alert_threshold_registry |
| 入考率 | 4 | alert_threshold_registry |
| 压力分级 | 4 | alert_threshold_registry |
| 基本面 | 4 | data_asset_registry |
| 币圈 | 4 | data_asset_registry |
| 性能 | 4 | candidate_module_registry |
| 成长 | 4 | macro_indicator_registry |
| 时间窗 | 4 | regime_cycle_registry |
| 死信 | 4 | alert_threshold_registry |
| 漂移 | 4 | alert_threshold_registry |
| A股特色 | 3 | candidate_module_registry |
| regime | 3 | candidate_module_registry, data_asset_registry |
| 产业 | 3 | data_asset_registry |
| 偏离 | 3 | alert_threshold_registry |
| 内存 | 3 | alert_threshold_registry |
| 前缀错误 | 3 | candidate_module_registry |
| 回补 | 3 | data_asset_registry |
| 操作风险 | 3 | alert_threshold_registry |
| 架构骨架残留 | 3 | candidate_module_registry |
| 模型风险 | 3 | alert_threshold_registry |
| 评审 | 3 | alert_threshold_registry |
| 运价 | 3 | data_asset_registry |
| 风险分级 | 3 | alert_threshold_registry |

### 4.2 长尾（出现 1-2 次，388 词，按次降序并列）

 · 92号清单(2)、BTC(2)、DDD仪式(2)、KBG-0040(2)、P2(2)、PSI(2)、Phase2(2)、RBAC(2)、Sharpe(2)、access_control(2)、anti_hallucination(2)、anti_schrodinger_rollback(2)
 · auto_intake(2)、depgraph(2)、event_driven(2)、fail_closed(2)、multifactor(2)、pre_commit_gate(2)、preventability(2)、principle(2)、security(2)、stub(2)、temporary_file(2)、低优先(2)
 · 偏差(2)、关注度(2)、分散实现(2)、功能上移(2)、历史(2)、可转债(2)、君子协定(2)、图形(2)、地产(2)、字典(2)、实盘缺口(2)、已实现组合(2)
 · 并发(2)、恐慌反弹(2)、指数择时(2)、数据接入(2)、无blueprint_id(2)、枚举值误登记为模块(2)、横切(2)、测试触发器(2)、海洋(2)、第一性原理裁定(2)、能见度(2)、误登记(2)
 · 贸易(2)、远期(2)、采集(2)、错误形态(2)、6层闭环模型(1)、AI开发减抽象层(1)、AI替代(1)、API超时(1)、ARCH-066(1)、ARCH-096(1)、ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001(1)、ARCH-COMMIT-SERIALIZATION-001(1)
 · ARCH-CROSS-COMMIT-ATOMICITY-001(1)、ARCH-FORCE-MERGE-SAFETY-001(1)、ARCH-STASH-ACCUMULATION-001(1)、ARCH-WORKTREE-BASE-FRESHNESS-001(1)、ARCH-WORKTREE-COMMIT-PERSISTENCE-001(1)、AUM(1)、Agent 安全(1)、BIAS(1)、CUSUM(1)、ClickHouse(1)、C轨占位(1)、DMI(1)
 · ETH(1)、FHS(1)、GARCH(1)、GPU(1)、Gann(1)、ONNX(1)、PB(1)、ROE(1)、RULE-CAPABILITY-LOOKUP-SCENE-CLASSIFY(1)、RULE-COMMIT-SERIALIZATION(1)、RULE-CROSS-COMMIT-ATOMICITY(1)、RULE-DATA-OPS(1)
 · RULE-EIGHTEEN(1)、RULE-FORCE-MERGE-SAFETY(1)、RULE-PREVENTABILITY(1)、RULE-SEVENTEEN(1)、RULE-STASH-LIFECYCLE(1)、RULE-WORKTREE-BASE-FRESHNESS(1)、RULE-WORKTREE-COMMIT-PERSISTENCE(1)、YAGNI(1)、abuse_monitoring(1)、aggressive_mode(1)、ai-governance(1)、ai_consumer_first(1)
 · ai_hallucination(1)、ai_model_routing(1)、anti_abuse(1)、anti_accumulation(1)、anti_dangling_import(1)、anti_drift(1)、anti_false_alarm(1)、arch_domain_capacity_governance(1)、architecture_blueprint(1)、architecture_ctr_injection(1)、architecture_dependency(1)、architecture_drift(1)
 · architecture_gate_transition(1)、architecture_governance_order(1)、architecture_path_registry(1)、architecture_qualification(1)、audit_dimensions(1)、audit_log(1)、audit_separation(1)、authority(1)、automation_dual_track(1)、autonomy(1)、backup_first(1)、bypass_scene_classification(1)
 · canonical_key(1)、capability_lookup(1)、capability_lookup_scene_classify(1)、capacity_audit(1)、checklist(1)、code_behavior(1)、code_modification(1)、code_naming(1)、code_operation_prohibition(1)、code_structure(1)、code_test_security(1)、code_type_import(1)
 · cold_start(1)、commit_gate(1)、commit_gateway(1)、commit_serialization(1)、compliance_audit(1)、conditional_prohibition_code_security(1)、conditional_prohibition_governance_doc(1)、crash_prevention(1)、create_no_window(1)、critical_section(1)、cross_blueprint_change_cleanup(1)、cross_commit_atomicity(1)
 · data_governance(1)、data_model(1)、data_ops_discipline(1)、decisiongraph_access_protocol(1)、depgraph_access_protocol(1)、depgraph_scan_exclusions(1)、design_intent_source(1)、design_maturity(1)、design_state(1)、destructive_ops(1)、doc_numbering_metadata(1)、doc_operation_safety(1)
 · doc_structure_naming(1)、domain_data_factor(1)、domain_risk_analytics(1)、engineering_code_restructure(1)、engineering_header_expansion(1)、escape_hatch_classification(1)、escape_hatch_collapse(1)、exclusion(1)、feature_creation(1)、features(1)、file_lock(1)、file_operation(1)
 · first_principles(1)、force_merge_safety(1)、format_policy(1)、frontend(1)、full_field_duplication_check(1)、git_call_budget(1)、git_subprocess(1)、governance_prohibition(1)、hot_file_cas(1)、human-gated(1)、immutable-core(1)、incremental_gate(1)
 · inward_consolidation(1)、lifecycle(1)、local_hooks(1)、meta_metadata_metrics(1)、meta_rule_classification(1)、meta_standard_template(1)、methodology_collaboration(1)、methodology_decision(1)、methodology_diagnosis(1)、methodology_quality(1)、migration_framework(1)、module_contract(1)
 · module_creation_workflow(1)、module_governance(1)、module_registry_sync(1)、multi_ai_concurrency(1)、network_single_point_failure(1)、no_external_dependency(1)、no_full_repo_scan(1)、non_bypassable(1)、offline_first(1)、operational(1)、operational_domain(1)、operational_vibe_coding(1)
 · ops_guard(1)、other_prohibition(1)、output_verification(1)、overruled_by_user(1)、panorama_alignment(1)、parts(1)、placement(1)、post_to_pre_migration(1)、powershell_prohibition(1)、powershell_window(1)、precommit_incremental(1)、precommit_offline(1)
 · primitive_inversion_fix(1)、procedural(1)、query_source_mapping(1)、read_before_write(1)、reconciler(1)、refactor非建模块(1)、rmtree(1)、rule_seventeen(1)、runcommand_discipline(1)、runcommand_purity(1)、scan_rules(1)、schema_version_protection(1)
 · script_execution(1)、secrets(1)、security_access(1)、security_guard(1)、security_prohibition(1)、session(1)、session_coordination(1)、shell_command_chaining(1)、single_entry(1)、single_source_of_truth(1)、source_of_truth(1)、ssot(1)
 · ssot_classification(1)、ssot_read(1)、staged_files_only(1)、stale_base_overwrite(1)、start_fail_closed(1)、stash_lifecycle(1)、symbol_convention(1)、task_card_lifecycle(1)、task_construction_verification(1)、task_management(1)、telemetry(1)、thresholds(1)
 · ttl_cleanup(1)、user_manual_protected(1)、v2.0备忘(1)、vibe-coding(1)、whistleblower(1)、window_flash(1)、worktree_base_freshness(1)、worktree_commit_persistence(1)、yaml_vs_db(1)、zero幻觉空间(1)、三窗全绿(1)、严重度(1)
 · 串谋检测(1)、举报人(1)、乖离率(1)、事件日历(1)、事件驱动(1)、五图对齐(1)、五级熔断(1)、交易规则(1)、价值(1)、会话(1)、传输(1)、传送带守护(1)
 · 位置超限(1)、体验优化(1)、信号增强(1)、公式轨(1)、内容层缺失(1)、冷却(1)、分布预测(1)、前端治理(1)、功能上移至基础设施层(1)、功能已实现(1)、功能已承接(1)、动量残差(1)
 · 升级链(1)、危机alpha(1)、去重(1)、双活(1)、双真源风险(1)、取证(1)、周期分析(1)、回撤漂移(1)、回测前置(1)、因子驱动(1)、地基(1)、复盘(1)
 · 多券商(1)、多头排列(1)、失败率(1)、学术架构(1)、宏观情绪(1)、实盘回测(1)、实盘扩展(1)、对冲(1)、小市值(1)、已修正错误登记(1)、延迟(1)、影子(1)
 · 待源调研(1)、微盘(1)、成交率(1)、打板族(1)、拆件(1)、拒单(1)、指数成分(1)、政府数据(1)、政策驱动(1)、数据健康(1)、数据回补(1)、数据完整性(1)
 · 数据模型(1)、断路器(1)、断连(1)、无消费者(1)、无重构驱动(1)、日亏(1)、日线(1)、日终(1)、时间体系(1)、显存(1)、月频(1)、标识约定(1)
 · 概念错误(1)、永续合约(1)、波段(1)、派生(1)、灾备(1)、熔断(1)、爆发(1)、用户裁定(1)、相关(1)、真源分类(1)、硬边界(1)、磁盘(1)
 · 离线(1)、积压(1)、稳定币(1)、组合分配(1)、缓存(1)、网络(1)、能力反查(1)、自愈(1)、自我指涉(1)、自治管线(1)、蓝筹(1)、衍生计算(1)
 · 补方法非建模块(1)、覆盖面(1)、设计准入一问标准(1)、语义理解类(1)、误删(1)、质量过滤(1)、超卖回归(1)、超时(1)、超短线(1)、超跌反转(1)、趋势择时(1)、跑输(1)
 · 跨市场消歧(1)、辅助(1)、迁移(1)、连败(1)、重构(1)、链上(1)、门槛(1)、防硬造编译器(1)、防误判(1)、防过度工程(1)、防过拟合(1)、防重复造轮子(1)
 · 防重新提议(1)、防风暴(1)、预警(1)、高开(1)

### 4.3 单独待裁：治理层级标记不入业务词表的处置

- 残留 `L0`/`L1`/`L2`（合计 61 次）系 #ARCH-024 明文"tier 真源=规则 frontmatter tags 的 Lx"+
  `generate_rule_catalog._extract_tier_from_tags` 实读该值——**本班未摘**（摘则 rule_catalog tier 静默清空=假绿级事故）。二选一待裁：①tier 改由 `layer:` 字段单一真源、生成器与闸同步改，再摘 tags 里的 Lx；②TAG-VOCAB 对治理层级轴开豁免命名空间（如 `tier:L1`）。
- 现状后果：这三词长期挂在闸的非枚举清单里，会稀释真缺口的可读性（736 残留中占 61）。
