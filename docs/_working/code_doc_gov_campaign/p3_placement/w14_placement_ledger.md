---
ttl: task_bound
session: st-code-doc-20260921
title: "WO-14 包① 企架施工文档归置台账（design_memos 50 件 + implementation_plans 17 件）"
date: "2026-09-20"
ruling: "裁定#384"
---

# WO-14 包① 归置台账（每件一行三裁）

**总策略**：本战役全部 66 件 movable 均判 **b) 历史施工记录→归档**（a 晋升=0、c 删除=0、特判搁置=1）。统一降档理由（a→b）：两目录活设计决策已由 docs/03_modules 542 张蓝图体系与活代码一级 [BLUEPRINT] 锚承载（抽验 ex_core/trading_session.py 一级锚=blueprint.md 非 memo），晋升=新写蓝图+GATE-12+module_id 登记+全引用改弦，成本明显超价值（宪法 §1 内收判据"同真源可派生→必并"）；归档保底不丢内容且 git 历史可逆（裁定#234 三段式）。

**归档目标**：`docs/_working/archive/2026-09/design_memos/`（49 件）+ `docs/_working/archive/2026-09/implementation_plans/`（17 件）。

**引用改齐口径**：①全路径引用（含相对链接/注册表 file: 条目/doc_ref）→机械改指归档新址（202 件宿主文件，见"引用改齐统计"）；②基名注释锚（如 `[BLUEPRINT] 40_execution_broker §2.8`）→不改（基名全仓唯一、按名仍可检索，改 hundreds 行注释违反最小 diff）；③既有陈旧引用（指向本战役前已删除的 11/44/52/56/57/62/AI_review_instructions/AI_fill_instructions/03_domain_boundary_definition 等件）→不属本战役 scope，维持原状留待 R10 顺手清；④`16_technical_indicator_catalog.md` 引用不改（文件留原位）。

## design_memos/（50 件）

