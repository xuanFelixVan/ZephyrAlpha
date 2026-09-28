---
ttl: task_bound
volume: 00_verification_table
session: st-ailayer-final-20260924
creation_token: fullflow-p0-verify-table-20260926
---

# 05_missing_p0/00 · 候选漏项逐条二验对账表

> 被测＝`../00_skeleton/90_crosscheck_link_census.md` §三·E「四轴交叉去重候选漏项＝29 项（P0 四项，建议 122→≈151，明写未验）」。
> 二验口径＝**每项两个独立证据源**：E1 代码/数据实扫（命令→实测输出），E2 注册表或地图册（ROOR 条目／TDM yaml／能力卡／F 册行）。
> 判定四态＝**成立**（环节面确有缺位）｜**不成立**（对象已在既有 122 某环节下＝重复/登记面欠账，或上棒依据证伪）｜**证据不足**（两向未齐，判待挖）｜**成立-待裁**（无位为真，归属需裁）。
> 全部实测在 worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`（分支 HEAD 含 119 件作业簿），命令见 §五。
> 车道：只读取证＋写本作业簿，零施工、零新建 .py、零提交。

## 〇、主表（31 行逐条二验）

**行数先纠一处**：上棒自称"29 项"，但其自身分解式「轴1 两＋轴2 十五＋轴4 十三＋轴3 零」＝**30**；再加上棒 P0 第四项（38 null 节点面，未占 A/B/D 编号）＝**31**。本表按 31 行逐条二验。→ 病灶 V-1。

| # | 候选漏项（上棒原文） | E1 代码/数据实扫（实测） | E2 注册表/地图册（实测锚点） | 判定 | 已在既有 122 哪一环下（重复 vs 漏项） | 落位 |
|---|---|---|---|---|---|---|
| A-1 | TDM `state_matrix` 段无 F 位 | TDM 顶层键 `state_matrix:` @`config/trading_decision_map.yaml:5556`，本册实测段内 **47 行**；消费方实测 7 件：`src/zephyr/trading/decision_map.py`、`strategy_pipeline/daily_decision_orchestrator.py`、`signal_ashare/core/environment_switch.py`、`pf_alloc/allocation_inputs.py`、`scripts/backtest/auto_mount.py` 等 | F 册 `grep state_matrix` ＝**0 命中**；ROOR `REG-STATE-VOCAB-001` 条目描述把 TDM 六段列入党轴；立法件 `docs/_working/vocab_legislation/02_state_vocabulary_mapping_register.md` 在盘 | **成立** | 无位（F38 只写"六传感器→7 态"未点 state_matrix 段） | **并 B-12 同一新环节**（同真源可派生→必并），不单独计 |
| A-2 | TDM `portfolio_plan` 段无 F 位 | TDM 顶层键 `portfolio_plan:` @`config/trading_decision_map.yaml:5639`，本册实测段内 **24 行**；消费方 `src/zephyr/pf_alloc/allocation_inputs.py`（注：pf_alloc 在他道在途热件清单，本车道只读不碰） | F 册 `grep portfolio_plan`＝0，但 **F27**（`:57`「E8 组装与资金分配：多策略 sleeve 装配+regime 元分配+风险平价」）＋**F49**（`:89`「C2 组合聚合：目标聚合净额轧平/约束栈/budget 三级」）＝同一对象已有位 | **不成立** | F27＋F49 已覆盖语义；缺的是"TDM 段→环节"挂接登记 | 登记面欠账（F 册补注 portfolio_plan 锚点），不计新增 |
| B-1 | REG-TECHNICAL-INDICATOR-001 技术指标册 | 文件在盘 `docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml`＝**4,796 行 / 4,468 键**（本册实测） | ROOR @`registry_of_registries.yaml:637` status=active；F 册全文 `grep 指标`＝**0 命中**（仅 F38 行有"宏观"无指标） | **成立** | 无位（F52 对象＝验证方法学+27 条 DAL 决策算法，非指标库） | 与 B-2 合 1 新环节"指标与形态特征库" |
| B-2 | REG-PAT-001 图表形态册 | `chart_pattern_registry.yaml`＝**12,295 行**在盘 | ROOR @`:648`；F 册 `grep 形态`＝仅命中"证据形态"（`:258` 表格头），与图表形态无关 | **成立** | 无位 | 并 B-1 |
| B-3 | REG-EXA-001 执行算法册 | `execution_algo_registry.yaml`＝441 行/53 键在盘 | F 册 **F55**（`:100`「执行算法路由 SOR 智能拆单/算法选择」真源 `src/zephyr/ex_sor/core/algo_execution_selector.py`）＝同一对象已有位，只是未写 REG 号 | **不成立** | F55 | 登记面欠账（F55 补挂 REG-EXA-001） |
| B-4 | REG-SEAT-001 席位册 | `seat_registry.yaml`＝559 行/49 键在盘 | ROOR @`:744`；F 册 `grep 席位`＝**0**、`grep 龙虎榜`＝**0** | **成立** | 无位 | 新增（C 段数据线族） |
| B-5 | REG-EVT-001 事件日历册 | `event_calendar_registry.yaml`＝498 行/41 键在盘 | ROOR @`:774`；F 册 `grep 日历`＝只命中 **F01/F13** 把"交易日历"当**触发器**（`:26/:43`），无事件/除权/披露数据线环节 | **成立** | 无位 | 新增（A/C 段交界） |
| B-6 | REG-MAC-001 宏观指标册 | `macro_indicator_registry.yaml`＝576 行/44 键在盘 | ROOR @`:784`；F 册 **F38**（`:78`「L1 大盘总闸+六传感器：指数/内部结构/赚钱效应/波动率/**宏观**/日级」）＝宏观已在环节内 | **不成立**（独立环节不成立） | F38 子目 | 环节内缺口：F38 补"宏观数据线（REG-MAC-001）"子目，不计新增 |
| B-7 | REG-FLD-001 字段字典 | `field_dictionary.yaml`＝**8,280 行 / 7,628 键**在盘 | ROOR @`:680`；F 册 `grep 字典`＝**0**；`grep 字段`＝只命中 F80"96 实体 18 字段"（无关对象） | **成立** | 无位 | **并 D-3 同一新环节**（数据资产·血缘·字段治理同真源族） |
| B-8 | REG-DATAFLOW-001 数据资产册 | `data_asset_registry.yaml`＝**15,517 行**在盘 | ROOR @`:669`：name=数据资产登记表、entry_count=342、status=active、description=「数据资产唯一真源（SSoT）三实体 sources/datasets/jobs 对标 OpenLineage」、owned_by=governance；F 册 `grep 数据资产`＝0，F11 对象＝业务资产库挂 TDM 交叉轴（`_XREF_SPECS`），非资产 SSoT | **成立** | 无位（F11 只挂轴，不持 SSoT 台账） | 并 D-3 |
| B-9 | **P0①：REG-MIGRATION-001 → "DB schema 迁移环节缺位"** | 册头实测：`migration_registry.yaml` **276 行/222 键**，条目字段＝`old_module/new_module/old_path/new_path/subdir/status`＝**模块路径重命名台账（ARCH-031）**；册头 `[MATURITY] deprecated`、`[STABILITY] frozen`、`[MODIFY-GUARD] 禁止新增条目（已冻结）`、`[AI_AUTONOMY] ai_read_only`。DB 侧 DDL 通道实测在盘：`scripts/ch/apply_timezone_migration.py`、`scripts/governance/migrations/`、`scripts/governance/registry_migration/` | F 册 **F02**（`:28`「数据源接入生命周期：源发现→报批→**建表**→接入→验收」）＋**F06**（`:31`「CH 热库落库：ClickHouse 热层 **DDL**/分区监控/落库，真源 `scripts/ch/apply_*_ddl.py`」）＝DB 建表与 DDL 应用已有位；ROOR @`:408` | **不成立（依据证伪）** | F02＋F06 覆盖 DB DDL 面；上棒把"模块路径迁移册"读成"DB schema 迁移"＝对象错配 | 撤回 P0①。残留真问题＝"schema 版本化迁移与回滚的自动化闭环"（本车道两向未齐）→ 判 **证据不足/待挖**，见 `pending_rulings.md` P-1 与 §一 V-2 |
| B-10 | REG-ARCH-ISSUE-001 架构问题册 | `architecture_issue_registry.yaml`＝**22,539 行/7,454 键**在盘（全仓最大注册表之一） | ROOR @`:420`；F 册 `grep 架构问题`/`grep ARCH-`＝**0**；最近似环节 **F36**（`:71`「L9 治理横切：问题治理状态机+净零资产对账」）但其真源字段实测只点 `TDM-E-L9-Z1/Z2；scripts/governance/reconcile_chain_refs.py`，未点该册 | **证据不足** | 待判：F36 与该册是"同一对象（问题治理）"还是"不同对象（架构议题 vs 链路引用一致性）"——需 F36 owner 逐条读条目键 | 待挖（缺 F36 条目级比对），不计新增 |
| B-11 | REG-INTF-001 接口契约册并入 F110 | 物理路径实测在 `_archive/` 下（`catalogs/_archive/interface_contract_registry.yaml`，189 行/11 键） | ROOR @`:300` 实测字段：name=「接口契约注册表（**已归档**）」、maintenance=**frozen**、entry_count=5、status=**archived**、description=「**2026-09-16 裁定#259 退役归档**」 | **不成立（伪证）** | 上棒拿**已裁定退役**的注册表当"漏项依据"；契约面已由 **F110**（`:185` freeze_manifest 38 契约+error_code 788）持有 | 撤销该候选；列入 §一 V-4（须引裁定#259 为据，本车道不自赋裁定） |
| B-12 | **P0②：REG-STATE-VOCAB-001 → 状态词表环节缺位（GATE-VOCAB 真在拦）** | 门禁实测：`gate_registry.yaml:185` `GATE-VOCAB`（status=active，source=pre-commit，`files_trigger` 含 `_registry/vocabularies/.*\.yaml`）＋`:1311` `STATE-VOCAB-REGISTRY`（own_scope=true，in-process GitCommitGateway）＋拦截件 `src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py` 在盘；词表数据面 `_registry/vocabularies/`＝**47 个 yaml** | ROOR @`:252`：name=状态词表中央登记表、status=active、entry_count=29，但 **physical_path 指向的 `catalogs/state_vocabulary_registry.yaml` 实测 FILE-MISSING**；条目还声称"官方词表本体=`zephyr.shared.vocab.market_state`（SH-VOCAB-001）"，而 `src/zephyr/shared/vocab` **实测 NOT-EXIST**（最接近件只有 `signal_ashare/market_state_sensor.py`）；F 册 `grep 词表`/`vocabulary`＝**0 命中** | **成立（P0，已开册）** | 无位——真实在拦的门禁＋47 份词表数据＋立法件，三者在 F 体系一个环节都不挂 | `01_state_vocabulary_lane.md` |
| B-13 | REG-TASK-META-001 任务卡元数据册 | `task_card_meta_registry.yaml`＝95 行/12 键在盘 | ROOR @`:319`；F 册 **F76**（`:141`「Windows 计划任务群：sch_*/ops_*/数据槽位/drill/event/manual/dynamic=96」）＝任务卡/计划任务面已有位，未挂 REG 号 | **不成立** | F76 | 登记面欠账（F76 补挂 REG-TASK-META-001） |
| B-14 | REG-TEMPLATE-001／REG-FRONTMATTER-001／REG-SCRIPT-001·002／REG-CAP-001 文档脚本资产族 | 五册全在盘：`docs/03_modules/template_registry.yaml` 143 行、`frontmatter_field_registry.yaml` 666 行、`scripts/script-manifest.yaml` **8,304 行**、`scripts/governance/script_manifest.yaml` **5,613 行**、`config/tech_stack_manifest.yaml` 181 行 | ROOR @`:501/:329/:40/:50/:69`；F 册 **F117**（`:202`「文档资产体系：目录册 87+统一资产索引 33249+rule_catalog 256」）持有文档资产面；F 册 `grep script_manifest`/`tech_stack`＝**0** | **成立-并入**（文档/模板/词外字段面 F117 已有；**脚本资产台账两册＋技术栈清单确无位**） | F117（部分） | F117 细化子目或 K 段新增 1 环"脚本与技术栈资产台账"→ **本表按"并入"计，不推高终数**（内收优先，待总筹择一） |
| B-15 | REG-CROSS-002／REG-CATALOG-001／REG-SM-001 三册 | `cross_module_dependency_registry.yaml` 1,746 行/1,257 键、`registry_master_index.yaml` 473 行/406 键 在盘；`src/zephyr/shared/_state_machine_registry.yaml` 在盘（**代码内注册表**） | ROOR @`:243/:149/:557`；F 册 **F109**（`:184`「注册表族治理：ROOR+**master_index**+一致性契约+净零审计」）＝REG-CATALOG-001 明确有位；REG-CROSS-002＝跨模块依赖，与 **F07**（PG 架构库 depgraph 依赖图）同族；REG-SM-001＝状态机中央登记，F 册 `grep 状态机` 只命中 F36/F38/F53/F60/F75（各持自身 FSM），**无"状态机登记面"环节** | **成立（部分，仅 REG-SM-001）** | REG-CATALOG-001→F109（不成立）；REG-CROSS-002→F07 族（不成立）；REG-SM-001→无位 | REG-SM-001 **并 B-12 同一新环节**（状态词表与状态机登记同一治理族） |
| D-1 | 代码域 `alt_data` | `src/zephyr/alt_data` 实存：**28 py（20 非 init）/6,277 行**，件名 `alt_data_catalog.py`、`alt_data_connector.py`、`alt_source_health_manager.py`、`alt_data_compliance_reviewer.py`、`alt_regime_signals.py`；`functional_domain_registry.yaml` 收录（3 处命中） | F 册 **F31**（`:66`「L9 源线·**另类数据**族：卫星/天气/招聘/电商/招投标/社媒/APP 榜」）＝同一对象已有位；F 册 `grep -w alt_data`＝0（缺包路径锚点） | **不成立** | F31（域→包锚点缺失＝F 册勘误项） | F31 补 `src/zephyr/alt_data` 代码锚点，不计新增 |
| D-2 | 代码域 `data_eng` | `src/zephyr/data_eng` 实存：16 py（9 非 init）/3,021 行，件名 `data_lake_manager.py`、`incremental_update_engine.py`、`cleaning_anomaly_engine.py`、`cold_data_archive_manager.py`、`quality_sla_breach_predictor.py`、`gpu_resource_manager.py`、`expectation_governance.py` | F 册：F01 采集调度、F05 判重与审计、F08 冷库归档、F13 算力问闸＝**四个既有环节各持其中一件**，但无"数据工程"总环；本车道未做逐件归属表 | **证据不足** | 疑为"F01/F05/F08/F13 的碎片覆盖"而非整环缺位 | 待挖（缺"9 件→4 环节"逐件归属判定），不计新增 |
| D-3 | **P0③：代码域 `data_governance`（数据治理本体）** | `src/zephyr/data_governance` 实存：**21 py（14 非 init）/3,046 行**，件名 `column_lineage_tracker.py`、`core/column_lineage_analyzer.py`、`core/lineage_parser.py`、`core/schema_registry.py`、`core/metadata_registry.py`、`openlineage_exporter.py`、`asset_auto_discovery.py`、`ml_lineage_tracker.py`、`lineage_change_detector.py`；跨域消费方实测 8 件（`data/data_service.py`、`backtest/core/data_handler.py`、`backtest/core/tick_replay.py`、`alt_data/alt_data_catalog.py`、`ex_core/open_order_resolver.py`、`frontend/dashboard/components/order_book.py`…）；测试 `tests/data_governance/` **4 件在盘** | F 册 `grep -w data_governance`＝**0**、`grep lineage`＝**0**、`grep 血缘`＝只命中 **F113**（`:193` 可视化渲染器"图谱/**血缘**/瀑布五视图"＝渲染消费端非本体）；**ROOR 全文 `grep data_governance`/`grep lineage`＝0 命中**＝该域连注册表都没有 | **成立（P0，已开册）** | 无位：本体域 3,046 行＋四向消费＋测试，在 F 体系与 ROOR 双双无登记 | `02_data_governance_lineage.md` |
| D-4 | 代码域 `data_security` | `src/zephyr/data_security` 实存：10 py（3 非 init）/724 行，件名 `data_masking_engine.py`、`ai_masking_pipeline.py`、`data_access_auditor.py`；domreg 收录 | F 册 **F88**＝LSG LLM 防御（对象＝LLM 调用面，非数据脱敏/访问审计）；F 册无脱敏环节 | **成立** | 无位（与 F88 跨域不同对象→按 w5_1 **不并**） | 新增（K 段）"数据安全与脱敏"，或作 D-3 治理环节子目——**本表按新增计** |
| D-5 | 代码域 `market_data` | `src/zephyr/market_data` 实存：20 py（9 非 init）/2,948 行，含 `connectors/`、`normalized_market_data_producer/`、`raw_data_cache/`、`failover/`；`module_translation_registry.yaml` 有 1 处命中 | F 册 **F03**（`:28` Provider 实现与源路由，真源 `src/zephyr/data/implementations/`）＋**F10**（`:35` 行情订阅分发）＝同对象已有位；两包并存＝**双真源嫌疑** | **不成立** | F03/F10 | 转"双真源收敛"工单（F 册勘误＋D3/D5 域比对），不计新增 |
| D-6 | 代码域 `ml_train` | `src/zephyr/ml_train` 实存：43 py（32 非 init）/6,781 行，含 `training_pipeline/`、`training_dataset_manager/`、`ai_operator/`、`core/model_version_registry.py`、`continual_learning_antiforget.py`；**`functional_domain_registry.yaml` 命中＝0**（连域注册都没有） | F 册 `grep 训练`＝**0 命中**；F19 只"模型基线对台"、F67＝experiment_tracking（上棒自认已覆盖） | **成立** | 无位（训练线整条：数据集/版本登记/持续学习） | 新增（B/J 段）"模型训练线" |
| D-7 | 代码域 `ml_serve` | `src/zephyr/ml_serve` 实存：11 py（4 非 init）/1,333 行，件名 `codegen_model_adapter.py`、`deep_review_model_adapter.py`、`model_compression_accelerator.py`、`core/model_drift_monitor.py` | F 册 `grep 推理`/`模型服务`＝**0 命中**；model_drift_monitor 与 F50/F81 监控面是否同对象未判 | **成立** | 无位（服役/推理线；漂移监控归属待判） | 新增"模型服役与漂移监控线"（与 D-6 可并为 1，本表先按各 1 计并给窄口径） |
| D-8 | 代码域 `nlp` | `src/zephyr/nlp` 实存：7 py（6 非 init）/1,782 行，件名 `sentiment_pipeline.py`、`sentiment_aggregator.py`、`news_dual_tagger.py`、`news_impact_grader.py`、`research_rating.py`、`nlp_inference.py`；domreg 命中＝0 | F 册 `grep NLP`/`舆情`＝**0**；F30 有"千股千评/互动易"**作为源线**（采集面），后端文本处理线无位 | **成立** | 无位（源线在 F30，加工线无环） | 新增"文本/舆情加工线"（亦可并 C 段源线族，待总筹） |
| D-9 | 代码域 `intelligence` | `src/zephyr/intelligence` 实存：**89 py（72 非 init）/24,834 行**（本次 13 域中最大），子包 `model_routing/`、`model_profiling/`、`model_evaluation/`、`reflexion/`、`switch_engine/`、`api/core/infrastructure/models/services` | F 册 **F96**（`:166` 胃·全网搜索消化设备，真源＝`docs/_working/automation/inbox/`）**非本域**；**F86**（`:156` AI 六族管线，真源＝`src/zephyr/ai_layer/`）**亦非本域**；F 册 `grep -w intelligence`＝0 | **成立** | 无位——24,834 行代码域在 F 册两处"最近似"环节里都不是它 | 新增（AI 段）"模型路由与智能体自省域" |
| D-10 | 代码域 `knowledge` | `src/zephyr/knowledge` 实存：15 py（14 非 init）/4,978 行，件名 `kb_engine.py`、`financial_knowledge_graph.py`、`factor_knowledge_base.py`、`knowledge_artifact_store.py`、`layered_memory_orchestrator.py`、`knowledge_quality_assessor.py` | F 册 **F93**（`:163` PG 图书馆，真源＝`src/zephyr/library/librarian.py、lookup.py`）＝**另一个包**；"知识面"语义 F 册有、包归属无 | **成立-待裁** | 语义层 F93 已有"知识面"，缺的是 knowledge 包的归属（新环 vs F93 扩展） | 见 `pending_rulings.md` P-2（终数默认**不**计入） |
| D-11 | 代码域 `infra_ops` | `src/zephyr/infra_ops` 实存：6 py（5 非 init）/1,278 行，件名 `loki_log_pipeline.py`、`wal_checkpoint_monitor.py`、`storage_cost_calculator.py`、`config_effect_checker.py`、`runtime_topology_visualizer.py` | F 册 F81 监控/告警、F85 环境与启动链、F118 四盘存储地图＝三面拆有；F 册 `grep -w infra_ops`＝0；本车道未做逐件归属 | **证据不足** | 疑被 F81/F85/F118 碎片覆盖 | 待挖（缺逐件归属表），不计新增 |
| D-12 | 代码域 `infra_runtime` | `src/zephyr/infra_runtime` 实存：9 py（8 非 init）/2,203 行，件名 `ha_sla_framework.py`、`latency_budget_allocator.py`、`resource_scheduler.py`、`runtime_admission.py`、`cold_plane_isolation.py`、`database_layer.py`、`shared_memory_zero_copy.py`、`ml_pipeline_process.py` | F 册 **F71**（`:126` AutoRuntime Core，真源＝`src/zephyr/trading/auto_runtime*`）＝不同包；F13 算力问闸与 `resource_scheduler.py` 疑同物 | **证据不足** | F71/F13 疑覆盖但未逐件比对；"是否同物"属架构取舍 | 待挖＋待裁（`pending_rulings.md` P-3），不计新增 |
| D-13 | 代码域 `gov_rule` | `src/zephyr/gov_rule` 实存：4 py（2 非 init）/576 行，唯一实体件在 `constitutional_update/` | F 册 **F101**（`:176`「规则与裁定体系：86 trae_*.yaml+ruling_registry 同 commit 原子」）＝规则面已有位；F 册 `grep -w gov_rule`＝0 | **不成立** | F101（宪法更新子链缺包锚点＝登记面欠账） | F101 补 `src/zephyr/gov_rule` 锚点，不计新增 |
| N-1 | **P0④：38 个 `module_ref: null` 节点无归属** | `config/trading_decision_map.yaml` 实测：`^- node_id:`＝**182**、`module_ref:`＝**182**、`module_ref: null`＝**38**（上棒三数全复现）；38 个逐条导出＝**全部 `TDM-E-L9-*`**（A01–A16 共 16、B01–B10 共 10、C01–C03 共 3、G1/G2/G4/G5、V2、AGG、D2、E2、Z1；16+10+3+4+1+1+1+1+1＝38 自校闭合）；`module_ref` 消费方实测 8 件（含 `self_evolution_fidelity_gate.py`、`dashboard/api_server.py`、`commit_gates/algo_note_sync_gate.py`） | **F 册 F30–F36 行原文（`:65-71`）以区间式逐段点名全部 38 节点**：F30＝`TDM-E-L9-A01..A16`、F31＝`B01..B10、C01..C03`、F32＝`G1..G5`、F33＝`V1..V3`、F34＝`TDM-E-L9-AGG（module_ref=null）`、F35＝`D1/D2/E1/E2`、F36＝`Z1/Z2` → **0 个节点无环节归属**；上棒"只 8 个 id 命中"是**字符串全名匹配 vs 区间写法**造成的假漏项 | **不成立（P0④ 证伪）** | 38/38 已落 F30–F36；真缺＝TDM 节点级 `module_ref` 代码锚（地图册内部登记面欠账，非 122 集合漏项） | `03_tdm_null_node_attribution.md`（全量归属表＋证伪）；终数计 **0** |

## 一、二验中新发现的漂移与病灶（现象/根因/修法草案/工作量/本车道可修否）

| # | 现象（实测） | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| V-1 | 上棒 §三·E 自称"29 项"，其自身分解式 2+15+13+0＝**30**；加 P0④＝**31** | 手工"条目列表+计数"必漂移（宪法 §9.5），上棒未做行数自校 | 终数与本表一律"行数机械相加＋逐行判定"，计数写成派生字段（宪法 §4.3） | 0（本表已按 31 行做） | 已修（本册） |
| V-2 | 上棒 P0①把 `REG-MIGRATION-001`（模块路径重命名台账，`deprecated/frozen/禁止新增条目`）当"DB schema 迁移环节缺位"的判据 | 只按册名关键词联想，未读册头元数据与条目字段 | P0① 撤回；改立"schema 版本化迁移与回滚闭环"待挖工单（两向取证） | 小 | 已修（判定层面） |
| V-3 | 上棒为 P0②举的旁证"死信 0036 死于词表（`00_orchestration.md:46`）"——原文实测 :52 记 0036＝**"replay 内容"**，与词表无关 | 引证未回原文 | B-12 仍**成立**（成立证据换成三件硬实测：GATE-VOCAB 在拦＋47 词表＋ROOR 断链）；死信旁证作废 | 0 | 已修（本表改证） |
| V-4 | 上棒 B-11 把 ROOR 里 `status=archived`、`maintenance=frozen`、描述"2026-09-16 裁定#259 退役归档"的注册表列为候选漏项 | 未读 ROOR 条目 status 字段 | 候选漏项判据补一条硬前置：**ROOR status≠active 者一律不得作漏项依据** | 0 | 已修（判据写入本表 §〇 上方） |
| V-5 | **ROOR `REG-STATE-VOCAB-001` 指向的 `catalogs/state_vocabulary_registry.yaml` 实测不存在**；同条目声称的"官方词表本体 `zephyr.shared.vocab.market_state`"目录也实测不存在 | ROOR 手工登记与文件面脱钩（无悬空校验门） | 新增"ROOR 悬空物理路径普查"工单（生成器侧，下一波施工，本车道不碰热册） | 中（1 施工袋） | 否（ROOR 是热文件，且宪法规程禁车道改） |
| V-6 | `src/zephyr/data_governance` 与 `src/zephyr/governance/data_governance` **两个同名包并存**（后者实测含 `akshare_provider.py`、`ch_tick_provider.py`） | 历史拆分（DM311/DM314 类迁移）未收口 | 归属裁定＋depgraph 登记；先登记不改动（更正5） | 中 | 否（属施工） |
| V-7 | `data_governance` 域在 **ROOR 零登记**（`grep data_governance|lineage`＝0），即 3,046 行本体域＋2 张被它治理的大册（15,517 行 / 8,280 行）之间的生产者-登记关系断链 | 域未编目→注册表归属无人写 | 见 `02_data_governance_lineage.md` §四 堵点 1 | 中 | 否 |
| V-8 | 能力卡面：13 个候选域在 `data/capability_cards/` 的**文件名命中全为 0** | 能力卡命名用业务别名不用包名（登记面欠账，非环节漏项） | F 册/能力卡补包名交叉索引（机生） | 小 | 否 |
| V-9 | 上棒"轴4 顶层域 57"与 `module_translation_registry.yaml` 覆盖率实测不一致：13 域中仅 `market_data`/`nlp`/`intelligence`/`gov_rule` 4 个有命中 | 模块翻译登记覆盖不全（TRANSLATION-COVERAGE gate 只管新建件） | 存量补登记工单 | 中 | 否 |
| V-10 | **P0④ 的取证方法本身有缺陷**：上棒用"F 册是否出现节点全名 id"判归属（`grep -o "TDM-E-L9-[A-Z0-9]*"` 实测只 8 命中→判"仅 8 个被点到，31 处未判"），而 F 册 F30–F36 行用的是**区间写法**（`A01..A16`、`B01..B10、C01..C03`、`G1..G5`、`V1..V3`、`D1/D2/E1/E2`、`Z1/Z2`）——那 8 个命中恰是 8 个区间的**头节点** | 散文表格＋字符串全等匹配＝系统性假漏项 | ①环节真源册的节点引用改为机生映射表（与对账表 §三·H/生成器四表同施工袋）；②二验判据加一条：**区间写法须展开后再比对**（本车道已按此法把 38/38 归完，见 `03_tdm_null_node_attribution.md` §三） | 小（方法已在本册固化） | 已修（判定层面） |
| V-11 | 同窗并发面：他会话/他棒已在做机生五向对账（`00_skeleton/91_machine_crosscheck.yaml` 已由 `scripts/governance/fullflow/generate_fullflow_crosscheck.py` 产出，记 `measured:` 字段），其**独立实测**与本表轴数一致：F 环节 **122**、TDM 节点 **182**、ROOR 注册表 **77**、src 顶层域 **57** | — | 本表因此获得第二方复算背书；后续本车道数字若与该 YAML 背离，以 YAML（机生）为准（宪法 §9.5） | 0 | 已核 |

## 二、成立项 → 成册清单

| 新环节（建议编号占位） | 合并自 | 册路径 |
|---|---|---|
| 状态词表与状态机登记治理 | B-12＋A-1＋B-15(REG-SM-001) | `05_missing_p0/01_state_vocabulary_lane.md` |
| 数据资产·血缘·字段字典治理 | D-3＋B-7＋B-8 | `05_missing_p0/02_data_governance_lineage.md` |
| TDM 38 个 null 节点归属（**P0④ 证伪册，非环节**） | N-1（判不成立） | `05_missing_p0/03_tdm_null_node_attribution.md`（38/38 已落 F30–F36，终数贡献 0） |
| 指标与形态特征库 | B-1＋B-2 | 未开册（P1，待下一波） |
| 席位（龙虎榜）数据线 | B-4 | 未开册（P1） |
| 事件/除权/披露日历数据线 | B-5 | 未开册（P1） |
| 模型训练线 | D-6 | 未开册（P1） |
| 模型服役与漂移监控线 | D-7 | 未开册（P1） |
| 文本/舆情加工线 | D-8 | 未开册（P2） |
| 模型路由与智能体自省域（intelligence） | D-9 | 未开册（P1，代码体量最大） |
| 数据安全与脱敏 | D-4 | 未开册（P1） |

## 三、终数建议（122 → N，机械推导）

1. **判定分布（31 行闭合，逐行可查主表"判定"列）**：
   - **成立 15 行**＝A-1、B-1、B-2、B-4、B-5、B-7、B-8、B-12、B-15、D-3、D-4、D-6、D-7、D-8、D-9
   - **成立-并入既有环节 1 行**＝B-14（并入 F117 细化）
   - **成立-待裁 1 行**＝D-10（knowledge 包归属新环 vs F93 扩展）
   - **不成立 10 行**＝A-2、B-3、B-6、B-9(P0①)、B-11、B-13、D-1、D-5、D-13、N-1(P0④)
   - **证据不足→待挖 4 行**＝B-10、D-2、D-11、D-12
   - 校验：15＋1＋1＋10＋4＝**31** ✅（上棒"29 项"与其分解式 30 从未闭合，见 V-1）
2. **去重内收后的新增环节数**（宪法 §4.2"同真源可派生→必并"）：15 个成立行 → **10 个新环节**
   - 计算式：`{B-12 组=A-1+B-12+B-15 → 1, D-3 组=D-3+B-7+B-8 → 1, B-1 组=B-1+B-2 → 1, B-4 → 1, B-5 → 1, D-4 → 1, D-6 → 1, D-7 → 1, D-8 → 1, D-9 → 1}` ＝ **10**
   - 行数守恒自校：3（B-12 组）＋3（D-3 组）＋2（B-1 组）＋7（各自 1 环）＝**15 行 → 10 环** ✅（N-1 证伪后贡献 0；B-14 并入既有贡献 0）。
3. **终数建议 N ＝ 122 ＋ 10 ＝ 132**
   - 宽口径（15 行不并册）＝122＋15＝**137**；窄口径（训练＋服役并 1、席位＋事件＋文本并 1、数据安全并入治理 1）＝122＋7＝**129**。
   - D-10 若裁为新增则 **133**；B-10/D-2/D-11/D-12 若后续挖干成立，最多再＋4（须另波取证，本波不预计入）。
4. **对上棒"≈151"的差**：上棒把 30 行（自称 29）全按新增环节相加＝122+29≈151，未做"已在既有环节"甄别与内收；本表实测 **10 行不成立（其中 2 项为 P0，依据被证伪）＋4 行证据不足**，成立行内收后仅 10 环 → **151 虚高 ≈19**（151−132）。
5. **重复而非漏项的行有多少**：31 行中 **10 行判"其实已在既有 122 的某环节下"**（A-2→F27/F49、B-3→F55、B-6→F38、B-9→F02/F06、B-11→F110＋已退役、B-13→F76、D-1→F31、D-5→F03/F10、D-13→F101、N-1→F30–F36），另 B-14 半重复（F117 已含文档面）＝**约 10–11 行为重复/登记面欠账，不是漏项**。
5. **另有环节内缺口（不占总数，须回写各环行）**：B-6→F38 宏观数据线子目、B-3→F55 挂 REG-EXA-001、B-13→F76 挂 REG-TASK-META-001、D-1→F31 补 alt_data 锚点、D-5→F03/F10 双真源收敛、D-13→F101 补 gov_rule 锚点、B-14→F117 细化、A-2→F27/F49 挂 portfolio_plan 锚点、B-15→F109/F07 已含。

## 四、自审闸三态

- **挖干可施工**：**B-12（状态词表环节，`01_` 册）** 与 **N-1（null 节点归属判定，`03_` 册）** 六向齐全可派下一波；**D-3（数据治理，`02_` 册）＝部分挖干**（五向齐、"自动化触发"一向实测零证据，缺口已在该册 §二 写明，**不算完**）。
- **本表自身**：31 行二验**已挖干**（每行两向证据＋判定＋落位，命令在 §五 可复跑）；未挖干的是成立行的六向台账（只做了"是否无位"二验）。
- **待挖**：B-1/B-2、B-4、B-5、B-14、D-4、D-6、D-7、D-8、D-9 九个成立行**只完成"是否无位"的二验，未做六向台账**（本车道预算=先二验后开 P0 册，非 P0 成立行不越预算开册）；B-10、D-2、D-11、D-12 四行＝两向未齐（缺什么已在主表写明）。
- **待裁**：**7 条**见 `pending_rulings.md`（P-1 schema 版本化迁移是否立新环、P-2 knowledge 包归属、P-3 infra_runtime 与 F71 同物否、P-4 双同名 `data_governance` 包真源、P-5 market_data 双真源收敛、P-6 V2 情绪快照与 L02 情绪状态变量层级、P-7 FSM 词表↔注册表词表对齐方向）。**均不自赋裁定号、不写"Owner 已裁"**；已检索既有裁定：六段温度词表本体**已裁（`裁定#398`／`裁定#399` 在 `ruling_registry.yaml`:5369/:5409，勿重裁）**，故本车道**未**把"六段词表怎么定"立案，只立"该环节无 F 位"这一件事实。

