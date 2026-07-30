---
doc_type: architecture_view
title: 数据流图（dataflowgraph）索引
version: "1.0"
status: active
date: 2026-07-30
owner: auto-generator
ttl: permanent
---

# 数据流图（dataflowgraph）索引

> 生成时间: 2026-07-30T11:49:31
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）
> 数据库: depgraph (PostgreSQL)
> 生成器: `scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

## 概述（自动生成 · 生成器: generate_dataflow_diagram.py）

数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖）
- dataflowgraph 表达"数据从哪流到哪"（数据流向）
- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联

## 统计（自动生成 · 生成器: generate_dataflow_diagram.py）

| 类型 | 生产 (production) | 回测内部 (backtest_internal) | 合计 |
|------|-------------------|------------------------------|------|
| Dataset | 10 | 4 | 14 |
| Job | 768 | 5 | 773 |
| Edge | - | - | 28 |

### 设计态 / 运营态统计（design_maturity）

| 类型 | 运营态 (production) | 设计态 (design) | 合计 |
|------|---------------------|-----------------|------|
| Dataset | 14 | 0 | 14 |
| Job | 695 | 78 | 773 |

> **设计态 vs 运营态 / Design vs Production**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。对标 depgraph 的设计态/运营态机制（decision_index.md）。

## Mermaid 图表（自动生成 · 生成器: generate_dataflow_diagram.py）

> 图表内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
>
> **设计态优先着色（design_maturity）**：
> - **紫色** = 设计态节点（design_maturity=design，蓝图规划，代码未写）
>
> **运营态按 scope 着色（design_maturity=production）**：
> - **蓝色矩形** = 生产 Dataset（dsProd）
> - **橙色矩形** = 回测 Dataset（dsBacktest）
> - **绿色圆角矩形** = 生产 Job（jobProd）
> - **粉色圆角矩形** = 回测 Job（jobBacktest）
>
> - `JOB -->|produces / 产出| DS` = Job 产出 Dataset
> - `DS -->|consumed by / 被消费于| JOB` = Job 消费 Dataset
> - 节点标签前缀 `[design]`/`[production]` 标注 design_maturity

### 全景图（设计态 + 运营态合并，标签标注 [design]/[production]）

> 节点数: 14 datasets / 数据集, 773 jobs / 作业, 28 edges / 边

```mermaid
flowchart LR
    DS11001["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS11002["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS11000["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10999["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    DS10998["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10992["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10991["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10996["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10990["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10989["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10995["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10997["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10994["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10993["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB718831("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB718829("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB718827("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB718828("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB718830("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB718832("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB718833("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB718834("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB718835("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB718836("[production]INFRA-DB-001<br/>蓝图: INFRA-DB-001"):::jobProd
    JOB718837("[production]INFRA-DB-002<br/>蓝图: INFRA-DB-002"):::jobProd
    JOB718838("[production]INFRA-DB-003<br/>蓝图: INFRA-DB-003"):::jobProd
    JOB718839("[production]INFRA-DB-006<br/>蓝图: INFRA-DB-006"):::jobProd
    JOB718840("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB35951("[design]MOD-ARCH-BIZDB"):::jobDesign
    JOB718841("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB718842("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB718843("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
    JOB672126("[design]MOD-BT-018"):::jobDesign
    JOB672128("[design]MOD-BT-019"):::jobDesign
    JOB672130("[design]MOD-BT-020"):::jobDesign
    JOB672131("[design]MOD-BT-021"):::jobDesign
    JOB672133("[design]MOD-BT-022"):::jobDesign
    JOB672135("[design]MOD-BT-023"):::jobDesign
    JOB672137("[design]MOD-BT-024"):::jobDesign
    JOB672139("[design]MOD-BT-025"):::jobDesign
    JOB672142("[design]MOD-BT-026"):::jobDesign
    JOB35548("[design]MOD-C1-MARKETCH"):::jobDesign
    JOB35760("[design]MOD-CONTEXT_ENGINE"):::jobDesign
    JOB718854("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB718855("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB718856("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB671597("[design]MOD-DATA_ENG"):::jobDesign
    JOB718858("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB718859("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB718860("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB718861("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB718862("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB718863("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB718864("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB718865("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB712063("[design]MOD-EX-001"):::jobDesign
    JOB718867("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB718868("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB718869("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB35940("[design]MOD-FEEDBACK_LOOP"):::jobDesign
    JOB35578("[design]MOD-GATE_ENGINE"):::jobDesign
    JOB718872("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB718873("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB718874("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB718875("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB36856("[design]MOD-GOV-ALIGN-PANORAMAS"):::jobDesign
    JOB718876("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB718877("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB718878("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB139307("[design]MOD-GOV-HEARTBEAT"):::jobDesign
    JOB718879("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB718880("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
    JOB293594("[design]MOD-GOV-blueprint_status_transition_reconciler"):::jobDesign
    JOB293546("[design]MOD-GOV-cross_layer_contract_signature_reconciler"):::jobDesign
    JOB293501("[design]MOD-GOV-depgraph_pre_registration_gate"):::jobDesign
    JOB293524("[design]MOD-GOV-derivation_annotation_gate"):::jobDesign
    JOB293480("[design]MOD-GOV-folder_capacity_hard_limit_gate"):::jobDesign
    JOB140122("[design]MOD-GOV-heartbeat_daemon"):::jobDesign
    JOB293571("[design]MOD-GOV-relative_path_literal_gate"):::jobDesign
    JOB87876("[design]MOD-GOV-rule_execution_pairing_gate"):::jobDesign
    JOB388555("[design]MOD-GOV-runtime_violation_snapshot"):::jobDesign
    JOB388557("[design]MOD-GOV-runtime_violation_snapshot_reconciler"):::jobDesign
    JOB118710("[design]MOD-GOV-session_startup_health_check"):::jobDesign
    JOB360945("[design]MOD-GOV-stash_accumulation_gate"):::jobDesign
    JOB118708("[design]MOD-GOV-workspace_hygiene_reconciler"):::jobDesign
    JOB296197("[design]MOD-GOV-worktree_lifecycle"):::jobDesign
    JOB35857("[design]MOD-GOVERNANCE"):::jobDesign
    JOB718882("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB718883("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB718884("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB718885("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB718886("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB718887("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB718888("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB718889("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB718890("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB718891("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB718892("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB718893("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB718894("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB718895("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB718896("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB718897("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB718898("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB718899("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB718900("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB718901("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB718902("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB718903("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB718904("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB718905("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB718906("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB718907("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB718908("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB718909("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB718910("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB718911("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB718912("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB718913("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB718914("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB718915("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB718916("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB718917("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB718918("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB718919("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB718920("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB718921("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB718922("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB718923("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB718924("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB718925("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB718926("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB718927("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB718928("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB718929("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB718930("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB718931("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB718932("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB718933("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB718934("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB718935("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB718936("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB718937("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB718938("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB718939("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB718940("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB718941("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB718942("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB718943("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB718944("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB718945("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB718946("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB718947("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB718948("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB718949("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB718950("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB718951("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB718952("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB718953("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB718954("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB718955("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB718956("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB718957("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB718958("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB718959("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB718960("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB718961("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB718962("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB718963("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB718964("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB718965("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB718966("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB718967("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB718968("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB718969("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB718970("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB718971("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB718972("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB718973("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB718974("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB718975("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB718976("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB718977("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB718978("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB718979("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB718980("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB718981("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB718982("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB718983("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB718984("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB718985("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB718986("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB718987("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB718988("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB718989("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB718990("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB718991("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB718992("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB718993("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB718994("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB718995("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB718996("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB718997("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB718998("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB718999("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB719000("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB719001("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB719002("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB719003("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB719004("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB719005("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB719006("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB719007("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB719008("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB719009("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB719010("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB719011("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB719012("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB719013("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB719014("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB719015("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB321362("[design]MOD-GOV_blueprint_status_transition_reconciler"):::jobDesign
    JOB321311("[design]MOD-GOV_cross_layer_contract_signature_reconciler"):::jobDesign
    JOB719016("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB719017("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB719018("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB36357("[design]MOD-INF-005"):::jobDesign
    JOB37139("[design]MOD-INF-009"):::jobDesign
    JOB35565("[design]MOD-INF-011"):::jobDesign
    JOB719022("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB719023("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB719024("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB35954("[design]MOD-INF-016"):::jobDesign
    JOB36274("[design]MOD-INF-017"):::jobDesign
    JOB719027("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB37172("[design]MOD-INF-019"):::jobDesign
    JOB36050("[design]MOD-INF-020"):::jobDesign
    JOB35903("[design]MOD-INF-021"):::jobDesign
    JOB36400("[design]MOD-INF-022"):::jobDesign
    JOB35522("[design]MOD-INF-023"):::jobDesign
    JOB37193("[design]MOD-INF-024"):::jobDesign
    JOB719034("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB719035("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB35574("[design]MOD-INF-027"):::jobDesign
    JOB36222("[design]MOD-INF-028"):::jobDesign
    JOB35930("[design]MOD-INF-029"):::jobDesign
    JOB37217("[design]MOD-INF-030"):::jobDesign
    JOB37220("[design]MOD-INF-031"):::jobDesign
    JOB36336("[design]MOD-INF-033"):::jobDesign
    JOB35554("[design]MOD-INF-034"):::jobDesign
    JOB719043("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB37237("[design]MOD-INF-036"):::jobDesign
    JOB35538("[design]MOD-INF-037"):::jobDesign
    JOB719046("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB36080("[design]MOD-INF-039"):::jobDesign
    JOB719048("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB719049("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB719050("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB719051("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB35939("[design]MOD-INFRA_OPS"):::jobDesign
    JOB719052("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB719053("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB719054("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB719055("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB36157("[design]MOD-L00-002"):::jobDesign
    JOB35520("[design]MOD-L00-003"):::jobDesign
    JOB61876("[design]MOD-L00-004"):::jobDesign
    JOB719057("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB719058("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB719059("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB551909("[design]MOD-L02-001"):::jobDesign
    JOB719061("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB719062("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB719063("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB719064("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB719065("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB719066("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB719067("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB719068("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB719069("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB719070("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB719071("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB719072("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB719073("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB719074("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB719075("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB719076("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB719077("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB719078("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB719079("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB719080("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB719081("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB719082("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB688297("[design]MOD-L04-001"):::jobDesign
    JOB719084("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB719085("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB719086("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB719087("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB719088("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB719089("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB719090("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB719091("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB719092("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB719093("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB36390("[design]MOD-MASTER-001"):::jobDesign
    JOB35517("[design]MOD-MASTER-002"):::jobDesign
    JOB36344("[design]MOD-MASTER-003"):::jobDesign
    JOB35528("[design]MOD-MASTER_BLUEPRINT"):::jobDesign
    JOB711884("[design]MOD-MKT-001"):::jobDesign
    JOB711954("[design]MOD-MKT-002"):::jobDesign
    JOB712012("[design]MOD-MKT-003"):::jobDesign
    JOB719098("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB719099("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB719100("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB36113("[design]MOD-PF_ALLOC"):::jobDesign
    JOB719101("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB719102("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB35898("[design]MOD-RESOURCE_OPTIMIZATION_ENGINE"):::jobDesign
    JOB719104("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB719105("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB719106("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB719107("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB719108("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB719109("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB719110("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB719111("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB719112("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB719113("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB719114("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB35600("[design]MOD-SIMULATION"):::jobDesign
    JOB119053("[design]MOD-SMOKE-TEST"):::jobDesign
    JOB719115("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB118981("[design]MOD-TEST"):::jobDesign
    JOB719117("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB719118("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB719119("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB719120("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB719121("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB719122("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB719123("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB719124("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB719125("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB719126("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB719127("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB719128("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB719129("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB719130("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB719131("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB719132("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB719133("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB719134("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB719135("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB719136("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB719137("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB719138("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB719139("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB719140("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB719141("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB719142("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB719143("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB719144("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB719145("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB719146("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB719147("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB719148("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB719149("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB719150("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB719151("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB719152("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB719153("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB719154("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB719155("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB719156("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB719157("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB719158("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB719159("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB719160("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB719161("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB719162("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB719163("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB719164("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB719165("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB719166("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB719167("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB719168("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB719169("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB719170("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB719171("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB719172("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB719173("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB719174("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB719175("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB719176("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB719177("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB719178("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB719179("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB719180("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB719181("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB719182("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB719183("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB719184("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB719185("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB719186("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB719187("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB719188("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB719189("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB719190("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB719191("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB719192("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB719193("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB719194("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB719195("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB719196("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB719197("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB719198("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB719199("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB719200("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB719201("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB719202("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB719203("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB719204("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB719205("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB719206("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB719207("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB719208("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB719209("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB719210("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB719211("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB719212("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB719213("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB719214("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB719215("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB719216("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB719217("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB719218("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB719219("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB719220("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB719221("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB719222("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB719223("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB719224("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB719225("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB719226("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB719227("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB719228("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB719229("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB719230("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB719231("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB719232("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB719233("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB719234("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB719235("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB719236("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB719237("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB719238("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB719239("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB719240("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB719241("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB719242("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB719243("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB719244("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB719245("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB719246("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB719247("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB719248("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB719249("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB719250("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB719251("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB719252("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB719253("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB719254("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB719255("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB719256("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB719257("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB719258("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB719259("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB719260("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB719261("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB719262("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB719263("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB719264("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB719265("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB719266("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB719267("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB719268("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB719269("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB719270("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB719271("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB719272("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB719273("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB719274("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB719275("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB719276("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB719277("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB719278("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB719279("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB719280("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB719281("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB719282("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB719283("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB719284("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB719285("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB719286("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB719287("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB719288("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB719289("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB719290("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB719291("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB719292("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB719293("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB719294("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB719295("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB719296("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB719297("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB719298("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB719299("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB719300("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB719301("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB719302("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB719303("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB719304("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB719305("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB719306("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB719307("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB719308("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB719309("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB719310("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB719311("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB719312("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB719313("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB719314("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB719315("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB719316("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB719317("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB719318("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB719319("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB719320("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB719321("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB719322("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB719323("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB719324("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB719325("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB719326("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB719327("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB719328("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB719329("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB719330("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB719331("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB719332("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB719333("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB719334("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB719335("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB719336("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB719337("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB719338("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB719339("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB719340("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB719341("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB719342("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB719343("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB719344("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB719345("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB719346("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB719347("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB719348("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB719349("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB719350("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB719351("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB719352("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB719353("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB719354("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB719355("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB719356("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB719357("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB719358("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB719359("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB719360("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB719361("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB719362("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB719363("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB719364("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB719365("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB719366("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB719367("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB719368("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB719369("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB719370("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB719371("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB719372("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB719373("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB719374("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB719375("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB719376("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB719377("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB719378("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB719379("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB719380("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB719381("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB719382("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB719383("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB719384("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB719385("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB719386("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB719387("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB719388("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB719389("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB719390("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB719391("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB719392("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB719393("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB719394("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB719395("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB719396("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB719397("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB719398("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB719399("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB719400("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB719401("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB719402("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB719403("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB719404("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB719405("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB719406("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB719407("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB719408("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB719409("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB719410("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB719411("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB719412("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB719413("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB719414("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB719415("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB719416("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB719417("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB719418("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB719419("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB719420("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB719421("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB719422("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB719423("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB719424("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB719425("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB719426("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB719427("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB719428("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB719429("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB719430("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB719431("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB719432("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB719433("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB719434("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB719435("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB719436("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB719437("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB719438("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB719439("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB719440("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB719441("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB719442("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB719443("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB719444("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB719445("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB719446("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB719447("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB719448("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB719449("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB719450("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB719451("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB719452("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB719453("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB719454("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB719455("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB719456("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB719457("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB719458("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB719459("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB719460("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB719461("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB719462("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB719463("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB719464("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB719465("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB719466("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB719467("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB719468("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB719469("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB719470("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB719471("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB719472("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB719473("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB719474("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB719475("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB719476("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB719477("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB719478("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB719479("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB719480("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB719481("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB719482("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB719483("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB719484("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB719485("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB719486("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB719487("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB719488("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB719489("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB719490("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB719491("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB719492("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB719493("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB719494("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB719495("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB719496("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB719497("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB719498("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB719499("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB719500("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB719501("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB719502("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB719503("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB719504("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB719505("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB719506("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB719507("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB719508("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB719509("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB719510("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB719511("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB719512("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB719513("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB719514("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB719515("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB719516("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB719517("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB719518("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB719519("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB719520("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB719521("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB719522("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB719523("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB719524("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB719525("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB719526("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB719527("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB719528("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB719529("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB719530("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB719531("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB719532("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB719533("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB719534("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB719535("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB719536("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB719537("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB719538("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB719539("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB719540("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB719541("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB719542("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB719543("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB719544("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB719545("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB719546("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB719547("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB719548("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB719549("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB719550("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB719551("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB719552("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB719553("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB719554("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB35838("[design]PLACEHOLDER-MOD-GOV-SYNC-PANORAMA"):::jobDesign
    JOB35636("[design]SH-DB-001"):::jobDesign
    JOB719556("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB591654("[design]SH-GOV-001"):::jobDesign
    JOB719558("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB719559("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB719560("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB37268("[design]SYS-MASTER-001"):::jobDesign
    JOB718820("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB718824("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB718822("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB718821("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB718826("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB718825("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB718819("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB718823("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB718819 -->|produces / 产出| DS10989
    JOB718820 -->|produces / 产出| DS10990
    JOB718821 -->|produces / 产出| DS10991
    JOB718822 -->|produces / 产出| DS10992
    JOB718823 -->|produces / 产出| DS10993
    JOB718824 -->|produces / 产出| DS10994
    JOB718825 -->|produces / 产出| DS10995
    JOB718826 -->|produces / 产出| DS10996
    JOB718826 -->|produces / 产出| DS10997
    JOB718831 -->|produces / 产出| DS10998
    JOB718827 -->|produces / 产出| DS10999
    JOB718828 -->|produces / 产出| DS11000
    JOB718829 -->|produces / 产出| DS11001
    JOB718830 -->|produces / 产出| DS11002
    DS10989 -->|consumed by / 被消费于| JOB718820
    DS10989 -->|consumed by / 被消费于| JOB718827
    DS10990 -->|consumed by / 被消费于| JOB718821
    DS10990 -->|consumed by / 被消费于| JOB718822
    DS10991 -->|consumed by / 被消费于| JOB718823
    DS10992 -->|consumed by / 被消费于| JOB718823
    DS10993 -->|consumed by / 被消费于| JOB718824
    DS10993 -->|consumed by / 被消费于| JOB718825
    DS10994 -->|consumed by / 被消费于| JOB718825
    DS10995 -->|consumed by / 被消费于| JOB718826
    DS10999 -->|consumed by / 被消费于| JOB718828
    DS11000 -->|consumed by / 被消费于| JOB718829
    DS11001 -->|consumed by / 被消费于| JOB718830
    DS11002 -->|consumed by / 被消费于| JOB718831

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

### 运营态全景图（仅 design_maturity=production）

> 仅展示已实现稳定运行的节点（运营态：14 datasets / 数据集, 695 jobs / 作业, 28 edges / 边）。

```mermaid
flowchart LR
    DS11001["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS11002["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS11000["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10999["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    DS10998["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10992["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10991["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10996["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10990["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10989["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10995["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10997["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10994["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10993["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB718831("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB718829("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB718827("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB718828("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB718830("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB718832("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB718833("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB718834("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB718835("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB718836("[production]INFRA-DB-001<br/>蓝图: INFRA-DB-001"):::jobProd
    JOB718837("[production]INFRA-DB-002<br/>蓝图: INFRA-DB-002"):::jobProd
    JOB718838("[production]INFRA-DB-003<br/>蓝图: INFRA-DB-003"):::jobProd
    JOB718839("[production]INFRA-DB-006<br/>蓝图: INFRA-DB-006"):::jobProd
    JOB718840("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB718841("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB718842("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB718843("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
    JOB718854("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB718855("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB718856("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB718858("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB718859("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB718860("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB718861("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB718862("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB718863("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB718864("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB718865("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB718867("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB718868("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB718869("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB718872("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB718873("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB718874("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB718875("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB718876("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB718877("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB718878("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB718879("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB718880("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
    JOB718882("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB718883("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB718884("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB718885("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB718886("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB718887("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB718888("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB718889("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB718890("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB718891("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB718892("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB718893("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB718894("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB718895("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB718896("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB718897("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB718898("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB718899("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB718900("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB718901("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB718902("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB718903("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB718904("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB718905("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB718906("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB718907("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB718908("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB718909("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB718910("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB718911("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB718912("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB718913("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB718914("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB718915("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB718916("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB718917("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB718918("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB718919("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB718920("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB718921("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB718922("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB718923("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB718924("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB718925("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB718926("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB718927("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB718928("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB718929("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB718930("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB718931("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB718932("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB718933("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB718934("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB718935("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB718936("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB718937("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB718938("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB718939("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB718940("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB718941("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB718942("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB718943("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB718944("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB718945("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB718946("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB718947("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB718948("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB718949("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB718950("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB718951("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB718952("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB718953("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB718954("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB718955("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB718956("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB718957("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB718958("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB718959("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB718960("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB718961("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB718962("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB718963("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB718964("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB718965("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB718966("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB718967("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB718968("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB718969("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB718970("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB718971("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB718972("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB718973("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB718974("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB718975("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB718976("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB718977("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB718978("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB718979("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB718980("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB718981("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB718982("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB718983("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB718984("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB718985("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB718986("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB718987("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB718988("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB718989("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB718990("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB718991("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB718992("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB718993("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB718994("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB718995("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB718996("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB718997("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB718998("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB718999("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB719000("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB719001("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB719002("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB719003("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB719004("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB719005("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB719006("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB719007("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB719008("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB719009("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB719010("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB719011("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB719012("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB719013("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB719014("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB719015("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB719016("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB719017("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB719018("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB719022("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB719023("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB719024("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB719027("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB719034("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB719035("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB719043("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB719046("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB719048("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB719049("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB719050("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB719051("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB719052("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB719053("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB719054("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB719055("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB719057("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB719058("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB719059("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB719061("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB719062("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB719063("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB719064("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB719065("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB719066("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB719067("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB719068("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB719069("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB719070("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB719071("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB719072("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB719073("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB719074("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB719075("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB719076("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB719077("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB719078("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB719079("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB719080("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB719081("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB719082("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB719084("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB719085("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB719086("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB719087("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB719088("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB719089("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB719090("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB719091("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB719092("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB719093("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB719098("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB719099("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB719100("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB719101("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB719102("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB719104("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB719105("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB719106("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB719107("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB719108("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB719109("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB719110("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB719111("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB719112("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB719113("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB719114("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB719115("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB719117("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB719118("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB719119("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB719120("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB719121("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB719122("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB719123("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB719124("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB719125("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB719126("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB719127("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB719128("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB719129("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB719130("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB719131("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB719132("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB719133("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB719134("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB719135("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB719136("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB719137("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB719138("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB719139("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB719140("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB719141("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB719142("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB719143("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB719144("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB719145("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB719146("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB719147("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB719148("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB719149("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB719150("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB719151("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB719152("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB719153("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB719154("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB719155("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB719156("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB719157("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB719158("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB719159("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB719160("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB719161("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB719162("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB719163("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB719164("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB719165("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB719166("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB719167("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB719168("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB719169("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB719170("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB719171("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB719172("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB719173("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB719174("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB719175("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB719176("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB719177("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB719178("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB719179("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB719180("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB719181("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB719182("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB719183("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB719184("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB719185("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB719186("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB719187("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB719188("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB719189("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB719190("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB719191("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB719192("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB719193("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB719194("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB719195("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB719196("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB719197("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB719198("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB719199("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB719200("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB719201("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB719202("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB719203("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB719204("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB719205("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB719206("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB719207("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB719208("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB719209("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB719210("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB719211("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB719212("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB719213("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB719214("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB719215("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB719216("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB719217("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB719218("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB719219("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB719220("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB719221("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB719222("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB719223("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB719224("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB719225("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB719226("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB719227("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB719228("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB719229("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB719230("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB719231("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB719232("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB719233("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB719234("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB719235("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB719236("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB719237("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB719238("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB719239("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB719240("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB719241("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB719242("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB719243("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB719244("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB719245("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB719246("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB719247("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB719248("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB719249("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB719250("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB719251("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB719252("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB719253("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB719254("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB719255("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB719256("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB719257("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB719258("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB719259("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB719260("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB719261("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB719262("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB719263("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB719264("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB719265("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB719266("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB719267("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB719268("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB719269("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB719270("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB719271("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB719272("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB719273("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB719274("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB719275("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB719276("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB719277("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB719278("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB719279("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB719280("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB719281("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB719282("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB719283("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB719284("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB719285("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB719286("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB719287("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB719288("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB719289("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB719290("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB719291("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB719292("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB719293("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB719294("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB719295("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB719296("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB719297("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB719298("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB719299("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB719300("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB719301("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB719302("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB719303("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB719304("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB719305("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB719306("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB719307("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB719308("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB719309("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB719310("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB719311("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB719312("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB719313("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB719314("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB719315("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB719316("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB719317("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB719318("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB719319("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB719320("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB719321("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB719322("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB719323("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB719324("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB719325("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB719326("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB719327("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB719328("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB719329("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB719330("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB719331("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB719332("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB719333("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB719334("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB719335("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB719336("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB719337("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB719338("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB719339("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB719340("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB719341("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB719342("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB719343("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB719344("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB719345("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB719346("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB719347("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB719348("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB719349("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB719350("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB719351("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB719352("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB719353("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB719354("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB719355("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB719356("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB719357("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB719358("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB719359("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB719360("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB719361("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB719362("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB719363("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB719364("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB719365("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB719366("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB719367("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB719368("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB719369("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB719370("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB719371("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB719372("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB719373("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB719374("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB719375("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB719376("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB719377("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB719378("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB719379("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB719380("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB719381("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB719382("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB719383("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB719384("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB719385("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB719386("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB719387("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB719388("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB719389("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB719390("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB719391("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB719392("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB719393("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB719394("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB719395("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB719396("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB719397("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB719398("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB719399("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB719400("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB719401("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB719402("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB719403("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB719404("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB719405("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB719406("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB719407("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB719408("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB719409("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB719410("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB719411("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB719412("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB719413("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB719414("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB719415("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB719416("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB719417("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB719418("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB719419("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB719420("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB719421("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB719422("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB719423("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB719424("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB719425("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB719426("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB719427("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB719428("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB719429("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB719430("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB719431("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB719432("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB719433("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB719434("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB719435("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB719436("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB719437("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB719438("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB719439("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB719440("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB719441("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB719442("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB719443("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB719444("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB719445("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB719446("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB719447("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB719448("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB719449("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB719450("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB719451("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB719452("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB719453("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB719454("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB719455("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB719456("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB719457("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB719458("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB719459("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB719460("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB719461("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB719462("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB719463("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB719464("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB719465("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB719466("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB719467("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB719468("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB719469("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB719470("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB719471("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB719472("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB719473("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB719474("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB719475("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB719476("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB719477("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB719478("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB719479("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB719480("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB719481("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB719482("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB719483("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB719484("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB719485("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB719486("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB719487("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB719488("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB719489("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB719490("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB719491("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB719492("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB719493("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB719494("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB719495("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB719496("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB719497("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB719498("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB719499("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB719500("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB719501("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB719502("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB719503("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB719504("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB719505("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB719506("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB719507("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB719508("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB719509("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB719510("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB719511("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB719512("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB719513("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB719514("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB719515("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB719516("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB719517("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB719518("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB719519("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB719520("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB719521("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB719522("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB719523("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB719524("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB719525("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB719526("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB719527("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB719528("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB719529("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB719530("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB719531("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB719532("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB719533("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB719534("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB719535("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB719536("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB719537("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB719538("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB719539("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB719540("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB719541("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB719542("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB719543("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB719544("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB719545("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB719546("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB719547("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB719548("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB719549("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB719550("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB719551("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB719552("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB719553("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB719554("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB719556("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB719558("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB719559("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB719560("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB718820("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB718824("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB718822("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB718821("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB718826("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB718825("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB718819("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB718823("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB718819 -->|produces / 产出| DS10989
    JOB718820 -->|produces / 产出| DS10990
    JOB718821 -->|produces / 产出| DS10991
    JOB718822 -->|produces / 产出| DS10992
    JOB718823 -->|produces / 产出| DS10993
    JOB718824 -->|produces / 产出| DS10994
    JOB718825 -->|produces / 产出| DS10995
    JOB718826 -->|produces / 产出| DS10996
    JOB718826 -->|produces / 产出| DS10997
    JOB718831 -->|produces / 产出| DS10998
    JOB718827 -->|produces / 产出| DS10999
    JOB718828 -->|produces / 产出| DS11000
    JOB718829 -->|produces / 产出| DS11001
    JOB718830 -->|produces / 产出| DS11002
    DS10989 -->|consumed by / 被消费于| JOB718820
    DS10989 -->|consumed by / 被消费于| JOB718827
    DS10990 -->|consumed by / 被消费于| JOB718821
    DS10990 -->|consumed by / 被消费于| JOB718822
    DS10991 -->|consumed by / 被消费于| JOB718823
    DS10992 -->|consumed by / 被消费于| JOB718823
    DS10993 -->|consumed by / 被消费于| JOB718824
    DS10993 -->|consumed by / 被消费于| JOB718825
    DS10994 -->|consumed by / 被消费于| JOB718825
    DS10995 -->|consumed by / 被消费于| JOB718826
    DS10999 -->|consumed by / 被消费于| JOB718828
    DS11000 -->|consumed by / 被消费于| JOB718829
    DS11001 -->|consumed by / 被消费于| JOB718830
    DS11002 -->|consumed by / 被消费于| JOB718831

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

### 生产数据流图（scope=production）

> 节点数: 10 datasets / 数据集, 768 jobs / 作业, 18 edges / 边

```mermaid
flowchart LR
    DS10998["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10992["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10991["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10996["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10990["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10989["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10995["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10997["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10994["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10993["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB718832("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB718833("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB718834("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB718835("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB718836("[production]INFRA-DB-001<br/>蓝图: INFRA-DB-001"):::jobProd
    JOB718837("[production]INFRA-DB-002<br/>蓝图: INFRA-DB-002"):::jobProd
    JOB718838("[production]INFRA-DB-003<br/>蓝图: INFRA-DB-003"):::jobProd
    JOB718839("[production]INFRA-DB-006<br/>蓝图: INFRA-DB-006"):::jobProd
    JOB718840("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB35951("[design]MOD-ARCH-BIZDB"):::jobDesign
    JOB718841("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB718842("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB718843("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
    JOB672126("[design]MOD-BT-018"):::jobDesign
    JOB672128("[design]MOD-BT-019"):::jobDesign
    JOB672130("[design]MOD-BT-020"):::jobDesign
    JOB672131("[design]MOD-BT-021"):::jobDesign
    JOB672133("[design]MOD-BT-022"):::jobDesign
    JOB672135("[design]MOD-BT-023"):::jobDesign
    JOB672137("[design]MOD-BT-024"):::jobDesign
    JOB672139("[design]MOD-BT-025"):::jobDesign
    JOB672142("[design]MOD-BT-026"):::jobDesign
    JOB35548("[design]MOD-C1-MARKETCH"):::jobDesign
    JOB35760("[design]MOD-CONTEXT_ENGINE"):::jobDesign
    JOB718854("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB718855("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB718856("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB671597("[design]MOD-DATA_ENG"):::jobDesign
    JOB718858("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB718859("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB718860("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB718861("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB718862("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB718863("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB718864("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB718865("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB712063("[design]MOD-EX-001"):::jobDesign
    JOB718867("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB718868("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB718869("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB35940("[design]MOD-FEEDBACK_LOOP"):::jobDesign
    JOB35578("[design]MOD-GATE_ENGINE"):::jobDesign
    JOB718872("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB718873("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB718874("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB718875("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB36856("[design]MOD-GOV-ALIGN-PANORAMAS"):::jobDesign
    JOB718876("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB718877("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB718878("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB139307("[design]MOD-GOV-HEARTBEAT"):::jobDesign
    JOB718879("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB718880("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
    JOB293594("[design]MOD-GOV-blueprint_status_transition_reconciler"):::jobDesign
    JOB293546("[design]MOD-GOV-cross_layer_contract_signature_reconciler"):::jobDesign
    JOB293501("[design]MOD-GOV-depgraph_pre_registration_gate"):::jobDesign
    JOB293524("[design]MOD-GOV-derivation_annotation_gate"):::jobDesign
    JOB293480("[design]MOD-GOV-folder_capacity_hard_limit_gate"):::jobDesign
    JOB140122("[design]MOD-GOV-heartbeat_daemon"):::jobDesign
    JOB293571("[design]MOD-GOV-relative_path_literal_gate"):::jobDesign
    JOB87876("[design]MOD-GOV-rule_execution_pairing_gate"):::jobDesign
    JOB388555("[design]MOD-GOV-runtime_violation_snapshot"):::jobDesign
    JOB388557("[design]MOD-GOV-runtime_violation_snapshot_reconciler"):::jobDesign
    JOB118710("[design]MOD-GOV-session_startup_health_check"):::jobDesign
    JOB360945("[design]MOD-GOV-stash_accumulation_gate"):::jobDesign
    JOB118708("[design]MOD-GOV-workspace_hygiene_reconciler"):::jobDesign
    JOB296197("[design]MOD-GOV-worktree_lifecycle"):::jobDesign
    JOB35857("[design]MOD-GOVERNANCE"):::jobDesign
    JOB718882("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB718883("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB718884("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB718885("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB718886("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB718887("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB718888("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB718889("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB718890("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB718891("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB718892("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB718893("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB718894("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB718895("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB718896("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB718897("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB718898("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB718899("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB718900("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB718901("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB718902("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB718903("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB718904("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB718905("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB718906("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB718907("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB718908("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB718909("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB718910("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB718911("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB718912("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB718913("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB718914("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB718915("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB718916("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB718917("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB718918("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB718919("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB718920("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB718921("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB718922("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB718923("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB718924("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB718925("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB718926("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB718927("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB718928("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB718929("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB718930("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB718931("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB718932("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB718933("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB718934("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB718935("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB718936("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB718937("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB718938("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB718939("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB718940("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB718941("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB718942("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB718943("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB718944("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB718945("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB718946("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB718947("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB718948("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB718949("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB718950("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB718951("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB718952("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB718953("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB718954("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB718955("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB718956("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB718957("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB718958("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB718959("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB718960("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB718961("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB718962("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB718963("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB718964("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB718965("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB718966("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB718967("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB718968("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB718969("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB718970("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB718971("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB718972("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB718973("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB718974("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB718975("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB718976("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB718977("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB718978("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB718979("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB718980("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB718981("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB718982("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB718983("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB718984("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB718985("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB718986("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB718987("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB718988("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB718989("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB718990("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB718991("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB718992("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB718993("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB718994("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB718995("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB718996("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB718997("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB718998("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB718999("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB719000("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB719001("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB719002("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB719003("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB719004("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB719005("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB719006("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB719007("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB719008("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB719009("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB719010("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB719011("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB719012("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB719013("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB719014("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB719015("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB321362("[design]MOD-GOV_blueprint_status_transition_reconciler"):::jobDesign
    JOB321311("[design]MOD-GOV_cross_layer_contract_signature_reconciler"):::jobDesign
    JOB719016("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB719017("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB719018("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB36357("[design]MOD-INF-005"):::jobDesign
    JOB37139("[design]MOD-INF-009"):::jobDesign
    JOB35565("[design]MOD-INF-011"):::jobDesign
    JOB719022("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB719023("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB719024("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB35954("[design]MOD-INF-016"):::jobDesign
    JOB36274("[design]MOD-INF-017"):::jobDesign
    JOB719027("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB37172("[design]MOD-INF-019"):::jobDesign
    JOB36050("[design]MOD-INF-020"):::jobDesign
    JOB35903("[design]MOD-INF-021"):::jobDesign
    JOB36400("[design]MOD-INF-022"):::jobDesign
    JOB35522("[design]MOD-INF-023"):::jobDesign
    JOB37193("[design]MOD-INF-024"):::jobDesign
    JOB719034("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB719035("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB35574("[design]MOD-INF-027"):::jobDesign
    JOB36222("[design]MOD-INF-028"):::jobDesign
    JOB35930("[design]MOD-INF-029"):::jobDesign
    JOB37217("[design]MOD-INF-030"):::jobDesign
    JOB37220("[design]MOD-INF-031"):::jobDesign
    JOB36336("[design]MOD-INF-033"):::jobDesign
    JOB35554("[design]MOD-INF-034"):::jobDesign
    JOB719043("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB37237("[design]MOD-INF-036"):::jobDesign
    JOB35538("[design]MOD-INF-037"):::jobDesign
    JOB719046("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB36080("[design]MOD-INF-039"):::jobDesign
    JOB719048("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB719049("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB719050("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB719051("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB35939("[design]MOD-INFRA_OPS"):::jobDesign
    JOB719052("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB719053("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB719054("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB719055("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB36157("[design]MOD-L00-002"):::jobDesign
    JOB35520("[design]MOD-L00-003"):::jobDesign
    JOB61876("[design]MOD-L00-004"):::jobDesign
    JOB719057("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB719058("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB719059("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB551909("[design]MOD-L02-001"):::jobDesign
    JOB719061("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB719062("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB719063("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB719064("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB719065("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB719066("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB719067("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB719068("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB719069("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB719070("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB719071("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB719072("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB719073("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB719074("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB719075("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB719076("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB719077("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB719078("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB719079("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB719080("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB719081("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB719082("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB688297("[design]MOD-L04-001"):::jobDesign
    JOB719084("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB719085("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB719086("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB719087("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB719088("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB719089("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB719090("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB719091("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB719092("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB719093("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB36390("[design]MOD-MASTER-001"):::jobDesign
    JOB35517("[design]MOD-MASTER-002"):::jobDesign
    JOB36344("[design]MOD-MASTER-003"):::jobDesign
    JOB35528("[design]MOD-MASTER_BLUEPRINT"):::jobDesign
    JOB711884("[design]MOD-MKT-001"):::jobDesign
    JOB711954("[design]MOD-MKT-002"):::jobDesign
    JOB712012("[design]MOD-MKT-003"):::jobDesign
    JOB719098("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB719099("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB719100("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB36113("[design]MOD-PF_ALLOC"):::jobDesign
    JOB719101("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB719102("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB35898("[design]MOD-RESOURCE_OPTIMIZATION_ENGINE"):::jobDesign
    JOB719104("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB719105("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB719106("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB719107("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB719108("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB719109("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB719110("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB719111("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB719112("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB719113("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB719114("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB35600("[design]MOD-SIMULATION"):::jobDesign
    JOB119053("[design]MOD-SMOKE-TEST"):::jobDesign
    JOB719115("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB118981("[design]MOD-TEST"):::jobDesign
    JOB719117("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB719118("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB719119("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB719120("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB719121("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB719122("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB719123("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB719124("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB719125("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB719126("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB719127("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB719128("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB719129("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB719130("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB719131("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB719132("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB719133("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB719134("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB719135("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB719136("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB719137("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB719138("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB719139("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB719140("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB719141("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB719142("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB719143("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB719144("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB719145("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB719146("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB719147("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB719148("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB719149("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB719150("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB719151("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB719152("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB719153("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB719154("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB719155("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB719156("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB719157("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB719158("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB719159("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB719160("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB719161("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB719162("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB719163("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB719164("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB719165("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB719166("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB719167("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB719168("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB719169("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB719170("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB719171("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB719172("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB719173("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB719174("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB719175("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB719176("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB719177("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB719178("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB719179("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB719180("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB719181("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB719182("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB719183("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB719184("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB719185("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB719186("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB719187("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB719188("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB719189("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB719190("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB719191("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB719192("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB719193("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB719194("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB719195("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB719196("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB719197("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB719198("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB719199("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB719200("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB719201("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB719202("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB719203("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB719204("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB719205("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB719206("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB719207("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB719208("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB719209("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB719210("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB719211("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB719212("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB719213("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB719214("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB719215("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB719216("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB719217("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB719218("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB719219("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB719220("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB719221("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB719222("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB719223("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB719224("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB719225("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB719226("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB719227("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB719228("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB719229("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB719230("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB719231("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB719232("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB719233("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB719234("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB719235("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB719236("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB719237("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB719238("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB719239("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB719240("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB719241("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB719242("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB719243("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB719244("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB719245("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB719246("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB719247("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB719248("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB719249("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB719250("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB719251("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB719252("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB719253("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB719254("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB719255("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB719256("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB719257("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB719258("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB719259("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB719260("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB719261("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB719262("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB719263("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB719264("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB719265("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB719266("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB719267("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB719268("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB719269("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB719270("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB719271("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB719272("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB719273("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB719274("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB719275("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB719276("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB719277("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB719278("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB719279("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB719280("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB719281("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB719282("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB719283("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB719284("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB719285("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB719286("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB719287("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB719288("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB719289("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB719290("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB719291("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB719292("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB719293("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB719294("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB719295("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB719296("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB719297("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB719298("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB719299("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB719300("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB719301("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB719302("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB719303("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB719304("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB719305("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB719306("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB719307("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB719308("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB719309("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB719310("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB719311("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB719312("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB719313("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB719314("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB719315("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB719316("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB719317("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB719318("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB719319("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB719320("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB719321("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB719322("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB719323("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB719324("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB719325("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB719326("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB719327("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB719328("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB719329("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB719330("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB719331("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB719332("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB719333("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB719334("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB719335("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB719336("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB719337("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB719338("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB719339("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB719340("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB719341("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB719342("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB719343("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB719344("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB719345("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB719346("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB719347("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB719348("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB719349("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB719350("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB719351("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB719352("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB719353("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB719354("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB719355("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB719356("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB719357("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB719358("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB719359("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB719360("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB719361("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB719362("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB719363("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB719364("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB719365("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB719366("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB719367("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB719368("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB719369("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB719370("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB719371("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB719372("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB719373("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB719374("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB719375("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB719376("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB719377("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB719378("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB719379("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB719380("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB719381("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB719382("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB719383("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB719384("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB719385("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB719386("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB719387("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB719388("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB719389("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB719390("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB719391("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB719392("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB719393("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB719394("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB719395("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB719396("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB719397("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB719398("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB719399("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB719400("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB719401("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB719402("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB719403("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB719404("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB719405("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB719406("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB719407("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB719408("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB719409("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB719410("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB719411("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB719412("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB719413("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB719414("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB719415("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB719416("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB719417("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB719418("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB719419("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB719420("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB719421("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB719422("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB719423("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB719424("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB719425("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB719426("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB719427("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB719428("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB719429("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB719430("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB719431("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB719432("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB719433("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB719434("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB719435("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB719436("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB719437("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB719438("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB719439("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB719440("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB719441("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB719442("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB719443("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB719444("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB719445("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB719446("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB719447("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB719448("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB719449("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB719450("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB719451("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB719452("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB719453("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB719454("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB719455("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB719456("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB719457("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB719458("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB719459("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB719460("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB719461("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB719462("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB719463("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB719464("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB719465("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB719466("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB719467("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB719468("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB719469("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB719470("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB719471("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB719472("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB719473("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB719474("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB719475("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB719476("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB719477("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB719478("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB719479("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB719480("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB719481("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB719482("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB719483("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB719484("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB719485("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB719486("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB719487("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB719488("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB719489("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB719490("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB719491("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB719492("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB719493("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB719494("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB719495("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB719496("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB719497("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB719498("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB719499("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB719500("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB719501("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB719502("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB719503("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB719504("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB719505("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB719506("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB719507("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB719508("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB719509("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB719510("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB719511("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB719512("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB719513("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB719514("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB719515("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB719516("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB719517("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB719518("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB719519("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB719520("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB719521("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB719522("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB719523("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB719524("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB719525("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB719526("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB719527("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB719528("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB719529("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB719530("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB719531("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB719532("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB719533("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB719534("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB719535("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB719536("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB719537("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB719538("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB719539("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB719540("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB719541("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB719542("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB719543("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB719544("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB719545("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB719546("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB719547("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB719548("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB719549("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB719550("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB719551("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB719552("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB719553("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB719554("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB35838("[design]PLACEHOLDER-MOD-GOV-SYNC-PANORAMA"):::jobDesign
    JOB35636("[design]SH-DB-001"):::jobDesign
    JOB719556("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB591654("[design]SH-GOV-001"):::jobDesign
    JOB719558("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB719559("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB719560("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB37268("[design]SYS-MASTER-001"):::jobDesign
    JOB718820("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB718824("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB718822("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB718821("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB718826("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB718825("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB718819("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB718823("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB718819 -->|produces / 产出| DS10989
    JOB718820 -->|produces / 产出| DS10990
    JOB718821 -->|produces / 产出| DS10991
    JOB718822 -->|produces / 产出| DS10992
    JOB718823 -->|produces / 产出| DS10993
    JOB718824 -->|produces / 产出| DS10994
    JOB718825 -->|produces / 产出| DS10995
    JOB718826 -->|produces / 产出| DS10996
    JOB718826 -->|produces / 产出| DS10997
    DS10989 -->|consumed by / 被消费于| JOB718820
    DS10990 -->|consumed by / 被消费于| JOB718821
    DS10990 -->|consumed by / 被消费于| JOB718822
    DS10991 -->|consumed by / 被消费于| JOB718823
    DS10992 -->|consumed by / 被消费于| JOB718823
    DS10993 -->|consumed by / 被消费于| JOB718824
    DS10993 -->|consumed by / 被消费于| JOB718825
    DS10994 -->|consumed by / 被消费于| JOB718825
    DS10995 -->|consumed by / 被消费于| JOB718826

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

### 回测内部数据流图（scope=backtest_internal）

> 节点数: 4 datasets / 数据集, 5 jobs / 作业, 8 edges / 边

```mermaid
flowchart LR
    DS11001["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS11002["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS11000["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10999["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    JOB718831("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB718829("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB718827("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB718828("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB718830("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB718827 -->|produces / 产出| DS10999
    JOB718828 -->|produces / 产出| DS11000
    JOB718829 -->|produces / 产出| DS11001
    JOB718830 -->|produces / 产出| DS11002
    DS10999 -->|consumed by / 被消费于| JOB718828
    DS11000 -->|consumed by / 被消费于| JOB718829
    DS11001 -->|consumed by / 被消费于| JOB718830
    DS11002 -->|consumed by / 被消费于| JOB718831

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

## Dataset 清单（自动生成 · 生成器: generate_dataflow_diagram.py）

| ID | entity_name / 实体名 | scope / 范围 | contract_ref / 契约引用 | domain / 域 | pit_policy / PIT策略 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |
|----|----------------------|--------------|---------------------------|------------|------------------|------------------|---------------------------|--------------------|----------|
| DS-11001 | backtest.fills / 回测.模拟成交 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测模拟成交（symbol/quantity/price/commission/slippage），撮合引擎产出 |
| DS-11002 | backtest.nav_series / 回测.净值序列 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测净值序列（timestamp/nav/cash/positions），组合更新产出 |
| DS-11000 | backtest.target_weights / 回测.目标权重 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测目标权重（symbol/target_weight/timestamp），策略根据tick事件生成 |
| DS-10999 | backtest.tick_event / 回测.Tick事件 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测Tick事件（历史tick重放，含timestamp/symbol/price/volume），回测内部类型 |
| DS-10998 | backtest.result / 回测.结果 | production / 生产 | CTR-P1-016 | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测结果（nav_series/sharpe/max_drawdown/trades），CTR-P1-016 BacktestResult |
| DS-10992 | factor.momentum_20d / 因子.20日动量 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | MOD-L02-001 | production / 生产 | generated / 已生成 | 20日动量因子信号（factor_id/symbol/as_of_date/raw_value/rank_pct），CTR-002 FactorSignal |
| DS-10991 | factor.value_factor / 因子.价值因子 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | MOD-L02-001 | production / 生产 | generated / 已生成 | 价值因子信号（factor_id/symbol/as_of_date/raw_value/normalized_value），CTR-002 FactorSignal |
| DS-10996 | fill.executed / 成交.已成交 | production / 生产 | CTR-005 | D_EX_CORE / 执行核心 | strict / 严格 | MOD-L06-001 | production / 生产 | generated / 已生成 | 成交回报（symbol/quantity/price/commission/timestamp），CTR-005 Fill |
| DS-10990 | market_data.ohlc_bar / 市场数据.OHLC K线 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 derived |
| DS-10989 | market_data.tick / 市场数据.Tick行情 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 标准化Tick行情（symbol/timestamp/OHLCV/quality_score），CTR-001 NormalizedMarketData |
| DS-10995 | order.target / 订单.目标订单 | production / 生产 | CTR-004 | D_PF_CORE / 持仓核心 | strict / 严格 | MOD-L05-001 | production / 生产 | generated / 已生成 | 目标订单（symbol/side/quantity/price/order_type），CTR-004 Order |
| DS-10997 | position.snapshot / 持仓.快照 | production / 生产 | CTR-006 | D_EX_CORE / 执行核心 | strict / 严格 | MOD-L06-001 | production / 生产 | generated / 已生成 | 持仓快照（symbol/quantity/avg_cost/market_value/timestamp），CTR-006 PositionSnapshot |
| DS-10994 | risk.limits / 风险.限额 | production / 生产 | CTR-003 | D_RISK / 风险 | strict / 严格 | MOD-L04-001 | production / 生产 | generated / 已生成 | 风险限额（max_position/max_drawdown/exposure_limits），CTR-003 RiskLimits |
| DS-10993 | signal.composite / 信号.合成信号 | production / 生产 | CTR-P1-015 | D_SIGLEGACY / 信号(legacy) | strict / 严格 | - | production / 生产 | generated / 已生成 | 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 SynthesizedSignal |

## Job 清单（自动生成 · 生成器: generate_dataflow_diagram.py）

| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |
|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|------------------|---------------------------|--------------------|----------|
| JOB-718831 | backtest.calc_metrics / 回测.计算指标 | backtest_internal / 回测内部 | src/zephyr/backtest/metrics.py | manual / 手动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PIT校验），产出DS-010 backtest.result |
| JOB-718829 | backtest.match_fills / 回测.撮合成交 | backtest_internal / 回测内部 | src/zephyr/backtest/matching_logic.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 backtest.fills |
| JOB-718827 | backtest.replay_ticks / 回测.Tick重放 | backtest_internal / 回测内部 | src/zephyr/backtest/tick_replay.py | manual / 手动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-011 backtest.tick_event |
| JOB-718828 | backtest.run_event_driven / 回测.事件驱动运行 | backtest_internal / 回测内部 | src/zephyr/backtest/event_engine.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 backtest.target_weights |
| JOB-718830 | backtest.update_portfolio / 回测.更新组合 | backtest_internal / 回测内部 | src/zephyr/backtest/portfolio.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtest.nav_series |
| JOB-718832 | CFG-rule-enforcement-registry | production / 生产 | - | - | - | CFG-rule-enforcement-registry | production / 生产 | stable | - |
| JOB-718833 | CFG-rule-registry-collection | production / 生产 | - | - | - | CFG-rule-registry-collection | production / 生产 | stable | - |
| JOB-718834 | CFG-scripts-registry | production / 生产 | - | - | - | CFG-scripts-registry | production / 生产 | stable | - |
| JOB-718835 | CFG-test-suite-registry | production / 生产 | - | - | - | CFG-test-suite-registry | production / 生产 | stable | - |
| JOB-718836 | INFRA-DB-001 | production / 生产 | - | - | - | INFRA-DB-001 | production / 生产 | stable | - |
| JOB-718837 | INFRA-DB-002 | production / 生产 | - | - | - | INFRA-DB-002 | production / 生产 | stable | - |
| JOB-718838 | INFRA-DB-003 | production / 生产 | - | - | - | INFRA-DB-003 | production / 生产 | stable | - |
| JOB-718839 | INFRA-DB-006 | production / 生产 | - | - | - | INFRA-DB-006 | production / 生产 | stable | - |
| JOB-718840 | MOD-ALT_DATA | production / 生产 | - | - | - | MOD-ALT_DATA | production / 生产 | generated / 已生成 | - |
| JOB-35951 | MOD-ARCH-BIZDB | production / 生产 | - | - | - | MOD-ARCH-BIZDB | design / 设计 | planned | - |
| JOB-718841 | MOD-AUTONOMY_CORE | production / 生产 | - | - | - | MOD-AUTONOMY_CORE | production / 生产 | stable | - |
| JOB-718842 | MOD-BT-001 | production / 生产 | - | - | - | MOD-BT-001 | production / 生产 | stable | - |
| JOB-718843 | MOD-BT-017 | production / 生产 | - | - | - | MOD-BT-017 | production / 生产 | stable | - |
| JOB-672126 | MOD-BT-018 | production / 生产 | - | - | - | MOD-BT-018 | design / 设计 | planned | - |
| JOB-672128 | MOD-BT-019 | production / 生产 | - | - | - | MOD-BT-019 | design / 设计 | planned | - |
| JOB-672130 | MOD-BT-020 | production / 生产 | - | - | - | MOD-BT-020 | design / 设计 | planned | - |
| JOB-672131 | MOD-BT-021 | production / 生产 | - | - | - | MOD-BT-021 | design / 设计 | planned | - |
| JOB-672133 | MOD-BT-022 | production / 生产 | - | - | - | MOD-BT-022 | design / 设计 | planned | - |
| JOB-672135 | MOD-BT-023 | production / 生产 | - | - | - | MOD-BT-023 | design / 设计 | planned | - |
| JOB-672137 | MOD-BT-024 | production / 生产 | - | - | - | MOD-BT-024 | design / 设计 | planned | - |
| JOB-672139 | MOD-BT-025 | production / 生产 | - | - | - | MOD-BT-025 | design / 设计 | planned | - |
| JOB-672142 | MOD-BT-026 | production / 生产 | - | - | - | MOD-BT-026 | design / 设计 | planned | - |
| JOB-35548 | MOD-C1-MARKETCH | production / 生产 | - | - | - | MOD-C1-MARKETCH | design / 设计 | planned | - |
| JOB-35760 | MOD-CONTEXT_ENGINE | production / 生产 | - | - | - | MOD-CONTEXT_ENGINE | design / 设计 | planned | - |
| JOB-718854 | MOD-CROSS_ASSET | production / 生产 | - | - | - | MOD-CROSS_ASSET | production / 生产 | generated / 已生成 | - |
| JOB-718855 | MOD-D5_ARCH_TOOLS | production / 生产 | - | - | - | MOD-D5_ARCH_TOOLS | production / 生产 | generated / 已生成 | - |
| JOB-718856 | MOD-DATABASE | production / 生产 | - | - | - | MOD-DATABASE | production / 生产 | generated / 已生成 | - |
| JOB-671597 | MOD-DATA_ENG | production / 生产 | - | - | - | MOD-DATA_ENG | design / 设计 | generated / 已生成 | - |
| JOB-718858 | MOD-DATA_GOV | production / 生产 | - | - | - | MOD-DATA_GOV | production / 生产 | generated / 已生成 | - |
| JOB-718859 | MOD-DATA_GOV-001 | production / 生产 | - | - | - | MOD-DATA_GOV-001 | production / 生产 | stable | - |
| JOB-718860 | MOD-DATA_GOV-002 | production / 生产 | - | - | - | MOD-DATA_GOV-002 | production / 生产 | stable | - |
| JOB-718861 | MOD-DATA_GOV-003 | production / 生产 | - | - | - | MOD-DATA_GOV-003 | production / 生产 | stable | - |
| JOB-718862 | MOD-DATA_SEC | production / 生产 | - | - | - | MOD-DATA_SEC | production / 生产 | generated / 已生成 | - |
| JOB-718863 | MOD-DIGITAL_TWIN | production / 生产 | - | - | - | MOD-DIGITAL_TWIN | production / 生产 | generated / 已生成 | - |
| JOB-718864 | MOD-D_GOV_SCRIPTS | production / 生产 | - | - | - | MOD-D_GOV_SCRIPTS | production / 生产 | generated / 已生成 | - |
| JOB-718865 | MOD-E2E-001 | production / 生产 | - | - | - | MOD-E2E-001 | production / 生产 | generated / 已生成 | - |
| JOB-712063 | MOD-EX-001 | production / 生产 | - | - | - | MOD-EX-001 | design / 设计 | planned | - |
| JOB-718867 | MOD-EXEC_SIM | production / 生产 | - | - | - | MOD-EXEC_SIM | production / 生产 | generated / 已生成 | - |
| JOB-718868 | MOD-EX_SOR | production / 生产 | - | - | - | MOD-EX_SOR | production / 生产 | generated / 已生成 | - |
| JOB-718869 | MOD-FEEDBACK-014 | production / 生产 | - | - | - | MOD-FEEDBACK-014 | production / 生产 | stable | - |
| JOB-35940 | MOD-FEEDBACK_LOOP | production / 生产 | - | - | - | MOD-FEEDBACK_LOOP | design / 设计 | planned | - |
| JOB-35578 | MOD-GATE_ENGINE | production / 生产 | - | - | - | MOD-GATE_ENGINE | design / 设计 | planned | - |
| JOB-718872 | MOD-GOV-008 | production / 生产 | - | - | - | MOD-GOV-008 | production / 生产 | generated / 已生成 | - |
| JOB-718873 | MOD-GOV-019 | production / 生产 | - | - | - | MOD-GOV-019 | production / 生产 | stable | - |
| JOB-718874 | MOD-GOV-029 | production / 生产 | - | - | - | MOD-GOV-029 | production / 生产 | generated / 已生成 | - |
| JOB-718875 | MOD-GOV-041 | production / 生产 | - | - | - | MOD-GOV-041 | production / 生产 | generated / 已生成 | - |
| JOB-36856 | MOD-GOV-ALIGN-PANORAMAS | production / 生产 | - | - | - | MOD-GOV-ALIGN-PANORAMAS | design / 设计 | stable | - |
| JOB-718876 | MOD-GOV-AUDIT | production / 生产 | - | - | - | MOD-GOV-AUDIT | production / 生产 | stable | - |
| JOB-718877 | MOD-GOV-CG | production / 生产 | - | - | - | MOD-GOV-CG | production / 生产 | stable | - |
| JOB-718878 | MOD-GOV-DOCS | production / 生产 | - | - | - | MOD-GOV-DOCS | production / 生产 | generated / 已生成 | - |
| JOB-139307 | MOD-GOV-HEARTBEAT | production / 生产 | - | - | - | MOD-GOV-HEARTBEAT | design / 设计 | planned | - |
| JOB-718879 | MOD-GOV-SCRIPTS | production / 生产 | - | - | - | MOD-GOV-SCRIPTS | production / 生产 | stable | - |
| JOB-718880 | MOD-GOV-backfill_checker | production / 生产 | - | - | - | MOD-GOV-backfill_checker | production / 生产 | generated / 已生成 | - |
| JOB-293594 | MOD-GOV-blueprint_status_transition_reconciler | production / 生产 | - | - | - | MOD-GOV-blueprint_status_transition_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-293546 | MOD-GOV-cross_layer_contract_signature_reconciler | production / 生产 | - | - | - | MOD-GOV-cross_layer_contract_signature_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-293501 | MOD-GOV-depgraph_pre_registration_gate | production / 生产 | - | - | - | MOD-GOV-depgraph_pre_registration_gate | design / 设计 | generated / 已生成 | - |
| JOB-293524 | MOD-GOV-derivation_annotation_gate | production / 生产 | - | - | - | MOD-GOV-derivation_annotation_gate | design / 设计 | generated / 已生成 | - |
| JOB-293480 | MOD-GOV-folder_capacity_hard_limit_gate | production / 生产 | - | - | - | MOD-GOV-folder_capacity_hard_limit_gate | design / 设计 | generated / 已生成 | - |
| JOB-140122 | MOD-GOV-heartbeat_daemon | production / 生产 | - | - | - | MOD-GOV-heartbeat_daemon | design / 设计 | planned | - |
| JOB-293571 | MOD-GOV-relative_path_literal_gate | production / 生产 | - | - | - | MOD-GOV-relative_path_literal_gate | design / 设计 | generated / 已生成 | - |
| JOB-87876 | MOD-GOV-rule_execution_pairing_gate | production / 生产 | - | - | - | MOD-GOV-rule_execution_pairing_gate | design / 设计 | stable | - |
| JOB-388555 | MOD-GOV-runtime_violation_snapshot | production / 生产 | - | - | - | MOD-GOV-runtime_violation_snapshot | design / 设计 | stable | - |
| JOB-388557 | MOD-GOV-runtime_violation_snapshot_reconciler | production / 生产 | - | - | - | MOD-GOV-runtime_violation_snapshot_reconciler | design / 设计 | stable | - |
| JOB-118710 | MOD-GOV-session_startup_health_check | production / 生产 | - | - | - | MOD-GOV-session_startup_health_check | design / 设计 | planned | - |
| JOB-360945 | MOD-GOV-stash_accumulation_gate | production / 生产 | - | - | - | MOD-GOV-stash_accumulation_gate | design / 设计 | deprecated | - |
| JOB-118708 | MOD-GOV-workspace_hygiene_reconciler | production / 生产 | - | - | - | MOD-GOV-workspace_hygiene_reconciler | design / 设计 | stable | - |
| JOB-296197 | MOD-GOV-worktree_lifecycle | production / 生产 | - | - | - | MOD-GOV-worktree_lifecycle | design / 设计 | generated / 已生成 | - |
| JOB-35857 | MOD-GOVERNANCE | production / 生产 | - | - | - | MOD-GOVERNANCE | design / 设计 | generated / 已生成 | - |
| JOB-718882 | MOD-GOV_AGENT_RBAC | production / 生产 | - | - | - | MOD-GOV_AGENT_RBAC | production / 生产 | generated / 已生成 | - |
| JOB-718883 | MOD-GOV_ALIGN_PANORAMAS | production / 生产 | - | - | - | MOD-GOV_ALIGN_PANORAMAS | production / 生产 | generated / 已生成 | - |
| JOB-718884 | MOD-GOV_ANALYZE_CHANGE_IMPACT | production / 生产 | - | - | - | MOD-GOV_ANALYZE_CHANGE_IMPACT | production / 生产 | generated / 已生成 | - |
| JOB-718885 | MOD-GOV_ANALYZE_ORPHAN_CONSUMERS | production / 生产 | - | - | - | MOD-GOV_ANALYZE_ORPHAN_CONSUMERS | production / 生产 | generated / 已生成 | - |
| JOB-718886 | MOD-GOV_ARCH_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_ARCH_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718887 | MOD-GOV_ASYNC_RUNTIME | production / 生产 | - | - | - | MOD-GOV_ASYNC_RUNTIME | production / 生产 | generated / 已生成 | - |
| JOB-718888 | MOD-GOV_AUDIT | production / 生产 | - | - | - | MOD-GOV_AUDIT | production / 生产 | generated / 已生成 | - |
| JOB-718889 | MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | production / 生产 | - | - | - | MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | production / 生产 | generated / 已生成 | - |
| JOB-718890 | MOD-GOV_AUDIT_TRAIL | production / 生产 | - | - | - | MOD-GOV_AUDIT_TRAIL | production / 生产 | generated / 已生成 | - |
| JOB-718891 | MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | production / 生产 | - | - | - | MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | production / 生产 | generated / 已生成 | - |
| JOB-718892 | MOD-GOV_BARE_GETENV_GATE | production / 生产 | - | - | - | MOD-GOV_BARE_GETENV_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718893 | MOD-GOV_BARE_SQL_GATE | production / 生产 | - | - | - | MOD-GOV_BARE_SQL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718894 | MOD-GOV_BATCHED_AUTO_COMMITTER | production / 生产 | - | - | - | MOD-GOV_BATCHED_AUTO_COMMITTER | production / 生产 | generated / 已生成 | - |
| JOB-718895 | MOD-GOV_BEHAVIORAL_ADMISSION | production / 生产 | - | - | - | MOD-GOV_BEHAVIORAL_ADMISSION | production / 生产 | generated / 已生成 | - |
| JOB-718896 | MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718897 | MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | production / 生产 | - | - | - | MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | production / 生产 | generated / 已生成 | - |
| JOB-718898 | MOD-GOV_CAPABILITY_OVERLAP_GATE | production / 生产 | - | - | - | MOD-GOV_CAPABILITY_OVERLAP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718899 | MOD-GOV_CHECK_ANY_ABUSE | production / 生产 | - | - | - | MOD-GOV_CHECK_ANY_ABUSE | production / 生产 | generated / 已生成 | - |
| JOB-718900 | MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | production / 生产 | - | - | - | MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | production / 生产 | generated / 已生成 | - |
| JOB-718901 | MOD-GOV_CHECK_RULE_COVERAGE | production / 生产 | - | - | - | MOD-GOV_CHECK_RULE_COVERAGE | production / 生产 | generated / 已生成 | - |
| JOB-718902 | MOD-GOV_CHECK_VOCAB_HARDCODE | production / 生产 | - | - | - | MOD-GOV_CHECK_VOCAB_HARDCODE | production / 生产 | generated / 已生成 | - |
| JOB-718903 | MOD-GOV_CH_BATCH_SIZE_GATE | production / 生产 | - | - | - | MOD-GOV_CH_BATCH_SIZE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718904 | MOD-GOV_CH_VERSION_COL_GATE | production / 生产 | - | - | - | MOD-GOV_CH_VERSION_COL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718905 | MOD-GOV_CLAIM_REQUIRED_GATE | production / 生产 | - | - | - | MOD-GOV_CLAIM_REQUIRED_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718906 | MOD-GOV_CODE_QUALITY_DOMAIN | production / 生产 | - | - | - | MOD-GOV_CODE_QUALITY_DOMAIN | production / 生产 | generated / 已生成 | - |
| JOB-718907 | MOD-GOV_COMMIT_GATES | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATES | production / 生产 | stable | - |
| JOB-718908 | MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | production / 生产 | stable | - |
| JOB-718909 | MOD-GOV_COMMIT_GATE_REGISTRY | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATE_REGISTRY | production / 生产 | stable | - |
| JOB-718910 | MOD-GOV_COMMON | production / 生产 | - | - | - | MOD-GOV_COMMON | production / 生产 | generated / 已生成 | - |
| JOB-718911 | MOD-GOV_CONCURRENT_WRITE_TEST | production / 生产 | - | - | - | MOD-GOV_CONCURRENT_WRITE_TEST | production / 生产 | generated / 已生成 | - |
| JOB-718912 | MOD-GOV_CREATE_GUARD | production / 生产 | - | - | - | MOD-GOV_CREATE_GUARD | production / 生产 | generated / 已生成 | - |
| JOB-718913 | MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | production / 生产 | - | - | - | MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | production / 生产 | generated / 已生成 | - |
| JOB-718914 | MOD-GOV_DANGLING_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_DANGLING_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718915 | MOD-GOV_DATABASE_SERVICE | production / 生产 | - | - | - | MOD-GOV_DATABASE_SERVICE | production / 生产 | generated / 已生成 | - |
| JOB-718916 | MOD-GOV_DATAFLOW_DIAGRAM | production / 生产 | - | - | - | MOD-GOV_DATAFLOW_DIAGRAM | production / 生产 | generated / 已生成 | - |
| JOB-718917 | MOD-GOV_DEEPSEEK_API | production / 生产 | - | - | - | MOD-GOV_DEEPSEEK_API | production / 生产 | generated / 已生成 | - |
| JOB-718918 | MOD-GOV_DEFERRED_EDGES | production / 生产 | - | - | - | MOD-GOV_DEFERRED_EDGES | production / 生产 | generated / 已生成 | - |
| JOB-718919 | MOD-GOV_DEFERRED_REG | production / 生产 | - | - | - | MOD-GOV_DEFERRED_REG | production / 生产 | generated / 已生成 | - |
| JOB-718920 | MOD-GOV_DEMO_EE_PIPELINE | production / 生产 | - | - | - | MOD-GOV_DEMO_EE_PIPELINE | production / 生产 | generated / 已生成 | - |
| JOB-718921 | MOD-GOV_DETECT_CAUSAL_CONFLICTS | production / 生产 | - | - | - | MOD-GOV_DETECT_CAUSAL_CONFLICTS | production / 生产 | generated / 已生成 | - |
| JOB-718922 | MOD-GOV_DIFF_HELPERS | production / 生产 | - | - | - | MOD-GOV_DIFF_HELPERS | production / 生产 | generated / 已生成 | - |
| JOB-718923 | MOD-GOV_DM200912_QUERY_DOMAINS | production / 生产 | - | - | - | MOD-GOV_DM200912_QUERY_DOMAINS | production / 生产 | generated / 已生成 | - |
| JOB-718924 | MOD-GOV_DM200916_WRITE_DIRECT | production / 生产 | - | - | - | MOD-GOV_DM200916_WRITE_DIRECT | production / 生产 | generated / 已生成 | - |
| JOB-718925 | MOD-GOV_DOC_REF_BROKEN_GATE | production / 生产 | - | - | - | MOD-GOV_DOC_REF_BROKEN_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718926 | MOD-GOV_DOMAIN_FK_GATE | production / 生产 | - | - | - | MOD-GOV_DOMAIN_FK_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718927 | MOD-GOV_DQ | production / 生产 | - | - | - | MOD-GOV_DQ | production / 生产 | generated / 已生成 | - |
| JOB-718928 | MOD-GOV_EMERGENCY_COMMIT | production / 生产 | - | - | - | MOD-GOV_EMERGENCY_COMMIT | production / 生产 | stable | - |
| JOB-718929 | MOD-GOV_EMPTY_HANDLER_GATE | production / 生产 | - | - | - | MOD-GOV_EMPTY_HANDLER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718930 | MOD-GOV_ENFORCEMENT | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT | production / 生产 | generated / 已生成 | - |
| JOB-718931 | MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | production / 生产 | stable | - |
| JOB-718932 | MOD-GOV_ENFORCEMENT_WORKTREE_POOL | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_WORKTREE_POOL | production / 生产 | stable | - |
| JOB-718933 | MOD-GOV_ENFORCEMENT_worktree_lifecycle | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_worktree_lifecycle | production / 生产 | generated / 已生成 | - |
| JOB-718934 | MOD-GOV_ERROR_PATTERN_CONSUMER | production / 生产 | - | - | - | MOD-GOV_ERROR_PATTERN_CONSUMER | production / 生产 | stable | - |
| JOB-718935 | MOD-GOV_ERROR_PATTERN_LIBRARY | production / 生产 | - | - | - | MOD-GOV_ERROR_PATTERN_LIBRARY | production / 生产 | stable | - |
| JOB-718936 | MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE | production / 生产 | - | - | - | MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718937 | MOD-GOV_F3_AUTO_INTEGRATION | production / 生产 | - | - | - | MOD-GOV_F3_AUTO_INTEGRATION | production / 生产 | generated / 已生成 | - |
| JOB-718938 | MOD-GOV_F3_EXTREME | production / 生产 | - | - | - | MOD-GOV_F3_EXTREME | production / 生产 | generated / 已生成 | - |
| JOB-718939 | MOD-GOV_FILE_COPY_GATE | production / 生产 | - | - | - | MOD-GOV_FILE_COPY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718940 | MOD-GOV_FUNCTION_DUP_GATE | production / 生产 | - | - | - | MOD-GOV_FUNCTION_DUP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718941 | MOD-GOV_GATE_CACHE | production / 生产 | - | - | - | MOD-GOV_GATE_CACHE | production / 生产 | generated / 已生成 | - |
| JOB-718942 | MOD-GOV_GENERATE_ASSET_CATALOG | production / 生产 | - | - | - | MOD-GOV_GENERATE_ASSET_CATALOG | production / 生产 | generated / 已生成 | - |
| JOB-718943 | MOD-GOV_GENERATE_CAPABILITY_HEATMAP | production / 生产 | - | - | - | MOD-GOV_GENERATE_CAPABILITY_HEATMAP | production / 生产 | generated / 已生成 | - |
| JOB-718944 | MOD-GOV_GENERATE_CAPACITY_REPORT | production / 生产 | - | - | - | MOD-GOV_GENERATE_CAPACITY_REPORT | production / 生产 | generated / 已生成 | - |
| JOB-718945 | MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS | production / 生产 | - | - | - | MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS | production / 生产 | generated / 已生成 | - |
| JOB-718946 | MOD-GOV_GENERATE_CONTRACT_CATALOG | production / 生产 | - | - | - | MOD-GOV_GENERATE_CONTRACT_CATALOG | production / 生产 | generated / 已生成 | - |
| JOB-718947 | MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX | production / 生产 | - | - | - | MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX | production / 生产 | generated / 已生成 | - |
| JOB-718948 | MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | production / 生产 | - | - | - | MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | production / 生产 | generated / 已生成 | - |
| JOB-718949 | MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION | production / 生产 | - | - | - | MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION | production / 生产 | generated / 已生成 | - |
| JOB-718950 | MOD-GOV_GENERATE_DOMAIN_DOC | production / 生产 | - | - | - | MOD-GOV_GENERATE_DOMAIN_DOC | production / 生产 | generated / 已生成 | - |
| JOB-718951 | MOD-GOV_GENERATE_DOMAIN_INDEX | production / 生产 | - | - | - | MOD-GOV_GENERATE_DOMAIN_INDEX | production / 生产 | generated / 已生成 | - |
| JOB-718952 | MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY | production / 生产 | - | - | - | MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY | production / 生产 | generated / 已生成 | - |
| JOB-718953 | MOD-GOV_GENERATE_NAVIGATION_INDEX | production / 生产 | - | - | - | MOD-GOV_GENERATE_NAVIGATION_INDEX | production / 生产 | generated / 已生成 | - |
| JOB-718954 | MOD-GOV_GENERATE_PATH_TREE | production / 生产 | - | - | - | MOD-GOV_GENERATE_PATH_TREE | production / 生产 | generated / 已生成 | - |
| JOB-718955 | MOD-GOV_GIT_HELPERS | production / 生产 | - | - | - | MOD-GOV_GIT_HELPERS | production / 生产 | generated / 已生成 | - |
| JOB-718956 | MOD-GOV_GIT_PERFORMANCE_MONITOR | production / 生产 | - | - | - | MOD-GOV_GIT_PERFORMANCE_MONITOR | production / 生产 | stable | - |
| JOB-718957 | MOD-GOV_GOD_CLASS_GATE | production / 生产 | - | - | - | MOD-GOV_GOD_CLASS_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718958 | MOD-GOV_GROUP_ORPHAN_MODULES | production / 生产 | - | - | - | MOD-GOV_GROUP_ORPHAN_MODULES | production / 生产 | generated / 已生成 | - |
| JOB-718959 | MOD-GOV_GUC_TRIGGER_FIX | production / 生产 | - | - | - | MOD-GOV_GUC_TRIGGER_FIX | production / 生产 | generated / 已生成 | - |
| JOB-718960 | MOD-GOV_HARDCODED_URL_GATE | production / 生产 | - | - | - | MOD-GOV_HARDCODED_URL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718961 | MOD-GOV_HEALTH_SCORE_CALCULATOR | production / 生产 | - | - | - | MOD-GOV_HEALTH_SCORE_CALCULATOR | production / 生产 | stable | - |
| JOB-718962 | MOD-GOV_HEALTH_SMOKE | production / 生产 | - | - | - | MOD-GOV_HEALTH_SMOKE | production / 生产 | generated / 已生成 | - |
| JOB-718963 | MOD-GOV_HEARTBEAT_DAEMON | production / 生产 | - | - | - | MOD-GOV_HEARTBEAT_DAEMON | production / 生产 | stable | - |
| JOB-718964 | MOD-GOV_HEARTBEAT_DAEMON_TEST | production / 生产 | - | - | - | MOD-GOV_HEARTBEAT_DAEMON_TEST | production / 生产 | generated / 已生成 | - |
| JOB-718965 | MOD-GOV_HELD_OVERLAP_GATE | production / 生产 | - | - | - | MOD-GOV_HELD_OVERLAP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718966 | MOD-GOV_HIGH_COMPLEXITY_GATE | production / 生产 | - | - | - | MOD-GOV_HIGH_COMPLEXITY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718967 | MOD-GOV_ID_UNIQUENESS_GATE | production / 生产 | - | - | - | MOD-GOV_ID_UNIQUENESS_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718968 | MOD-GOV_IMPORT_DIRECTION_GATE | production / 生产 | - | - | - | MOD-GOV_IMPORT_DIRECTION_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718969 | MOD-GOV_LONG_PARAM_LIST_GATE | production / 生产 | - | - | - | MOD-GOV_LONG_PARAM_LIST_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718970 | MOD-GOV_MIGRATE_METADATA | production / 生产 | - | - | - | MOD-GOV_MIGRATE_METADATA | production / 生产 | generated / 已生成 | - |
| JOB-718971 | MOD-GOV_MODULE_ID_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_MODULE_ID_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718972 | MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | production / 生产 | - | - | - | MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718973 | MOD-GOV_ORPHAN_MODULE_GATE | production / 生产 | - | - | - | MOD-GOV_ORPHAN_MODULE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718974 | MOD-GOV_PANORAMA_ALIGNMENT_GATE | production / 生产 | - | - | - | MOD-GOV_PANORAMA_ALIGNMENT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718975 | MOD-GOV_PERF_DEPGRAPH_BASELINE | production / 生产 | - | - | - | MOD-GOV_PERF_DEPGRAPH_BASELINE | production / 生产 | generated / 已生成 | - |
| JOB-718976 | MOD-GOV_PERM_TRIGGER_GATE | production / 生产 | - | - | - | MOD-GOV_PERM_TRIGGER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718977 | MOD-GOV_PRE_WRITE_GATE | production / 生产 | - | - | - | MOD-GOV_PRE_WRITE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718978 | MOD-GOV_R5_DIGIT_SUFFIX_GATE | production / 生产 | - | - | - | MOD-GOV_R5_DIGIT_SUFFIX_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718979 | MOD-GOV_RECONCILE_RUNNER | production / 生产 | - | - | - | MOD-GOV_RECONCILE_RUNNER | production / 生产 | stable | - |
| JOB-718980 | MOD-GOV_RECONCILE_WORKER | production / 生产 | - | - | - | MOD-GOV_RECONCILE_WORKER | production / 生产 | stable | - |
| JOB-718981 | MOD-GOV_RECONCILIATION_REGISTRY | production / 生产 | - | - | - | MOD-GOV_RECONCILIATION_REGISTRY | production / 生产 | stable | - |
| JOB-718982 | MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | production / 生产 | - | - | - | MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718983 | MOD-GOV_REPAIR | production / 生产 | - | - | - | MOD-GOV_REPAIR | production / 生产 | generated / 已生成 | - |
| JOB-718984 | MOD-GOV_RESILIENCE_GOVERNANCE | production / 生产 | - | - | - | MOD-GOV_RESILIENCE_GOVERNANCE | production / 生产 | generated / 已生成 | - |
| JOB-718985 | MOD-GOV_ROLLBACK | production / 生产 | - | - | - | MOD-GOV_ROLLBACK | production / 生产 | generated / 已生成 | - |
| JOB-718986 | MOD-GOV_RULE_DOMAIN | production / 生产 | - | - | - | MOD-GOV_RULE_DOMAIN | production / 生产 | generated / 已生成 | - |
| JOB-718987 | MOD-GOV_RULE_EXECUTION_PAIRING_GATE | production / 生产 | - | - | - | MOD-GOV_RULE_EXECUTION_PAIRING_GATE | production / 生产 | stable | - |
| JOB-718988 | MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE | production / 生产 | - | - | - | MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718989 | MOD-GOV_RULE_PATTERNS | production / 生产 | - | - | - | MOD-GOV_RULE_PATTERNS | production / 生产 | stable | - |
| JOB-718990 | MOD-GOV_RULING_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_RULING_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-718991 | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | production / 生产 | - | - | - | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | production / 生产 | stable | - |
| JOB-718992 | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | production / 生产 | - | - | - | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | production / 生产 | stable | - |
| JOB-718993 | MOD-GOV_SCAN_CONSUMERS_ACCURACY | production / 生产 | - | - | - | MOD-GOV_SCAN_CONSUMERS_ACCURACY | production / 生产 | generated / 已生成 | - |
| JOB-718994 | MOD-GOV_SCAN_DEBT | production / 生产 | - | - | - | MOD-GOV_SCAN_DEBT | production / 生产 | generated / 已生成 | - |
| JOB-718995 | MOD-GOV_SCRIPTS | production / 生产 | - | - | - | MOD-GOV_SCRIPTS | production / 生产 | generated / 已生成 | - |
| JOB-718996 | MOD-GOV_SCRIPTS_ARCH | production / 生产 | - | - | - | MOD-GOV_SCRIPTS_ARCH | production / 生产 | stable | - |
| JOB-718997 | MOD-GOV_SECURITY_GOVERNANCE | production / 生产 | - | - | - | MOD-GOV_SECURITY_GOVERNANCE | production / 生产 | generated / 已生成 | - |
| JOB-718998 | MOD-GOV_SESSION_CLAIM | production / 生产 | - | - | - | MOD-GOV_SESSION_CLAIM | production / 生产 | generated / 已生成 | - |
| JOB-718999 | MOD-GOV_SESSION_REQUIRED_GATE | production / 生产 | - | - | - | MOD-GOV_SESSION_REQUIRED_GATE | production / 生产 | generated / 已生成 | - |
| JOB-719000 | MOD-GOV_SESSION_WORKTREE | production / 生产 | - | - | - | MOD-GOV_SESSION_WORKTREE | production / 生产 | stable | - |
| JOB-719001 | MOD-GOV_SILENT_FAILURE_REGRESSION | production / 生产 | - | - | - | MOD-GOV_SILENT_FAILURE_REGRESSION | production / 生产 | generated / 已生成 | - |
| JOB-719002 | MOD-GOV_SSOT_REDEFINITION_GATE | production / 生产 | - | - | - | MOD-GOV_SSOT_REDEFINITION_GATE | production / 生产 | generated / 已生成 | - |
| JOB-719003 | MOD-GOV_SYNC_PANORAMA | production / 生产 | - | - | - | MOD-GOV_SYNC_PANORAMA | production / 生产 | generated / 已生成 | - |
| JOB-719004 | MOD-GOV_SYNC_SAVEPOINT_TEST | production / 生产 | - | - | - | MOD-GOV_SYNC_SAVEPOINT_TEST | production / 生产 | generated / 已生成 | - |
| JOB-719005 | MOD-GOV_TASK_SYSTEM_RED_TEAM | production / 生产 | - | - | - | MOD-GOV_TASK_SYSTEM_RED_TEAM | production / 生产 | generated / 已生成 | - |
| JOB-719006 | MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | production / 生产 | - | - | - | MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | production / 生产 | generated / 已生成 | - |
| JOB-719007 | MOD-GOV_TEST_EMERGENCY_COMMIT | production / 生产 | - | - | - | MOD-GOV_TEST_EMERGENCY_COMMIT | production / 生产 | generated / 已生成 | - |
| JOB-719008 | MOD-GOV_TEST_RECONCILE_ASYNC | production / 生产 | - | - | - | MOD-GOV_TEST_RECONCILE_ASYNC | production / 生产 | generated / 已生成 | - |
| JOB-719009 | MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | production / 生产 | - | - | - | MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | production / 生产 | generated / 已生成 | - |
| JOB-719010 | MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-719011 | MOD-GOV_VERIFY_KEY_IMPORTS | production / 生产 | - | - | - | MOD-GOV_VERIFY_KEY_IMPORTS | production / 生产 | generated / 已生成 | - |
| JOB-719012 | MOD-GOV_VOCAB_HARDCODE_GATE | production / 生产 | - | - | - | MOD-GOV_VOCAB_HARDCODE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-719013 | MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | production / 生产 | - | - | - | MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | production / 生产 | stable | - |
| JOB-719014 | MOD-GOV_WORKTREE_MANAGER | production / 生产 | - | - | - | MOD-GOV_WORKTREE_MANAGER | production / 生产 | stable | - |
| JOB-719015 | MOD-GOV_YAML_SYNC_ERROR_CLASS | production / 生产 | - | - | - | MOD-GOV_YAML_SYNC_ERROR_CLASS | production / 生产 | generated / 已生成 | - |
| JOB-321362 | MOD-GOV_blueprint_status_transition_reconciler | production / 生产 | - | - | - | MOD-GOV_blueprint_status_transition_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-321311 | MOD-GOV_cross_layer_contract_signature_reconciler | production / 生产 | - | - | - | MOD-GOV_cross_layer_contract_signature_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-719016 | MOD-INF-001 | production / 生产 | - | - | - | MOD-INF-001 | production / 生产 | generated / 已生成 | - |
| JOB-719017 | MOD-INF-002 | production / 生产 | - | - | - | MOD-INF-002 | production / 生产 | generated / 已生成 | - |
| JOB-719018 | MOD-INF-003 | production / 生产 | - | - | - | MOD-INF-003 | production / 生产 | stable | - |
| JOB-36357 | MOD-INF-005 | production / 生产 | - | - | - | MOD-INF-005 | design / 设计 | planned | - |
| JOB-37139 | MOD-INF-009 | production / 生产 | - | - | - | MOD-INF-009 | design / 设计 | planned | - |
| JOB-35565 | MOD-INF-011 | production / 生产 | - | - | - | MOD-INF-011 | design / 设计 | planned | - |
| JOB-719022 | MOD-INF-013 | production / 生产 | - | - | - | MOD-INF-013 | production / 生产 | generated / 已生成 | - |
| JOB-719023 | MOD-INF-014 | production / 生产 | - | - | - | MOD-INF-014 | production / 生产 | stable | - |
| JOB-719024 | MOD-INF-015 | production / 生产 | - | - | - | MOD-INF-015 | production / 生产 | stable | - |
| JOB-35954 | MOD-INF-016 | production / 生产 | - | - | - | MOD-INF-016 | design / 设计 | planned | - |
| JOB-36274 | MOD-INF-017 | production / 生产 | - | - | - | MOD-INF-017 | design / 设计 | planned | - |
| JOB-719027 | MOD-INF-018 | production / 生产 | - | - | - | MOD-INF-018 | production / 生产 | generated / 已生成 | - |
| JOB-37172 | MOD-INF-019 | production / 生产 | - | - | - | MOD-INF-019 | design / 设计 | planned | - |
| JOB-36050 | MOD-INF-020 | production / 生产 | - | - | - | MOD-INF-020 | design / 设计 | planned | - |
| JOB-35903 | MOD-INF-021 | production / 生产 | - | - | - | MOD-INF-021 | design / 设计 | planned | - |
| JOB-36400 | MOD-INF-022 | production / 生产 | - | - | - | MOD-INF-022 | design / 设计 | planned | - |
| JOB-35522 | MOD-INF-023 | production / 生产 | - | - | - | MOD-INF-023 | design / 设计 | planned | - |
| JOB-37193 | MOD-INF-024 | production / 生产 | - | - | - | MOD-INF-024 | design / 设计 | generated / 已生成 | - |
| JOB-719034 | MOD-INF-025 | production / 生产 | - | - | - | MOD-INF-025 | production / 生产 | generated / 已生成 | - |
| JOB-719035 | MOD-INF-026 | production / 生产 | - | - | - | MOD-INF-026 | production / 生产 | stable | - |
| JOB-35574 | MOD-INF-027 | production / 生产 | - | - | - | MOD-INF-027 | design / 设计 | planned | - |
| JOB-36222 | MOD-INF-028 | production / 生产 | - | - | - | MOD-INF-028 | design / 设计 | planned | - |
| JOB-35930 | MOD-INF-029 | production / 生产 | - | - | - | MOD-INF-029 | design / 设计 | planned | - |
| JOB-37217 | MOD-INF-030 | production / 生产 | - | - | - | MOD-INF-030 | design / 设计 | planned | - |
| JOB-37220 | MOD-INF-031 | production / 生产 | - | - | - | MOD-INF-031 | design / 设计 | planned | - |
| JOB-36336 | MOD-INF-033 | production / 生产 | - | - | - | MOD-INF-033 | design / 设计 | planned | - |
| JOB-35554 | MOD-INF-034 | production / 生产 | - | - | - | MOD-INF-034 | design / 设计 | planned | - |
| JOB-719043 | MOD-INF-035 | production / 生产 | - | - | - | MOD-INF-035 | production / 生产 | generated / 已生成 | - |
| JOB-37237 | MOD-INF-036 | production / 生产 | - | - | - | MOD-INF-036 | design / 设计 | planned | - |
| JOB-35538 | MOD-INF-037 | production / 生产 | - | - | - | MOD-INF-037 | design / 设计 | planned | - |
| JOB-719046 | MOD-INF-038 | production / 生产 | - | - | - | MOD-INF-038 | production / 生产 | stable | - |
| JOB-36080 | MOD-INF-039 | production / 生产 | - | - | - | MOD-INF-039 | design / 设计 | planned | - |
| JOB-719048 | MOD-INF-040 | production / 生产 | - | - | - | MOD-INF-040 | production / 生产 | generated / 已生成 | - |
| JOB-719049 | MOD-INF-042 | production / 生产 | - | - | - | MOD-INF-042 | production / 生产 | generated / 已生成 | - |
| JOB-719050 | MOD-INF-043 | production / 生产 | - | - | - | MOD-INF-043 | production / 生产 | generated / 已生成 | - |
| JOB-719051 | MOD-INF-044 | production / 生产 | - | - | - | MOD-INF-044 | production / 生产 | stable | - |
| JOB-35939 | MOD-INFRA_OPS | production / 生产 | - | - | - | MOD-INFRA_OPS | design / 设计 | planned | - |
| JOB-719052 | MOD-INFRA_RUNTIME | production / 生产 | - | - | - | MOD-INFRA_RUNTIME | production / 生产 | generated / 已生成 | - |
| JOB-719053 | MOD-INF_GOV | production / 生产 | - | - | - | MOD-INF_GOV | production / 生产 | generated / 已生成 | - |
| JOB-719054 | MOD-INTEGRATION | production / 生产 | - | - | - | MOD-INTEGRATION | production / 生产 | generated / 已生成 | - |
| JOB-719055 | MOD-L00-001 | production / 生产 | - | - | - | MOD-L00-001 | production / 生产 | generated / 已生成 | - |
| JOB-36157 | MOD-L00-002 | production / 生产 | - | - | - | MOD-L00-002 | design / 设计 | stable | - |
| JOB-35520 | MOD-L00-003 | production / 生产 | - | - | - | MOD-L00-003 | design / 设计 | stable | - |
| JOB-61876 | MOD-L00-004 | production / 生产 | - | - | - | MOD-L00-004 | design / 设计 | generated / 已生成 | - |
| JOB-719057 | MOD-L00-005 | production / 生产 | - | - | - | MOD-L00-005 | production / 生产 | generated / 已生成 | - |
| JOB-719058 | MOD-L00-006 | production / 生产 | - | - | - | MOD-L00-006 | production / 生产 | stable | - |
| JOB-719059 | MOD-L00-007 | production / 生产 | - | - | - | MOD-L00-007 | production / 生产 | generated / 已生成 | - |
| JOB-551909 | MOD-L02-001 | production / 生产 | - | - | - | MOD-L02-001 | design / 设计 | stable | - |
| JOB-719061 | MOD-L02-002 | production / 生产 | - | - | - | MOD-L02-002 | production / 生产 | stable | - |
| JOB-719062 | MOD-L02-003 | production / 生产 | - | - | - | MOD-L02-003 | production / 生产 | stable | - |
| JOB-719063 | MOD-L02-004 | production / 生产 | - | - | - | MOD-L02-004 | production / 生产 | stable | - |
| JOB-719064 | MOD-L02-005 | production / 生产 | - | - | - | MOD-L02-005 | production / 生产 | stable | - |
| JOB-719065 | MOD-L02-006 | production / 生产 | - | - | - | MOD-L02-006 | production / 生产 | stable | - |
| JOB-719066 | MOD-L02-007 | production / 生产 | - | - | - | MOD-L02-007 | production / 生产 | generated / 已生成 | - |
| JOB-719067 | MOD-L02-008 | production / 生产 | - | - | - | MOD-L02-008 | production / 生产 | generated / 已生成 | - |
| JOB-719068 | MOD-L02-009 | production / 生产 | - | - | - | MOD-L02-009 | production / 生产 | generated / 已生成 | - |
| JOB-719069 | MOD-L02-010 | production / 生产 | - | - | - | MOD-L02-010 | production / 生产 | generated / 已生成 | - |
| JOB-719070 | MOD-L02-011 | production / 生产 | - | - | - | MOD-L02-011 | production / 生产 | generated / 已生成 | - |
| JOB-719071 | MOD-L02-012 | production / 生产 | - | - | - | MOD-L02-012 | production / 生产 | generated / 已生成 | - |
| JOB-719072 | MOD-L02-013 | production / 生产 | - | - | - | MOD-L02-013 | production / 生产 | stable | - |
| JOB-719073 | MOD-L02-014 | production / 生产 | - | - | - | MOD-L02-014 | production / 生产 | stable | - |
| JOB-719074 | MOD-L02-015 | production / 生产 | - | - | - | MOD-L02-015 | production / 生产 | stable | - |
| JOB-719075 | MOD-L02-016 | production / 生产 | - | - | - | MOD-L02-016 | production / 生产 | stable | - |
| JOB-719076 | MOD-L02-017 | production / 生产 | - | - | - | MOD-L02-017 | production / 生产 | stable | - |
| JOB-719077 | MOD-L02-018 | production / 生产 | - | - | - | MOD-L02-018 | production / 生产 | stable | - |
| JOB-719078 | MOD-L02-024 | production / 生产 | - | - | - | MOD-L02-024 | production / 生产 | generated / 已生成 | - |
| JOB-719079 | MOD-L02-025 | production / 生产 | - | - | - | MOD-L02-025 | production / 生产 | generated / 已生成 | - |
| JOB-719080 | MOD-L02-ANA | production / 生产 | - | - | - | MOD-L02-ANA | production / 生产 | stable | - |
| JOB-719081 | MOD-L02-GOV | production / 生产 | - | - | - | MOD-L02-GOV | production / 生产 | generated / 已生成 | - |
| JOB-719082 | MOD-L03-001 | production / 生产 | - | - | - | MOD-L03-001 | production / 生产 | generated / 已生成 | - |
| JOB-688297 | MOD-L04-001 | production / 生产 | - | - | - | MOD-L04-001 | design / 设计 | generated / 已生成 | - |
| JOB-719084 | MOD-L04-002 | production / 生产 | - | - | - | MOD-L04-002 | production / 生产 | generated / 已生成 | - |
| JOB-719085 | MOD-L05-001 | production / 生产 | - | - | - | MOD-L05-001 | production / 生产 | generated / 已生成 | - |
| JOB-719086 | MOD-L06-001 | production / 生产 | - | - | - | MOD-L06-001 | production / 生产 | stable | - |
| JOB-719087 | MOD-L07-001 | production / 生产 | - | - | - | MOD-L07-001 | production / 生产 | generated / 已生成 | - |
| JOB-719088 | MOD-L08-001 | production / 生产 | - | - | - | MOD-L08-001 | production / 生产 | generated / 已生成 | - |
| JOB-719089 | MOD-L09-001 | production / 生产 | - | - | - | MOD-L09-001 | production / 生产 | generated / 已生成 | - |
| JOB-719090 | MOD-L10-001 | production / 生产 | - | - | - | MOD-L10-001 | production / 生产 | generated / 已生成 | - |
| JOB-719091 | MOD-L11-001 | production / 生产 | - | - | - | MOD-L11-001 | production / 生产 | generated / 已生成 | - |
| JOB-719092 | MOD-L13-001 | production / 生产 | - | - | - | MOD-L13-001 | production / 生产 | generated / 已生成 | - |
| JOB-719093 | MOD-LLM_SECURITY | production / 生产 | - | - | - | MOD-LLM_SECURITY | production / 生产 | generated / 已生成 | - |
| JOB-36390 | MOD-MASTER-001 | production / 生产 | - | - | - | MOD-MASTER-001 | design / 设计 | stable | - |
| JOB-35517 | MOD-MASTER-002 | production / 生产 | - | - | - | MOD-MASTER-002 | design / 设计 | stable | - |
| JOB-36344 | MOD-MASTER-003 | production / 生产 | - | - | - | MOD-MASTER-003 | design / 设计 | planned | - |
| JOB-35528 | MOD-MASTER_BLUEPRINT | production / 生产 | - | - | - | MOD-MASTER_BLUEPRINT | design / 设计 | deprecated | - |
| JOB-711884 | MOD-MKT-001 | production / 生产 | - | - | - | MOD-MKT-001 | design / 设计 | planned | - |
| JOB-711954 | MOD-MKT-002 | production / 生产 | - | - | - | MOD-MKT-002 | design / 设计 | planned | - |
| JOB-712012 | MOD-MKT-003 | production / 生产 | - | - | - | MOD-MKT-003 | design / 设计 | planned | - |
| JOB-719098 | MOD-MKT_DATA | production / 生产 | - | - | - | MOD-MKT_DATA | production / 生产 | generated / 已生成 | - |
| JOB-719099 | MOD-ML_SERVE | production / 生产 | - | - | - | MOD-ML_SERVE | production / 生产 | generated / 已生成 | - |
| JOB-719100 | MOD-OPS-018 | production / 生产 | - | - | - | MOD-OPS-018 | production / 生产 | generated / 已生成 | - |
| JOB-36113 | MOD-PF_ALLOC | production / 生产 | - | - | - | MOD-PF_ALLOC | design / 设计 | planned | - |
| JOB-719101 | MOD-REMEDIATION_PROGRESS | production / 生产 | - | - | - | MOD-REMEDIATION_PROGRESS | production / 生产 | generated / 已生成 | - |
| JOB-719102 | MOD-REMEDIATION_PROGRESS_SMOKE | production / 生产 | - | - | - | MOD-REMEDIATION_PROGRESS_SMOKE | production / 生产 | generated / 已生成 | - |
| JOB-35898 | MOD-RESOURCE_OPTIMIZATION_ENGINE | production / 生产 | - | - | - | MOD-RESOURCE_OPTIMIZATION_ENGINE | design / 设计 | planned | - |
| JOB-719104 | MOD-RULE_ENGINE | production / 生产 | - | - | - | MOD-RULE_ENGINE | production / 生产 | generated / 已生成 | - |
| JOB-719105 | MOD-SCRIPTS-006 | production / 生产 | - | - | - | MOD-SCRIPTS-006 | production / 生产 | generated / 已生成 | - |
| JOB-719106 | MOD-SEC-030 | production / 生产 | - | - | - | MOD-SEC-030 | production / 生产 | generated / 已生成 | - |
| JOB-719107 | MOD-SEC_IMMUTABLE_CORE | production / 生产 | - | - | - | MOD-SEC_IMMUTABLE_CORE | production / 生产 | generated / 已生成 | - |
| JOB-719108 | MOD-SELL_DECISION | production / 生产 | - | - | - | MOD-SELL_DECISION | production / 生产 | generated / 已生成 | - |
| JOB-719109 | MOD-SHARED-001 | production / 生产 | - | - | - | MOD-SHARED-001 | production / 生产 | generated / 已生成 | - |
| JOB-719110 | MOD-SHARED-002 | production / 生产 | - | - | - | MOD-SHARED-002 | production / 生产 | generated / 已生成 | - |
| JOB-719111 | MOD-SHR_CONVERTERS | production / 生产 | - | - | - | MOD-SHR_CONVERTERS | production / 生产 | stable | - |
| JOB-719112 | MOD-SHR_IO_YAML | production / 生产 | - | - | - | MOD-SHR_IO_YAML | production / 生产 | generated / 已生成 | - |
| JOB-719113 | MOD-SIGNAL_ASHARE | production / 生产 | - | - | - | MOD-SIGNAL_ASHARE | production / 生产 | generated / 已生成 | - |
| JOB-719114 | MOD-SIGQC-001 | production / 生产 | - | - | - | MOD-SIGQC-001 | production / 生产 | generated / 已生成 | - |
| JOB-35600 | MOD-SIMULATION | production / 生产 | - | - | - | MOD-SIMULATION | design / 设计 | planned | - |
| JOB-119053 | MOD-SMOKE-TEST | production / 生产 | - | - | - | MOD-SMOKE-TEST | design / 设计 | planned | - |
| JOB-719115 | MOD-TASK_SYSTEM | production / 生产 | - | - | - | MOD-TASK_SYSTEM | production / 生产 | generated / 已生成 | - |
| JOB-118981 | MOD-TEST | production / 生产 | - | - | - | MOD-TEST | design / 设计 | planned | - |
| JOB-719117 | MOD-TEST-202 | production / 生产 | - | - | - | MOD-TEST-202 | production / 生产 | generated / 已生成 | - |
| JOB-719118 | MOD-TEST-203 | production / 生产 | - | - | - | MOD-TEST-203 | production / 生产 | generated / 已生成 | - |
| JOB-719119 | MOD-TEST-204 | production / 生产 | - | - | - | MOD-TEST-204 | production / 生产 | generated / 已生成 | - |
| JOB-719120 | MOD-TEST-205 | production / 生产 | - | - | - | MOD-TEST-205 | production / 生产 | generated / 已生成 | - |
| JOB-719121 | MOD-TEST-206 | production / 生产 | - | - | - | MOD-TEST-206 | production / 生产 | generated / 已生成 | - |
| JOB-719122 | MOD-TEST-210 | production / 生产 | - | - | - | MOD-TEST-210 | production / 生产 | generated / 已生成 | - |
| JOB-719123 | MOD-TEST-211 | production / 生产 | - | - | - | MOD-TEST-211 | production / 生产 | generated / 已生成 | - |
| JOB-719124 | MOD-TEST-212 | production / 生产 | - | - | - | MOD-TEST-212 | production / 生产 | generated / 已生成 | - |
| JOB-719125 | MOD-TEST-213 | production / 生产 | - | - | - | MOD-TEST-213 | production / 生产 | generated / 已生成 | - |
| JOB-719126 | MOD-TEST-215 | production / 生产 | - | - | - | MOD-TEST-215 | production / 生产 | generated / 已生成 | - |
| JOB-719127 | MOD-TEST-216 | production / 生产 | - | - | - | MOD-TEST-216 | production / 生产 | generated / 已生成 | - |
| JOB-719128 | MOD-TEST-217 | production / 生产 | - | - | - | MOD-TEST-217 | production / 生产 | generated / 已生成 | - |
| JOB-719129 | MOD-TEST-218 | production / 生产 | - | - | - | MOD-TEST-218 | production / 生产 | generated / 已生成 | - |
| JOB-719130 | MOD-TEST-219 | production / 生产 | - | - | - | MOD-TEST-219 | production / 生产 | generated / 已生成 | - |
| JOB-719131 | MOD-TEST-220 | production / 生产 | - | - | - | MOD-TEST-220 | production / 生产 | generated / 已生成 | - |
| JOB-719132 | MOD-TEST-221 | production / 生产 | - | - | - | MOD-TEST-221 | production / 生产 | generated / 已生成 | - |
| JOB-719133 | MOD-TEST-222 | production / 生产 | - | - | - | MOD-TEST-222 | production / 生产 | generated / 已生成 | - |
| JOB-719134 | MOD-TEST-223 | production / 生产 | - | - | - | MOD-TEST-223 | production / 生产 | generated / 已生成 | - |
| JOB-719135 | MOD-TEST-224 | production / 生产 | - | - | - | MOD-TEST-224 | production / 生产 | generated / 已生成 | - |
| JOB-719136 | MOD-TEST-225 | production / 生产 | - | - | - | MOD-TEST-225 | production / 生产 | generated / 已生成 | - |
| JOB-719137 | MOD-TEST-226 | production / 生产 | - | - | - | MOD-TEST-226 | production / 生产 | generated / 已生成 | - |
| JOB-719138 | MOD-TEST-227 | production / 生产 | - | - | - | MOD-TEST-227 | production / 生产 | generated / 已生成 | - |
| JOB-719139 | MOD-TEST-228 | production / 生产 | - | - | - | MOD-TEST-228 | production / 生产 | generated / 已生成 | - |
| JOB-719140 | MOD-TEST-229 | production / 生产 | - | - | - | MOD-TEST-229 | production / 生产 | generated / 已生成 | - |
| JOB-719141 | MOD-TEST-230 | production / 生产 | - | - | - | MOD-TEST-230 | production / 生产 | generated / 已生成 | - |
| JOB-719142 | MOD-TEST-231 | production / 生产 | - | - | - | MOD-TEST-231 | production / 生产 | generated / 已生成 | - |
| JOB-719143 | MOD-TEST-232 | production / 生产 | - | - | - | MOD-TEST-232 | production / 生产 | generated / 已生成 | - |
| JOB-719144 | MOD-TEST-233 | production / 生产 | - | - | - | MOD-TEST-233 | production / 生产 | generated / 已生成 | - |
| JOB-719145 | MOD-TEST-234 | production / 生产 | - | - | - | MOD-TEST-234 | production / 生产 | generated / 已生成 | - |
| JOB-719146 | MOD-TEST-235 | production / 生产 | - | - | - | MOD-TEST-235 | production / 生产 | generated / 已生成 | - |
| JOB-719147 | MOD-TEST-236 | production / 生产 | - | - | - | MOD-TEST-236 | production / 生产 | generated / 已生成 | - |
| JOB-719148 | MOD-TEST-237 | production / 生产 | - | - | - | MOD-TEST-237 | production / 生产 | generated / 已生成 | - |
| JOB-719149 | MOD-TEST-238 | production / 生产 | - | - | - | MOD-TEST-238 | production / 生产 | generated / 已生成 | - |
| JOB-719150 | MOD-TEST-239 | production / 生产 | - | - | - | MOD-TEST-239 | production / 生产 | generated / 已生成 | - |
| JOB-719151 | MOD-TEST-240 | production / 生产 | - | - | - | MOD-TEST-240 | production / 生产 | generated / 已生成 | - |
| JOB-719152 | MOD-TEST-241 | production / 生产 | - | - | - | MOD-TEST-241 | production / 生产 | generated / 已生成 | - |
| JOB-719153 | MOD-TEST-242 | production / 生产 | - | - | - | MOD-TEST-242 | production / 生产 | generated / 已生成 | - |
| JOB-719154 | MOD-TEST-246 | production / 生产 | - | - | - | MOD-TEST-246 | production / 生产 | generated / 已生成 | - |
| JOB-719155 | MOD-TEST-247 | production / 生产 | - | - | - | MOD-TEST-247 | production / 生产 | generated / 已生成 | - |
| JOB-719156 | MOD-TEST-248 | production / 生产 | - | - | - | MOD-TEST-248 | production / 生产 | generated / 已生成 | - |
| JOB-719157 | MOD-TEST-250 | production / 生产 | - | - | - | MOD-TEST-250 | production / 生产 | generated / 已生成 | - |
| JOB-719158 | MOD-TEST-251 | production / 生产 | - | - | - | MOD-TEST-251 | production / 生产 | generated / 已生成 | - |
| JOB-719159 | MOD-TEST-252 | production / 生产 | - | - | - | MOD-TEST-252 | production / 生产 | generated / 已生成 | - |
| JOB-719160 | MOD-TEST-253 | production / 生产 | - | - | - | MOD-TEST-253 | production / 生产 | generated / 已生成 | - |
| JOB-719161 | MOD-TEST-254 | production / 生产 | - | - | - | MOD-TEST-254 | production / 生产 | generated / 已生成 | - |
| JOB-719162 | MOD-TEST-255 | production / 生产 | - | - | - | MOD-TEST-255 | production / 生产 | generated / 已生成 | - |
| JOB-719163 | MOD-TEST-256 | production / 生产 | - | - | - | MOD-TEST-256 | production / 生产 | generated / 已生成 | - |
| JOB-719164 | MOD-TEST-257 | production / 生产 | - | - | - | MOD-TEST-257 | production / 生产 | generated / 已生成 | - |
| JOB-719165 | MOD-TEST-258 | production / 生产 | - | - | - | MOD-TEST-258 | production / 生产 | generated / 已生成 | - |
| JOB-719166 | MOD-TEST-260 | production / 生产 | - | - | - | MOD-TEST-260 | production / 生产 | generated / 已生成 | - |
| JOB-719167 | MOD-TEST-261 | production / 生产 | - | - | - | MOD-TEST-261 | production / 生产 | generated / 已生成 | - |
| JOB-719168 | MOD-TEST-262 | production / 生产 | - | - | - | MOD-TEST-262 | production / 生产 | generated / 已生成 | - |
| JOB-719169 | MOD-TEST-263 | production / 生产 | - | - | - | MOD-TEST-263 | production / 生产 | generated / 已生成 | - |
| JOB-719170 | MOD-TEST-264 | production / 生产 | - | - | - | MOD-TEST-264 | production / 生产 | generated / 已生成 | - |
| JOB-719171 | MOD-TEST-265 | production / 生产 | - | - | - | MOD-TEST-265 | production / 生产 | generated / 已生成 | - |
| JOB-719172 | MOD-TEST-266 | production / 生产 | - | - | - | MOD-TEST-266 | production / 生产 | generated / 已生成 | - |
| JOB-719173 | MOD-TEST-268 | production / 生产 | - | - | - | MOD-TEST-268 | production / 生产 | generated / 已生成 | - |
| JOB-719174 | MOD-TEST-272 | production / 生产 | - | - | - | MOD-TEST-272 | production / 生产 | generated / 已生成 | - |
| JOB-719175 | MOD-TEST-273 | production / 生产 | - | - | - | MOD-TEST-273 | production / 生产 | generated / 已生成 | - |
| JOB-719176 | MOD-TEST-274 | production / 生产 | - | - | - | MOD-TEST-274 | production / 生产 | generated / 已生成 | - |
| JOB-719177 | MOD-TEST-275 | production / 生产 | - | - | - | MOD-TEST-275 | production / 生产 | generated / 已生成 | - |
| JOB-719178 | MOD-TEST-276 | production / 生产 | - | - | - | MOD-TEST-276 | production / 生产 | generated / 已生成 | - |
| JOB-719179 | MOD-TEST-277 | production / 生产 | - | - | - | MOD-TEST-277 | production / 生产 | generated / 已生成 | - |
| JOB-719180 | MOD-TEST-278 | production / 生产 | - | - | - | MOD-TEST-278 | production / 生产 | generated / 已生成 | - |
| JOB-719181 | MOD-TEST-279 | production / 生产 | - | - | - | MOD-TEST-279 | production / 生产 | generated / 已生成 | - |
| JOB-719182 | MOD-TEST-280 | production / 生产 | - | - | - | MOD-TEST-280 | production / 生产 | generated / 已生成 | - |
| JOB-719183 | MOD-TEST-281 | production / 生产 | - | - | - | MOD-TEST-281 | production / 生产 | generated / 已生成 | - |
| JOB-719184 | MOD-TEST-282 | production / 生产 | - | - | - | MOD-TEST-282 | production / 生产 | generated / 已生成 | - |
| JOB-719185 | MOD-TEST-283 | production / 生产 | - | - | - | MOD-TEST-283 | production / 生产 | generated / 已生成 | - |
| JOB-719186 | MOD-TEST-284 | production / 生产 | - | - | - | MOD-TEST-284 | production / 生产 | generated / 已生成 | - |
| JOB-719187 | MOD-TEST-285 | production / 生产 | - | - | - | MOD-TEST-285 | production / 生产 | generated / 已生成 | - |
| JOB-719188 | MOD-TEST-286 | production / 生产 | - | - | - | MOD-TEST-286 | production / 生产 | generated / 已生成 | - |
| JOB-719189 | MOD-TEST-287 | production / 生产 | - | - | - | MOD-TEST-287 | production / 生产 | generated / 已生成 | - |
| JOB-719190 | MOD-TEST-288 | production / 生产 | - | - | - | MOD-TEST-288 | production / 生产 | generated / 已生成 | - |
| JOB-719191 | MOD-TEST-289 | production / 生产 | - | - | - | MOD-TEST-289 | production / 生产 | generated / 已生成 | - |
| JOB-719192 | MOD-TEST-290 | production / 生产 | - | - | - | MOD-TEST-290 | production / 生产 | generated / 已生成 | - |
| JOB-719193 | MOD-TEST-291 | production / 生产 | - | - | - | MOD-TEST-291 | production / 生产 | generated / 已生成 | - |
| JOB-719194 | MOD-TEST-292 | production / 生产 | - | - | - | MOD-TEST-292 | production / 生产 | generated / 已生成 | - |
| JOB-719195 | MOD-TEST-293 | production / 生产 | - | - | - | MOD-TEST-293 | production / 生产 | generated / 已生成 | - |
| JOB-719196 | MOD-TEST-294 | production / 生产 | - | - | - | MOD-TEST-294 | production / 生产 | generated / 已生成 | - |
| JOB-719197 | MOD-TEST-295 | production / 生产 | - | - | - | MOD-TEST-295 | production / 生产 | generated / 已生成 | - |
| JOB-719198 | MOD-TEST-296 | production / 生产 | - | - | - | MOD-TEST-296 | production / 生产 | generated / 已生成 | - |
| JOB-719199 | MOD-TEST-297 | production / 生产 | - | - | - | MOD-TEST-297 | production / 生产 | generated / 已生成 | - |
| JOB-719200 | MOD-TEST-298 | production / 生产 | - | - | - | MOD-TEST-298 | production / 生产 | generated / 已生成 | - |
| JOB-719201 | MOD-TEST-299 | production / 生产 | - | - | - | MOD-TEST-299 | production / 生产 | generated / 已生成 | - |
| JOB-719202 | MOD-TEST-300 | production / 生产 | - | - | - | MOD-TEST-300 | production / 生产 | generated / 已生成 | - |
| JOB-719203 | MOD-TEST-301 | production / 生产 | - | - | - | MOD-TEST-301 | production / 生产 | generated / 已生成 | - |
| JOB-719204 | MOD-TEST-302 | production / 生产 | - | - | - | MOD-TEST-302 | production / 生产 | generated / 已生成 | - |
| JOB-719205 | MOD-TEST-303 | production / 生产 | - | - | - | MOD-TEST-303 | production / 生产 | generated / 已生成 | - |
| JOB-719206 | MOD-TEST-304 | production / 生产 | - | - | - | MOD-TEST-304 | production / 生产 | generated / 已生成 | - |
| JOB-719207 | MOD-TEST-305 | production / 生产 | - | - | - | MOD-TEST-305 | production / 生产 | generated / 已生成 | - |
| JOB-719208 | MOD-TEST-306 | production / 生产 | - | - | - | MOD-TEST-306 | production / 生产 | generated / 已生成 | - |
| JOB-719209 | MOD-TEST-307 | production / 生产 | - | - | - | MOD-TEST-307 | production / 生产 | generated / 已生成 | - |
| JOB-719210 | MOD-TEST-308 | production / 生产 | - | - | - | MOD-TEST-308 | production / 生产 | generated / 已生成 | - |
| JOB-719211 | MOD-TEST-309 | production / 生产 | - | - | - | MOD-TEST-309 | production / 生产 | generated / 已生成 | - |
| JOB-719212 | MOD-TEST-310 | production / 生产 | - | - | - | MOD-TEST-310 | production / 生产 | generated / 已生成 | - |
| JOB-719213 | MOD-TEST-311 | production / 生产 | - | - | - | MOD-TEST-311 | production / 生产 | generated / 已生成 | - |
| JOB-719214 | MOD-TEST-312 | production / 生产 | - | - | - | MOD-TEST-312 | production / 生产 | generated / 已生成 | - |
| JOB-719215 | MOD-TEST-313 | production / 生产 | - | - | - | MOD-TEST-313 | production / 生产 | generated / 已生成 | - |
| JOB-719216 | MOD-TEST-314 | production / 生产 | - | - | - | MOD-TEST-314 | production / 生产 | generated / 已生成 | - |
| JOB-719217 | MOD-TEST-315 | production / 生产 | - | - | - | MOD-TEST-315 | production / 生产 | generated / 已生成 | - |
| JOB-719218 | MOD-TEST-316 | production / 生产 | - | - | - | MOD-TEST-316 | production / 生产 | generated / 已生成 | - |
| JOB-719219 | MOD-TEST-319 | production / 生产 | - | - | - | MOD-TEST-319 | production / 生产 | generated / 已生成 | - |
| JOB-719220 | MOD-TEST-320 | production / 生产 | - | - | - | MOD-TEST-320 | production / 生产 | generated / 已生成 | - |
| JOB-719221 | MOD-TEST-322 | production / 生产 | - | - | - | MOD-TEST-322 | production / 生产 | generated / 已生成 | - |
| JOB-719222 | MOD-TEST-323 | production / 生产 | - | - | - | MOD-TEST-323 | production / 生产 | generated / 已生成 | - |
| JOB-719223 | MOD-TEST-324 | production / 生产 | - | - | - | MOD-TEST-324 | production / 生产 | generated / 已生成 | - |
| JOB-719224 | MOD-TEST-325 | production / 生产 | - | - | - | MOD-TEST-325 | production / 生产 | generated / 已生成 | - |
| JOB-719225 | MOD-TEST-326 | production / 生产 | - | - | - | MOD-TEST-326 | production / 生产 | generated / 已生成 | - |
| JOB-719226 | MOD-TEST-328 | production / 生产 | - | - | - | MOD-TEST-328 | production / 生产 | generated / 已生成 | - |
| JOB-719227 | MOD-TEST-329 | production / 生产 | - | - | - | MOD-TEST-329 | production / 生产 | generated / 已生成 | - |
| JOB-719228 | MOD-TEST-330 | production / 生产 | - | - | - | MOD-TEST-330 | production / 生产 | generated / 已生成 | - |
| JOB-719229 | MOD-TEST-331 | production / 生产 | - | - | - | MOD-TEST-331 | production / 生产 | generated / 已生成 | - |
| JOB-719230 | MOD-TEST-332 | production / 生产 | - | - | - | MOD-TEST-332 | production / 生产 | generated / 已生成 | - |
| JOB-719231 | MOD-TEST-333 | production / 生产 | - | - | - | MOD-TEST-333 | production / 生产 | generated / 已生成 | - |
| JOB-719232 | MOD-TEST-334 | production / 生产 | - | - | - | MOD-TEST-334 | production / 生产 | generated / 已生成 | - |
| JOB-719233 | MOD-TEST-335 | production / 生产 | - | - | - | MOD-TEST-335 | production / 生产 | generated / 已生成 | - |
| JOB-719234 | MOD-TEST-336 | production / 生产 | - | - | - | MOD-TEST-336 | production / 生产 | generated / 已生成 | - |
| JOB-719235 | MOD-TEST-337 | production / 生产 | - | - | - | MOD-TEST-337 | production / 生产 | generated / 已生成 | - |
| JOB-719236 | MOD-TEST-338 | production / 生产 | - | - | - | MOD-TEST-338 | production / 生产 | generated / 已生成 | - |
| JOB-719237 | MOD-TEST-339 | production / 生产 | - | - | - | MOD-TEST-339 | production / 生产 | generated / 已生成 | - |
| JOB-719238 | MOD-TEST-340 | production / 生产 | - | - | - | MOD-TEST-340 | production / 生产 | generated / 已生成 | - |
| JOB-719239 | MOD-TEST-342 | production / 生产 | - | - | - | MOD-TEST-342 | production / 生产 | generated / 已生成 | - |
| JOB-719240 | MOD-TEST-343 | production / 生产 | - | - | - | MOD-TEST-343 | production / 生产 | generated / 已生成 | - |
| JOB-719241 | MOD-TEST-344 | production / 生产 | - | - | - | MOD-TEST-344 | production / 生产 | generated / 已生成 | - |
| JOB-719242 | MOD-TEST-345 | production / 生产 | - | - | - | MOD-TEST-345 | production / 生产 | generated / 已生成 | - |
| JOB-719243 | MOD-TEST-346 | production / 生产 | - | - | - | MOD-TEST-346 | production / 生产 | generated / 已生成 | - |
| JOB-719244 | MOD-TEST-347 | production / 生产 | - | - | - | MOD-TEST-347 | production / 生产 | generated / 已生成 | - |
| JOB-719245 | MOD-TEST-348 | production / 生产 | - | - | - | MOD-TEST-348 | production / 生产 | generated / 已生成 | - |
| JOB-719246 | MOD-TEST-349 | production / 生产 | - | - | - | MOD-TEST-349 | production / 生产 | generated / 已生成 | - |
| JOB-719247 | MOD-TEST-350 | production / 生产 | - | - | - | MOD-TEST-350 | production / 生产 | generated / 已生成 | - |
| JOB-719248 | MOD-TEST-351 | production / 生产 | - | - | - | MOD-TEST-351 | production / 生产 | generated / 已生成 | - |
| JOB-719249 | MOD-TEST-354 | production / 生产 | - | - | - | MOD-TEST-354 | production / 生产 | generated / 已生成 | - |
| JOB-719250 | MOD-TEST-355 | production / 生产 | - | - | - | MOD-TEST-355 | production / 生产 | generated / 已生成 | - |
| JOB-719251 | MOD-TEST-356 | production / 生产 | - | - | - | MOD-TEST-356 | production / 生产 | generated / 已生成 | - |
| JOB-719252 | MOD-TEST-357 | production / 生产 | - | - | - | MOD-TEST-357 | production / 生产 | generated / 已生成 | - |
| JOB-719253 | MOD-TEST-358 | production / 生产 | - | - | - | MOD-TEST-358 | production / 生产 | generated / 已生成 | - |
| JOB-719254 | MOD-TEST-359 | production / 生产 | - | - | - | MOD-TEST-359 | production / 生产 | generated / 已生成 | - |
| JOB-719255 | MOD-TEST-360 | production / 生产 | - | - | - | MOD-TEST-360 | production / 生产 | generated / 已生成 | - |
| JOB-719256 | MOD-TEST-361 | production / 生产 | - | - | - | MOD-TEST-361 | production / 生产 | generated / 已生成 | - |
| JOB-719257 | MOD-TEST-362 | production / 生产 | - | - | - | MOD-TEST-362 | production / 生产 | generated / 已生成 | - |
| JOB-719258 | MOD-TEST-363 | production / 生产 | - | - | - | MOD-TEST-363 | production / 生产 | generated / 已生成 | - |
| JOB-719259 | MOD-TEST-364 | production / 生产 | - | - | - | MOD-TEST-364 | production / 生产 | generated / 已生成 | - |
| JOB-719260 | MOD-TEST-365 | production / 生产 | - | - | - | MOD-TEST-365 | production / 生产 | generated / 已生成 | - |
| JOB-719261 | MOD-TEST-366 | production / 生产 | - | - | - | MOD-TEST-366 | production / 生产 | generated / 已生成 | - |
| JOB-719262 | MOD-TEST-367 | production / 生产 | - | - | - | MOD-TEST-367 | production / 生产 | generated / 已生成 | - |
| JOB-719263 | MOD-TEST-368 | production / 生产 | - | - | - | MOD-TEST-368 | production / 生产 | generated / 已生成 | - |
| JOB-719264 | MOD-TEST-369 | production / 生产 | - | - | - | MOD-TEST-369 | production / 生产 | generated / 已生成 | - |
| JOB-719265 | MOD-TEST-370 | production / 生产 | - | - | - | MOD-TEST-370 | production / 生产 | generated / 已生成 | - |
| JOB-719266 | MOD-TEST-371 | production / 生产 | - | - | - | MOD-TEST-371 | production / 生产 | generated / 已生成 | - |
| JOB-719267 | MOD-TEST-372 | production / 生产 | - | - | - | MOD-TEST-372 | production / 生产 | generated / 已生成 | - |
| JOB-719268 | MOD-TEST-373 | production / 生产 | - | - | - | MOD-TEST-373 | production / 生产 | generated / 已生成 | - |
| JOB-719269 | MOD-TEST-374 | production / 生产 | - | - | - | MOD-TEST-374 | production / 生产 | generated / 已生成 | - |
| JOB-719270 | MOD-TEST-375 | production / 生产 | - | - | - | MOD-TEST-375 | production / 生产 | generated / 已生成 | - |
| JOB-719271 | MOD-TEST-376 | production / 生产 | - | - | - | MOD-TEST-376 | production / 生产 | generated / 已生成 | - |
| JOB-719272 | MOD-TEST-377 | production / 生产 | - | - | - | MOD-TEST-377 | production / 生产 | generated / 已生成 | - |
| JOB-719273 | MOD-TEST-378 | production / 生产 | - | - | - | MOD-TEST-378 | production / 生产 | generated / 已生成 | - |
| JOB-719274 | MOD-TEST-379 | production / 生产 | - | - | - | MOD-TEST-379 | production / 生产 | generated / 已生成 | - |
| JOB-719275 | MOD-TEST-380 | production / 生产 | - | - | - | MOD-TEST-380 | production / 生产 | generated / 已生成 | - |
| JOB-719276 | MOD-TEST-381 | production / 生产 | - | - | - | MOD-TEST-381 | production / 生产 | generated / 已生成 | - |
| JOB-719277 | MOD-TEST-382 | production / 生产 | - | - | - | MOD-TEST-382 | production / 生产 | generated / 已生成 | - |
| JOB-719278 | MOD-TEST-383 | production / 生产 | - | - | - | MOD-TEST-383 | production / 生产 | generated / 已生成 | - |
| JOB-719279 | MOD-TEST-384 | production / 生产 | - | - | - | MOD-TEST-384 | production / 生产 | generated / 已生成 | - |
| JOB-719280 | MOD-TEST-385 | production / 生产 | - | - | - | MOD-TEST-385 | production / 生产 | generated / 已生成 | - |
| JOB-719281 | MOD-TEST-386 | production / 生产 | - | - | - | MOD-TEST-386 | production / 生产 | generated / 已生成 | - |
| JOB-719282 | MOD-TEST-387 | production / 生产 | - | - | - | MOD-TEST-387 | production / 生产 | generated / 已生成 | - |
| JOB-719283 | MOD-TEST-388 | production / 生产 | - | - | - | MOD-TEST-388 | production / 生产 | generated / 已生成 | - |
| JOB-719284 | MOD-TEST-389 | production / 生产 | - | - | - | MOD-TEST-389 | production / 生产 | generated / 已生成 | - |
| JOB-719285 | MOD-TEST-390 | production / 生产 | - | - | - | MOD-TEST-390 | production / 生产 | generated / 已生成 | - |
| JOB-719286 | MOD-TEST-391 | production / 生产 | - | - | - | MOD-TEST-391 | production / 生产 | generated / 已生成 | - |
| JOB-719287 | MOD-TEST-392 | production / 生产 | - | - | - | MOD-TEST-392 | production / 生产 | generated / 已生成 | - |
| JOB-719288 | MOD-TEST-393 | production / 生产 | - | - | - | MOD-TEST-393 | production / 生产 | generated / 已生成 | - |
| JOB-719289 | MOD-TEST-394 | production / 生产 | - | - | - | MOD-TEST-394 | production / 生产 | generated / 已生成 | - |
| JOB-719290 | MOD-TEST-395 | production / 生产 | - | - | - | MOD-TEST-395 | production / 生产 | generated / 已生成 | - |
| JOB-719291 | MOD-TEST-396 | production / 生产 | - | - | - | MOD-TEST-396 | production / 生产 | generated / 已生成 | - |
| JOB-719292 | MOD-TEST-397 | production / 生产 | - | - | - | MOD-TEST-397 | production / 生产 | generated / 已生成 | - |
| JOB-719293 | MOD-TEST-402 | production / 生产 | - | - | - | MOD-TEST-402 | production / 生产 | generated / 已生成 | - |
| JOB-719294 | MOD-TEST-403 | production / 生产 | - | - | - | MOD-TEST-403 | production / 生产 | generated / 已生成 | - |
| JOB-719295 | MOD-TEST-404 | production / 生产 | - | - | - | MOD-TEST-404 | production / 生产 | generated / 已生成 | - |
| JOB-719296 | MOD-TEST-406 | production / 生产 | - | - | - | MOD-TEST-406 | production / 生产 | generated / 已生成 | - |
| JOB-719297 | MOD-TEST-407 | production / 生产 | - | - | - | MOD-TEST-407 | production / 生产 | generated / 已生成 | - |
| JOB-719298 | MOD-TEST-408 | production / 生产 | - | - | - | MOD-TEST-408 | production / 生产 | generated / 已生成 | - |
| JOB-719299 | MOD-TEST-409 | production / 生产 | - | - | - | MOD-TEST-409 | production / 生产 | generated / 已生成 | - |
| JOB-719300 | MOD-TEST-410 | production / 生产 | - | - | - | MOD-TEST-410 | production / 生产 | generated / 已生成 | - |
| JOB-719301 | MOD-TEST-411 | production / 生产 | - | - | - | MOD-TEST-411 | production / 生产 | generated / 已生成 | - |
| JOB-719302 | MOD-TEST-412 | production / 生产 | - | - | - | MOD-TEST-412 | production / 生产 | generated / 已生成 | - |
| JOB-719303 | MOD-TEST-413 | production / 生产 | - | - | - | MOD-TEST-413 | production / 生产 | generated / 已生成 | - |
| JOB-719304 | MOD-TEST-414 | production / 生产 | - | - | - | MOD-TEST-414 | production / 生产 | generated / 已生成 | - |
| JOB-719305 | MOD-TEST-415 | production / 生产 | - | - | - | MOD-TEST-415 | production / 生产 | generated / 已生成 | - |
| JOB-719306 | MOD-TEST-416 | production / 生产 | - | - | - | MOD-TEST-416 | production / 生产 | generated / 已生成 | - |
| JOB-719307 | MOD-TEST-417 | production / 生产 | - | - | - | MOD-TEST-417 | production / 生产 | generated / 已生成 | - |
| JOB-719308 | MOD-TEST-418 | production / 生产 | - | - | - | MOD-TEST-418 | production / 生产 | generated / 已生成 | - |
| JOB-719309 | MOD-TEST-419 | production / 生产 | - | - | - | MOD-TEST-419 | production / 生产 | generated / 已生成 | - |
| JOB-719310 | MOD-TEST-420 | production / 生产 | - | - | - | MOD-TEST-420 | production / 生产 | generated / 已生成 | - |
| JOB-719311 | MOD-TEST-421 | production / 生产 | - | - | - | MOD-TEST-421 | production / 生产 | generated / 已生成 | - |
| JOB-719312 | MOD-TEST-422 | production / 生产 | - | - | - | MOD-TEST-422 | production / 生产 | generated / 已生成 | - |
| JOB-719313 | MOD-TEST-423 | production / 生产 | - | - | - | MOD-TEST-423 | production / 生产 | generated / 已生成 | - |
| JOB-719314 | MOD-TEST-424 | production / 生产 | - | - | - | MOD-TEST-424 | production / 生产 | generated / 已生成 | - |
| JOB-719315 | MOD-TEST-425 | production / 生产 | - | - | - | MOD-TEST-425 | production / 生产 | generated / 已生成 | - |
| JOB-719316 | MOD-TEST-426 | production / 生产 | - | - | - | MOD-TEST-426 | production / 生产 | generated / 已生成 | - |
| JOB-719317 | MOD-TEST-427 | production / 生产 | - | - | - | MOD-TEST-427 | production / 生产 | generated / 已生成 | - |
| JOB-719318 | MOD-TEST-428 | production / 生产 | - | - | - | MOD-TEST-428 | production / 生产 | generated / 已生成 | - |
| JOB-719319 | MOD-TEST-429 | production / 生产 | - | - | - | MOD-TEST-429 | production / 生产 | generated / 已生成 | - |
| JOB-719320 | MOD-TEST-430 | production / 生产 | - | - | - | MOD-TEST-430 | production / 生产 | generated / 已生成 | - |
| JOB-719321 | MOD-TEST-431 | production / 生产 | - | - | - | MOD-TEST-431 | production / 生产 | generated / 已生成 | - |
| JOB-719322 | MOD-TEST-432 | production / 生产 | - | - | - | MOD-TEST-432 | production / 生产 | generated / 已生成 | - |
| JOB-719323 | MOD-TEST-433 | production / 生产 | - | - | - | MOD-TEST-433 | production / 生产 | generated / 已生成 | - |
| JOB-719324 | MOD-TEST-434 | production / 生产 | - | - | - | MOD-TEST-434 | production / 生产 | generated / 已生成 | - |
| JOB-719325 | MOD-TEST-435 | production / 生产 | - | - | - | MOD-TEST-435 | production / 生产 | generated / 已生成 | - |
| JOB-719326 | MOD-TEST-436 | production / 生产 | - | - | - | MOD-TEST-436 | production / 生产 | generated / 已生成 | - |
| JOB-719327 | MOD-TEST-437 | production / 生产 | - | - | - | MOD-TEST-437 | production / 生产 | generated / 已生成 | - |
| JOB-719328 | MOD-TEST-438 | production / 生产 | - | - | - | MOD-TEST-438 | production / 生产 | generated / 已生成 | - |
| JOB-719329 | MOD-TEST-439 | production / 生产 | - | - | - | MOD-TEST-439 | production / 生产 | generated / 已生成 | - |
| JOB-719330 | MOD-TEST-440 | production / 生产 | - | - | - | MOD-TEST-440 | production / 生产 | generated / 已生成 | - |
| JOB-719331 | MOD-TEST-441 | production / 生产 | - | - | - | MOD-TEST-441 | production / 生产 | generated / 已生成 | - |
| JOB-719332 | MOD-TEST-444 | production / 生产 | - | - | - | MOD-TEST-444 | production / 生产 | generated / 已生成 | - |
| JOB-719333 | MOD-TEST-447 | production / 生产 | - | - | - | MOD-TEST-447 | production / 生产 | generated / 已生成 | - |
| JOB-719334 | MOD-TEST-449 | production / 生产 | - | - | - | MOD-TEST-449 | production / 生产 | generated / 已生成 | - |
| JOB-719335 | MOD-TEST-450 | production / 生产 | - | - | - | MOD-TEST-450 | production / 生产 | generated / 已生成 | - |
| JOB-719336 | MOD-TEST-452 | production / 生产 | - | - | - | MOD-TEST-452 | production / 生产 | generated / 已生成 | - |
| JOB-719337 | MOD-TEST-454 | production / 生产 | - | - | - | MOD-TEST-454 | production / 生产 | generated / 已生成 | - |
| JOB-719338 | MOD-TEST-455 | production / 生产 | - | - | - | MOD-TEST-455 | production / 生产 | generated / 已生成 | - |
| JOB-719339 | MOD-TEST-456 | production / 生产 | - | - | - | MOD-TEST-456 | production / 生产 | generated / 已生成 | - |
| JOB-719340 | MOD-TEST-457 | production / 生产 | - | - | - | MOD-TEST-457 | production / 生产 | generated / 已生成 | - |
| JOB-719341 | MOD-TEST-459 | production / 生产 | - | - | - | MOD-TEST-459 | production / 生产 | generated / 已生成 | - |
| JOB-719342 | MOD-TEST-460 | production / 生产 | - | - | - | MOD-TEST-460 | production / 生产 | generated / 已生成 | - |
| JOB-719343 | MOD-TEST-461 | production / 生产 | - | - | - | MOD-TEST-461 | production / 生产 | generated / 已生成 | - |
| JOB-719344 | MOD-TEST-462 | production / 生产 | - | - | - | MOD-TEST-462 | production / 生产 | generated / 已生成 | - |
| JOB-719345 | MOD-TEST-463 | production / 生产 | - | - | - | MOD-TEST-463 | production / 生产 | generated / 已生成 | - |
| JOB-719346 | MOD-TEST-464 | production / 生产 | - | - | - | MOD-TEST-464 | production / 生产 | generated / 已生成 | - |
| JOB-719347 | MOD-TEST-466 | production / 生产 | - | - | - | MOD-TEST-466 | production / 生产 | generated / 已生成 | - |
| JOB-719348 | MOD-TEST-467 | production / 生产 | - | - | - | MOD-TEST-467 | production / 生产 | generated / 已生成 | - |
| JOB-719349 | MOD-TEST-468 | production / 生产 | - | - | - | MOD-TEST-468 | production / 生产 | generated / 已生成 | - |
| JOB-719350 | MOD-TEST-469 | production / 生产 | - | - | - | MOD-TEST-469 | production / 生产 | generated / 已生成 | - |
| JOB-719351 | MOD-TEST-470 | production / 生产 | - | - | - | MOD-TEST-470 | production / 生产 | generated / 已生成 | - |
| JOB-719352 | MOD-TEST-471 | production / 生产 | - | - | - | MOD-TEST-471 | production / 生产 | generated / 已生成 | - |
| JOB-719353 | MOD-TEST-472 | production / 生产 | - | - | - | MOD-TEST-472 | production / 生产 | generated / 已生成 | - |
| JOB-719354 | MOD-TEST-473 | production / 生产 | - | - | - | MOD-TEST-473 | production / 生产 | generated / 已生成 | - |
| JOB-719355 | MOD-TEST-475 | production / 生产 | - | - | - | MOD-TEST-475 | production / 生产 | generated / 已生成 | - |
| JOB-719356 | MOD-TEST-476 | production / 生产 | - | - | - | MOD-TEST-476 | production / 生产 | generated / 已生成 | - |
| JOB-719357 | MOD-TEST-477 | production / 生产 | - | - | - | MOD-TEST-477 | production / 生产 | generated / 已生成 | - |
| JOB-719358 | MOD-TEST-479 | production / 生产 | - | - | - | MOD-TEST-479 | production / 生产 | generated / 已生成 | - |
| JOB-719359 | MOD-TEST-481 | production / 生产 | - | - | - | MOD-TEST-481 | production / 生产 | generated / 已生成 | - |
| JOB-719360 | MOD-TEST-482 | production / 生产 | - | - | - | MOD-TEST-482 | production / 生产 | generated / 已生成 | - |
| JOB-719361 | MOD-TEST-484 | production / 生产 | - | - | - | MOD-TEST-484 | production / 生产 | generated / 已生成 | - |
| JOB-719362 | MOD-TEST-485 | production / 生产 | - | - | - | MOD-TEST-485 | production / 生产 | generated / 已生成 | - |
| JOB-719363 | MOD-TEST-487 | production / 生产 | - | - | - | MOD-TEST-487 | production / 生产 | generated / 已生成 | - |
| JOB-719364 | MOD-TEST-488 | production / 生产 | - | - | - | MOD-TEST-488 | production / 生产 | generated / 已生成 | - |
| JOB-719365 | MOD-TEST-489 | production / 生产 | - | - | - | MOD-TEST-489 | production / 生产 | generated / 已生成 | - |
| JOB-719366 | MOD-TEST-490 | production / 生产 | - | - | - | MOD-TEST-490 | production / 生产 | generated / 已生成 | - |
| JOB-719367 | MOD-TEST-491 | production / 生产 | - | - | - | MOD-TEST-491 | production / 生产 | generated / 已生成 | - |
| JOB-719368 | MOD-TEST-492 | production / 生产 | - | - | - | MOD-TEST-492 | production / 生产 | generated / 已生成 | - |
| JOB-719369 | MOD-TEST-494 | production / 生产 | - | - | - | MOD-TEST-494 | production / 生产 | generated / 已生成 | - |
| JOB-719370 | MOD-TEST-495 | production / 生产 | - | - | - | MOD-TEST-495 | production / 生产 | generated / 已生成 | - |
| JOB-719371 | MOD-TEST-496 | production / 生产 | - | - | - | MOD-TEST-496 | production / 生产 | generated / 已生成 | - |
| JOB-719372 | MOD-TEST-497 | production / 生产 | - | - | - | MOD-TEST-497 | production / 生产 | generated / 已生成 | - |
| JOB-719373 | MOD-TEST-498 | production / 生产 | - | - | - | MOD-TEST-498 | production / 生产 | generated / 已生成 | - |
| JOB-719374 | MOD-TEST-499 | production / 生产 | - | - | - | MOD-TEST-499 | production / 生产 | generated / 已生成 | - |
| JOB-719375 | MOD-TEST-501 | production / 生产 | - | - | - | MOD-TEST-501 | production / 生产 | generated / 已生成 | - |
| JOB-719376 | MOD-TEST-502 | production / 生产 | - | - | - | MOD-TEST-502 | production / 生产 | generated / 已生成 | - |
| JOB-719377 | MOD-TEST-504 | production / 生产 | - | - | - | MOD-TEST-504 | production / 生产 | generated / 已生成 | - |
| JOB-719378 | MOD-TEST-505 | production / 生产 | - | - | - | MOD-TEST-505 | production / 生产 | generated / 已生成 | - |
| JOB-719379 | MOD-TEST-506 | production / 生产 | - | - | - | MOD-TEST-506 | production / 生产 | generated / 已生成 | - |
| JOB-719380 | MOD-TEST-508 | production / 生产 | - | - | - | MOD-TEST-508 | production / 生产 | generated / 已生成 | - |
| JOB-719381 | MOD-TEST-509 | production / 生产 | - | - | - | MOD-TEST-509 | production / 生产 | generated / 已生成 | - |
| JOB-719382 | MOD-TEST-510 | production / 生产 | - | - | - | MOD-TEST-510 | production / 生产 | generated / 已生成 | - |
| JOB-719383 | MOD-TEST-511 | production / 生产 | - | - | - | MOD-TEST-511 | production / 生产 | generated / 已生成 | - |
| JOB-719384 | MOD-TEST-512 | production / 生产 | - | - | - | MOD-TEST-512 | production / 生产 | generated / 已生成 | - |
| JOB-719385 | MOD-TEST-513 | production / 生产 | - | - | - | MOD-TEST-513 | production / 生产 | generated / 已生成 | - |
| JOB-719386 | MOD-TEST-514 | production / 生产 | - | - | - | MOD-TEST-514 | production / 生产 | generated / 已生成 | - |
| JOB-719387 | MOD-TEST-528 | production / 生产 | - | - | - | MOD-TEST-528 | production / 生产 | generated / 已生成 | - |
| JOB-719388 | MOD-TEST-529 | production / 生产 | - | - | - | MOD-TEST-529 | production / 生产 | generated / 已生成 | - |
| JOB-719389 | MOD-TEST-530 | production / 生产 | - | - | - | MOD-TEST-530 | production / 生产 | generated / 已生成 | - |
| JOB-719390 | MOD-TEST-532 | production / 生产 | - | - | - | MOD-TEST-532 | production / 生产 | generated / 已生成 | - |
| JOB-719391 | MOD-TEST-533 | production / 生产 | - | - | - | MOD-TEST-533 | production / 生产 | generated / 已生成 | - |
| JOB-719392 | MOD-TEST-534 | production / 生产 | - | - | - | MOD-TEST-534 | production / 生产 | generated / 已生成 | - |
| JOB-719393 | MOD-TEST-535 | production / 生产 | - | - | - | MOD-TEST-535 | production / 生产 | generated / 已生成 | - |
| JOB-719394 | MOD-TEST-536 | production / 生产 | - | - | - | MOD-TEST-536 | production / 生产 | generated / 已生成 | - |
| JOB-719395 | MOD-TEST-537 | production / 生产 | - | - | - | MOD-TEST-537 | production / 生产 | generated / 已生成 | - |
| JOB-719396 | MOD-TEST-538 | production / 生产 | - | - | - | MOD-TEST-538 | production / 生产 | generated / 已生成 | - |
| JOB-719397 | MOD-TEST-539 | production / 生产 | - | - | - | MOD-TEST-539 | production / 生产 | generated / 已生成 | - |
| JOB-719398 | MOD-TEST-540 | production / 生产 | - | - | - | MOD-TEST-540 | production / 生产 | generated / 已生成 | - |
| JOB-719399 | MOD-TEST-541 | production / 生产 | - | - | - | MOD-TEST-541 | production / 生产 | generated / 已生成 | - |
| JOB-719400 | MOD-TEST-543 | production / 生产 | - | - | - | MOD-TEST-543 | production / 生产 | generated / 已生成 | - |
| JOB-719401 | MOD-TEST-544 | production / 生产 | - | - | - | MOD-TEST-544 | production / 生产 | generated / 已生成 | - |
| JOB-719402 | MOD-TEST-545 | production / 生产 | - | - | - | MOD-TEST-545 | production / 生产 | generated / 已生成 | - |
| JOB-719403 | MOD-TEST-547 | production / 生产 | - | - | - | MOD-TEST-547 | production / 生产 | generated / 已生成 | - |
| JOB-719404 | MOD-TEST-548 | production / 生产 | - | - | - | MOD-TEST-548 | production / 生产 | generated / 已生成 | - |
| JOB-719405 | MOD-TEST-549 | production / 生产 | - | - | - | MOD-TEST-549 | production / 生产 | generated / 已生成 | - |
| JOB-719406 | MOD-TEST-550 | production / 生产 | - | - | - | MOD-TEST-550 | production / 生产 | generated / 已生成 | - |
| JOB-719407 | MOD-TEST-551 | production / 生产 | - | - | - | MOD-TEST-551 | production / 生产 | generated / 已生成 | - |
| JOB-719408 | MOD-TEST-552 | production / 生产 | - | - | - | MOD-TEST-552 | production / 生产 | generated / 已生成 | - |
| JOB-719409 | MOD-TEST-553 | production / 生产 | - | - | - | MOD-TEST-553 | production / 生产 | generated / 已生成 | - |
| JOB-719410 | MOD-TEST-554 | production / 生产 | - | - | - | MOD-TEST-554 | production / 生产 | generated / 已生成 | - |
| JOB-719411 | MOD-TEST-555 | production / 生产 | - | - | - | MOD-TEST-555 | production / 生产 | generated / 已生成 | - |
| JOB-719412 | MOD-TEST-557 | production / 生产 | - | - | - | MOD-TEST-557 | production / 生产 | generated / 已生成 | - |
| JOB-719413 | MOD-TEST-558 | production / 生产 | - | - | - | MOD-TEST-558 | production / 生产 | generated / 已生成 | - |
| JOB-719414 | MOD-TEST-559 | production / 生产 | - | - | - | MOD-TEST-559 | production / 生产 | generated / 已生成 | - |
| JOB-719415 | MOD-TEST-560 | production / 生产 | - | - | - | MOD-TEST-560 | production / 生产 | generated / 已生成 | - |
| JOB-719416 | MOD-TEST-561 | production / 生产 | - | - | - | MOD-TEST-561 | production / 生产 | generated / 已生成 | - |
| JOB-719417 | MOD-TEST-562 | production / 生产 | - | - | - | MOD-TEST-562 | production / 生产 | generated / 已生成 | - |
| JOB-719418 | MOD-TEST-563 | production / 生产 | - | - | - | MOD-TEST-563 | production / 生产 | generated / 已生成 | - |
| JOB-719419 | MOD-TEST-564 | production / 生产 | - | - | - | MOD-TEST-564 | production / 生产 | generated / 已生成 | - |
| JOB-719420 | MOD-TEST-565 | production / 生产 | - | - | - | MOD-TEST-565 | production / 生产 | generated / 已生成 | - |
| JOB-719421 | MOD-TEST-566 | production / 生产 | - | - | - | MOD-TEST-566 | production / 生产 | generated / 已生成 | - |
| JOB-719422 | MOD-TEST-567 | production / 生产 | - | - | - | MOD-TEST-567 | production / 生产 | generated / 已生成 | - |
| JOB-719423 | MOD-TEST-568 | production / 生产 | - | - | - | MOD-TEST-568 | production / 生产 | generated / 已生成 | - |
| JOB-719424 | MOD-TEST-569 | production / 生产 | - | - | - | MOD-TEST-569 | production / 生产 | generated / 已生成 | - |
| JOB-719425 | MOD-TEST-570 | production / 生产 | - | - | - | MOD-TEST-570 | production / 生产 | generated / 已生成 | - |
| JOB-719426 | MOD-TEST-571 | production / 生产 | - | - | - | MOD-TEST-571 | production / 生产 | generated / 已生成 | - |
| JOB-719427 | MOD-TEST-572 | production / 生产 | - | - | - | MOD-TEST-572 | production / 生产 | generated / 已生成 | - |
| JOB-719428 | MOD-TEST-573 | production / 生产 | - | - | - | MOD-TEST-573 | production / 生产 | generated / 已生成 | - |
| JOB-719429 | MOD-TEST-574 | production / 生产 | - | - | - | MOD-TEST-574 | production / 生产 | generated / 已生成 | - |
| JOB-719430 | MOD-TEST-575 | production / 生产 | - | - | - | MOD-TEST-575 | production / 生产 | generated / 已生成 | - |
| JOB-719431 | MOD-TEST-576 | production / 生产 | - | - | - | MOD-TEST-576 | production / 生产 | generated / 已生成 | - |
| JOB-719432 | MOD-TEST-577 | production / 生产 | - | - | - | MOD-TEST-577 | production / 生产 | generated / 已生成 | - |
| JOB-719433 | MOD-TEST-579 | production / 生产 | - | - | - | MOD-TEST-579 | production / 生产 | generated / 已生成 | - |
| JOB-719434 | MOD-TEST-580 | production / 生产 | - | - | - | MOD-TEST-580 | production / 生产 | generated / 已生成 | - |
| JOB-719435 | MOD-TEST-582 | production / 生产 | - | - | - | MOD-TEST-582 | production / 生产 | generated / 已生成 | - |
| JOB-719436 | MOD-TEST-583 | production / 生产 | - | - | - | MOD-TEST-583 | production / 生产 | generated / 已生成 | - |
| JOB-719437 | MOD-TEST-584 | production / 生产 | - | - | - | MOD-TEST-584 | production / 生产 | generated / 已生成 | - |
| JOB-719438 | MOD-TEST-585 | production / 生产 | - | - | - | MOD-TEST-585 | production / 生产 | generated / 已生成 | - |
| JOB-719439 | MOD-TEST-586 | production / 生产 | - | - | - | MOD-TEST-586 | production / 生产 | generated / 已生成 | - |
| JOB-719440 | MOD-TEST-587 | production / 生产 | - | - | - | MOD-TEST-587 | production / 生产 | generated / 已生成 | - |
| JOB-719441 | MOD-TEST-588 | production / 生产 | - | - | - | MOD-TEST-588 | production / 生产 | generated / 已生成 | - |
| JOB-719442 | MOD-TEST-590 | production / 生产 | - | - | - | MOD-TEST-590 | production / 生产 | generated / 已生成 | - |
| JOB-719443 | MOD-TEST-591 | production / 生产 | - | - | - | MOD-TEST-591 | production / 生产 | generated / 已生成 | - |
| JOB-719444 | MOD-TEST-592 | production / 生产 | - | - | - | MOD-TEST-592 | production / 生产 | generated / 已生成 | - |
| JOB-719445 | MOD-TEST-593 | production / 生产 | - | - | - | MOD-TEST-593 | production / 生产 | generated / 已生成 | - |
| JOB-719446 | MOD-TEST-594 | production / 生产 | - | - | - | MOD-TEST-594 | production / 生产 | generated / 已生成 | - |
| JOB-719447 | MOD-TEST-595 | production / 生产 | - | - | - | MOD-TEST-595 | production / 生产 | generated / 已生成 | - |
| JOB-719448 | MOD-TEST-597 | production / 生产 | - | - | - | MOD-TEST-597 | production / 生产 | generated / 已生成 | - |
| JOB-719449 | MOD-TEST-598 | production / 生产 | - | - | - | MOD-TEST-598 | production / 生产 | generated / 已生成 | - |
| JOB-719450 | MOD-TEST-599 | production / 生产 | - | - | - | MOD-TEST-599 | production / 生产 | generated / 已生成 | - |
| JOB-719451 | MOD-TEST-600 | production / 生产 | - | - | - | MOD-TEST-600 | production / 生产 | generated / 已生成 | - |
| JOB-719452 | MOD-TEST-601 | production / 生产 | - | - | - | MOD-TEST-601 | production / 生产 | generated / 已生成 | - |
| JOB-719453 | MOD-TEST-602 | production / 生产 | - | - | - | MOD-TEST-602 | production / 生产 | generated / 已生成 | - |
| JOB-719454 | MOD-TEST-603 | production / 生产 | - | - | - | MOD-TEST-603 | production / 生产 | generated / 已生成 | - |
| JOB-719455 | MOD-TEST-604 | production / 生产 | - | - | - | MOD-TEST-604 | production / 生产 | generated / 已生成 | - |
| JOB-719456 | MOD-TEST-605 | production / 生产 | - | - | - | MOD-TEST-605 | production / 生产 | generated / 已生成 | - |
| JOB-719457 | MOD-TEST-606 | production / 生产 | - | - | - | MOD-TEST-606 | production / 生产 | generated / 已生成 | - |
| JOB-719458 | MOD-TEST-607 | production / 生产 | - | - | - | MOD-TEST-607 | production / 生产 | generated / 已生成 | - |
| JOB-719459 | MOD-TEST-608 | production / 生产 | - | - | - | MOD-TEST-608 | production / 生产 | generated / 已生成 | - |
| JOB-719460 | MOD-TEST-609 | production / 生产 | - | - | - | MOD-TEST-609 | production / 生产 | generated / 已生成 | - |
| JOB-719461 | MOD-TEST-610 | production / 生产 | - | - | - | MOD-TEST-610 | production / 生产 | generated / 已生成 | - |
| JOB-719462 | MOD-TEST-611 | production / 生产 | - | - | - | MOD-TEST-611 | production / 生产 | generated / 已生成 | - |
| JOB-719463 | MOD-TEST-612 | production / 生产 | - | - | - | MOD-TEST-612 | production / 生产 | generated / 已生成 | - |
| JOB-719464 | MOD-TEST-613 | production / 生产 | - | - | - | MOD-TEST-613 | production / 生产 | generated / 已生成 | - |
| JOB-719465 | MOD-TEST-614 | production / 生产 | - | - | - | MOD-TEST-614 | production / 生产 | generated / 已生成 | - |
| JOB-719466 | MOD-TEST-616 | production / 生产 | - | - | - | MOD-TEST-616 | production / 生产 | generated / 已生成 | - |
| JOB-719467 | MOD-TEST-617 | production / 生产 | - | - | - | MOD-TEST-617 | production / 生产 | generated / 已生成 | - |
| JOB-719468 | MOD-TEST-618 | production / 生产 | - | - | - | MOD-TEST-618 | production / 生产 | generated / 已生成 | - |
| JOB-719469 | MOD-TEST-619 | production / 生产 | - | - | - | MOD-TEST-619 | production / 生产 | generated / 已生成 | - |
| JOB-719470 | MOD-TEST-620 | production / 生产 | - | - | - | MOD-TEST-620 | production / 生产 | generated / 已生成 | - |
| JOB-719471 | MOD-TEST-621 | production / 生产 | - | - | - | MOD-TEST-621 | production / 生产 | generated / 已生成 | - |
| JOB-719472 | MOD-TEST-622 | production / 生产 | - | - | - | MOD-TEST-622 | production / 生产 | generated / 已生成 | - |
| JOB-719473 | MOD-TEST-623 | production / 生产 | - | - | - | MOD-TEST-623 | production / 生产 | generated / 已生成 | - |
| JOB-719474 | MOD-TEST-624 | production / 生产 | - | - | - | MOD-TEST-624 | production / 生产 | generated / 已生成 | - |
| JOB-719475 | MOD-TEST-625 | production / 生产 | - | - | - | MOD-TEST-625 | production / 生产 | generated / 已生成 | - |
| JOB-719476 | MOD-TEST-626 | production / 生产 | - | - | - | MOD-TEST-626 | production / 生产 | generated / 已生成 | - |
| JOB-719477 | MOD-TEST-627 | production / 生产 | - | - | - | MOD-TEST-627 | production / 生产 | generated / 已生成 | - |
| JOB-719478 | MOD-TEST-628 | production / 生产 | - | - | - | MOD-TEST-628 | production / 生产 | generated / 已生成 | - |
| JOB-719479 | MOD-TEST-629 | production / 生产 | - | - | - | MOD-TEST-629 | production / 生产 | generated / 已生成 | - |
| JOB-719480 | MOD-TEST-630 | production / 生产 | - | - | - | MOD-TEST-630 | production / 生产 | generated / 已生成 | - |
| JOB-719481 | MOD-TEST-631 | production / 生产 | - | - | - | MOD-TEST-631 | production / 生产 | generated / 已生成 | - |
| JOB-719482 | MOD-TEST-633 | production / 生产 | - | - | - | MOD-TEST-633 | production / 生产 | generated / 已生成 | - |
| JOB-719483 | MOD-TEST-634 | production / 生产 | - | - | - | MOD-TEST-634 | production / 生产 | generated / 已生成 | - |
| JOB-719484 | MOD-TEST-635 | production / 生产 | - | - | - | MOD-TEST-635 | production / 生产 | generated / 已生成 | - |
| JOB-719485 | MOD-TEST-636 | production / 生产 | - | - | - | MOD-TEST-636 | production / 生产 | generated / 已生成 | - |
| JOB-719486 | MOD-TEST-637 | production / 生产 | - | - | - | MOD-TEST-637 | production / 生产 | generated / 已生成 | - |
| JOB-719487 | MOD-TEST-639 | production / 生产 | - | - | - | MOD-TEST-639 | production / 生产 | generated / 已生成 | - |
| JOB-719488 | MOD-TEST-640 | production / 生产 | - | - | - | MOD-TEST-640 | production / 生产 | generated / 已生成 | - |
| JOB-719489 | MOD-TEST-641 | production / 生产 | - | - | - | MOD-TEST-641 | production / 生产 | generated / 已生成 | - |
| JOB-719490 | MOD-TEST-642 | production / 生产 | - | - | - | MOD-TEST-642 | production / 生产 | generated / 已生成 | - |
| JOB-719491 | MOD-TEST-643 | production / 生产 | - | - | - | MOD-TEST-643 | production / 生产 | generated / 已生成 | - |
| JOB-719492 | MOD-TEST-644 | production / 生产 | - | - | - | MOD-TEST-644 | production / 生产 | generated / 已生成 | - |
| JOB-719493 | MOD-TEST-646 | production / 生产 | - | - | - | MOD-TEST-646 | production / 生产 | generated / 已生成 | - |
| JOB-719494 | MOD-TEST-647 | production / 生产 | - | - | - | MOD-TEST-647 | production / 生产 | generated / 已生成 | - |
| JOB-719495 | MOD-TEST-648 | production / 生产 | - | - | - | MOD-TEST-648 | production / 生产 | generated / 已生成 | - |
| JOB-719496 | MOD-TEST-649 | production / 生产 | - | - | - | MOD-TEST-649 | production / 生产 | generated / 已生成 | - |
| JOB-719497 | MOD-TEST-651 | production / 生产 | - | - | - | MOD-TEST-651 | production / 生产 | generated / 已生成 | - |
| JOB-719498 | MOD-TEST-652 | production / 生产 | - | - | - | MOD-TEST-652 | production / 生产 | generated / 已生成 | - |
| JOB-719499 | MOD-TEST-653 | production / 生产 | - | - | - | MOD-TEST-653 | production / 生产 | generated / 已生成 | - |
| JOB-719500 | MOD-TEST-654 | production / 生产 | - | - | - | MOD-TEST-654 | production / 生产 | generated / 已生成 | - |
| JOB-719501 | MOD-TEST-655 | production / 生产 | - | - | - | MOD-TEST-655 | production / 生产 | generated / 已生成 | - |
| JOB-719502 | MOD-TEST-660 | production / 生产 | - | - | - | MOD-TEST-660 | production / 生产 | generated / 已生成 | - |
| JOB-719503 | MOD-TEST-661 | production / 生产 | - | - | - | MOD-TEST-661 | production / 生产 | generated / 已生成 | - |
| JOB-719504 | MOD-TEST-662 | production / 生产 | - | - | - | MOD-TEST-662 | production / 生产 | generated / 已生成 | - |
| JOB-719505 | MOD-TEST-663 | production / 生产 | - | - | - | MOD-TEST-663 | production / 生产 | generated / 已生成 | - |
| JOB-719506 | MOD-TEST-664 | production / 生产 | - | - | - | MOD-TEST-664 | production / 生产 | generated / 已生成 | - |
| JOB-719507 | MOD-TEST-665 | production / 生产 | - | - | - | MOD-TEST-665 | production / 生产 | generated / 已生成 | - |
| JOB-719508 | MOD-TEST-668 | production / 生产 | - | - | - | MOD-TEST-668 | production / 生产 | generated / 已生成 | - |
| JOB-719509 | MOD-TEST-669 | production / 生产 | - | - | - | MOD-TEST-669 | production / 生产 | generated / 已生成 | - |
| JOB-719510 | MOD-TEST-670 | production / 生产 | - | - | - | MOD-TEST-670 | production / 生产 | generated / 已生成 | - |
| JOB-719511 | MOD-TEST-671 | production / 生产 | - | - | - | MOD-TEST-671 | production / 生产 | generated / 已生成 | - |
| JOB-719512 | MOD-TEST-672 | production / 生产 | - | - | - | MOD-TEST-672 | production / 生产 | generated / 已生成 | - |
| JOB-719513 | MOD-TEST-673 | production / 生产 | - | - | - | MOD-TEST-673 | production / 生产 | generated / 已生成 | - |
| JOB-719514 | MOD-TEST-674 | production / 生产 | - | - | - | MOD-TEST-674 | production / 生产 | generated / 已生成 | - |
| JOB-719515 | MOD-TEST-675 | production / 生产 | - | - | - | MOD-TEST-675 | production / 生产 | generated / 已生成 | - |
| JOB-719516 | MOD-TEST-676 | production / 生产 | - | - | - | MOD-TEST-676 | production / 生产 | generated / 已生成 | - |
| JOB-719517 | MOD-TEST-677 | production / 生产 | - | - | - | MOD-TEST-677 | production / 生产 | generated / 已生成 | - |
| JOB-719518 | MOD-TEST-678 | production / 生产 | - | - | - | MOD-TEST-678 | production / 生产 | generated / 已生成 | - |
| JOB-719519 | MOD-TEST-679 | production / 生产 | - | - | - | MOD-TEST-679 | production / 生产 | generated / 已生成 | - |
| JOB-719520 | MOD-TEST-680 | production / 生产 | - | - | - | MOD-TEST-680 | production / 生产 | generated / 已生成 | - |
| JOB-719521 | MOD-TEST-681 | production / 生产 | - | - | - | MOD-TEST-681 | production / 生产 | generated / 已生成 | - |
| JOB-719522 | MOD-TEST-682 | production / 生产 | - | - | - | MOD-TEST-682 | production / 生产 | generated / 已生成 | - |
| JOB-719523 | MOD-TEST-683 | production / 生产 | - | - | - | MOD-TEST-683 | production / 生产 | generated / 已生成 | - |
| JOB-719524 | MOD-TEST-684 | production / 生产 | - | - | - | MOD-TEST-684 | production / 生产 | generated / 已生成 | - |
| JOB-719525 | MOD-TEST-685 | production / 生产 | - | - | - | MOD-TEST-685 | production / 生产 | generated / 已生成 | - |
| JOB-719526 | MOD-TEST-686 | production / 生产 | - | - | - | MOD-TEST-686 | production / 生产 | generated / 已生成 | - |
| JOB-719527 | MOD-TEST-687 | production / 生产 | - | - | - | MOD-TEST-687 | production / 生产 | generated / 已生成 | - |
| JOB-719528 | MOD-TEST-688 | production / 生产 | - | - | - | MOD-TEST-688 | production / 生产 | generated / 已生成 | - |
| JOB-719529 | MOD-TEST-689 | production / 生产 | - | - | - | MOD-TEST-689 | production / 生产 | generated / 已生成 | - |
| JOB-719530 | MOD-TEST-690 | production / 生产 | - | - | - | MOD-TEST-690 | production / 生产 | generated / 已生成 | - |
| JOB-719531 | MOD-TEST-691 | production / 生产 | - | - | - | MOD-TEST-691 | production / 生产 | generated / 已生成 | - |
| JOB-719532 | MOD-TEST-692 | production / 生产 | - | - | - | MOD-TEST-692 | production / 生产 | generated / 已生成 | - |
| JOB-719533 | MOD-TEST-693 | production / 生产 | - | - | - | MOD-TEST-693 | production / 生产 | generated / 已生成 | - |
| JOB-719534 | MOD-TEST-694 | production / 生产 | - | - | - | MOD-TEST-694 | production / 生产 | generated / 已生成 | - |
| JOB-719535 | MOD-TEST-695 | production / 生产 | - | - | - | MOD-TEST-695 | production / 生产 | generated / 已生成 | - |
| JOB-719536 | MOD-TEST-696 | production / 生产 | - | - | - | MOD-TEST-696 | production / 生产 | generated / 已生成 | - |
| JOB-719537 | MOD-TEST-697 | production / 生产 | - | - | - | MOD-TEST-697 | production / 生产 | generated / 已生成 | - |
| JOB-719538 | MOD-TEST-698 | production / 生产 | - | - | - | MOD-TEST-698 | production / 生产 | generated / 已生成 | - |
| JOB-719539 | MOD-TEST-699 | production / 生产 | - | - | - | MOD-TEST-699 | production / 生产 | generated / 已生成 | - |
| JOB-719540 | MOD-TEST-700 | production / 生产 | - | - | - | MOD-TEST-700 | production / 生产 | generated / 已生成 | - |
| JOB-719541 | MOD-TEST-701 | production / 生产 | - | - | - | MOD-TEST-701 | production / 生产 | generated / 已生成 | - |
| JOB-719542 | MOD-TEST-702 | production / 生产 | - | - | - | MOD-TEST-702 | production / 生产 | generated / 已生成 | - |
| JOB-719543 | MOD-TEST-703 | production / 生产 | - | - | - | MOD-TEST-703 | production / 生产 | generated / 已生成 | - |
| JOB-719544 | MOD-TEST-704 | production / 生产 | - | - | - | MOD-TEST-704 | production / 生产 | generated / 已生成 | - |
| JOB-719545 | MOD-TEST-705 | production / 生产 | - | - | - | MOD-TEST-705 | production / 生产 | generated / 已生成 | - |
| JOB-719546 | MOD-TEST-706 | production / 生产 | - | - | - | MOD-TEST-706 | production / 生产 | generated / 已生成 | - |
| JOB-719547 | MOD-TEST-708 | production / 生产 | - | - | - | MOD-TEST-708 | production / 生产 | generated / 已生成 | - |
| JOB-719548 | MOD-TEST-710 | production / 生产 | - | - | - | MOD-TEST-710 | production / 生产 | generated / 已生成 | - |
| JOB-719549 | MOD-TRADING-001 | production / 生产 | - | - | - | MOD-TRADING-001 | production / 生产 | generated / 已生成 | - |
| JOB-719550 | MOD-WORKSPACE_TELEMETRY | production / 生产 | - | - | - | MOD-WORKSPACE_TELEMETRY | production / 生产 | generated / 已生成 | - |
| JOB-719551 | MOD-XLR-003 | production / 生产 | - | - | - | MOD-XLR-003 | production / 生产 | generated / 已生成 | - |
| JOB-719552 | MOD-metric_count_drift | production / 生产 | - | - | - | MOD-metric_count_drift | production / 生产 | generated / 已生成 | - |
| JOB-719553 | MOD-migrate_sqlite_to_pg | production / 生产 | - | - | - | MOD-migrate_sqlite_to_pg | production / 生产 | generated / 已生成 | - |
| JOB-719554 | MOD-readme_version_sync | production / 生产 | - | - | - | MOD-readme_version_sync | production / 生产 | generated / 已生成 | - |
| JOB-35838 | PLACEHOLDER-MOD-GOV-SYNC-PANORAMA | production / 生产 | - | - | - | PLACEHOLDER-MOD-GOV-SYNC-PANORAMA | design / 设计 | planned | - |
| JOB-35636 | SH-DB-001 | production / 生产 | - | - | - | SH-DB-001 | design / 设计 | planned | - |
| JOB-719556 | SH-DB-002 | production / 生产 | - | - | - | SH-DB-002 | production / 生产 | stable | - |
| JOB-591654 | SH-GOV-001 | production / 生产 | - | - | - | SH-GOV-001 | design / 设计 | generated / 已生成 | - |
| JOB-719558 | SH-GOV-003 | production / 生产 | - | - | - | SH-GOV-003 | production / 生产 | generated / 已生成 | - |
| JOB-719559 | SH-GOV-004 | production / 生产 | - | - | - | SH-GOV-004 | production / 生产 | generated / 已生成 | - |
| JOB-719560 | SH-MAIN-001 | production / 生产 | - | - | - | SH-MAIN-001 | production / 生产 | stable | - |
| JOB-37268 | SYS-MASTER-001 | production / 生产 | - | - | - | SYS-MASTER-001 | design / 设计 | stable | - |
| JOB-718820 | aggregate.ohlc_bar / 聚合.OHLC K线 | production / 生产 | src/zephyr/data/aggregator.py | event_driven / 事件驱动 | production / 生产 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 market_data.ohlc_bar |
| JOB-718824 | check.risk_limits / 检查.风险限额 | production / 生产 | src/zephyr/risk/risk_checker.py | event_driven / 事件驱动 | production / 生产 | MOD-L04-001 | production / 生产 | generated / 已生成 | 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits |
| JOB-718822 | compute.momentum_20d / 计算.20日动量 | production / 生产 | src/zephyr/factor/momentum.py | event_driven / 事件驱动 | production / 生产 | MOD-L02-001 | production / 生产 | generated / 已生成 | 计算20日动量因子（收益率/相对强度），产出DS-004 factor.momentum_20d |
| JOB-718821 | compute.value_factor / 计算.价值因子 | production / 生产 | src/zephyr/factor/value_factor.py | event_driven / 事件驱动 | production / 生产 | MOD-L02-001 | production / 生产 | generated / 已生成 | 计算价值因子（PE/PB/股息率等），产出DS-003 factor.value_factor |
| JOB-718826 | execute.order / 执行.订单 | production / 生产 | src/zephyr/ex_core/executor.py | event_driven / 事件驱动 | production / 生产 | MOD-L06-001 | production / 生产 | generated / 已生成 | 执行订单（实盘/模拟），产出DS-008 fill.executed + DS-009 position.snapshot |
| JOB-718825 | generate.order / 生成.订单 | production / 生产 | src/zephyr/pf_core/order_generator.py | event_driven / 事件驱动 | production / 生产 | MOD-L05-001 | production / 生产 | generated / 已生成 | 根据信号+风险限额生成目标订单，产出DS-007 order.target |
| JOB-718819 | ingest.ifind_kline / 采集.iFind行情 | production / 生产 | src/zephyr/data/ingest_ifind.py | scheduled / 定时 | production / 生产 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-001 market_data.tick |
| JOB-718823 | synthesize.signal / 合成.信号 | production / 生产 | src/zephyr/signal_ashare/synthesizer.py | event_driven / 事件驱动 | production / 生产 | - | production / 生产 | generated / 已生成 | 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.composite |