| 文件 | 去向 | 判据理由 | 引用改齐 |
|---|---|---|---|
| 00_index_trading_decision.md | b→archive/design_memos/ | 目录历史索引，被台账+壳 README 取代 | 宿主 3 件（file_utils 热表/d6 豁免表/架构悬账册） |
| 01_design_memo_management_spec.md | b→archive/design_memos/ | 备忘录管理规范=本目录过程治理规范，目录清零后失效 | 基名引用仅存（SOP 内），无需改 |
| 10_regime_detector_spec.md | b→archive/design_memos/ | 内容已被 regime_detector 等 4 蓝图承载（BP=4） | 宿主 5 件（3 src 锚+悬账册+13 号互引） |
| 13_regime_phase3_engineering_plan.md | b→archive/design_memos/ | Phase3 工程计划=历史施工排程 | 宿主 17 件（ml 脚本注释+nlp src+域文档） |
| 14_regime_s2_diagnosis.md | b→archive/design_memos/ | S2 诊断=历史问题排查记录 | 宿主 2 件（悬账册+13 号互引） |
| 15_data_feature_layer_spec.md | b→archive/design_memos/ | nan_processor 蓝图已承载（BP=1） | 宿主 1 件（蓝图相对链接） |
| 2026-08-28-industry-graph-frontend.md | b→archive/design_memos/ | 产业图前端施工稿，industry_graph.py 已落地 | 宿主 2 件（src 锚+域文档） |
| 21_stock_selection_engine.md | b→archive/design_memos/ | 选股引擎 spec，代码+selection_confidence 蓝图已承载 | 宿主 21 件（pf_core/signal_ashare src 锚等） |
| 22_sector_rotation_spec.md | b→archive/design_memos/ | 板块轮动 spec，sector/* 模块群已落地 | 宿主 11 件（sector src 锚+tdm doc_ref） |
| 24_daban_strategy_detail.md | b→archive/design_memos/ | 打板策略细节，ex_core daban_* 已落地 | 宿主 1 件（tdm doc_ref） |
| 25_multifactor_strategy_detail.md | b→archive/design_memos/ | 多因子策略细节，multifactor_sleeve 已落地 | 宿主 3 件（tdm+causal_factor_validator+测试） |
| 26_event_driven_strategy_detail.md | b→archive/design_memos/ | 事件驱动细节，news_sentiment_analyzer 蓝图已承载 | 宿主 17 件（intelligence src+域文档） |
| 27_second_batch_strategies.md | b→archive/design_memos/ | 二批策略汇总=历史批次施工记录 | 零全路径引用 |
| 28_sentiment_cycle_trading.md | b→archive/design_memos/ | sentiment_cycle 蓝图已承载（BP=1） | 宿主 8 件（tdm+sentiment src+验证脚本） |
| 30_multi_strategy_concurrency.md | b→archive/design_memos/ | 多策略并发 spec，strategy_book 等 4 蓝图承载（BP=4） | 宿主 1 件（悬账册） |
| 31_position_sizing.md | b→archive/design_memos/ | 仓位管理 spec，batched_position_builder 等 2 蓝图承载 | 宿主 2 件（悬账册+蓝图链接） |
| 32_firm_risk_aggregator.md | b→archive/design_memos/ | firm_risk_aggregator 蓝图已承载（BP=1） | 宿主 2 件（tdm+悬账册） |
| 33_budget_change_handler.md | b→archive/design_memos/ | budget_change_handler 蓝图已承载 | 宿主 1 件（tdm doc_ref） |
| 34_regime_meta_allocator.md | b→archive/design_memos/ | regime_meta_allocator 蓝图已承载 | 宿主 1 件（d6 豁免表路径改指归档） |
| 35_drawdown_protocol_impl.md | b→archive/design_memos/ | drawdown_state_machine 等 2 蓝图承载（BP=2） | 宿主 10 件（risk/core src 锚+候选册） |
| 36_var_es_monitoring.md | b→archive/design_memos/ | fhs_engine 蓝图已承载（BP=1） | 宿主 5 件（risk/core src 锚+悬账册） |
| 37_liquidity_crisis_protocol.md | b→archive/design_memos/ | 流动性危机协议=风控历史 spec | 宿主 2 件（悬账册+business_data_categories.yaml） |
| 40_execution_broker.md | b→archive/design_memos/ | 执行层活真源=execution_core/blueprint.md（trading_session 一级锚实证），memo=历史 spec | 宿主 3 件（悬账册+候选册） |
| 41_buy_flow.md | b→archive/design_memos/ | 买入流 spec，trigger_registry 等 5 蓝图承载（BP=5） | 宿主 6 件（tdm+4 蓝图链接） |
| 42_sell_flow.md | b→archive/design_memos/ | 卖出流 spec，sell_decision 4 蓝图承载（BP=5） | 宿主 8 件（tdm+sell src+蓝图链接） |
| 43_compliance_discipline.md | b→archive/design_memos/ | 合规纪律，compliance 域 7 蓝图承载（BP=7） | 宿主 2 件（悬账册+capability 册） |
| 45_warroom_playbook.md | b→archive/design_memos/ | warroom 作战手册=运维 playbook 归档 | 宿主 1 件（capability 册） |
| 53_simulation_live_path.md | b→archive/design_memos/ | 模拟实盘路径 spec，rollback_state_machine 蓝图已承载 | 宿主 5 件（simulation src+悬账册） |
| 54_reconciliation_attribution.md | b→archive/design_memos/ | 对账归因 spec=历史施工记录 | 宿主 2 件（tdm+悬账册） |
| 55_monitoring_review.md | b→archive/design_memos/ | monitoring 2 蓝图承载（BP=2） | 宿主 3 件（tdm+告警阈值册+悬账册） |
| 61_lifecycle_multi_ai.md | b→archive/design_memos/ | msprt_champion_challenger 蓝图已承载（BP=1） | 宿主 2 件（src 锚+蓝图链接） |
| 63_data_utilization_audit.md | b→archive/design_memos/ | 数据利用审计=历史治理记录 | 宿主 2 件（悬账册+d6 豁免表） |
| 64_data_source_download_spec.md | b→archive/design_memos/ | 数据源下载 spec，数据域已由 TDM/transport 真源承载 | 基名引用仅存 |
| 65_git_safety_governance.md | b→archive/design_memos/ | git 安全治理，真源已入 git_safety_wrapper/d6 体系 | 宿主 5 件（d6 豁免表×2+git safety 脚本×3，豁免路径随移改指归档） |
| 66_commit_queue_serialization.md | b→archive/design_memos/ | 提交队列序列化，真源已入 commit_queue.py 体系 | 宿主 1 件（悬账册） |
| 67_news_data_dedup_design.md | b→archive/design_memos/ | 新闻去重设计，news 域蓝图已承载 | 基名引用仅存（CH 脚本注释） |
| 68_code_algorithm_review_pipeline.md | b→archive/design_memos/ | 代码算法审查管线=历史设计 | 宿主 1 件（capability 册） |
| 69_trading_decision_map.md | b→archive/design_memos/ | TDM 真源已迁 config/trading_decision_map.yaml+decision_map 蓝图（BP=1） | 宿主 5 件（tdm+capability 册+src 锚） |
| 90_methodology_open_questions.md | b→archive/design_memos/ | 方法论开放问题=裁定源历史卷宗（裁定正文已在 ruling_registry） | 宿主 5 件（tdm+signal src 锚+测试） |
| 91_density_prediction.md | b→archive/design_memos/ | 密度预测 spec，ml_forecast 密度族已落地 | 宿主 10 件（ml_forecast src+factor+测试） |
| 93_qmt_file_bridge_playbook.md | b→archive/design_memos/ | QMT 桥 playbook，blueprint_qmt_file_bridge 已承载（BP=2） | 宿主 4 件（tdm+capability 册+蓝图） |
| 94_crypto_quant_expansion.md | b→archive/design_memos/ | crypto 扩张设计，transport 蓝图+calendar 代码已承载（BP=1） | 宿主 24 件中可改 18 件；**src/zephyr/data/** 6 件禁碰留 stale**（甲线域，台账登记） |
| 95_crypto_system_blueprint.md | b→archive/design_memos/ | crypto 系统蓝图，crypto_universe_selector 已落地 | 宿主 2 件中可改 1 件；src/zephyr/data 禁碰 1 件留 stale |
| 96_tdm_v13_validation_metadata.md | b→archive/design_memos/ | TDM v13 验证元数据=历史验证记录 | 宿主 1 件（capability 册） |
| construction_progress_tracker.md | b→archive/design_memos/ | 施工进度 tracker=历史进度账 | 宿主 6 件（悬账册+capability 册+SOP+d6/file_utils 热表） |
| handoff_construction_coordinator.md | b→archive/design_memos/ | 历史会话交接书 | 宿主 2 件（capability 册+d6 豁免表） |
| index.md | b→archive/design_memos/ | 目录索引，被壳 README 取代 | 宿主 1 件（capability 册） |
| observability_contract_todo.md | b→archive/design_memos/ | 可观测性 TODO=历史待办卷宗 | 零全路径引用 |
| pre_expiry_full_backlog_roadmap.md | b→archive/design_memos/ | 到期前 backlog 路线图=历史排程 | 宿主 1 件（capability 册） |
| **16_technical_indicator_catalog.md** | **特判搁置（零动作）** | tilib 指标库 138 条 v1.10.0 终态活真源；数据线批 10（CYQ/SCR/CYC）完工前不动（裁定#384 特判+包① Owner 原文） | 不适用 |

## implementation_plans/（17 件）

| 文件 | 去向 | 判据理由 | 引用改齐 |
|---|---|---|---|
| 00_index.md | b→archive/implementation_plans/ | 目录索引，被壳 README 取代 | 宿主 1 件（capability 册） |
| 01_external_benchmark_analysis.md | b→archive/implementation_plans/ | 外部基准调研=历史分析稿 | 宿主 1 件（capability 册） |
| 02_design_asset_inventory.md | b→archive/implementation_plans/ | 设计资产盘点=历史快照 | 宿主 2 件（capability 册+kimi 审计件[他线不改]） |
| 04_autoruntime_core_build.md | b→archive/implementation_plans/ | AutoRuntime 施工计划=已完工历史 | 宿主 1 件（capability 册） |
| 06_model_profiling_pipeline.md | b→archive/implementation_plans/ | model_profiler 蓝图已承载（BP=1） | 宿主 2 件（capability 册+蓝图） |
| 07_context_engine_build.md | b→archive/implementation_plans/ | context_engine 蓝图已承载（BP=1） | 宿主 1 件（capability 册） |
| 08_multi_ai_concurrency_governance.md | b→archive/implementation_plans/ | 多 AI 并发治理=过程稿 | 宿主 1 件（capability 册） |
| 09_llm_security_integration.md | b→archive/implementation_plans/ | LSG 已落地（zephyr.security.llm_defense） | 宿主 1 件（capability 册） |
| 10_llm_infrastructure.md | b→archive/implementation_plans/ | LLM 基建施工=已完工历史 | 宿主 3 件（capability 册+2 测试注释） |
| 11_evidence_skill_router.md | b→archive/implementation_plans/ | 证据技能路由，model_routing 代码已落地 | 宿主 7 件（model_routing src+路由政策+capability 册） |
| 12_reflexion_multi_agent.md | b→archive/implementation_plans/ | reflexion 代码群+vote_review_shell 蓝图已承载 | 宿主 11 件（reflexion src+capability 册+蓝图） |
| 13_module_factory.md | b→archive/implementation_plans/ | module_factory，module_mapper 等 2 蓝图承载（BP=2） | 宿主 3 件（capability 册+蓝图×2） |
| 14_execution_layer.md | b→archive/implementation_plans/ | 执行层 S11，autonomy_core/agents 代码群已落地 | 宿主 17 件（agents src+测试） |
| 15_autonomy_boundary_risk.md | b→archive/implementation_plans/ | 自治边界，autonomy_core gate 群已落地（裁定#224 批已回填蓝图区） | 宿主 10 件（autonomy_core src+capability 册） |
| 16_ai_security_ops.md | b→archive/implementation_plans/ | AI 安全运维，killswitch 代码+security_event_bus 已落地 | 宿主 4 件（src+capability 册+测试） |
| 17_phase_roadmap.md | b→archive/implementation_plans/ | 阶段路线图=历史排程 | 宿主 1 件（capability 册） |
| index.md | b→archive/implementation_plans/ | 目录索引，被壳 README 取代 | 宿主 1 件（capability 册） |

## 三裁分布统计

- **a) 蓝图晋升：0 件**（统一降档理由见头部；逐件 BP 承载数已列台账）
- **b) 归档：66 件**（design_memos 49 + implementation_plans 17）
- **c) 删除+salvage：0 件**（无"内容错误且零考古价值"件；历史卷宗全部保底归档）
- **特判搁置：1 件**（16_technical_indicator_catalog.md 原位不动；technical_indicator_registry.yaml 零动作）

## 引用改齐统计

- 宿主文件改齐：**197 件**（实测分布：src 107 / tests 41 / docs/03_modules 蓝图与 cross_layer 22 / scripts 13 / docs/01 SOP+政策 7 / docs/01 注册表 5 / config 2——含热文件 architecture_issue_registry、capability_canonical_file_registry、candidate_module_registry，均走 safe_write_text CAS）
- 特殊处置：DEFAULT_HOT_FILES 三条目随移改指归档新址；d6 豁免表（detect_git_dangerous/detect_shell_dangerous/git_safety 脚本）路径随移改指归档（**保住总包提交不被危险命令扫描器误拦**）；tdm doc_ref 13 处
- 不改项：基名注释锚（全仓唯一可检索）；16 号件引用（原位）；既有陈旧引用（本战役前已删文件，R10 scope）；src/zephyr/data/** 7 件禁碰（94/95 号的 6+1 处全路径注释成 stale，甲线域顺路清，台账留痕）

## 留壳与目录契约

- design_memos/ 留壳：README.md + 16_technical_indicator_catalog.md
- implementation_plans/ 留壳：README.md
- directory_contract.yaml 目录条目维持（目录本体未删）；capability_canonical_file_registry 中指向更早已删文件（56/57/03/05/19/AI_review/AI_fill/29）的陈旧条目维持原状（R10 scope）
- depgraph 重建：`python scripts/governance/generate_project_depgraph.py --force` 已跑，project_handbook 统计块两文件随移更新已 stage

## 验证

- 移动后全路径断链扫描（老前缀）：移动集 66 件零残留（残留命中均为上述"不改项"）
- tests/db：**243/244 passed**；1 失败=test_directory_tree_filesystem_alignment 断言 depgraph 树含 30 个磁盘不存在文件——经逐条归零核验（mine=0，30 件全为 docs/01 历史 batch 既遂改名/退役件：*_sop.md→*_policy.md 改名批 07b0e937f3、僵尸处置批 35ffcb91ab、sop 七族重分类 bb44bbbebe 的 design 态注册），生成器按设计保护 design 态行不删（--write 与 --force 均不覆盖），属 pre-existing 失败、他战役欠账，已本裁定台账留痕待治理归口清理，非本战役引入
- tests/path：**全绿（25 passed, 13 xfailed, 8 xpassed，200.58s）**；注：默认全局 timeout=120 不够红蓝对抗件（连跑生成器 10 次×全仓 9.6 万文件扫描），须 `--timeout 3000` 方可跑完，已留痕（本轮未加 -p no:cacheprovider，合规）

## creation_token

本台账与两壳 README 新建 .md 共 3 件：creation_token 登记由总包统一提交时补登（本会话不走 capability 册登记通道，台账内声明代替）。