## 五、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 3.12.8
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
ROOR=docs/registry_of_registries.yaml
GR=docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# 行数与分解式（预期：本表 31 行；上棒分解 2+15+13=30）
grep -c "^| A-[0-9]\|^| B-[0-9]* \|^| B-1[0-5] \|^| D-[0-9]* \|^| N-1 " docs/_working/fullflow_mining/05_missing_p0/00_verification_table.md

# 轴1 TDM（预期 182 / 182 / 38；state_matrix@5556 47 行；portfolio_plan@5639 24 行）
grep -c "^- node_id:" config/trading_decision_map.yaml
grep -c "module_ref:" config/trading_decision_map.yaml; grep -c "module_ref: null" config/trading_decision_map.yaml
grep -n "^state_matrix:\|^portfolio_plan:" config/trading_decision_map.yaml
awk '/^state_matrix:/{f=1;next} /^[a-z_]*:/{f=0} f' config/trading_decision_map.yaml | grep -c ":"
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' config/trading_decision_map.yaml | tr '\n' ' '
grep -o "TDM-E-L9-[A-Z0-9]*" $S | sort -u | tr '\n' ' '   # 8 个命中＝F30–F36 的**区间头节点**（A01/B01/G1/V1/D1/AGG/Z1…），非"只点 8 个"——见 V-10
sed -n '65,71p' $S | cut -c1-200                          # 区间写法原文（F30=A01..A16 / F31=B01..B10、C01..C03 / F32=G1..G5 / F33=V1..V3 / F34=AGG / F35=D1/D2/E1/E2 / F36=Z1/Z2）

# 轴2 ROOR 21 册：在盘性＋status＋F 册命中（预期见主表）
for r in REG-TECHNICAL-INDICATOR-001 REG-PAT-001 REG-EXA-001 REG-SEAT-001 REG-EVT-001 REG-MAC-001 REG-FLD-001 \
         REG-DATAFLOW-001 REG-MIGRATION-001 REG-ARCH-ISSUE-001 REG-INTF-001 REG-STATE-VOCAB-001 REG-TASK-META-001 \
         REG-TEMPLATE-001 REG-FRONTMATTER-001 REG-SCRIPT-001 REG-SCRIPT-002 REG-CAP-001 REG-CROSS-002 REG-CATALOG-001 REG-SM-001; do \
  p=$(grep -A8 -m1 "registry_id: $r" $ROOR | grep -m1 -o "physical_path:.*" | cut -c16-); st=$(grep -A8 -m1 "registry_id: $r" $ROOR | grep -m1 "status:" | cut -c9-); \
  [ -f "$p" ] && e=EXISTS || e=FILE-MISSING; echo "$r|$e|$st|inF=$(grep -c "$r" $S)"; done

# B-9 证伪用：迁移册册头（预期 deprecated/frozen/禁止新增）＋DB DDL 面在 F02/F06
sed -n '1,15p' docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml | cut -c1-120
grep -n "建表\|DDL" $S | cut -c1-120 | head -4
# B-11 证伪用：接口契约册 status=archived
sed -n '300,308p' $ROOR | cut -c1-150
# B-12 成立用：GATE-VOCAB 真拦＋47 词表＋ROOR 物理文件与"本体"包双双不存在
grep -n "gate_id: GATE-VOCAB" -A9 $GR | cut -c1-140; grep -n "gate_id: STATE-VOCAB-REGISTRY" -A10 $GR | cut -c1-120
ls docs/01_policies_and_standards/_registry/vocabularies/ | wc -l          # 47
ls docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml 2>&1 | tail -1
ls -d src/zephyr/shared/vocab 2>&1 | tail -1                                # NOT-EXIST
ls src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py
# 死信 0036 原文（V-3：=replay 内容，非词表）
grep -n "0036" docs/_working/fullflow_mining/00_orchestration.md | cut -c1-160

# 轴4 13 域（预期实扫见主表：py 数/真实件数/行数/域注册/F 册命中）
M=docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml
DR=docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml
for d in alt_data data_eng data_governance data_security market_data ml_train ml_serve nlp intelligence knowledge infra_ops infra_runtime gov_rule; do \
  rp=$(find src/zephyr/$d -name "*.py" ! -name "__init__.py" | grep -v __pycache__ | wc -l); \
  ln=$(find src/zephyr/$d -name "*.py" ! -name "__init__.py" | grep -v __pycache__ | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'); \
  echo "$d realpy=$rp lines=$ln domreg=$(grep -c $d $DR) modtrans=$(grep -c "zephyr\.$d\." $M) inF=$(grep -c -w $d $S)"; done
find src/zephyr/governance/data_governance -name "*.py" | head -4          # V-6 双同名包
grep -rn "data_governance\|lineage" $ROOR | head                           # V-7 预期 0 命中
```
