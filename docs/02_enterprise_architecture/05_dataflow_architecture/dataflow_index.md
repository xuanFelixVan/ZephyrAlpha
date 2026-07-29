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

> 生成时间: 2026-07-30T03:02:39
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
| Job | 764 | 5 | 769 |
| Edge | - | - | 28 |

### 设计态 / 运营态统计（design_maturity）

| 类型 | 运营态 (production) | 设计态 (design) | 合计 |
|------|---------------------|-----------------|------|
| Dataset | 14 | 0 | 14 |
| Job | 691 | 78 | 769 |

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

> 节点数: 14 datasets / 数据集, 769 jobs / 作业, 28 edges / 边

```mermaid
flowchart LR
    DS10959["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS10960["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS10958["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10957["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    DS10956["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10950["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10949["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10954["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10948["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10947["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10953["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10955["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10952["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10951["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB709378("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB709376("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB709374("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB709375("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB709377("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB709379("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB709380("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB709381("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB709382("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB709383("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB35951("[design]MOD-ARCH-BIZDB"):::jobDesign
    JOB709384("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB709385("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB709386("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
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
    JOB709397("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB709398("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB709399("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB671597("[design]MOD-DATA_ENG"):::jobDesign
    JOB709401("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB709402("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB709403("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB709404("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB709405("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB709406("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB709407("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB709408("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB712063("[design]MOD-EX-001"):::jobDesign
    JOB709409("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB709410("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB709411("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB35940("[design]MOD-FEEDBACK_LOOP"):::jobDesign
    JOB35578("[design]MOD-GATE_ENGINE"):::jobDesign
    JOB709414("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB709415("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB709416("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB709417("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB36856("[design]MOD-GOV-ALIGN-PANORAMAS"):::jobDesign
    JOB709418("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB709419("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB709420("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB139307("[design]MOD-GOV-HEARTBEAT"):::jobDesign
    JOB709421("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB709422("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
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
    JOB709424("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB709425("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB709426("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB709427("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB709428("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB709429("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB709430("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB709431("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB709432("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB709433("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB709434("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB709435("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB709436("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB709437("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB709438("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB709439("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB709440("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB709441("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB709442("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB709443("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB709444("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB709445("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB709446("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB709447("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB709448("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB709449("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB709450("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB709451("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB709452("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB709453("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB709454("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB709455("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB709456("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB709457("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB709458("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB709459("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB709460("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB709461("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB709462("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB709463("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB709464("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB709465("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB709466("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB709467("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB709468("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB709469("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB709470("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB709471("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB709472("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB709473("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB709474("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB709475("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB709476("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB709477("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB709478("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB709479("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB709480("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB709481("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB709482("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB709483("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB709484("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB709485("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB709486("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB709487("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB709488("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB709489("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB709490("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB709491("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB709492("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB709493("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB709494("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB709495("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB709496("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB709497("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB709498("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB709499("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB709500("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB709501("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB709502("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB709503("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB709504("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB709505("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB709506("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB709507("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB709508("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB709509("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB709510("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB709511("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB709512("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB709513("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB709514("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB709515("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB709516("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB709517("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB709518("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB709519("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB709520("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB709521("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB709522("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB709523("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB709524("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB709525("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB709526("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB709527("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB709528("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB709529("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB709530("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB709531("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB709532("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB709533("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB709534("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB709535("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB709536("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB709537("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB709538("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB709539("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB709540("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB709541("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB709542("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB709543("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB709544("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB709545("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB709546("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB709547("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB709548("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB709549("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB709550("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB709551("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB709552("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB709553("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB709554("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB709555("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB709556("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB709557("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB321362("[design]MOD-GOV_blueprint_status_transition_reconciler"):::jobDesign
    JOB321311("[design]MOD-GOV_cross_layer_contract_signature_reconciler"):::jobDesign
    JOB709558("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB709559("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB709560("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB36357("[design]MOD-INF-005"):::jobDesign
    JOB37139("[design]MOD-INF-009"):::jobDesign
    JOB35565("[design]MOD-INF-011"):::jobDesign
    JOB709564("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB709565("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB709566("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB35954("[design]MOD-INF-016"):::jobDesign
    JOB36274("[design]MOD-INF-017"):::jobDesign
    JOB709569("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB37172("[design]MOD-INF-019"):::jobDesign
    JOB36050("[design]MOD-INF-020"):::jobDesign
    JOB35903("[design]MOD-INF-021"):::jobDesign
    JOB36400("[design]MOD-INF-022"):::jobDesign
    JOB35522("[design]MOD-INF-023"):::jobDesign
    JOB37193("[design]MOD-INF-024"):::jobDesign
    JOB709576("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB709577("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB35574("[design]MOD-INF-027"):::jobDesign
    JOB36222("[design]MOD-INF-028"):::jobDesign
    JOB35930("[design]MOD-INF-029"):::jobDesign
    JOB37217("[design]MOD-INF-030"):::jobDesign
    JOB37220("[design]MOD-INF-031"):::jobDesign
    JOB36336("[design]MOD-INF-033"):::jobDesign
    JOB35554("[design]MOD-INF-034"):::jobDesign
    JOB709585("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB37237("[design]MOD-INF-036"):::jobDesign
    JOB35538("[design]MOD-INF-037"):::jobDesign
    JOB709588("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB36080("[design]MOD-INF-039"):::jobDesign
    JOB709590("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB709591("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB709592("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB709593("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB35939("[design]MOD-INFRA_OPS"):::jobDesign
    JOB709594("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB709595("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB709596("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB709597("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB36157("[design]MOD-L00-002"):::jobDesign
    JOB35520("[design]MOD-L00-003"):::jobDesign
    JOB61876("[design]MOD-L00-004"):::jobDesign
    JOB709599("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB709600("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB709601("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB551909("[design]MOD-L02-001"):::jobDesign
    JOB709603("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB709604("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB709605("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB709606("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB709607("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB709608("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB709609("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB709610("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB709611("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB709612("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB709613("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB709614("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB709615("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB709616("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB709617("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB709618("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB709619("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB709620("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB709621("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB709622("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB709623("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB709624("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB688297("[design]MOD-L04-001"):::jobDesign
    JOB709626("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB709627("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB709628("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB709629("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB709630("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB709631("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB709632("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB709633("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB709634("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB709635("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB36390("[design]MOD-MASTER-001"):::jobDesign
    JOB35517("[design]MOD-MASTER-002"):::jobDesign
    JOB36344("[design]MOD-MASTER-003"):::jobDesign
    JOB35528("[design]MOD-MASTER_BLUEPRINT"):::jobDesign
    JOB711884("[design]MOD-MKT-001"):::jobDesign
    JOB711954("[design]MOD-MKT-002"):::jobDesign
    JOB712012("[design]MOD-MKT-003"):::jobDesign
    JOB709637("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB709638("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB709639("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB36113("[design]MOD-PF_ALLOC"):::jobDesign
    JOB709640("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB709641("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB35898("[design]MOD-RESOURCE_OPTIMIZATION_ENGINE"):::jobDesign
    JOB709643("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB709644("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB709645("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB709646("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB709647("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB709648("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB709649("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB709650("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB709651("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB709652("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB709653("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB35600("[design]MOD-SIMULATION"):::jobDesign
    JOB119053("[design]MOD-SMOKE-TEST"):::jobDesign
    JOB709654("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB118981("[design]MOD-TEST"):::jobDesign
    JOB709656("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB709657("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB709658("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB709659("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB709660("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB709661("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB709662("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB709663("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB709664("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB709665("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB709666("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB709667("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB709668("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB709669("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB709670("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB709671("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB709672("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB709673("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB709674("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB709675("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB709676("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB709677("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB709678("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB709679("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB709680("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB709681("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB709682("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB709683("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB709684("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB709685("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB709686("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB709687("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB709688("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB709689("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB709690("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB709691("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB709692("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB709693("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB709694("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB709695("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB709696("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB709697("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB709698("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB709699("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB709700("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB709701("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB709702("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB709703("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB709704("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB709705("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB709706("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB709707("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB709708("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB709709("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB709710("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB709711("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB709712("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB709713("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB709714("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB709715("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB709716("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB709717("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB709718("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB709719("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB709720("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB709721("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB709722("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB709723("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB709724("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB709725("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB709726("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB709727("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB709728("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB709729("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB709730("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB709731("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB709732("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB709733("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB709734("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB709735("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB709736("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB709737("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB709738("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB709739("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB709740("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB709741("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB709742("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB709743("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB709744("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB709745("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB709746("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB709747("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB709748("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB709749("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB709750("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB709751("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB709752("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB709753("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB709754("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB709755("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB709756("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB709757("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB709758("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB709759("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB709760("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB709761("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB709762("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB709763("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB709764("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB709765("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB709766("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB709767("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB709768("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB709769("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB709770("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB709771("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB709772("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB709773("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB709774("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB709775("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB709776("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB709777("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB709778("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB709779("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB709780("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB709781("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB709782("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB709783("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB709784("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB709785("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB709786("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB709787("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB709788("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB709789("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB709790("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB709791("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB709792("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB709793("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB709794("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB709795("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB709796("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB709797("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB709798("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB709799("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB709800("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB709801("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB709802("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB709803("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB709804("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB709805("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB709806("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB709807("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB709808("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB709809("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB709810("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB709811("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB709812("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB709813("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB709814("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB709815("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB709816("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB709817("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB709818("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB709819("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB709820("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB709821("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB709822("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB709823("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB709824("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB709825("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB709826("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB709827("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB709828("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB709829("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB709830("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB709831("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB709832("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB709833("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB709834("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB709835("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB709836("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB709837("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB709838("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB709839("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB709840("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB709841("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB709842("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB709843("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB709844("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB709845("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB709846("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB709847("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB709848("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB709849("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB709850("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB709851("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB709852("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB709853("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB709854("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB709855("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB709856("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB709857("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB709858("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB709859("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB709860("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB709861("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB709862("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB709863("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB709864("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB709865("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB709866("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB709867("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB709868("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB709869("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB709870("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB709871("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB709872("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB709873("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB709874("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB709875("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB709876("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB709877("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB709878("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB709879("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB709880("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB709881("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB709882("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB709883("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB709884("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB709885("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB709886("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB709887("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB709888("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB709889("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB709890("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB709891("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB709892("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB709893("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB709894("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB709895("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB709896("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB709897("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB709898("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB709899("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB709900("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB709901("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB709902("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB709903("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB709904("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB709905("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB709906("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB709907("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB709908("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB709909("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB709910("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB709911("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB709912("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB709913("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB709914("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB709915("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB709916("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB709917("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB709918("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB709919("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB709920("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB709921("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB709922("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB709923("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB709924("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB709925("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB709926("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB709927("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB709928("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB709929("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB709930("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB709931("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB709932("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB709933("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB709934("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB709935("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB709936("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB709937("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB709938("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB709939("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB709940("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB709941("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB709942("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB709943("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB709944("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB709945("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB709946("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB709947("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB709948("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB709949("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB709950("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB709951("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB709952("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB709953("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB709954("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB709955("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB709956("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB709957("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB709958("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB709959("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB709960("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB709961("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB709962("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB709963("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB709964("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB709965("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB709966("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB709967("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB709968("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB709969("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB709970("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB709971("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB709972("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB709973("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB709974("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB709975("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB709976("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB709977("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB709978("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB709979("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB709980("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB709981("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB709982("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB709983("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB709984("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB709985("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB709986("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB709987("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB709988("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB709989("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB709990("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB709991("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB709992("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB709993("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB709994("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB709995("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB709996("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB709997("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB709998("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB709999("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB710000("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB710001("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB710002("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB710003("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB710004("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB710005("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB710006("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB710007("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB710008("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB710009("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB710010("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB710011("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB710012("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB710013("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB710014("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB710015("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB710016("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB710017("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB710018("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB710019("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB710020("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB710021("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB710022("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB710023("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB710024("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB710025("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB710026("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB710027("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB710028("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB710029("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB710030("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB710031("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB710032("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB710033("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB710034("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB710035("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB710036("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB710037("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB710038("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB710039("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB710040("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB710041("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB710042("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB710043("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB710044("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB710045("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB710046("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB710047("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB710048("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB710049("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB710050("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB710051("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB710052("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB710053("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB710054("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB710055("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB710056("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB710057("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB710058("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB710059("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB710060("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB710061("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB710062("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB710063("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB710064("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB710065("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB710066("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB710067("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB710068("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB710069("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB710070("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB710071("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB710072("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB710073("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB710074("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB710075("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB710076("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB710077("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB710078("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB710079("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB710080("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB710081("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB710082("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB710083("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB710084("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB710085("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB710086("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB710087("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB710088("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB710089("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB710090("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB710091("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB710092("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB710093("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB35838("[design]PLACEHOLDER-MOD-GOV-SYNC-PANORAMA"):::jobDesign
    JOB35636("[design]SH-DB-001"):::jobDesign
    JOB710095("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB591654("[design]SH-GOV-001"):::jobDesign
    JOB710097("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB710098("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB710099("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB37268("[design]SYS-MASTER-001"):::jobDesign
    JOB709367("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB709371("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB709369("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB709368("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB709373("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB709372("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB709366("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB709370("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB709366 -->|produces / 产出| DS10947
    JOB709367 -->|produces / 产出| DS10948
    JOB709368 -->|produces / 产出| DS10949
    JOB709369 -->|produces / 产出| DS10950
    JOB709370 -->|produces / 产出| DS10951
    JOB709371 -->|produces / 产出| DS10952
    JOB709372 -->|produces / 产出| DS10953
    JOB709373 -->|produces / 产出| DS10954
    JOB709373 -->|produces / 产出| DS10955
    JOB709378 -->|produces / 产出| DS10956
    JOB709374 -->|produces / 产出| DS10957
    JOB709375 -->|produces / 产出| DS10958
    JOB709376 -->|produces / 产出| DS10959
    JOB709377 -->|produces / 产出| DS10960
    DS10947 -->|consumed by / 被消费于| JOB709367
    DS10947 -->|consumed by / 被消费于| JOB709374
    DS10948 -->|consumed by / 被消费于| JOB709368
    DS10948 -->|consumed by / 被消费于| JOB709369
    DS10949 -->|consumed by / 被消费于| JOB709370
    DS10950 -->|consumed by / 被消费于| JOB709370
    DS10951 -->|consumed by / 被消费于| JOB709371
    DS10951 -->|consumed by / 被消费于| JOB709372
    DS10952 -->|consumed by / 被消费于| JOB709372
    DS10953 -->|consumed by / 被消费于| JOB709373
    DS10957 -->|consumed by / 被消费于| JOB709375
    DS10958 -->|consumed by / 被消费于| JOB709376
    DS10959 -->|consumed by / 被消费于| JOB709377
    DS10960 -->|consumed by / 被消费于| JOB709378

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

### 运营态全景图（仅 design_maturity=production）

> 仅展示已实现稳定运行的节点（运营态：14 datasets / 数据集, 691 jobs / 作业, 28 edges / 边）。

```mermaid
flowchart LR
    DS10959["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS10960["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS10958["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10957["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    DS10956["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10950["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10949["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10954["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10948["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10947["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10953["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10955["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10952["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10951["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB709378("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB709376("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB709374("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB709375("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB709377("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB709379("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB709380("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB709381("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB709382("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB709383("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB709384("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB709385("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB709386("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
    JOB709397("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB709398("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB709399("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB709401("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB709402("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB709403("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB709404("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB709405("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB709406("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB709407("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB709408("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB709409("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB709410("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB709411("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB709414("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB709415("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB709416("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB709417("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB709418("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB709419("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB709420("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB709421("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB709422("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
    JOB709424("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB709425("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB709426("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB709427("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB709428("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB709429("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB709430("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB709431("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB709432("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB709433("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB709434("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB709435("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB709436("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB709437("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB709438("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB709439("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB709440("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB709441("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB709442("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB709443("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB709444("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB709445("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB709446("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB709447("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB709448("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB709449("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB709450("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB709451("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB709452("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB709453("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB709454("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB709455("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB709456("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB709457("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB709458("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB709459("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB709460("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB709461("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB709462("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB709463("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB709464("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB709465("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB709466("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB709467("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB709468("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB709469("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB709470("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB709471("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB709472("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB709473("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB709474("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB709475("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB709476("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB709477("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB709478("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB709479("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB709480("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB709481("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB709482("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB709483("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB709484("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB709485("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB709486("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB709487("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB709488("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB709489("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB709490("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB709491("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB709492("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB709493("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB709494("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB709495("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB709496("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB709497("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB709498("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB709499("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB709500("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB709501("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB709502("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB709503("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB709504("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB709505("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB709506("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB709507("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB709508("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB709509("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB709510("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB709511("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB709512("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB709513("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB709514("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB709515("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB709516("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB709517("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB709518("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB709519("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB709520("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB709521("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB709522("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB709523("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB709524("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB709525("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB709526("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB709527("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB709528("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB709529("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB709530("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB709531("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB709532("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB709533("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB709534("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB709535("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB709536("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB709537("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB709538("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB709539("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB709540("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB709541("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB709542("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB709543("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB709544("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB709545("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB709546("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB709547("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB709548("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB709549("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB709550("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB709551("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB709552("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB709553("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB709554("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB709555("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB709556("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB709557("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB709558("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB709559("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB709560("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB709564("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB709565("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB709566("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB709569("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB709576("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB709577("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB709585("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB709588("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB709590("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB709591("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB709592("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB709593("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB709594("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB709595("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB709596("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB709597("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB709599("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB709600("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB709601("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB709603("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB709604("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB709605("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB709606("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB709607("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB709608("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB709609("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB709610("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB709611("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB709612("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB709613("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB709614("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB709615("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB709616("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB709617("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB709618("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB709619("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB709620("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB709621("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB709622("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB709623("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB709624("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB709626("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB709627("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB709628("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB709629("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB709630("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB709631("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB709632("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB709633("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB709634("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB709635("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB709637("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB709638("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB709639("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB709640("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB709641("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB709643("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB709644("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB709645("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB709646("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB709647("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB709648("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB709649("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB709650("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB709651("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB709652("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB709653("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB709654("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB709656("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB709657("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB709658("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB709659("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB709660("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB709661("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB709662("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB709663("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB709664("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB709665("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB709666("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB709667("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB709668("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB709669("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB709670("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB709671("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB709672("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB709673("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB709674("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB709675("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB709676("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB709677("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB709678("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB709679("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB709680("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB709681("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB709682("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB709683("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB709684("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB709685("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB709686("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB709687("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB709688("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB709689("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB709690("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB709691("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB709692("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB709693("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB709694("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB709695("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB709696("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB709697("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB709698("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB709699("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB709700("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB709701("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB709702("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB709703("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB709704("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB709705("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB709706("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB709707("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB709708("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB709709("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB709710("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB709711("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB709712("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB709713("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB709714("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB709715("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB709716("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB709717("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB709718("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB709719("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB709720("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB709721("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB709722("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB709723("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB709724("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB709725("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB709726("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB709727("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB709728("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB709729("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB709730("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB709731("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB709732("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB709733("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB709734("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB709735("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB709736("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB709737("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB709738("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB709739("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB709740("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB709741("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB709742("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB709743("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB709744("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB709745("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB709746("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB709747("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB709748("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB709749("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB709750("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB709751("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB709752("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB709753("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB709754("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB709755("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB709756("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB709757("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB709758("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB709759("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB709760("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB709761("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB709762("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB709763("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB709764("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB709765("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB709766("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB709767("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB709768("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB709769("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB709770("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB709771("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB709772("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB709773("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB709774("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB709775("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB709776("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB709777("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB709778("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB709779("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB709780("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB709781("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB709782("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB709783("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB709784("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB709785("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB709786("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB709787("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB709788("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB709789("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB709790("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB709791("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB709792("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB709793("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB709794("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB709795("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB709796("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB709797("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB709798("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB709799("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB709800("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB709801("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB709802("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB709803("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB709804("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB709805("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB709806("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB709807("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB709808("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB709809("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB709810("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB709811("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB709812("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB709813("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB709814("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB709815("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB709816("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB709817("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB709818("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB709819("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB709820("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB709821("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB709822("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB709823("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB709824("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB709825("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB709826("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB709827("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB709828("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB709829("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB709830("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB709831("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB709832("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB709833("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB709834("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB709835("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB709836("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB709837("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB709838("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB709839("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB709840("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB709841("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB709842("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB709843("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB709844("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB709845("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB709846("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB709847("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB709848("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB709849("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB709850("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB709851("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB709852("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB709853("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB709854("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB709855("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB709856("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB709857("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB709858("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB709859("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB709860("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB709861("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB709862("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB709863("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB709864("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB709865("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB709866("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB709867("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB709868("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB709869("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB709870("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB709871("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB709872("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB709873("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB709874("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB709875("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB709876("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB709877("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB709878("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB709879("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB709880("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB709881("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB709882("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB709883("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB709884("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB709885("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB709886("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB709887("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB709888("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB709889("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB709890("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB709891("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB709892("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB709893("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB709894("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB709895("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB709896("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB709897("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB709898("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB709899("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB709900("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB709901("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB709902("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB709903("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB709904("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB709905("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB709906("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB709907("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB709908("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB709909("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB709910("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB709911("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB709912("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB709913("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB709914("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB709915("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB709916("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB709917("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB709918("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB709919("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB709920("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB709921("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB709922("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB709923("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB709924("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB709925("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB709926("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB709927("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB709928("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB709929("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB709930("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB709931("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB709932("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB709933("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB709934("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB709935("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB709936("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB709937("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB709938("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB709939("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB709940("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB709941("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB709942("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB709943("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB709944("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB709945("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB709946("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB709947("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB709948("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB709949("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB709950("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB709951("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB709952("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB709953("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB709954("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB709955("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB709956("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB709957("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB709958("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB709959("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB709960("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB709961("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB709962("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB709963("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB709964("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB709965("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB709966("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB709967("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB709968("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB709969("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB709970("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB709971("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB709972("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB709973("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB709974("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB709975("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB709976("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB709977("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB709978("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB709979("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB709980("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB709981("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB709982("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB709983("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB709984("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB709985("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB709986("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB709987("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB709988("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB709989("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB709990("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB709991("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB709992("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB709993("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB709994("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB709995("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB709996("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB709997("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB709998("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB709999("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB710000("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB710001("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB710002("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB710003("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB710004("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB710005("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB710006("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB710007("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB710008("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB710009("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB710010("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB710011("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB710012("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB710013("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB710014("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB710015("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB710016("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB710017("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB710018("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB710019("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB710020("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB710021("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB710022("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB710023("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB710024("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB710025("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB710026("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB710027("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB710028("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB710029("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB710030("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB710031("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB710032("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB710033("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB710034("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB710035("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB710036("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB710037("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB710038("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB710039("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB710040("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB710041("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB710042("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB710043("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB710044("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB710045("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB710046("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB710047("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB710048("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB710049("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB710050("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB710051("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB710052("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB710053("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB710054("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB710055("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB710056("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB710057("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB710058("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB710059("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB710060("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB710061("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB710062("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB710063("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB710064("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB710065("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB710066("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB710067("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB710068("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB710069("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB710070("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB710071("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB710072("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB710073("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB710074("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB710075("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB710076("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB710077("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB710078("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB710079("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB710080("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB710081("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB710082("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB710083("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB710084("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB710085("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB710086("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB710087("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB710088("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB710089("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB710090("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB710091("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB710092("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB710093("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB710095("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB710097("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB710098("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB710099("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB709367("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB709371("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB709369("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB709368("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB709373("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB709372("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB709366("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB709370("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB709366 -->|produces / 产出| DS10947
    JOB709367 -->|produces / 产出| DS10948
    JOB709368 -->|produces / 产出| DS10949
    JOB709369 -->|produces / 产出| DS10950
    JOB709370 -->|produces / 产出| DS10951
    JOB709371 -->|produces / 产出| DS10952
    JOB709372 -->|produces / 产出| DS10953
    JOB709373 -->|produces / 产出| DS10954
    JOB709373 -->|produces / 产出| DS10955
    JOB709378 -->|produces / 产出| DS10956
    JOB709374 -->|produces / 产出| DS10957
    JOB709375 -->|produces / 产出| DS10958
    JOB709376 -->|produces / 产出| DS10959
    JOB709377 -->|produces / 产出| DS10960
    DS10947 -->|consumed by / 被消费于| JOB709367
    DS10947 -->|consumed by / 被消费于| JOB709374
    DS10948 -->|consumed by / 被消费于| JOB709368
    DS10948 -->|consumed by / 被消费于| JOB709369
    DS10949 -->|consumed by / 被消费于| JOB709370
    DS10950 -->|consumed by / 被消费于| JOB709370
    DS10951 -->|consumed by / 被消费于| JOB709371
    DS10951 -->|consumed by / 被消费于| JOB709372
    DS10952 -->|consumed by / 被消费于| JOB709372
    DS10953 -->|consumed by / 被消费于| JOB709373
    DS10957 -->|consumed by / 被消费于| JOB709375
    DS10958 -->|consumed by / 被消费于| JOB709376
    DS10959 -->|consumed by / 被消费于| JOB709377
    DS10960 -->|consumed by / 被消费于| JOB709378

    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100
    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
```

### 生产数据流图（scope=production）

> 节点数: 10 datasets / 数据集, 764 jobs / 作业, 18 edges / 边

```mermaid
flowchart LR
    DS10956["[production]backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测结果（nav_series/sharpe/max_drawdown/tra…"]:::dsProd
    DS10950["[production]factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 20日动量因子信号（factor_id/symbol/as_of_date/r…"]:::dsProd
    DS10949["[production]factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]<br/>蓝图: MOD-L02-001<br/>功能: 价值因子信号（factor_id/symbol/as_of_date/raw_…"]:::dsProd
    DS10954["[production]fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 成交回报（symbol/quantity/price/commission/t…"]:::dsProd
    DS10948["[production]market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 der…"]:::dsProd
    DS10947["[production]market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]<br/>蓝图: MOD-MKT_DATA<br/>功能: 标准化Tick行情（symbol/timestamp/OHLCV/qualit…"]:::dsProd
    DS10953["[production]order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]<br/>蓝图: MOD-L05-001<br/>功能: 目标订单（symbol/side/quantity/price/order_t…"]:::dsProd
    DS10955["[production]position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]<br/>蓝图: MOD-L06-001<br/>功能: 持仓快照（symbol/quantity/avg_cost/market_va…"]:::dsProd
    DS10952["[production]risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]<br/>蓝图: MOD-L04-001<br/>功能: 风险限额（max_position/max_drawdown/exposure…"]:::dsProd
    DS10951["[production]signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]<br/>功能: 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 Synth…"]:::dsProd
    JOB709379("[production]CFG-rule-enforcement-registry<br/>蓝图: CFG-rule-enforcement-registry"):::jobProd
    JOB709380("[production]CFG-rule-registry-collection<br/>蓝图: CFG-rule-registry-collection"):::jobProd
    JOB709381("[production]CFG-scripts-registry<br/>蓝图: CFG-scripts-registry"):::jobProd
    JOB709382("[production]CFG-test-suite-registry<br/>蓝图: CFG-test-suite-registry"):::jobProd
    JOB709383("[production]MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA"):::jobProd
    JOB35951("[design]MOD-ARCH-BIZDB"):::jobDesign
    JOB709384("[production]MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE"):::jobProd
    JOB709385("[production]MOD-BT-001<br/>蓝图: MOD-BT-001"):::jobProd
    JOB709386("[production]MOD-BT-017<br/>蓝图: MOD-BT-017"):::jobProd
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
    JOB709397("[production]MOD-CROSS_ASSET<br/>蓝图: MOD-CROSS_ASSET"):::jobProd
    JOB709398("[production]MOD-D5_ARCH_TOOLS<br/>蓝图: MOD-D5_ARCH_TOOLS"):::jobProd
    JOB709399("[production]MOD-DATABASE<br/>蓝图: MOD-DATABASE"):::jobProd
    JOB671597("[design]MOD-DATA_ENG"):::jobDesign
    JOB709401("[production]MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV"):::jobProd
    JOB709402("[production]MOD-DATA_GOV-001<br/>蓝图: MOD-DATA_GOV-001"):::jobProd
    JOB709403("[production]MOD-DATA_GOV-002<br/>蓝图: MOD-DATA_GOV-002"):::jobProd
    JOB709404("[production]MOD-DATA_GOV-003<br/>蓝图: MOD-DATA_GOV-003"):::jobProd
    JOB709405("[production]MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC"):::jobProd
    JOB709406("[production]MOD-DIGITAL_TWIN<br/>蓝图: MOD-DIGITAL_TWIN"):::jobProd
    JOB709407("[production]MOD-D_GOV_SCRIPTS<br/>蓝图: MOD-D_GOV_SCRIPTS"):::jobProd
    JOB709408("[production]MOD-E2E-001<br/>蓝图: MOD-E2E-001"):::jobProd
    JOB712063("[design]MOD-EX-001"):::jobDesign
    JOB709409("[production]MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM"):::jobProd
    JOB709410("[production]MOD-EX_SOR<br/>蓝图: MOD-EX_SOR"):::jobProd
    JOB709411("[production]MOD-FEEDBACK-014<br/>蓝图: MOD-FEEDBACK-014"):::jobProd
    JOB35940("[design]MOD-FEEDBACK_LOOP"):::jobDesign
    JOB35578("[design]MOD-GATE_ENGINE"):::jobDesign
    JOB709414("[production]MOD-GOV-008<br/>蓝图: MOD-GOV-008"):::jobProd
    JOB709415("[production]MOD-GOV-019<br/>蓝图: MOD-GOV-019"):::jobProd
    JOB709416("[production]MOD-GOV-029<br/>蓝图: MOD-GOV-029"):::jobProd
    JOB709417("[production]MOD-GOV-041<br/>蓝图: MOD-GOV-041"):::jobProd
    JOB36856("[design]MOD-GOV-ALIGN-PANORAMAS"):::jobDesign
    JOB709418("[production]MOD-GOV-AUDIT<br/>蓝图: MOD-GOV-AUDIT"):::jobProd
    JOB709419("[production]MOD-GOV-CG<br/>蓝图: MOD-GOV-CG"):::jobProd
    JOB709420("[production]MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS"):::jobProd
    JOB139307("[design]MOD-GOV-HEARTBEAT"):::jobDesign
    JOB709421("[production]MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS"):::jobProd
    JOB709422("[production]MOD-GOV-backfill_checker<br/>蓝图: MOD-GOV-backfill_checker"):::jobProd
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
    JOB709424("[production]MOD-GOV_AGENT_RBAC<br/>蓝图: MOD-GOV_AGENT_RBAC"):::jobProd
    JOB709425("[production]MOD-GOV_ALIGN_PANORAMAS<br/>蓝图: MOD-GOV_ALIGN_PANORAMAS"):::jobProd
    JOB709426("[production]MOD-GOV_ANALYZE_CHANGE_IMPACT<br/>蓝图: MOD-GOV_ANALYZE_CHANGE_IMPACT"):::jobProd
    JOB709427("[production]MOD-GOV_ANALYZE_ORPHAN_CONSUMERS<br/>蓝图: MOD-GOV_ANALYZE_ORPHAN_CONSUMERS"):::jobProd
    JOB709428("[production]MOD-GOV_ARCH_REFERENCE_GATE<br/>蓝图: MOD-GOV_ARCH_REFERENCE_GATE"):::jobProd
    JOB709429("[production]MOD-GOV_ASYNC_RUNTIME<br/>蓝图: MOD-GOV_ASYNC_RUNTIME"):::jobProd
    JOB709430("[production]MOD-GOV_AUDIT<br/>蓝图: MOD-GOV_AUDIT"):::jobProd
    JOB709431("[production]MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE<br/>蓝图: MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE"):::jobProd
    JOB709432("[production]MOD-GOV_AUDIT_TRAIL<br/>蓝图: MOD-GOV_AUDIT_TRAIL"):::jobProd
    JOB709433("[production]MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY<br/>蓝图: MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY"):::jobProd
    JOB709434("[production]MOD-GOV_BARE_GETENV_GATE<br/>蓝图: MOD-GOV_BARE_GETENV_GATE"):::jobProd
    JOB709435("[production]MOD-GOV_BARE_SQL_GATE<br/>蓝图: MOD-GOV_BARE_SQL_GATE"):::jobProd
    JOB709436("[production]MOD-GOV_BATCHED_AUTO_COMMITTER<br/>蓝图: MOD-GOV_BATCHED_AUTO_COMMITTER"):::jobProd
    JOB709437("[production]MOD-GOV_BEHAVIORAL_ADMISSION<br/>蓝图: MOD-GOV_BEHAVIORAL_ADMISSION"):::jobProd
    JOB709438("[production]MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE"):::jobProd
    JOB709439("[production]MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER<br/>蓝图: MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER"):::jobProd
    JOB709440("[production]MOD-GOV_CAPABILITY_OVERLAP_GATE<br/>蓝图: MOD-GOV_CAPABILITY_OVERLAP_GATE"):::jobProd
    JOB709441("[production]MOD-GOV_CHECK_ANY_ABUSE<br/>蓝图: MOD-GOV_CHECK_ANY_ABUSE"):::jobProd
    JOB709442("[production]MOD-GOV_CHECK_CANONICAL_YAML_DRIFT<br/>蓝图: MOD-GOV_CHECK_CANONICAL_YAML_DRIFT"):::jobProd
    JOB709443("[production]MOD-GOV_CHECK_RULE_COVERAGE<br/>蓝图: MOD-GOV_CHECK_RULE_COVERAGE"):::jobProd
    JOB709444("[production]MOD-GOV_CHECK_VOCAB_HARDCODE<br/>蓝图: MOD-GOV_CHECK_VOCAB_HARDCODE"):::jobProd
    JOB709445("[production]MOD-GOV_CH_BATCH_SIZE_GATE<br/>蓝图: MOD-GOV_CH_BATCH_SIZE_GATE"):::jobProd
    JOB709446("[production]MOD-GOV_CH_VERSION_COL_GATE<br/>蓝图: MOD-GOV_CH_VERSION_COL_GATE"):::jobProd
    JOB709447("[production]MOD-GOV_CLAIM_REQUIRED_GATE<br/>蓝图: MOD-GOV_CLAIM_REQUIRED_GATE"):::jobProd
    JOB709448("[production]MOD-GOV_CODE_QUALITY_DOMAIN<br/>蓝图: MOD-GOV_CODE_QUALITY_DOMAIN"):::jobProd
    JOB709449("[production]MOD-GOV_COMMIT_GATES<br/>蓝图: MOD-GOV_COMMIT_GATES"):::jobProd
    JOB709450("[production]MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR<br/>蓝图: MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR"):::jobProd
    JOB709451("[production]MOD-GOV_COMMIT_GATE_REGISTRY<br/>蓝图: MOD-GOV_COMMIT_GATE_REGISTRY"):::jobProd
    JOB709452("[production]MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON"):::jobProd
    JOB709453("[production]MOD-GOV_CONCURRENT_WRITE_TEST<br/>蓝图: MOD-GOV_CONCURRENT_WRITE_TEST"):::jobProd
    JOB709454("[production]MOD-GOV_CREATE_GUARD<br/>蓝图: MOD-GOV_CREATE_GUARD"):::jobProd
    JOB709455("[production]MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER<br/>蓝图: MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER"):::jobProd
    JOB709456("[production]MOD-GOV_DANGLING_REFERENCE_GATE<br/>蓝图: MOD-GOV_DANGLING_REFERENCE_GATE"):::jobProd
    JOB709457("[production]MOD-GOV_DATABASE_SERVICE<br/>蓝图: MOD-GOV_DATABASE_SERVICE"):::jobProd
    JOB709458("[production]MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM"):::jobProd
    JOB709459("[production]MOD-GOV_DEEPSEEK_API<br/>蓝图: MOD-GOV_DEEPSEEK_API"):::jobProd
    JOB709460("[production]MOD-GOV_DEFERRED_EDGES<br/>蓝图: MOD-GOV_DEFERRED_EDGES"):::jobProd
    JOB709461("[production]MOD-GOV_DEFERRED_REG<br/>蓝图: MOD-GOV_DEFERRED_REG"):::jobProd
    JOB709462("[production]MOD-GOV_DEMO_EE_PIPELINE<br/>蓝图: MOD-GOV_DEMO_EE_PIPELINE"):::jobProd
    JOB709463("[production]MOD-GOV_DETECT_CAUSAL_CONFLICTS<br/>蓝图: MOD-GOV_DETECT_CAUSAL_CONFLICTS"):::jobProd
    JOB709464("[production]MOD-GOV_DIFF_HELPERS<br/>蓝图: MOD-GOV_DIFF_HELPERS"):::jobProd
    JOB709465("[production]MOD-GOV_DM200912_QUERY_DOMAINS<br/>蓝图: MOD-GOV_DM200912_QUERY_DOMAINS"):::jobProd
    JOB709466("[production]MOD-GOV_DM200916_WRITE_DIRECT<br/>蓝图: MOD-GOV_DM200916_WRITE_DIRECT"):::jobProd
    JOB709467("[production]MOD-GOV_DOC_REF_BROKEN_GATE<br/>蓝图: MOD-GOV_DOC_REF_BROKEN_GATE"):::jobProd
    JOB709468("[production]MOD-GOV_DOMAIN_FK_GATE<br/>蓝图: MOD-GOV_DOMAIN_FK_GATE"):::jobProd
    JOB709469("[production]MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ"):::jobProd
    JOB709470("[production]MOD-GOV_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_EMERGENCY_COMMIT"):::jobProd
    JOB709471("[production]MOD-GOV_EMPTY_HANDLER_GATE<br/>蓝图: MOD-GOV_EMPTY_HANDLER_GATE"):::jobProd
    JOB709472("[production]MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT"):::jobProd
    JOB709473("[production]MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE"):::jobProd
    JOB709474("[production]MOD-GOV_ENFORCEMENT_WORKTREE_POOL<br/>蓝图: MOD-GOV_ENFORCEMENT_WORKTREE_POOL"):::jobProd
    JOB709475("[production]MOD-GOV_ENFORCEMENT_worktree_lifecycle<br/>蓝图: MOD-GOV_ENFORCEMENT_worktree_lifecycle"):::jobProd
    JOB709476("[production]MOD-GOV_ERROR_PATTERN_CONSUMER<br/>蓝图: MOD-GOV_ERROR_PATTERN_CONSUMER"):::jobProd
    JOB709477("[production]MOD-GOV_ERROR_PATTERN_LIBRARY<br/>蓝图: MOD-GOV_ERROR_PATTERN_LIBRARY"):::jobProd
    JOB709478("[production]MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE<br/>蓝图: MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE"):::jobProd
    JOB709479("[production]MOD-GOV_F3_AUTO_INTEGRATION<br/>蓝图: MOD-GOV_F3_AUTO_INTEGRATION"):::jobProd
    JOB709480("[production]MOD-GOV_F3_EXTREME<br/>蓝图: MOD-GOV_F3_EXTREME"):::jobProd
    JOB709481("[production]MOD-GOV_FILE_COPY_GATE<br/>蓝图: MOD-GOV_FILE_COPY_GATE"):::jobProd
    JOB709482("[production]MOD-GOV_FUNCTION_DUP_GATE<br/>蓝图: MOD-GOV_FUNCTION_DUP_GATE"):::jobProd
    JOB709483("[production]MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE"):::jobProd
    JOB709484("[production]MOD-GOV_GENERATE_ASSET_CATALOG<br/>蓝图: MOD-GOV_GENERATE_ASSET_CATALOG"):::jobProd
    JOB709485("[production]MOD-GOV_GENERATE_CAPABILITY_HEATMAP<br/>蓝图: MOD-GOV_GENERATE_CAPABILITY_HEATMAP"):::jobProd
    JOB709486("[production]MOD-GOV_GENERATE_CAPACITY_REPORT<br/>蓝图: MOD-GOV_GENERATE_CAPACITY_REPORT"):::jobProd
    JOB709487("[production]MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS<br/>蓝图: MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS"):::jobProd
    JOB709488("[production]MOD-GOV_GENERATE_CONTRACT_CATALOG<br/>蓝图: MOD-GOV_GENERATE_CONTRACT_CATALOG"):::jobProd
    JOB709489("[production]MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX<br/>蓝图: MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX"):::jobProd
    JOB709490("[production]MOD-GOV_GENERATE_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_GENERATE_DATAFLOW_DIAGRAM"):::jobProd
    JOB709491("[production]MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION<br/>蓝图: MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION"):::jobProd
    JOB709492("[production]MOD-GOV_GENERATE_DOMAIN_DOC<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_DOC"):::jobProd
    JOB709493("[production]MOD-GOV_GENERATE_DOMAIN_INDEX<br/>蓝图: MOD-GOV_GENERATE_DOMAIN_INDEX"):::jobProd
    JOB709494("[production]MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY<br/>蓝图: MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY"):::jobProd
    JOB709495("[production]MOD-GOV_GENERATE_NAVIGATION_INDEX<br/>蓝图: MOD-GOV_GENERATE_NAVIGATION_INDEX"):::jobProd
    JOB709496("[production]MOD-GOV_GENERATE_PATH_TREE<br/>蓝图: MOD-GOV_GENERATE_PATH_TREE"):::jobProd
    JOB709497("[production]MOD-GOV_GIT_HELPERS<br/>蓝图: MOD-GOV_GIT_HELPERS"):::jobProd
    JOB709498("[production]MOD-GOV_GIT_PERFORMANCE_MONITOR<br/>蓝图: MOD-GOV_GIT_PERFORMANCE_MONITOR"):::jobProd
    JOB709499("[production]MOD-GOV_GOD_CLASS_GATE<br/>蓝图: MOD-GOV_GOD_CLASS_GATE"):::jobProd
    JOB709500("[production]MOD-GOV_GROUP_ORPHAN_MODULES<br/>蓝图: MOD-GOV_GROUP_ORPHAN_MODULES"):::jobProd
    JOB709501("[production]MOD-GOV_GUC_TRIGGER_FIX<br/>蓝图: MOD-GOV_GUC_TRIGGER_FIX"):::jobProd
    JOB709502("[production]MOD-GOV_HARDCODED_URL_GATE<br/>蓝图: MOD-GOV_HARDCODED_URL_GATE"):::jobProd
    JOB709503("[production]MOD-GOV_HEALTH_SCORE_CALCULATOR<br/>蓝图: MOD-GOV_HEALTH_SCORE_CALCULATOR"):::jobProd
    JOB709504("[production]MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE"):::jobProd
    JOB709505("[production]MOD-GOV_HEARTBEAT_DAEMON<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON"):::jobProd
    JOB709506("[production]MOD-GOV_HEARTBEAT_DAEMON_TEST<br/>蓝图: MOD-GOV_HEARTBEAT_DAEMON_TEST"):::jobProd
    JOB709507("[production]MOD-GOV_HELD_OVERLAP_GATE<br/>蓝图: MOD-GOV_HELD_OVERLAP_GATE"):::jobProd
    JOB709508("[production]MOD-GOV_HIGH_COMPLEXITY_GATE<br/>蓝图: MOD-GOV_HIGH_COMPLEXITY_GATE"):::jobProd
    JOB709509("[production]MOD-GOV_ID_UNIQUENESS_GATE<br/>蓝图: MOD-GOV_ID_UNIQUENESS_GATE"):::jobProd
    JOB709510("[production]MOD-GOV_IMPORT_DIRECTION_GATE<br/>蓝图: MOD-GOV_IMPORT_DIRECTION_GATE"):::jobProd
    JOB709511("[production]MOD-GOV_LONG_PARAM_LIST_GATE<br/>蓝图: MOD-GOV_LONG_PARAM_LIST_GATE"):::jobProd
    JOB709512("[production]MOD-GOV_MIGRATE_METADATA<br/>蓝图: MOD-GOV_MIGRATE_METADATA"):::jobProd
    JOB709513("[production]MOD-GOV_MODULE_ID_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_MODULE_ID_CONSISTENCY_GATE"):::jobProd
    JOB709514("[production]MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE<br/>蓝图: MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE"):::jobProd
    JOB709515("[production]MOD-GOV_ORPHAN_MODULE_GATE<br/>蓝图: MOD-GOV_ORPHAN_MODULE_GATE"):::jobProd
    JOB709516("[production]MOD-GOV_PANORAMA_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_PANORAMA_ALIGNMENT_GATE"):::jobProd
    JOB709517("[production]MOD-GOV_PERF_DEPGRAPH_BASELINE<br/>蓝图: MOD-GOV_PERF_DEPGRAPH_BASELINE"):::jobProd
    JOB709518("[production]MOD-GOV_PERM_TRIGGER_GATE<br/>蓝图: MOD-GOV_PERM_TRIGGER_GATE"):::jobProd
    JOB709519("[production]MOD-GOV_PRE_WRITE_GATE<br/>蓝图: MOD-GOV_PRE_WRITE_GATE"):::jobProd
    JOB709520("[production]MOD-GOV_R5_DIGIT_SUFFIX_GATE<br/>蓝图: MOD-GOV_R5_DIGIT_SUFFIX_GATE"):::jobProd
    JOB709521("[production]MOD-GOV_RECONCILE_RUNNER<br/>蓝图: MOD-GOV_RECONCILE_RUNNER"):::jobProd
    JOB709522("[production]MOD-GOV_RECONCILE_WORKER<br/>蓝图: MOD-GOV_RECONCILE_WORKER"):::jobProd
    JOB709523("[production]MOD-GOV_RECONCILIATION_REGISTRY<br/>蓝图: MOD-GOV_RECONCILIATION_REGISTRY"):::jobProd
    JOB709524("[production]MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE<br/>蓝图: MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE"):::jobProd
    JOB709525("[production]MOD-GOV_REPAIR<br/>蓝图: MOD-GOV_REPAIR"):::jobProd
    JOB709526("[production]MOD-GOV_RESILIENCE_GOVERNANCE<br/>蓝图: MOD-GOV_RESILIENCE_GOVERNANCE"):::jobProd
    JOB709527("[production]MOD-GOV_ROLLBACK<br/>蓝图: MOD-GOV_ROLLBACK"):::jobProd
    JOB709528("[production]MOD-GOV_RULE_DOMAIN<br/>蓝图: MOD-GOV_RULE_DOMAIN"):::jobProd
    JOB709529("[production]MOD-GOV_RULE_EXECUTION_PAIRING_GATE<br/>蓝图: MOD-GOV_RULE_EXECUTION_PAIRING_GATE"):::jobProd
    JOB709530("[production]MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE<br/>蓝图: MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE"):::jobProd
    JOB709531("[production]MOD-GOV_RULE_PATTERNS<br/>蓝图: MOD-GOV_RULE_PATTERNS"):::jobProd
    JOB709532("[production]MOD-GOV_RULING_REFERENCE_GATE<br/>蓝图: MOD-GOV_RULING_REFERENCE_GATE"):::jobProd
    JOB709533("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT"):::jobProd
    JOB709534("[production]MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER<br/>蓝图: MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER"):::jobProd
    JOB709535("[production]MOD-GOV_SCAN_CONSUMERS_ACCURACY<br/>蓝图: MOD-GOV_SCAN_CONSUMERS_ACCURACY"):::jobProd
    JOB709536("[production]MOD-GOV_SCAN_DEBT<br/>蓝图: MOD-GOV_SCAN_DEBT"):::jobProd
    JOB709537("[production]MOD-GOV_SCRIPTS<br/>蓝图: MOD-GOV_SCRIPTS"):::jobProd
    JOB709538("[production]MOD-GOV_SCRIPTS_ARCH<br/>蓝图: MOD-GOV_SCRIPTS_ARCH"):::jobProd
    JOB709539("[production]MOD-GOV_SECURITY_GOVERNANCE<br/>蓝图: MOD-GOV_SECURITY_GOVERNANCE"):::jobProd
    JOB709540("[production]MOD-GOV_SESSION_CLAIM<br/>蓝图: MOD-GOV_SESSION_CLAIM"):::jobProd
    JOB709541("[production]MOD-GOV_SESSION_REQUIRED_GATE<br/>蓝图: MOD-GOV_SESSION_REQUIRED_GATE"):::jobProd
    JOB709542("[production]MOD-GOV_SESSION_WORKTREE<br/>蓝图: MOD-GOV_SESSION_WORKTREE"):::jobProd
    JOB709543("[production]MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION"):::jobProd
    JOB709544("[production]MOD-GOV_SSOT_REDEFINITION_GATE<br/>蓝图: MOD-GOV_SSOT_REDEFINITION_GATE"):::jobProd
    JOB709545("[production]MOD-GOV_SYNC_PANORAMA<br/>蓝图: MOD-GOV_SYNC_PANORAMA"):::jobProd
    JOB709546("[production]MOD-GOV_SYNC_SAVEPOINT_TEST<br/>蓝图: MOD-GOV_SYNC_SAVEPOINT_TEST"):::jobProd
    JOB709547("[production]MOD-GOV_TASK_SYSTEM_RED_TEAM<br/>蓝图: MOD-GOV_TASK_SYSTEM_RED_TEAM"):::jobProd
    JOB709548("[production]MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT<br/>蓝图: MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT"):::jobProd
    JOB709549("[production]MOD-GOV_TEST_EMERGENCY_COMMIT<br/>蓝图: MOD-GOV_TEST_EMERGENCY_COMMIT"):::jobProd
    JOB709550("[production]MOD-GOV_TEST_RECONCILE_ASYNC<br/>蓝图: MOD-GOV_TEST_RECONCILE_ASYNC"):::jobProd
    JOB709551("[production]MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE<br/>蓝图: MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE"):::jobProd
    JOB709552("[production]MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE<br/>蓝图: MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE"):::jobProd
    JOB709553("[production]MOD-GOV_VERIFY_KEY_IMPORTS<br/>蓝图: MOD-GOV_VERIFY_KEY_IMPORTS"):::jobProd
    JOB709554("[production]MOD-GOV_VOCAB_HARDCODE_GATE<br/>蓝图: MOD-GOV_VOCAB_HARDCODE_GATE"):::jobProd
    JOB709555("[production]MOD-GOV_WORKSPACE_HYGIENE_RECONCILER<br/>蓝图: MOD-GOV_WORKSPACE_HYGIENE_RECONCILER"):::jobProd
    JOB709556("[production]MOD-GOV_WORKTREE_MANAGER<br/>蓝图: MOD-GOV_WORKTREE_MANAGER"):::jobProd
    JOB709557("[production]MOD-GOV_YAML_SYNC_ERROR_CLASS<br/>蓝图: MOD-GOV_YAML_SYNC_ERROR_CLASS"):::jobProd
    JOB321362("[design]MOD-GOV_blueprint_status_transition_reconciler"):::jobDesign
    JOB321311("[design]MOD-GOV_cross_layer_contract_signature_reconciler"):::jobDesign
    JOB709558("[production]MOD-INF-001<br/>蓝图: MOD-INF-001"):::jobProd
    JOB709559("[production]MOD-INF-002<br/>蓝图: MOD-INF-002"):::jobProd
    JOB709560("[production]MOD-INF-003<br/>蓝图: MOD-INF-003"):::jobProd
    JOB36357("[design]MOD-INF-005"):::jobDesign
    JOB37139("[design]MOD-INF-009"):::jobDesign
    JOB35565("[design]MOD-INF-011"):::jobDesign
    JOB709564("[production]MOD-INF-013<br/>蓝图: MOD-INF-013"):::jobProd
    JOB709565("[production]MOD-INF-014<br/>蓝图: MOD-INF-014"):::jobProd
    JOB709566("[production]MOD-INF-015<br/>蓝图: MOD-INF-015"):::jobProd
    JOB35954("[design]MOD-INF-016"):::jobDesign
    JOB36274("[design]MOD-INF-017"):::jobDesign
    JOB709569("[production]MOD-INF-018<br/>蓝图: MOD-INF-018"):::jobProd
    JOB37172("[design]MOD-INF-019"):::jobDesign
    JOB36050("[design]MOD-INF-020"):::jobDesign
    JOB35903("[design]MOD-INF-021"):::jobDesign
    JOB36400("[design]MOD-INF-022"):::jobDesign
    JOB35522("[design]MOD-INF-023"):::jobDesign
    JOB37193("[design]MOD-INF-024"):::jobDesign
    JOB709576("[production]MOD-INF-025<br/>蓝图: MOD-INF-025"):::jobProd
    JOB709577("[production]MOD-INF-026<br/>蓝图: MOD-INF-026"):::jobProd
    JOB35574("[design]MOD-INF-027"):::jobDesign
    JOB36222("[design]MOD-INF-028"):::jobDesign
    JOB35930("[design]MOD-INF-029"):::jobDesign
    JOB37217("[design]MOD-INF-030"):::jobDesign
    JOB37220("[design]MOD-INF-031"):::jobDesign
    JOB36336("[design]MOD-INF-033"):::jobDesign
    JOB35554("[design]MOD-INF-034"):::jobDesign
    JOB709585("[production]MOD-INF-035<br/>蓝图: MOD-INF-035"):::jobProd
    JOB37237("[design]MOD-INF-036"):::jobDesign
    JOB35538("[design]MOD-INF-037"):::jobDesign
    JOB709588("[production]MOD-INF-038<br/>蓝图: MOD-INF-038"):::jobProd
    JOB36080("[design]MOD-INF-039"):::jobDesign
    JOB709590("[production]MOD-INF-040<br/>蓝图: MOD-INF-040"):::jobProd
    JOB709591("[production]MOD-INF-042<br/>蓝图: MOD-INF-042"):::jobProd
    JOB709592("[production]MOD-INF-043<br/>蓝图: MOD-INF-043"):::jobProd
    JOB709593("[production]MOD-INF-044<br/>蓝图: MOD-INF-044"):::jobProd
    JOB35939("[design]MOD-INFRA_OPS"):::jobDesign
    JOB709594("[production]MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME"):::jobProd
    JOB709595("[production]MOD-INF_GOV<br/>蓝图: MOD-INF_GOV"):::jobProd
    JOB709596("[production]MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION"):::jobProd
    JOB709597("[production]MOD-L00-001<br/>蓝图: MOD-L00-001"):::jobProd
    JOB36157("[design]MOD-L00-002"):::jobDesign
    JOB35520("[design]MOD-L00-003"):::jobDesign
    JOB61876("[design]MOD-L00-004"):::jobDesign
    JOB709599("[production]MOD-L00-005<br/>蓝图: MOD-L00-005"):::jobProd
    JOB709600("[production]MOD-L00-006<br/>蓝图: MOD-L00-006"):::jobProd
    JOB709601("[production]MOD-L00-007<br/>蓝图: MOD-L00-007"):::jobProd
    JOB551909("[design]MOD-L02-001"):::jobDesign
    JOB709603("[production]MOD-L02-002<br/>蓝图: MOD-L02-002"):::jobProd
    JOB709604("[production]MOD-L02-003<br/>蓝图: MOD-L02-003"):::jobProd
    JOB709605("[production]MOD-L02-004<br/>蓝图: MOD-L02-004"):::jobProd
    JOB709606("[production]MOD-L02-005<br/>蓝图: MOD-L02-005"):::jobProd
    JOB709607("[production]MOD-L02-006<br/>蓝图: MOD-L02-006"):::jobProd
    JOB709608("[production]MOD-L02-007<br/>蓝图: MOD-L02-007"):::jobProd
    JOB709609("[production]MOD-L02-008<br/>蓝图: MOD-L02-008"):::jobProd
    JOB709610("[production]MOD-L02-009<br/>蓝图: MOD-L02-009"):::jobProd
    JOB709611("[production]MOD-L02-010<br/>蓝图: MOD-L02-010"):::jobProd
    JOB709612("[production]MOD-L02-011<br/>蓝图: MOD-L02-011"):::jobProd
    JOB709613("[production]MOD-L02-012<br/>蓝图: MOD-L02-012"):::jobProd
    JOB709614("[production]MOD-L02-013<br/>蓝图: MOD-L02-013"):::jobProd
    JOB709615("[production]MOD-L02-014<br/>蓝图: MOD-L02-014"):::jobProd
    JOB709616("[production]MOD-L02-015<br/>蓝图: MOD-L02-015"):::jobProd
    JOB709617("[production]MOD-L02-016<br/>蓝图: MOD-L02-016"):::jobProd
    JOB709618("[production]MOD-L02-017<br/>蓝图: MOD-L02-017"):::jobProd
    JOB709619("[production]MOD-L02-018<br/>蓝图: MOD-L02-018"):::jobProd
    JOB709620("[production]MOD-L02-024<br/>蓝图: MOD-L02-024"):::jobProd
    JOB709621("[production]MOD-L02-025<br/>蓝图: MOD-L02-025"):::jobProd
    JOB709622("[production]MOD-L02-ANA<br/>蓝图: MOD-L02-ANA"):::jobProd
    JOB709623("[production]MOD-L02-GOV<br/>蓝图: MOD-L02-GOV"):::jobProd
    JOB709624("[production]MOD-L03-001<br/>蓝图: MOD-L03-001"):::jobProd
    JOB688297("[design]MOD-L04-001"):::jobDesign
    JOB709626("[production]MOD-L04-002<br/>蓝图: MOD-L04-002"):::jobProd
    JOB709627("[production]MOD-L05-001<br/>蓝图: MOD-L05-001"):::jobProd
    JOB709628("[production]MOD-L06-001<br/>蓝图: MOD-L06-001"):::jobProd
    JOB709629("[production]MOD-L07-001<br/>蓝图: MOD-L07-001"):::jobProd
    JOB709630("[production]MOD-L08-001<br/>蓝图: MOD-L08-001"):::jobProd
    JOB709631("[production]MOD-L09-001<br/>蓝图: MOD-L09-001"):::jobProd
    JOB709632("[production]MOD-L10-001<br/>蓝图: MOD-L10-001"):::jobProd
    JOB709633("[production]MOD-L11-001<br/>蓝图: MOD-L11-001"):::jobProd
    JOB709634("[production]MOD-L13-001<br/>蓝图: MOD-L13-001"):::jobProd
    JOB709635("[production]MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY"):::jobProd
    JOB36390("[design]MOD-MASTER-001"):::jobDesign
    JOB35517("[design]MOD-MASTER-002"):::jobDesign
    JOB36344("[design]MOD-MASTER-003"):::jobDesign
    JOB35528("[design]MOD-MASTER_BLUEPRINT"):::jobDesign
    JOB711884("[design]MOD-MKT-001"):::jobDesign
    JOB711954("[design]MOD-MKT-002"):::jobDesign
    JOB712012("[design]MOD-MKT-003"):::jobDesign
    JOB709637("[production]MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA"):::jobProd
    JOB709638("[production]MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE"):::jobProd
    JOB709639("[production]MOD-OPS-018<br/>蓝图: MOD-OPS-018"):::jobProd
    JOB36113("[design]MOD-PF_ALLOC"):::jobDesign
    JOB709640("[production]MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS"):::jobProd
    JOB709641("[production]MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE"):::jobProd
    JOB35898("[design]MOD-RESOURCE_OPTIMIZATION_ENGINE"):::jobDesign
    JOB709643("[production]MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE"):::jobProd
    JOB709644("[production]MOD-SCRIPTS-006<br/>蓝图: MOD-SCRIPTS-006"):::jobProd
    JOB709645("[production]MOD-SEC-030<br/>蓝图: MOD-SEC-030"):::jobProd
    JOB709646("[production]MOD-SEC_IMMUTABLE_CORE<br/>蓝图: MOD-SEC_IMMUTABLE_CORE"):::jobProd
    JOB709647("[production]MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION"):::jobProd
    JOB709648("[production]MOD-SHARED-001<br/>蓝图: MOD-SHARED-001"):::jobProd
    JOB709649("[production]MOD-SHARED-002<br/>蓝图: MOD-SHARED-002"):::jobProd
    JOB709650("[production]MOD-SHR_CONVERTERS<br/>蓝图: MOD-SHR_CONVERTERS"):::jobProd
    JOB709651("[production]MOD-SHR_IO_YAML<br/>蓝图: MOD-SHR_IO_YAML"):::jobProd
    JOB709652("[production]MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE"):::jobProd
    JOB709653("[production]MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001"):::jobProd
    JOB35600("[design]MOD-SIMULATION"):::jobDesign
    JOB119053("[design]MOD-SMOKE-TEST"):::jobDesign
    JOB709654("[production]MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM"):::jobProd
    JOB118981("[design]MOD-TEST"):::jobDesign
    JOB709656("[production]MOD-TEST-202<br/>蓝图: MOD-TEST-202"):::jobProd
    JOB709657("[production]MOD-TEST-203<br/>蓝图: MOD-TEST-203"):::jobProd
    JOB709658("[production]MOD-TEST-204<br/>蓝图: MOD-TEST-204"):::jobProd
    JOB709659("[production]MOD-TEST-205<br/>蓝图: MOD-TEST-205"):::jobProd
    JOB709660("[production]MOD-TEST-206<br/>蓝图: MOD-TEST-206"):::jobProd
    JOB709661("[production]MOD-TEST-210<br/>蓝图: MOD-TEST-210"):::jobProd
    JOB709662("[production]MOD-TEST-211<br/>蓝图: MOD-TEST-211"):::jobProd
    JOB709663("[production]MOD-TEST-212<br/>蓝图: MOD-TEST-212"):::jobProd
    JOB709664("[production]MOD-TEST-213<br/>蓝图: MOD-TEST-213"):::jobProd
    JOB709665("[production]MOD-TEST-215<br/>蓝图: MOD-TEST-215"):::jobProd
    JOB709666("[production]MOD-TEST-216<br/>蓝图: MOD-TEST-216"):::jobProd
    JOB709667("[production]MOD-TEST-217<br/>蓝图: MOD-TEST-217"):::jobProd
    JOB709668("[production]MOD-TEST-218<br/>蓝图: MOD-TEST-218"):::jobProd
    JOB709669("[production]MOD-TEST-219<br/>蓝图: MOD-TEST-219"):::jobProd
    JOB709670("[production]MOD-TEST-220<br/>蓝图: MOD-TEST-220"):::jobProd
    JOB709671("[production]MOD-TEST-221<br/>蓝图: MOD-TEST-221"):::jobProd
    JOB709672("[production]MOD-TEST-222<br/>蓝图: MOD-TEST-222"):::jobProd
    JOB709673("[production]MOD-TEST-223<br/>蓝图: MOD-TEST-223"):::jobProd
    JOB709674("[production]MOD-TEST-224<br/>蓝图: MOD-TEST-224"):::jobProd
    JOB709675("[production]MOD-TEST-225<br/>蓝图: MOD-TEST-225"):::jobProd
    JOB709676("[production]MOD-TEST-226<br/>蓝图: MOD-TEST-226"):::jobProd
    JOB709677("[production]MOD-TEST-227<br/>蓝图: MOD-TEST-227"):::jobProd
    JOB709678("[production]MOD-TEST-228<br/>蓝图: MOD-TEST-228"):::jobProd
    JOB709679("[production]MOD-TEST-229<br/>蓝图: MOD-TEST-229"):::jobProd
    JOB709680("[production]MOD-TEST-230<br/>蓝图: MOD-TEST-230"):::jobProd
    JOB709681("[production]MOD-TEST-231<br/>蓝图: MOD-TEST-231"):::jobProd
    JOB709682("[production]MOD-TEST-232<br/>蓝图: MOD-TEST-232"):::jobProd
    JOB709683("[production]MOD-TEST-233<br/>蓝图: MOD-TEST-233"):::jobProd
    JOB709684("[production]MOD-TEST-234<br/>蓝图: MOD-TEST-234"):::jobProd
    JOB709685("[production]MOD-TEST-235<br/>蓝图: MOD-TEST-235"):::jobProd
    JOB709686("[production]MOD-TEST-236<br/>蓝图: MOD-TEST-236"):::jobProd
    JOB709687("[production]MOD-TEST-237<br/>蓝图: MOD-TEST-237"):::jobProd
    JOB709688("[production]MOD-TEST-238<br/>蓝图: MOD-TEST-238"):::jobProd
    JOB709689("[production]MOD-TEST-239<br/>蓝图: MOD-TEST-239"):::jobProd
    JOB709690("[production]MOD-TEST-240<br/>蓝图: MOD-TEST-240"):::jobProd
    JOB709691("[production]MOD-TEST-241<br/>蓝图: MOD-TEST-241"):::jobProd
    JOB709692("[production]MOD-TEST-242<br/>蓝图: MOD-TEST-242"):::jobProd
    JOB709693("[production]MOD-TEST-246<br/>蓝图: MOD-TEST-246"):::jobProd
    JOB709694("[production]MOD-TEST-247<br/>蓝图: MOD-TEST-247"):::jobProd
    JOB709695("[production]MOD-TEST-248<br/>蓝图: MOD-TEST-248"):::jobProd
    JOB709696("[production]MOD-TEST-250<br/>蓝图: MOD-TEST-250"):::jobProd
    JOB709697("[production]MOD-TEST-251<br/>蓝图: MOD-TEST-251"):::jobProd
    JOB709698("[production]MOD-TEST-252<br/>蓝图: MOD-TEST-252"):::jobProd
    JOB709699("[production]MOD-TEST-253<br/>蓝图: MOD-TEST-253"):::jobProd
    JOB709700("[production]MOD-TEST-254<br/>蓝图: MOD-TEST-254"):::jobProd
    JOB709701("[production]MOD-TEST-255<br/>蓝图: MOD-TEST-255"):::jobProd
    JOB709702("[production]MOD-TEST-256<br/>蓝图: MOD-TEST-256"):::jobProd
    JOB709703("[production]MOD-TEST-257<br/>蓝图: MOD-TEST-257"):::jobProd
    JOB709704("[production]MOD-TEST-258<br/>蓝图: MOD-TEST-258"):::jobProd
    JOB709705("[production]MOD-TEST-260<br/>蓝图: MOD-TEST-260"):::jobProd
    JOB709706("[production]MOD-TEST-261<br/>蓝图: MOD-TEST-261"):::jobProd
    JOB709707("[production]MOD-TEST-262<br/>蓝图: MOD-TEST-262"):::jobProd
    JOB709708("[production]MOD-TEST-263<br/>蓝图: MOD-TEST-263"):::jobProd
    JOB709709("[production]MOD-TEST-264<br/>蓝图: MOD-TEST-264"):::jobProd
    JOB709710("[production]MOD-TEST-265<br/>蓝图: MOD-TEST-265"):::jobProd
    JOB709711("[production]MOD-TEST-266<br/>蓝图: MOD-TEST-266"):::jobProd
    JOB709712("[production]MOD-TEST-268<br/>蓝图: MOD-TEST-268"):::jobProd
    JOB709713("[production]MOD-TEST-272<br/>蓝图: MOD-TEST-272"):::jobProd
    JOB709714("[production]MOD-TEST-273<br/>蓝图: MOD-TEST-273"):::jobProd
    JOB709715("[production]MOD-TEST-274<br/>蓝图: MOD-TEST-274"):::jobProd
    JOB709716("[production]MOD-TEST-275<br/>蓝图: MOD-TEST-275"):::jobProd
    JOB709717("[production]MOD-TEST-276<br/>蓝图: MOD-TEST-276"):::jobProd
    JOB709718("[production]MOD-TEST-277<br/>蓝图: MOD-TEST-277"):::jobProd
    JOB709719("[production]MOD-TEST-278<br/>蓝图: MOD-TEST-278"):::jobProd
    JOB709720("[production]MOD-TEST-279<br/>蓝图: MOD-TEST-279"):::jobProd
    JOB709721("[production]MOD-TEST-280<br/>蓝图: MOD-TEST-280"):::jobProd
    JOB709722("[production]MOD-TEST-281<br/>蓝图: MOD-TEST-281"):::jobProd
    JOB709723("[production]MOD-TEST-282<br/>蓝图: MOD-TEST-282"):::jobProd
    JOB709724("[production]MOD-TEST-283<br/>蓝图: MOD-TEST-283"):::jobProd
    JOB709725("[production]MOD-TEST-284<br/>蓝图: MOD-TEST-284"):::jobProd
    JOB709726("[production]MOD-TEST-285<br/>蓝图: MOD-TEST-285"):::jobProd
    JOB709727("[production]MOD-TEST-286<br/>蓝图: MOD-TEST-286"):::jobProd
    JOB709728("[production]MOD-TEST-287<br/>蓝图: MOD-TEST-287"):::jobProd
    JOB709729("[production]MOD-TEST-288<br/>蓝图: MOD-TEST-288"):::jobProd
    JOB709730("[production]MOD-TEST-289<br/>蓝图: MOD-TEST-289"):::jobProd
    JOB709731("[production]MOD-TEST-290<br/>蓝图: MOD-TEST-290"):::jobProd
    JOB709732("[production]MOD-TEST-291<br/>蓝图: MOD-TEST-291"):::jobProd
    JOB709733("[production]MOD-TEST-292<br/>蓝图: MOD-TEST-292"):::jobProd
    JOB709734("[production]MOD-TEST-293<br/>蓝图: MOD-TEST-293"):::jobProd
    JOB709735("[production]MOD-TEST-294<br/>蓝图: MOD-TEST-294"):::jobProd
    JOB709736("[production]MOD-TEST-295<br/>蓝图: MOD-TEST-295"):::jobProd
    JOB709737("[production]MOD-TEST-296<br/>蓝图: MOD-TEST-296"):::jobProd
    JOB709738("[production]MOD-TEST-297<br/>蓝图: MOD-TEST-297"):::jobProd
    JOB709739("[production]MOD-TEST-298<br/>蓝图: MOD-TEST-298"):::jobProd
    JOB709740("[production]MOD-TEST-299<br/>蓝图: MOD-TEST-299"):::jobProd
    JOB709741("[production]MOD-TEST-300<br/>蓝图: MOD-TEST-300"):::jobProd
    JOB709742("[production]MOD-TEST-301<br/>蓝图: MOD-TEST-301"):::jobProd
    JOB709743("[production]MOD-TEST-302<br/>蓝图: MOD-TEST-302"):::jobProd
    JOB709744("[production]MOD-TEST-303<br/>蓝图: MOD-TEST-303"):::jobProd
    JOB709745("[production]MOD-TEST-304<br/>蓝图: MOD-TEST-304"):::jobProd
    JOB709746("[production]MOD-TEST-305<br/>蓝图: MOD-TEST-305"):::jobProd
    JOB709747("[production]MOD-TEST-306<br/>蓝图: MOD-TEST-306"):::jobProd
    JOB709748("[production]MOD-TEST-307<br/>蓝图: MOD-TEST-307"):::jobProd
    JOB709749("[production]MOD-TEST-308<br/>蓝图: MOD-TEST-308"):::jobProd
    JOB709750("[production]MOD-TEST-309<br/>蓝图: MOD-TEST-309"):::jobProd
    JOB709751("[production]MOD-TEST-310<br/>蓝图: MOD-TEST-310"):::jobProd
    JOB709752("[production]MOD-TEST-311<br/>蓝图: MOD-TEST-311"):::jobProd
    JOB709753("[production]MOD-TEST-312<br/>蓝图: MOD-TEST-312"):::jobProd
    JOB709754("[production]MOD-TEST-313<br/>蓝图: MOD-TEST-313"):::jobProd
    JOB709755("[production]MOD-TEST-314<br/>蓝图: MOD-TEST-314"):::jobProd
    JOB709756("[production]MOD-TEST-315<br/>蓝图: MOD-TEST-315"):::jobProd
    JOB709757("[production]MOD-TEST-316<br/>蓝图: MOD-TEST-316"):::jobProd
    JOB709758("[production]MOD-TEST-319<br/>蓝图: MOD-TEST-319"):::jobProd
    JOB709759("[production]MOD-TEST-320<br/>蓝图: MOD-TEST-320"):::jobProd
    JOB709760("[production]MOD-TEST-322<br/>蓝图: MOD-TEST-322"):::jobProd
    JOB709761("[production]MOD-TEST-323<br/>蓝图: MOD-TEST-323"):::jobProd
    JOB709762("[production]MOD-TEST-324<br/>蓝图: MOD-TEST-324"):::jobProd
    JOB709763("[production]MOD-TEST-325<br/>蓝图: MOD-TEST-325"):::jobProd
    JOB709764("[production]MOD-TEST-326<br/>蓝图: MOD-TEST-326"):::jobProd
    JOB709765("[production]MOD-TEST-328<br/>蓝图: MOD-TEST-328"):::jobProd
    JOB709766("[production]MOD-TEST-329<br/>蓝图: MOD-TEST-329"):::jobProd
    JOB709767("[production]MOD-TEST-330<br/>蓝图: MOD-TEST-330"):::jobProd
    JOB709768("[production]MOD-TEST-331<br/>蓝图: MOD-TEST-331"):::jobProd
    JOB709769("[production]MOD-TEST-332<br/>蓝图: MOD-TEST-332"):::jobProd
    JOB709770("[production]MOD-TEST-333<br/>蓝图: MOD-TEST-333"):::jobProd
    JOB709771("[production]MOD-TEST-334<br/>蓝图: MOD-TEST-334"):::jobProd
    JOB709772("[production]MOD-TEST-335<br/>蓝图: MOD-TEST-335"):::jobProd
    JOB709773("[production]MOD-TEST-336<br/>蓝图: MOD-TEST-336"):::jobProd
    JOB709774("[production]MOD-TEST-337<br/>蓝图: MOD-TEST-337"):::jobProd
    JOB709775("[production]MOD-TEST-338<br/>蓝图: MOD-TEST-338"):::jobProd
    JOB709776("[production]MOD-TEST-339<br/>蓝图: MOD-TEST-339"):::jobProd
    JOB709777("[production]MOD-TEST-340<br/>蓝图: MOD-TEST-340"):::jobProd
    JOB709778("[production]MOD-TEST-342<br/>蓝图: MOD-TEST-342"):::jobProd
    JOB709779("[production]MOD-TEST-343<br/>蓝图: MOD-TEST-343"):::jobProd
    JOB709780("[production]MOD-TEST-344<br/>蓝图: MOD-TEST-344"):::jobProd
    JOB709781("[production]MOD-TEST-345<br/>蓝图: MOD-TEST-345"):::jobProd
    JOB709782("[production]MOD-TEST-346<br/>蓝图: MOD-TEST-346"):::jobProd
    JOB709783("[production]MOD-TEST-347<br/>蓝图: MOD-TEST-347"):::jobProd
    JOB709784("[production]MOD-TEST-348<br/>蓝图: MOD-TEST-348"):::jobProd
    JOB709785("[production]MOD-TEST-349<br/>蓝图: MOD-TEST-349"):::jobProd
    JOB709786("[production]MOD-TEST-350<br/>蓝图: MOD-TEST-350"):::jobProd
    JOB709787("[production]MOD-TEST-351<br/>蓝图: MOD-TEST-351"):::jobProd
    JOB709788("[production]MOD-TEST-354<br/>蓝图: MOD-TEST-354"):::jobProd
    JOB709789("[production]MOD-TEST-355<br/>蓝图: MOD-TEST-355"):::jobProd
    JOB709790("[production]MOD-TEST-356<br/>蓝图: MOD-TEST-356"):::jobProd
    JOB709791("[production]MOD-TEST-357<br/>蓝图: MOD-TEST-357"):::jobProd
    JOB709792("[production]MOD-TEST-358<br/>蓝图: MOD-TEST-358"):::jobProd
    JOB709793("[production]MOD-TEST-359<br/>蓝图: MOD-TEST-359"):::jobProd
    JOB709794("[production]MOD-TEST-360<br/>蓝图: MOD-TEST-360"):::jobProd
    JOB709795("[production]MOD-TEST-361<br/>蓝图: MOD-TEST-361"):::jobProd
    JOB709796("[production]MOD-TEST-362<br/>蓝图: MOD-TEST-362"):::jobProd
    JOB709797("[production]MOD-TEST-363<br/>蓝图: MOD-TEST-363"):::jobProd
    JOB709798("[production]MOD-TEST-364<br/>蓝图: MOD-TEST-364"):::jobProd
    JOB709799("[production]MOD-TEST-365<br/>蓝图: MOD-TEST-365"):::jobProd
    JOB709800("[production]MOD-TEST-366<br/>蓝图: MOD-TEST-366"):::jobProd
    JOB709801("[production]MOD-TEST-367<br/>蓝图: MOD-TEST-367"):::jobProd
    JOB709802("[production]MOD-TEST-368<br/>蓝图: MOD-TEST-368"):::jobProd
    JOB709803("[production]MOD-TEST-369<br/>蓝图: MOD-TEST-369"):::jobProd
    JOB709804("[production]MOD-TEST-370<br/>蓝图: MOD-TEST-370"):::jobProd
    JOB709805("[production]MOD-TEST-371<br/>蓝图: MOD-TEST-371"):::jobProd
    JOB709806("[production]MOD-TEST-372<br/>蓝图: MOD-TEST-372"):::jobProd
    JOB709807("[production]MOD-TEST-373<br/>蓝图: MOD-TEST-373"):::jobProd
    JOB709808("[production]MOD-TEST-374<br/>蓝图: MOD-TEST-374"):::jobProd
    JOB709809("[production]MOD-TEST-375<br/>蓝图: MOD-TEST-375"):::jobProd
    JOB709810("[production]MOD-TEST-376<br/>蓝图: MOD-TEST-376"):::jobProd
    JOB709811("[production]MOD-TEST-377<br/>蓝图: MOD-TEST-377"):::jobProd
    JOB709812("[production]MOD-TEST-378<br/>蓝图: MOD-TEST-378"):::jobProd
    JOB709813("[production]MOD-TEST-379<br/>蓝图: MOD-TEST-379"):::jobProd
    JOB709814("[production]MOD-TEST-380<br/>蓝图: MOD-TEST-380"):::jobProd
    JOB709815("[production]MOD-TEST-381<br/>蓝图: MOD-TEST-381"):::jobProd
    JOB709816("[production]MOD-TEST-382<br/>蓝图: MOD-TEST-382"):::jobProd
    JOB709817("[production]MOD-TEST-383<br/>蓝图: MOD-TEST-383"):::jobProd
    JOB709818("[production]MOD-TEST-384<br/>蓝图: MOD-TEST-384"):::jobProd
    JOB709819("[production]MOD-TEST-385<br/>蓝图: MOD-TEST-385"):::jobProd
    JOB709820("[production]MOD-TEST-386<br/>蓝图: MOD-TEST-386"):::jobProd
    JOB709821("[production]MOD-TEST-387<br/>蓝图: MOD-TEST-387"):::jobProd
    JOB709822("[production]MOD-TEST-388<br/>蓝图: MOD-TEST-388"):::jobProd
    JOB709823("[production]MOD-TEST-389<br/>蓝图: MOD-TEST-389"):::jobProd
    JOB709824("[production]MOD-TEST-390<br/>蓝图: MOD-TEST-390"):::jobProd
    JOB709825("[production]MOD-TEST-391<br/>蓝图: MOD-TEST-391"):::jobProd
    JOB709826("[production]MOD-TEST-392<br/>蓝图: MOD-TEST-392"):::jobProd
    JOB709827("[production]MOD-TEST-393<br/>蓝图: MOD-TEST-393"):::jobProd
    JOB709828("[production]MOD-TEST-394<br/>蓝图: MOD-TEST-394"):::jobProd
    JOB709829("[production]MOD-TEST-395<br/>蓝图: MOD-TEST-395"):::jobProd
    JOB709830("[production]MOD-TEST-396<br/>蓝图: MOD-TEST-396"):::jobProd
    JOB709831("[production]MOD-TEST-397<br/>蓝图: MOD-TEST-397"):::jobProd
    JOB709832("[production]MOD-TEST-402<br/>蓝图: MOD-TEST-402"):::jobProd
    JOB709833("[production]MOD-TEST-403<br/>蓝图: MOD-TEST-403"):::jobProd
    JOB709834("[production]MOD-TEST-404<br/>蓝图: MOD-TEST-404"):::jobProd
    JOB709835("[production]MOD-TEST-406<br/>蓝图: MOD-TEST-406"):::jobProd
    JOB709836("[production]MOD-TEST-407<br/>蓝图: MOD-TEST-407"):::jobProd
    JOB709837("[production]MOD-TEST-408<br/>蓝图: MOD-TEST-408"):::jobProd
    JOB709838("[production]MOD-TEST-409<br/>蓝图: MOD-TEST-409"):::jobProd
    JOB709839("[production]MOD-TEST-410<br/>蓝图: MOD-TEST-410"):::jobProd
    JOB709840("[production]MOD-TEST-411<br/>蓝图: MOD-TEST-411"):::jobProd
    JOB709841("[production]MOD-TEST-412<br/>蓝图: MOD-TEST-412"):::jobProd
    JOB709842("[production]MOD-TEST-413<br/>蓝图: MOD-TEST-413"):::jobProd
    JOB709843("[production]MOD-TEST-414<br/>蓝图: MOD-TEST-414"):::jobProd
    JOB709844("[production]MOD-TEST-415<br/>蓝图: MOD-TEST-415"):::jobProd
    JOB709845("[production]MOD-TEST-416<br/>蓝图: MOD-TEST-416"):::jobProd
    JOB709846("[production]MOD-TEST-417<br/>蓝图: MOD-TEST-417"):::jobProd
    JOB709847("[production]MOD-TEST-418<br/>蓝图: MOD-TEST-418"):::jobProd
    JOB709848("[production]MOD-TEST-419<br/>蓝图: MOD-TEST-419"):::jobProd
    JOB709849("[production]MOD-TEST-420<br/>蓝图: MOD-TEST-420"):::jobProd
    JOB709850("[production]MOD-TEST-421<br/>蓝图: MOD-TEST-421"):::jobProd
    JOB709851("[production]MOD-TEST-422<br/>蓝图: MOD-TEST-422"):::jobProd
    JOB709852("[production]MOD-TEST-423<br/>蓝图: MOD-TEST-423"):::jobProd
    JOB709853("[production]MOD-TEST-424<br/>蓝图: MOD-TEST-424"):::jobProd
    JOB709854("[production]MOD-TEST-425<br/>蓝图: MOD-TEST-425"):::jobProd
    JOB709855("[production]MOD-TEST-426<br/>蓝图: MOD-TEST-426"):::jobProd
    JOB709856("[production]MOD-TEST-427<br/>蓝图: MOD-TEST-427"):::jobProd
    JOB709857("[production]MOD-TEST-428<br/>蓝图: MOD-TEST-428"):::jobProd
    JOB709858("[production]MOD-TEST-429<br/>蓝图: MOD-TEST-429"):::jobProd
    JOB709859("[production]MOD-TEST-430<br/>蓝图: MOD-TEST-430"):::jobProd
    JOB709860("[production]MOD-TEST-431<br/>蓝图: MOD-TEST-431"):::jobProd
    JOB709861("[production]MOD-TEST-432<br/>蓝图: MOD-TEST-432"):::jobProd
    JOB709862("[production]MOD-TEST-433<br/>蓝图: MOD-TEST-433"):::jobProd
    JOB709863("[production]MOD-TEST-434<br/>蓝图: MOD-TEST-434"):::jobProd
    JOB709864("[production]MOD-TEST-435<br/>蓝图: MOD-TEST-435"):::jobProd
    JOB709865("[production]MOD-TEST-436<br/>蓝图: MOD-TEST-436"):::jobProd
    JOB709866("[production]MOD-TEST-437<br/>蓝图: MOD-TEST-437"):::jobProd
    JOB709867("[production]MOD-TEST-438<br/>蓝图: MOD-TEST-438"):::jobProd
    JOB709868("[production]MOD-TEST-439<br/>蓝图: MOD-TEST-439"):::jobProd
    JOB709869("[production]MOD-TEST-440<br/>蓝图: MOD-TEST-440"):::jobProd
    JOB709870("[production]MOD-TEST-441<br/>蓝图: MOD-TEST-441"):::jobProd
    JOB709871("[production]MOD-TEST-444<br/>蓝图: MOD-TEST-444"):::jobProd
    JOB709872("[production]MOD-TEST-447<br/>蓝图: MOD-TEST-447"):::jobProd
    JOB709873("[production]MOD-TEST-449<br/>蓝图: MOD-TEST-449"):::jobProd
    JOB709874("[production]MOD-TEST-450<br/>蓝图: MOD-TEST-450"):::jobProd
    JOB709875("[production]MOD-TEST-452<br/>蓝图: MOD-TEST-452"):::jobProd
    JOB709876("[production]MOD-TEST-454<br/>蓝图: MOD-TEST-454"):::jobProd
    JOB709877("[production]MOD-TEST-455<br/>蓝图: MOD-TEST-455"):::jobProd
    JOB709878("[production]MOD-TEST-456<br/>蓝图: MOD-TEST-456"):::jobProd
    JOB709879("[production]MOD-TEST-457<br/>蓝图: MOD-TEST-457"):::jobProd
    JOB709880("[production]MOD-TEST-459<br/>蓝图: MOD-TEST-459"):::jobProd
    JOB709881("[production]MOD-TEST-460<br/>蓝图: MOD-TEST-460"):::jobProd
    JOB709882("[production]MOD-TEST-461<br/>蓝图: MOD-TEST-461"):::jobProd
    JOB709883("[production]MOD-TEST-462<br/>蓝图: MOD-TEST-462"):::jobProd
    JOB709884("[production]MOD-TEST-463<br/>蓝图: MOD-TEST-463"):::jobProd
    JOB709885("[production]MOD-TEST-464<br/>蓝图: MOD-TEST-464"):::jobProd
    JOB709886("[production]MOD-TEST-466<br/>蓝图: MOD-TEST-466"):::jobProd
    JOB709887("[production]MOD-TEST-467<br/>蓝图: MOD-TEST-467"):::jobProd
    JOB709888("[production]MOD-TEST-468<br/>蓝图: MOD-TEST-468"):::jobProd
    JOB709889("[production]MOD-TEST-469<br/>蓝图: MOD-TEST-469"):::jobProd
    JOB709890("[production]MOD-TEST-470<br/>蓝图: MOD-TEST-470"):::jobProd
    JOB709891("[production]MOD-TEST-471<br/>蓝图: MOD-TEST-471"):::jobProd
    JOB709892("[production]MOD-TEST-472<br/>蓝图: MOD-TEST-472"):::jobProd
    JOB709893("[production]MOD-TEST-473<br/>蓝图: MOD-TEST-473"):::jobProd
    JOB709894("[production]MOD-TEST-475<br/>蓝图: MOD-TEST-475"):::jobProd
    JOB709895("[production]MOD-TEST-476<br/>蓝图: MOD-TEST-476"):::jobProd
    JOB709896("[production]MOD-TEST-477<br/>蓝图: MOD-TEST-477"):::jobProd
    JOB709897("[production]MOD-TEST-479<br/>蓝图: MOD-TEST-479"):::jobProd
    JOB709898("[production]MOD-TEST-481<br/>蓝图: MOD-TEST-481"):::jobProd
    JOB709899("[production]MOD-TEST-482<br/>蓝图: MOD-TEST-482"):::jobProd
    JOB709900("[production]MOD-TEST-484<br/>蓝图: MOD-TEST-484"):::jobProd
    JOB709901("[production]MOD-TEST-485<br/>蓝图: MOD-TEST-485"):::jobProd
    JOB709902("[production]MOD-TEST-487<br/>蓝图: MOD-TEST-487"):::jobProd
    JOB709903("[production]MOD-TEST-488<br/>蓝图: MOD-TEST-488"):::jobProd
    JOB709904("[production]MOD-TEST-489<br/>蓝图: MOD-TEST-489"):::jobProd
    JOB709905("[production]MOD-TEST-490<br/>蓝图: MOD-TEST-490"):::jobProd
    JOB709906("[production]MOD-TEST-491<br/>蓝图: MOD-TEST-491"):::jobProd
    JOB709907("[production]MOD-TEST-492<br/>蓝图: MOD-TEST-492"):::jobProd
    JOB709908("[production]MOD-TEST-494<br/>蓝图: MOD-TEST-494"):::jobProd
    JOB709909("[production]MOD-TEST-495<br/>蓝图: MOD-TEST-495"):::jobProd
    JOB709910("[production]MOD-TEST-496<br/>蓝图: MOD-TEST-496"):::jobProd
    JOB709911("[production]MOD-TEST-497<br/>蓝图: MOD-TEST-497"):::jobProd
    JOB709912("[production]MOD-TEST-498<br/>蓝图: MOD-TEST-498"):::jobProd
    JOB709913("[production]MOD-TEST-499<br/>蓝图: MOD-TEST-499"):::jobProd
    JOB709914("[production]MOD-TEST-501<br/>蓝图: MOD-TEST-501"):::jobProd
    JOB709915("[production]MOD-TEST-502<br/>蓝图: MOD-TEST-502"):::jobProd
    JOB709916("[production]MOD-TEST-504<br/>蓝图: MOD-TEST-504"):::jobProd
    JOB709917("[production]MOD-TEST-505<br/>蓝图: MOD-TEST-505"):::jobProd
    JOB709918("[production]MOD-TEST-506<br/>蓝图: MOD-TEST-506"):::jobProd
    JOB709919("[production]MOD-TEST-508<br/>蓝图: MOD-TEST-508"):::jobProd
    JOB709920("[production]MOD-TEST-509<br/>蓝图: MOD-TEST-509"):::jobProd
    JOB709921("[production]MOD-TEST-510<br/>蓝图: MOD-TEST-510"):::jobProd
    JOB709922("[production]MOD-TEST-511<br/>蓝图: MOD-TEST-511"):::jobProd
    JOB709923("[production]MOD-TEST-512<br/>蓝图: MOD-TEST-512"):::jobProd
    JOB709924("[production]MOD-TEST-513<br/>蓝图: MOD-TEST-513"):::jobProd
    JOB709925("[production]MOD-TEST-514<br/>蓝图: MOD-TEST-514"):::jobProd
    JOB709926("[production]MOD-TEST-528<br/>蓝图: MOD-TEST-528"):::jobProd
    JOB709927("[production]MOD-TEST-529<br/>蓝图: MOD-TEST-529"):::jobProd
    JOB709928("[production]MOD-TEST-530<br/>蓝图: MOD-TEST-530"):::jobProd
    JOB709929("[production]MOD-TEST-532<br/>蓝图: MOD-TEST-532"):::jobProd
    JOB709930("[production]MOD-TEST-533<br/>蓝图: MOD-TEST-533"):::jobProd
    JOB709931("[production]MOD-TEST-534<br/>蓝图: MOD-TEST-534"):::jobProd
    JOB709932("[production]MOD-TEST-535<br/>蓝图: MOD-TEST-535"):::jobProd
    JOB709933("[production]MOD-TEST-536<br/>蓝图: MOD-TEST-536"):::jobProd
    JOB709934("[production]MOD-TEST-537<br/>蓝图: MOD-TEST-537"):::jobProd
    JOB709935("[production]MOD-TEST-538<br/>蓝图: MOD-TEST-538"):::jobProd
    JOB709936("[production]MOD-TEST-539<br/>蓝图: MOD-TEST-539"):::jobProd
    JOB709937("[production]MOD-TEST-540<br/>蓝图: MOD-TEST-540"):::jobProd
    JOB709938("[production]MOD-TEST-541<br/>蓝图: MOD-TEST-541"):::jobProd
    JOB709939("[production]MOD-TEST-543<br/>蓝图: MOD-TEST-543"):::jobProd
    JOB709940("[production]MOD-TEST-544<br/>蓝图: MOD-TEST-544"):::jobProd
    JOB709941("[production]MOD-TEST-545<br/>蓝图: MOD-TEST-545"):::jobProd
    JOB709942("[production]MOD-TEST-547<br/>蓝图: MOD-TEST-547"):::jobProd
    JOB709943("[production]MOD-TEST-548<br/>蓝图: MOD-TEST-548"):::jobProd
    JOB709944("[production]MOD-TEST-549<br/>蓝图: MOD-TEST-549"):::jobProd
    JOB709945("[production]MOD-TEST-550<br/>蓝图: MOD-TEST-550"):::jobProd
    JOB709946("[production]MOD-TEST-551<br/>蓝图: MOD-TEST-551"):::jobProd
    JOB709947("[production]MOD-TEST-552<br/>蓝图: MOD-TEST-552"):::jobProd
    JOB709948("[production]MOD-TEST-553<br/>蓝图: MOD-TEST-553"):::jobProd
    JOB709949("[production]MOD-TEST-554<br/>蓝图: MOD-TEST-554"):::jobProd
    JOB709950("[production]MOD-TEST-555<br/>蓝图: MOD-TEST-555"):::jobProd
    JOB709951("[production]MOD-TEST-557<br/>蓝图: MOD-TEST-557"):::jobProd
    JOB709952("[production]MOD-TEST-558<br/>蓝图: MOD-TEST-558"):::jobProd
    JOB709953("[production]MOD-TEST-559<br/>蓝图: MOD-TEST-559"):::jobProd
    JOB709954("[production]MOD-TEST-560<br/>蓝图: MOD-TEST-560"):::jobProd
    JOB709955("[production]MOD-TEST-561<br/>蓝图: MOD-TEST-561"):::jobProd
    JOB709956("[production]MOD-TEST-562<br/>蓝图: MOD-TEST-562"):::jobProd
    JOB709957("[production]MOD-TEST-563<br/>蓝图: MOD-TEST-563"):::jobProd
    JOB709958("[production]MOD-TEST-564<br/>蓝图: MOD-TEST-564"):::jobProd
    JOB709959("[production]MOD-TEST-565<br/>蓝图: MOD-TEST-565"):::jobProd
    JOB709960("[production]MOD-TEST-566<br/>蓝图: MOD-TEST-566"):::jobProd
    JOB709961("[production]MOD-TEST-567<br/>蓝图: MOD-TEST-567"):::jobProd
    JOB709962("[production]MOD-TEST-568<br/>蓝图: MOD-TEST-568"):::jobProd
    JOB709963("[production]MOD-TEST-569<br/>蓝图: MOD-TEST-569"):::jobProd
    JOB709964("[production]MOD-TEST-570<br/>蓝图: MOD-TEST-570"):::jobProd
    JOB709965("[production]MOD-TEST-571<br/>蓝图: MOD-TEST-571"):::jobProd
    JOB709966("[production]MOD-TEST-572<br/>蓝图: MOD-TEST-572"):::jobProd
    JOB709967("[production]MOD-TEST-573<br/>蓝图: MOD-TEST-573"):::jobProd
    JOB709968("[production]MOD-TEST-574<br/>蓝图: MOD-TEST-574"):::jobProd
    JOB709969("[production]MOD-TEST-575<br/>蓝图: MOD-TEST-575"):::jobProd
    JOB709970("[production]MOD-TEST-576<br/>蓝图: MOD-TEST-576"):::jobProd
    JOB709971("[production]MOD-TEST-577<br/>蓝图: MOD-TEST-577"):::jobProd
    JOB709972("[production]MOD-TEST-579<br/>蓝图: MOD-TEST-579"):::jobProd
    JOB709973("[production]MOD-TEST-580<br/>蓝图: MOD-TEST-580"):::jobProd
    JOB709974("[production]MOD-TEST-582<br/>蓝图: MOD-TEST-582"):::jobProd
    JOB709975("[production]MOD-TEST-583<br/>蓝图: MOD-TEST-583"):::jobProd
    JOB709976("[production]MOD-TEST-584<br/>蓝图: MOD-TEST-584"):::jobProd
    JOB709977("[production]MOD-TEST-585<br/>蓝图: MOD-TEST-585"):::jobProd
    JOB709978("[production]MOD-TEST-586<br/>蓝图: MOD-TEST-586"):::jobProd
    JOB709979("[production]MOD-TEST-587<br/>蓝图: MOD-TEST-587"):::jobProd
    JOB709980("[production]MOD-TEST-588<br/>蓝图: MOD-TEST-588"):::jobProd
    JOB709981("[production]MOD-TEST-590<br/>蓝图: MOD-TEST-590"):::jobProd
    JOB709982("[production]MOD-TEST-591<br/>蓝图: MOD-TEST-591"):::jobProd
    JOB709983("[production]MOD-TEST-592<br/>蓝图: MOD-TEST-592"):::jobProd
    JOB709984("[production]MOD-TEST-593<br/>蓝图: MOD-TEST-593"):::jobProd
    JOB709985("[production]MOD-TEST-594<br/>蓝图: MOD-TEST-594"):::jobProd
    JOB709986("[production]MOD-TEST-595<br/>蓝图: MOD-TEST-595"):::jobProd
    JOB709987("[production]MOD-TEST-597<br/>蓝图: MOD-TEST-597"):::jobProd
    JOB709988("[production]MOD-TEST-598<br/>蓝图: MOD-TEST-598"):::jobProd
    JOB709989("[production]MOD-TEST-599<br/>蓝图: MOD-TEST-599"):::jobProd
    JOB709990("[production]MOD-TEST-600<br/>蓝图: MOD-TEST-600"):::jobProd
    JOB709991("[production]MOD-TEST-601<br/>蓝图: MOD-TEST-601"):::jobProd
    JOB709992("[production]MOD-TEST-602<br/>蓝图: MOD-TEST-602"):::jobProd
    JOB709993("[production]MOD-TEST-603<br/>蓝图: MOD-TEST-603"):::jobProd
    JOB709994("[production]MOD-TEST-604<br/>蓝图: MOD-TEST-604"):::jobProd
    JOB709995("[production]MOD-TEST-605<br/>蓝图: MOD-TEST-605"):::jobProd
    JOB709996("[production]MOD-TEST-606<br/>蓝图: MOD-TEST-606"):::jobProd
    JOB709997("[production]MOD-TEST-607<br/>蓝图: MOD-TEST-607"):::jobProd
    JOB709998("[production]MOD-TEST-608<br/>蓝图: MOD-TEST-608"):::jobProd
    JOB709999("[production]MOD-TEST-609<br/>蓝图: MOD-TEST-609"):::jobProd
    JOB710000("[production]MOD-TEST-610<br/>蓝图: MOD-TEST-610"):::jobProd
    JOB710001("[production]MOD-TEST-611<br/>蓝图: MOD-TEST-611"):::jobProd
    JOB710002("[production]MOD-TEST-612<br/>蓝图: MOD-TEST-612"):::jobProd
    JOB710003("[production]MOD-TEST-613<br/>蓝图: MOD-TEST-613"):::jobProd
    JOB710004("[production]MOD-TEST-614<br/>蓝图: MOD-TEST-614"):::jobProd
    JOB710005("[production]MOD-TEST-616<br/>蓝图: MOD-TEST-616"):::jobProd
    JOB710006("[production]MOD-TEST-617<br/>蓝图: MOD-TEST-617"):::jobProd
    JOB710007("[production]MOD-TEST-618<br/>蓝图: MOD-TEST-618"):::jobProd
    JOB710008("[production]MOD-TEST-619<br/>蓝图: MOD-TEST-619"):::jobProd
    JOB710009("[production]MOD-TEST-620<br/>蓝图: MOD-TEST-620"):::jobProd
    JOB710010("[production]MOD-TEST-621<br/>蓝图: MOD-TEST-621"):::jobProd
    JOB710011("[production]MOD-TEST-622<br/>蓝图: MOD-TEST-622"):::jobProd
    JOB710012("[production]MOD-TEST-623<br/>蓝图: MOD-TEST-623"):::jobProd
    JOB710013("[production]MOD-TEST-624<br/>蓝图: MOD-TEST-624"):::jobProd
    JOB710014("[production]MOD-TEST-625<br/>蓝图: MOD-TEST-625"):::jobProd
    JOB710015("[production]MOD-TEST-626<br/>蓝图: MOD-TEST-626"):::jobProd
    JOB710016("[production]MOD-TEST-627<br/>蓝图: MOD-TEST-627"):::jobProd
    JOB710017("[production]MOD-TEST-628<br/>蓝图: MOD-TEST-628"):::jobProd
    JOB710018("[production]MOD-TEST-629<br/>蓝图: MOD-TEST-629"):::jobProd
    JOB710019("[production]MOD-TEST-630<br/>蓝图: MOD-TEST-630"):::jobProd
    JOB710020("[production]MOD-TEST-631<br/>蓝图: MOD-TEST-631"):::jobProd
    JOB710021("[production]MOD-TEST-633<br/>蓝图: MOD-TEST-633"):::jobProd
    JOB710022("[production]MOD-TEST-634<br/>蓝图: MOD-TEST-634"):::jobProd
    JOB710023("[production]MOD-TEST-635<br/>蓝图: MOD-TEST-635"):::jobProd
    JOB710024("[production]MOD-TEST-636<br/>蓝图: MOD-TEST-636"):::jobProd
    JOB710025("[production]MOD-TEST-637<br/>蓝图: MOD-TEST-637"):::jobProd
    JOB710026("[production]MOD-TEST-639<br/>蓝图: MOD-TEST-639"):::jobProd
    JOB710027("[production]MOD-TEST-640<br/>蓝图: MOD-TEST-640"):::jobProd
    JOB710028("[production]MOD-TEST-641<br/>蓝图: MOD-TEST-641"):::jobProd
    JOB710029("[production]MOD-TEST-642<br/>蓝图: MOD-TEST-642"):::jobProd
    JOB710030("[production]MOD-TEST-643<br/>蓝图: MOD-TEST-643"):::jobProd
    JOB710031("[production]MOD-TEST-644<br/>蓝图: MOD-TEST-644"):::jobProd
    JOB710032("[production]MOD-TEST-646<br/>蓝图: MOD-TEST-646"):::jobProd
    JOB710033("[production]MOD-TEST-647<br/>蓝图: MOD-TEST-647"):::jobProd
    JOB710034("[production]MOD-TEST-648<br/>蓝图: MOD-TEST-648"):::jobProd
    JOB710035("[production]MOD-TEST-649<br/>蓝图: MOD-TEST-649"):::jobProd
    JOB710036("[production]MOD-TEST-651<br/>蓝图: MOD-TEST-651"):::jobProd
    JOB710037("[production]MOD-TEST-652<br/>蓝图: MOD-TEST-652"):::jobProd
    JOB710038("[production]MOD-TEST-653<br/>蓝图: MOD-TEST-653"):::jobProd
    JOB710039("[production]MOD-TEST-654<br/>蓝图: MOD-TEST-654"):::jobProd
    JOB710040("[production]MOD-TEST-655<br/>蓝图: MOD-TEST-655"):::jobProd
    JOB710041("[production]MOD-TEST-660<br/>蓝图: MOD-TEST-660"):::jobProd
    JOB710042("[production]MOD-TEST-661<br/>蓝图: MOD-TEST-661"):::jobProd
    JOB710043("[production]MOD-TEST-662<br/>蓝图: MOD-TEST-662"):::jobProd
    JOB710044("[production]MOD-TEST-663<br/>蓝图: MOD-TEST-663"):::jobProd
    JOB710045("[production]MOD-TEST-664<br/>蓝图: MOD-TEST-664"):::jobProd
    JOB710046("[production]MOD-TEST-665<br/>蓝图: MOD-TEST-665"):::jobProd
    JOB710047("[production]MOD-TEST-668<br/>蓝图: MOD-TEST-668"):::jobProd
    JOB710048("[production]MOD-TEST-669<br/>蓝图: MOD-TEST-669"):::jobProd
    JOB710049("[production]MOD-TEST-670<br/>蓝图: MOD-TEST-670"):::jobProd
    JOB710050("[production]MOD-TEST-671<br/>蓝图: MOD-TEST-671"):::jobProd
    JOB710051("[production]MOD-TEST-672<br/>蓝图: MOD-TEST-672"):::jobProd
    JOB710052("[production]MOD-TEST-673<br/>蓝图: MOD-TEST-673"):::jobProd
    JOB710053("[production]MOD-TEST-674<br/>蓝图: MOD-TEST-674"):::jobProd
    JOB710054("[production]MOD-TEST-675<br/>蓝图: MOD-TEST-675"):::jobProd
    JOB710055("[production]MOD-TEST-676<br/>蓝图: MOD-TEST-676"):::jobProd
    JOB710056("[production]MOD-TEST-677<br/>蓝图: MOD-TEST-677"):::jobProd
    JOB710057("[production]MOD-TEST-678<br/>蓝图: MOD-TEST-678"):::jobProd
    JOB710058("[production]MOD-TEST-679<br/>蓝图: MOD-TEST-679"):::jobProd
    JOB710059("[production]MOD-TEST-680<br/>蓝图: MOD-TEST-680"):::jobProd
    JOB710060("[production]MOD-TEST-681<br/>蓝图: MOD-TEST-681"):::jobProd
    JOB710061("[production]MOD-TEST-682<br/>蓝图: MOD-TEST-682"):::jobProd
    JOB710062("[production]MOD-TEST-683<br/>蓝图: MOD-TEST-683"):::jobProd
    JOB710063("[production]MOD-TEST-684<br/>蓝图: MOD-TEST-684"):::jobProd
    JOB710064("[production]MOD-TEST-685<br/>蓝图: MOD-TEST-685"):::jobProd
    JOB710065("[production]MOD-TEST-686<br/>蓝图: MOD-TEST-686"):::jobProd
    JOB710066("[production]MOD-TEST-687<br/>蓝图: MOD-TEST-687"):::jobProd
    JOB710067("[production]MOD-TEST-688<br/>蓝图: MOD-TEST-688"):::jobProd
    JOB710068("[production]MOD-TEST-689<br/>蓝图: MOD-TEST-689"):::jobProd
    JOB710069("[production]MOD-TEST-690<br/>蓝图: MOD-TEST-690"):::jobProd
    JOB710070("[production]MOD-TEST-691<br/>蓝图: MOD-TEST-691"):::jobProd
    JOB710071("[production]MOD-TEST-692<br/>蓝图: MOD-TEST-692"):::jobProd
    JOB710072("[production]MOD-TEST-693<br/>蓝图: MOD-TEST-693"):::jobProd
    JOB710073("[production]MOD-TEST-694<br/>蓝图: MOD-TEST-694"):::jobProd
    JOB710074("[production]MOD-TEST-695<br/>蓝图: MOD-TEST-695"):::jobProd
    JOB710075("[production]MOD-TEST-696<br/>蓝图: MOD-TEST-696"):::jobProd
    JOB710076("[production]MOD-TEST-697<br/>蓝图: MOD-TEST-697"):::jobProd
    JOB710077("[production]MOD-TEST-698<br/>蓝图: MOD-TEST-698"):::jobProd
    JOB710078("[production]MOD-TEST-699<br/>蓝图: MOD-TEST-699"):::jobProd
    JOB710079("[production]MOD-TEST-700<br/>蓝图: MOD-TEST-700"):::jobProd
    JOB710080("[production]MOD-TEST-701<br/>蓝图: MOD-TEST-701"):::jobProd
    JOB710081("[production]MOD-TEST-702<br/>蓝图: MOD-TEST-702"):::jobProd
    JOB710082("[production]MOD-TEST-703<br/>蓝图: MOD-TEST-703"):::jobProd
    JOB710083("[production]MOD-TEST-704<br/>蓝图: MOD-TEST-704"):::jobProd
    JOB710084("[production]MOD-TEST-705<br/>蓝图: MOD-TEST-705"):::jobProd
    JOB710085("[production]MOD-TEST-706<br/>蓝图: MOD-TEST-706"):::jobProd
    JOB710086("[production]MOD-TEST-708<br/>蓝图: MOD-TEST-708"):::jobProd
    JOB710087("[production]MOD-TEST-710<br/>蓝图: MOD-TEST-710"):::jobProd
    JOB710088("[production]MOD-TRADING-001<br/>蓝图: MOD-TRADING-001"):::jobProd
    JOB710089("[production]MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY"):::jobProd
    JOB710090("[production]MOD-XLR-003<br/>蓝图: MOD-XLR-003"):::jobProd
    JOB710091("[production]MOD-metric_count_drift<br/>蓝图: MOD-metric_count_drift"):::jobProd
    JOB710092("[production]MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg"):::jobProd
    JOB710093("[production]MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync"):::jobProd
    JOB35838("[design]PLACEHOLDER-MOD-GOV-SYNC-PANORAMA"):::jobDesign
    JOB35636("[design]SH-DB-001"):::jobDesign
    JOB710095("[production]SH-DB-002<br/>蓝图: SH-DB-002"):::jobProd
    JOB591654("[design]SH-GOV-001"):::jobDesign
    JOB710097("[production]SH-GOV-003<br/>蓝图: SH-GOV-003"):::jobProd
    JOB710098("[production]SH-GOV-004<br/>蓝图: SH-GOV-004"):::jobProd
    JOB710099("[production]SH-MAIN-001<br/>蓝图: SH-MAIN-001"):::jobProd
    JOB37268("[design]SYS-MASTER-001"):::jobDesign
    JOB709367("[production]aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-MKT_DATA<br/>功能: 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 ma…"):::jobProd
    JOB709371("[production]check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L04-001<br/>功能: 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits"):::jobProd
    JOB709369("[production]compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算20日动量因子（收益率/相对强度），产出DS-004 factor.mom…"):::jobProd
    JOB709368("[production]compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L02-001<br/>功能: 计算价值因子（PE/PB/股息率等），产出DS-003 factor.valu…"):::jobProd
    JOB709373("[production]execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L06-001<br/>功能: 执行订单（实盘/模拟），产出DS-008 fill.executed + DS…"):::jobProd
    JOB709372("[production]generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-L05-001<br/>功能: 根据信号+风险限额生成目标订单，产出DS-007 order.target"):::jobProd
    JOB709366("[production]ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时<br/>蓝图: MOD-MKT_DATA<br/>功能: 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-00…"):::jobProd
    JOB709370("[production]synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动<br/>功能: 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.co…"):::jobProd
    JOB709366 -->|produces / 产出| DS10947
    JOB709367 -->|produces / 产出| DS10948
    JOB709368 -->|produces / 产出| DS10949
    JOB709369 -->|produces / 产出| DS10950
    JOB709370 -->|produces / 产出| DS10951
    JOB709371 -->|produces / 产出| DS10952
    JOB709372 -->|produces / 产出| DS10953
    JOB709373 -->|produces / 产出| DS10954
    JOB709373 -->|produces / 产出| DS10955
    DS10947 -->|consumed by / 被消费于| JOB709367
    DS10948 -->|consumed by / 被消费于| JOB709368
    DS10948 -->|consumed by / 被消费于| JOB709369
    DS10949 -->|consumed by / 被消费于| JOB709370
    DS10950 -->|consumed by / 被消费于| JOB709370
    DS10951 -->|consumed by / 被消费于| JOB709371
    DS10951 -->|consumed by / 被消费于| JOB709372
    DS10952 -->|consumed by / 被消费于| JOB709372
    DS10953 -->|consumed by / 被消费于| JOB709373

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
    DS10959["[production]backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测模拟成交（symbol/quantity/price/commission…"]:::dsBacktest
    DS10960["[production]backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测净值序列（timestamp/nav/cash/positions），组合…"]:::dsBacktest
    DS10958["[production]backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测目标权重（symbol/target_weight/timestamp），…"]:::dsBacktest
    DS10957["[production]backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]<br/>蓝图: MOD-BT-001<br/>功能: 回测Tick事件（历史tick重放，含timestamp/symbol/pri…"]:::dsBacktest
    JOB709378("[production]backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PI…"):::jobBacktest
    JOB709376("[production]backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 bac…"):::jobBacktest
    JOB709374("[production]backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动<br/>蓝图: MOD-BT-001<br/>功能: 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-…"):::jobBacktest
    JOB709375("[production]backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 …"):::jobBacktest
    JOB709377("[production]backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动<br/>蓝图: MOD-BT-001<br/>功能: 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtes…"):::jobBacktest
    JOB709374 -->|produces / 产出| DS10957
    JOB709375 -->|produces / 产出| DS10958
    JOB709376 -->|produces / 产出| DS10959
    JOB709377 -->|produces / 产出| DS10960
    DS10957 -->|consumed by / 被消费于| JOB709375
    DS10958 -->|consumed by / 被消费于| JOB709376
    DS10959 -->|consumed by / 被消费于| JOB709377
    DS10960 -->|consumed by / 被消费于| JOB709378

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
| DS-10959 | backtest.fills / 回测.模拟成交 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测模拟成交（symbol/quantity/price/commission/slippage），撮合引擎产出 |
| DS-10960 | backtest.nav_series / 回测.净值序列 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测净值序列（timestamp/nav/cash/positions），组合更新产出 |
| DS-10958 | backtest.target_weights / 回测.目标权重 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测目标权重（symbol/target_weight/timestamp），策略根据tick事件生成 |
| DS-10957 | backtest.tick_event / 回测.Tick事件 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测Tick事件（历史tick重放，含timestamp/symbol/price/volume），回测内部类型 |
| DS-10956 | backtest.result / 回测.结果 | production / 生产 | CTR-P1-016 | D_BACKTEST / 回测 | strict / 严格 | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测结果（nav_series/sharpe/max_drawdown/trades），CTR-P1-016 BacktestResult |
| DS-10950 | factor.momentum_20d / 因子.20日动量 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | MOD-L02-001 | production / 生产 | generated / 已生成 | 20日动量因子信号（factor_id/symbol/as_of_date/raw_value/rank_pct），CTR-002 FactorSignal |
| DS-10949 | factor.value_factor / 因子.价值因子 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | MOD-L02-001 | production / 生产 | generated / 已生成 | 价值因子信号（factor_id/symbol/as_of_date/raw_value/normalized_value），CTR-002 FactorSignal |
| DS-10954 | fill.executed / 成交.已成交 | production / 生产 | CTR-005 | D_EX_CORE / 执行核心 | strict / 严格 | MOD-L06-001 | production / 生产 | generated / 已生成 | 成交回报（symbol/quantity/price/commission/timestamp），CTR-005 Fill |
| DS-10948 | market_data.ohlc_bar / 市场数据.OHLC K线 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 聚合OHLC K线（1m/5m/日线，由tick聚合），CTR-001 derived |
| DS-10947 | market_data.tick / 市场数据.Tick行情 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 标准化Tick行情（symbol/timestamp/OHLCV/quality_score），CTR-001 NormalizedMarketData |
| DS-10953 | order.target / 订单.目标订单 | production / 生产 | CTR-004 | D_PF_CORE / 持仓核心 | strict / 严格 | MOD-L05-001 | production / 生产 | generated / 已生成 | 目标订单（symbol/side/quantity/price/order_type），CTR-004 Order |
| DS-10955 | position.snapshot / 持仓.快照 | production / 生产 | CTR-006 | D_EX_CORE / 执行核心 | strict / 严格 | MOD-L06-001 | production / 生产 | generated / 已生成 | 持仓快照（symbol/quantity/avg_cost/market_value/timestamp），CTR-006 PositionSnapshot |
| DS-10952 | risk.limits / 风险.限额 | production / 生产 | CTR-003 | D_RISK / 风险 | strict / 严格 | MOD-L04-001 | production / 生产 | generated / 已生成 | 风险限额（max_position/max_drawdown/exposure_limits），CTR-003 RiskLimits |
| DS-10951 | signal.composite / 信号.合成信号 | production / 生产 | CTR-P1-015 | D_SIGLEGACY / 信号(legacy) | strict / 严格 | - | production / 生产 | generated / 已生成 | 合成交易信号（多因子加权/截面排名/置信度），CTR-P1-015 SynthesizedSignal |

## Job 清单（自动生成 · 生成器: generate_dataflow_diagram.py）

| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |
|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|------------------|---------------------------|--------------------|----------|
| JOB-709378 | backtest.calc_metrics / 回测.计算指标 | backtest_internal / 回测内部 | src/zephyr/backtest/metrics.py | manual / 手动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测指标计算（Sharpe/MaxDrawdown/胜率等，含DSR修正+PIT校验），产出DS-010 backtest.result |
| JOB-709376 | backtest.match_fills / 回测.撮合成交 | backtest_internal / 回测内部 | src/zephyr/backtest/matching_logic.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测撮合引擎（根据目标权重模拟成交，含滑点/手续费），产出DS-013 backtest.fills |
| JOB-709374 | backtest.replay_ticks / 回测.Tick重放 | backtest_internal / 回测内部 | src/zephyr/backtest/tick_replay.py | manual / 手动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 历史Tick重放（从DS-001读取历史tick，按时间顺序重放），产出DS-011 backtest.tick_event |
| JOB-709375 | backtest.run_event_driven / 回测.事件驱动运行 | backtest_internal / 回测内部 | src/zephyr/backtest/event_engine.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 事件驱动回测引擎（消费tick事件，运行策略生成目标权重），产出DS-012 backtest.target_weights |
| JOB-709377 | backtest.update_portfolio / 回测.更新组合 | backtest_internal / 回测内部 | src/zephyr/backtest/portfolio.py | event_driven / 事件驱动 | backtest_tick | MOD-BT-001 | production / 生产 | generated / 已生成 | 回测组合更新（根据成交更新持仓/现金/净值），产出DS-014 backtest.nav_series |
| JOB-709379 | CFG-rule-enforcement-registry | production / 生产 | - | - | - | CFG-rule-enforcement-registry | production / 生产 | stable | - |
| JOB-709380 | CFG-rule-registry-collection | production / 生产 | - | - | - | CFG-rule-registry-collection | production / 生产 | stable | - |
| JOB-709381 | CFG-scripts-registry | production / 生产 | - | - | - | CFG-scripts-registry | production / 生产 | stable | - |
| JOB-709382 | CFG-test-suite-registry | production / 生产 | - | - | - | CFG-test-suite-registry | production / 生产 | stable | - |
| JOB-709383 | MOD-ALT_DATA | production / 生产 | - | - | - | MOD-ALT_DATA | production / 生产 | generated / 已生成 | - |
| JOB-35951 | MOD-ARCH-BIZDB | production / 生产 | - | - | - | MOD-ARCH-BIZDB | design / 设计 | planned | - |
| JOB-709384 | MOD-AUTONOMY_CORE | production / 生产 | - | - | - | MOD-AUTONOMY_CORE | production / 生产 | stable | - |
| JOB-709385 | MOD-BT-001 | production / 生产 | - | - | - | MOD-BT-001 | production / 生产 | stable | - |
| JOB-709386 | MOD-BT-017 | production / 生产 | - | - | - | MOD-BT-017 | production / 生产 | stable | - |
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
| JOB-709397 | MOD-CROSS_ASSET | production / 生产 | - | - | - | MOD-CROSS_ASSET | production / 生产 | generated / 已生成 | - |
| JOB-709398 | MOD-D5_ARCH_TOOLS | production / 生产 | - | - | - | MOD-D5_ARCH_TOOLS | production / 生产 | generated / 已生成 | - |
| JOB-709399 | MOD-DATABASE | production / 生产 | - | - | - | MOD-DATABASE | production / 生产 | generated / 已生成 | - |
| JOB-671597 | MOD-DATA_ENG | production / 生产 | - | - | - | MOD-DATA_ENG | design / 设计 | generated / 已生成 | - |
| JOB-709401 | MOD-DATA_GOV | production / 生产 | - | - | - | MOD-DATA_GOV | production / 生产 | generated / 已生成 | - |
| JOB-709402 | MOD-DATA_GOV-001 | production / 生产 | - | - | - | MOD-DATA_GOV-001 | production / 生产 | stable | - |
| JOB-709403 | MOD-DATA_GOV-002 | production / 生产 | - | - | - | MOD-DATA_GOV-002 | production / 生产 | stable | - |
| JOB-709404 | MOD-DATA_GOV-003 | production / 生产 | - | - | - | MOD-DATA_GOV-003 | production / 生产 | stable | - |
| JOB-709405 | MOD-DATA_SEC | production / 生产 | - | - | - | MOD-DATA_SEC | production / 生产 | generated / 已生成 | - |
| JOB-709406 | MOD-DIGITAL_TWIN | production / 生产 | - | - | - | MOD-DIGITAL_TWIN | production / 生产 | generated / 已生成 | - |
| JOB-709407 | MOD-D_GOV_SCRIPTS | production / 生产 | - | - | - | MOD-D_GOV_SCRIPTS | production / 生产 | generated / 已生成 | - |
| JOB-709408 | MOD-E2E-001 | production / 生产 | - | - | - | MOD-E2E-001 | production / 生产 | generated / 已生成 | - |
| JOB-712063 | MOD-EX-001 | production / 生产 | - | - | - | MOD-EX-001 | design / 设计 | planned | - |
| JOB-709409 | MOD-EXEC_SIM | production / 生产 | - | - | - | MOD-EXEC_SIM | production / 生产 | generated / 已生成 | - |
| JOB-709410 | MOD-EX_SOR | production / 生产 | - | - | - | MOD-EX_SOR | production / 生产 | generated / 已生成 | - |
| JOB-709411 | MOD-FEEDBACK-014 | production / 生产 | - | - | - | MOD-FEEDBACK-014 | production / 生产 | stable | - |
| JOB-35940 | MOD-FEEDBACK_LOOP | production / 生产 | - | - | - | MOD-FEEDBACK_LOOP | design / 设计 | planned | - |
| JOB-35578 | MOD-GATE_ENGINE | production / 生产 | - | - | - | MOD-GATE_ENGINE | design / 设计 | planned | - |
| JOB-709414 | MOD-GOV-008 | production / 生产 | - | - | - | MOD-GOV-008 | production / 生产 | generated / 已生成 | - |
| JOB-709415 | MOD-GOV-019 | production / 生产 | - | - | - | MOD-GOV-019 | production / 生产 | stable | - |
| JOB-709416 | MOD-GOV-029 | production / 生产 | - | - | - | MOD-GOV-029 | production / 生产 | generated / 已生成 | - |
| JOB-709417 | MOD-GOV-041 | production / 生产 | - | - | - | MOD-GOV-041 | production / 生产 | generated / 已生成 | - |
| JOB-36856 | MOD-GOV-ALIGN-PANORAMAS | production / 生产 | - | - | - | MOD-GOV-ALIGN-PANORAMAS | design / 设计 | stable | - |
| JOB-709418 | MOD-GOV-AUDIT | production / 生产 | - | - | - | MOD-GOV-AUDIT | production / 生产 | stable | - |
| JOB-709419 | MOD-GOV-CG | production / 生产 | - | - | - | MOD-GOV-CG | production / 生产 | stable | - |
| JOB-709420 | MOD-GOV-DOCS | production / 生产 | - | - | - | MOD-GOV-DOCS | production / 生产 | generated / 已生成 | - |
| JOB-139307 | MOD-GOV-HEARTBEAT | production / 生产 | - | - | - | MOD-GOV-HEARTBEAT | design / 设计 | planned | - |
| JOB-709421 | MOD-GOV-SCRIPTS | production / 生产 | - | - | - | MOD-GOV-SCRIPTS | production / 生产 | stable | - |
| JOB-709422 | MOD-GOV-backfill_checker | production / 生产 | - | - | - | MOD-GOV-backfill_checker | production / 生产 | generated / 已生成 | - |
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
| JOB-709424 | MOD-GOV_AGENT_RBAC | production / 生产 | - | - | - | MOD-GOV_AGENT_RBAC | production / 生产 | generated / 已生成 | - |
| JOB-709425 | MOD-GOV_ALIGN_PANORAMAS | production / 生产 | - | - | - | MOD-GOV_ALIGN_PANORAMAS | production / 生产 | generated / 已生成 | - |
| JOB-709426 | MOD-GOV_ANALYZE_CHANGE_IMPACT | production / 生产 | - | - | - | MOD-GOV_ANALYZE_CHANGE_IMPACT | production / 生产 | generated / 已生成 | - |
| JOB-709427 | MOD-GOV_ANALYZE_ORPHAN_CONSUMERS | production / 生产 | - | - | - | MOD-GOV_ANALYZE_ORPHAN_CONSUMERS | production / 生产 | generated / 已生成 | - |
| JOB-709428 | MOD-GOV_ARCH_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_ARCH_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709429 | MOD-GOV_ASYNC_RUNTIME | production / 生产 | - | - | - | MOD-GOV_ASYNC_RUNTIME | production / 生产 | generated / 已生成 | - |
| JOB-709430 | MOD-GOV_AUDIT | production / 生产 | - | - | - | MOD-GOV_AUDIT | production / 生产 | generated / 已生成 | - |
| JOB-709431 | MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | production / 生产 | - | - | - | MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | production / 生产 | generated / 已生成 | - |
| JOB-709432 | MOD-GOV_AUDIT_TRAIL | production / 生产 | - | - | - | MOD-GOV_AUDIT_TRAIL | production / 生产 | generated / 已生成 | - |
| JOB-709433 | MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | production / 生产 | - | - | - | MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | production / 生产 | generated / 已生成 | - |
| JOB-709434 | MOD-GOV_BARE_GETENV_GATE | production / 生产 | - | - | - | MOD-GOV_BARE_GETENV_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709435 | MOD-GOV_BARE_SQL_GATE | production / 生产 | - | - | - | MOD-GOV_BARE_SQL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709436 | MOD-GOV_BATCHED_AUTO_COMMITTER | production / 生产 | - | - | - | MOD-GOV_BATCHED_AUTO_COMMITTER | production / 生产 | generated / 已生成 | - |
| JOB-709437 | MOD-GOV_BEHAVIORAL_ADMISSION | production / 生产 | - | - | - | MOD-GOV_BEHAVIORAL_ADMISSION | production / 生产 | generated / 已生成 | - |
| JOB-709438 | MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709439 | MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | production / 生产 | - | - | - | MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | production / 生产 | generated / 已生成 | - |
| JOB-709440 | MOD-GOV_CAPABILITY_OVERLAP_GATE | production / 生产 | - | - | - | MOD-GOV_CAPABILITY_OVERLAP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709441 | MOD-GOV_CHECK_ANY_ABUSE | production / 生产 | - | - | - | MOD-GOV_CHECK_ANY_ABUSE | production / 生产 | generated / 已生成 | - |
| JOB-709442 | MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | production / 生产 | - | - | - | MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | production / 生产 | generated / 已生成 | - |
| JOB-709443 | MOD-GOV_CHECK_RULE_COVERAGE | production / 生产 | - | - | - | MOD-GOV_CHECK_RULE_COVERAGE | production / 生产 | generated / 已生成 | - |
| JOB-709444 | MOD-GOV_CHECK_VOCAB_HARDCODE | production / 生产 | - | - | - | MOD-GOV_CHECK_VOCAB_HARDCODE | production / 生产 | generated / 已生成 | - |
| JOB-709445 | MOD-GOV_CH_BATCH_SIZE_GATE | production / 生产 | - | - | - | MOD-GOV_CH_BATCH_SIZE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709446 | MOD-GOV_CH_VERSION_COL_GATE | production / 生产 | - | - | - | MOD-GOV_CH_VERSION_COL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709447 | MOD-GOV_CLAIM_REQUIRED_GATE | production / 生产 | - | - | - | MOD-GOV_CLAIM_REQUIRED_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709448 | MOD-GOV_CODE_QUALITY_DOMAIN | production / 生产 | - | - | - | MOD-GOV_CODE_QUALITY_DOMAIN | production / 生产 | generated / 已生成 | - |
| JOB-709449 | MOD-GOV_COMMIT_GATES | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATES | production / 生产 | stable | - |
| JOB-709450 | MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | production / 生产 | stable | - |
| JOB-709451 | MOD-GOV_COMMIT_GATE_REGISTRY | production / 生产 | - | - | - | MOD-GOV_COMMIT_GATE_REGISTRY | production / 生产 | stable | - |
| JOB-709452 | MOD-GOV_COMMON | production / 生产 | - | - | - | MOD-GOV_COMMON | production / 生产 | generated / 已生成 | - |
| JOB-709453 | MOD-GOV_CONCURRENT_WRITE_TEST | production / 生产 | - | - | - | MOD-GOV_CONCURRENT_WRITE_TEST | production / 生产 | generated / 已生成 | - |
| JOB-709454 | MOD-GOV_CREATE_GUARD | production / 生产 | - | - | - | MOD-GOV_CREATE_GUARD | production / 生产 | generated / 已生成 | - |
| JOB-709455 | MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | production / 生产 | - | - | - | MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | production / 生产 | generated / 已生成 | - |
| JOB-709456 | MOD-GOV_DANGLING_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_DANGLING_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709457 | MOD-GOV_DATABASE_SERVICE | production / 生产 | - | - | - | MOD-GOV_DATABASE_SERVICE | production / 生产 | generated / 已生成 | - |
| JOB-709458 | MOD-GOV_DATAFLOW_DIAGRAM | production / 生产 | - | - | - | MOD-GOV_DATAFLOW_DIAGRAM | production / 生产 | generated / 已生成 | - |
| JOB-709459 | MOD-GOV_DEEPSEEK_API | production / 生产 | - | - | - | MOD-GOV_DEEPSEEK_API | production / 生产 | generated / 已生成 | - |
| JOB-709460 | MOD-GOV_DEFERRED_EDGES | production / 生产 | - | - | - | MOD-GOV_DEFERRED_EDGES | production / 生产 | generated / 已生成 | - |
| JOB-709461 | MOD-GOV_DEFERRED_REG | production / 生产 | - | - | - | MOD-GOV_DEFERRED_REG | production / 生产 | generated / 已生成 | - |
| JOB-709462 | MOD-GOV_DEMO_EE_PIPELINE | production / 生产 | - | - | - | MOD-GOV_DEMO_EE_PIPELINE | production / 生产 | generated / 已生成 | - |
| JOB-709463 | MOD-GOV_DETECT_CAUSAL_CONFLICTS | production / 生产 | - | - | - | MOD-GOV_DETECT_CAUSAL_CONFLICTS | production / 生产 | generated / 已生成 | - |
| JOB-709464 | MOD-GOV_DIFF_HELPERS | production / 生产 | - | - | - | MOD-GOV_DIFF_HELPERS | production / 生产 | generated / 已生成 | - |
| JOB-709465 | MOD-GOV_DM200912_QUERY_DOMAINS | production / 生产 | - | - | - | MOD-GOV_DM200912_QUERY_DOMAINS | production / 生产 | generated / 已生成 | - |
| JOB-709466 | MOD-GOV_DM200916_WRITE_DIRECT | production / 生产 | - | - | - | MOD-GOV_DM200916_WRITE_DIRECT | production / 生产 | generated / 已生成 | - |
| JOB-709467 | MOD-GOV_DOC_REF_BROKEN_GATE | production / 生产 | - | - | - | MOD-GOV_DOC_REF_BROKEN_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709468 | MOD-GOV_DOMAIN_FK_GATE | production / 生产 | - | - | - | MOD-GOV_DOMAIN_FK_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709469 | MOD-GOV_DQ | production / 生产 | - | - | - | MOD-GOV_DQ | production / 生产 | generated / 已生成 | - |
| JOB-709470 | MOD-GOV_EMERGENCY_COMMIT | production / 生产 | - | - | - | MOD-GOV_EMERGENCY_COMMIT | production / 生产 | stable | - |
| JOB-709471 | MOD-GOV_EMPTY_HANDLER_GATE | production / 生产 | - | - | - | MOD-GOV_EMPTY_HANDLER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709472 | MOD-GOV_ENFORCEMENT | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT | production / 生产 | generated / 已生成 | - |
| JOB-709473 | MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | production / 生产 | stable | - |
| JOB-709474 | MOD-GOV_ENFORCEMENT_WORKTREE_POOL | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_WORKTREE_POOL | production / 生产 | stable | - |
| JOB-709475 | MOD-GOV_ENFORCEMENT_worktree_lifecycle | production / 生产 | - | - | - | MOD-GOV_ENFORCEMENT_worktree_lifecycle | production / 生产 | generated / 已生成 | - |
| JOB-709476 | MOD-GOV_ERROR_PATTERN_CONSUMER | production / 生产 | - | - | - | MOD-GOV_ERROR_PATTERN_CONSUMER | production / 生产 | stable | - |
| JOB-709477 | MOD-GOV_ERROR_PATTERN_LIBRARY | production / 生产 | - | - | - | MOD-GOV_ERROR_PATTERN_LIBRARY | production / 生产 | stable | - |
| JOB-709478 | MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE | production / 生产 | - | - | - | MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709479 | MOD-GOV_F3_AUTO_INTEGRATION | production / 生产 | - | - | - | MOD-GOV_F3_AUTO_INTEGRATION | production / 生产 | generated / 已生成 | - |
| JOB-709480 | MOD-GOV_F3_EXTREME | production / 生产 | - | - | - | MOD-GOV_F3_EXTREME | production / 生产 | generated / 已生成 | - |
| JOB-709481 | MOD-GOV_FILE_COPY_GATE | production / 生产 | - | - | - | MOD-GOV_FILE_COPY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709482 | MOD-GOV_FUNCTION_DUP_GATE | production / 生产 | - | - | - | MOD-GOV_FUNCTION_DUP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709483 | MOD-GOV_GATE_CACHE | production / 生产 | - | - | - | MOD-GOV_GATE_CACHE | production / 生产 | generated / 已生成 | - |
| JOB-709484 | MOD-GOV_GENERATE_ASSET_CATALOG | production / 生产 | - | - | - | MOD-GOV_GENERATE_ASSET_CATALOG | production / 生产 | generated / 已生成 | - |
| JOB-709485 | MOD-GOV_GENERATE_CAPABILITY_HEATMAP | production / 生产 | - | - | - | MOD-GOV_GENERATE_CAPABILITY_HEATMAP | production / 生产 | generated / 已生成 | - |
| JOB-709486 | MOD-GOV_GENERATE_CAPACITY_REPORT | production / 生产 | - | - | - | MOD-GOV_GENERATE_CAPACITY_REPORT | production / 生产 | generated / 已生成 | - |
| JOB-709487 | MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS | production / 生产 | - | - | - | MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS | production / 生产 | generated / 已生成 | - |
| JOB-709488 | MOD-GOV_GENERATE_CONTRACT_CATALOG | production / 生产 | - | - | - | MOD-GOV_GENERATE_CONTRACT_CATALOG | production / 生产 | generated / 已生成 | - |
| JOB-709489 | MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX | production / 生产 | - | - | - | MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX | production / 生产 | generated / 已生成 | - |
| JOB-709490 | MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | production / 生产 | - | - | - | MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | production / 生产 | generated / 已生成 | - |
| JOB-709491 | MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION | production / 生产 | - | - | - | MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION | production / 生产 | generated / 已生成 | - |
| JOB-709492 | MOD-GOV_GENERATE_DOMAIN_DOC | production / 生产 | - | - | - | MOD-GOV_GENERATE_DOMAIN_DOC | production / 生产 | generated / 已生成 | - |
| JOB-709493 | MOD-GOV_GENERATE_DOMAIN_INDEX | production / 生产 | - | - | - | MOD-GOV_GENERATE_DOMAIN_INDEX | production / 生产 | generated / 已生成 | - |
| JOB-709494 | MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY | production / 生产 | - | - | - | MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY | production / 生产 | generated / 已生成 | - |
| JOB-709495 | MOD-GOV_GENERATE_NAVIGATION_INDEX | production / 生产 | - | - | - | MOD-GOV_GENERATE_NAVIGATION_INDEX | production / 生产 | generated / 已生成 | - |
| JOB-709496 | MOD-GOV_GENERATE_PATH_TREE | production / 生产 | - | - | - | MOD-GOV_GENERATE_PATH_TREE | production / 生产 | generated / 已生成 | - |
| JOB-709497 | MOD-GOV_GIT_HELPERS | production / 生产 | - | - | - | MOD-GOV_GIT_HELPERS | production / 生产 | generated / 已生成 | - |
| JOB-709498 | MOD-GOV_GIT_PERFORMANCE_MONITOR | production / 生产 | - | - | - | MOD-GOV_GIT_PERFORMANCE_MONITOR | production / 生产 | stable | - |
| JOB-709499 | MOD-GOV_GOD_CLASS_GATE | production / 生产 | - | - | - | MOD-GOV_GOD_CLASS_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709500 | MOD-GOV_GROUP_ORPHAN_MODULES | production / 生产 | - | - | - | MOD-GOV_GROUP_ORPHAN_MODULES | production / 生产 | generated / 已生成 | - |
| JOB-709501 | MOD-GOV_GUC_TRIGGER_FIX | production / 生产 | - | - | - | MOD-GOV_GUC_TRIGGER_FIX | production / 生产 | generated / 已生成 | - |
| JOB-709502 | MOD-GOV_HARDCODED_URL_GATE | production / 生产 | - | - | - | MOD-GOV_HARDCODED_URL_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709503 | MOD-GOV_HEALTH_SCORE_CALCULATOR | production / 生产 | - | - | - | MOD-GOV_HEALTH_SCORE_CALCULATOR | production / 生产 | stable | - |
| JOB-709504 | MOD-GOV_HEALTH_SMOKE | production / 生产 | - | - | - | MOD-GOV_HEALTH_SMOKE | production / 生产 | generated / 已生成 | - |
| JOB-709505 | MOD-GOV_HEARTBEAT_DAEMON | production / 生产 | - | - | - | MOD-GOV_HEARTBEAT_DAEMON | production / 生产 | stable | - |
| JOB-709506 | MOD-GOV_HEARTBEAT_DAEMON_TEST | production / 生产 | - | - | - | MOD-GOV_HEARTBEAT_DAEMON_TEST | production / 生产 | generated / 已生成 | - |
| JOB-709507 | MOD-GOV_HELD_OVERLAP_GATE | production / 生产 | - | - | - | MOD-GOV_HELD_OVERLAP_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709508 | MOD-GOV_HIGH_COMPLEXITY_GATE | production / 生产 | - | - | - | MOD-GOV_HIGH_COMPLEXITY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709509 | MOD-GOV_ID_UNIQUENESS_GATE | production / 生产 | - | - | - | MOD-GOV_ID_UNIQUENESS_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709510 | MOD-GOV_IMPORT_DIRECTION_GATE | production / 生产 | - | - | - | MOD-GOV_IMPORT_DIRECTION_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709511 | MOD-GOV_LONG_PARAM_LIST_GATE | production / 生产 | - | - | - | MOD-GOV_LONG_PARAM_LIST_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709512 | MOD-GOV_MIGRATE_METADATA | production / 生产 | - | - | - | MOD-GOV_MIGRATE_METADATA | production / 生产 | generated / 已生成 | - |
| JOB-709513 | MOD-GOV_MODULE_ID_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_MODULE_ID_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709514 | MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | production / 生产 | - | - | - | MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709515 | MOD-GOV_ORPHAN_MODULE_GATE | production / 生产 | - | - | - | MOD-GOV_ORPHAN_MODULE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709516 | MOD-GOV_PANORAMA_ALIGNMENT_GATE | production / 生产 | - | - | - | MOD-GOV_PANORAMA_ALIGNMENT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709517 | MOD-GOV_PERF_DEPGRAPH_BASELINE | production / 生产 | - | - | - | MOD-GOV_PERF_DEPGRAPH_BASELINE | production / 生产 | generated / 已生成 | - |
| JOB-709518 | MOD-GOV_PERM_TRIGGER_GATE | production / 生产 | - | - | - | MOD-GOV_PERM_TRIGGER_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709519 | MOD-GOV_PRE_WRITE_GATE | production / 生产 | - | - | - | MOD-GOV_PRE_WRITE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709520 | MOD-GOV_R5_DIGIT_SUFFIX_GATE | production / 生产 | - | - | - | MOD-GOV_R5_DIGIT_SUFFIX_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709521 | MOD-GOV_RECONCILE_RUNNER | production / 生产 | - | - | - | MOD-GOV_RECONCILE_RUNNER | production / 生产 | stable | - |
| JOB-709522 | MOD-GOV_RECONCILE_WORKER | production / 生产 | - | - | - | MOD-GOV_RECONCILE_WORKER | production / 生产 | stable | - |
| JOB-709523 | MOD-GOV_RECONCILIATION_REGISTRY | production / 生产 | - | - | - | MOD-GOV_RECONCILIATION_REGISTRY | production / 生产 | stable | - |
| JOB-709524 | MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | production / 生产 | - | - | - | MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709525 | MOD-GOV_REPAIR | production / 生产 | - | - | - | MOD-GOV_REPAIR | production / 生产 | generated / 已生成 | - |
| JOB-709526 | MOD-GOV_RESILIENCE_GOVERNANCE | production / 生产 | - | - | - | MOD-GOV_RESILIENCE_GOVERNANCE | production / 生产 | generated / 已生成 | - |
| JOB-709527 | MOD-GOV_ROLLBACK | production / 生产 | - | - | - | MOD-GOV_ROLLBACK | production / 生产 | generated / 已生成 | - |
| JOB-709528 | MOD-GOV_RULE_DOMAIN | production / 生产 | - | - | - | MOD-GOV_RULE_DOMAIN | production / 生产 | generated / 已生成 | - |
| JOB-709529 | MOD-GOV_RULE_EXECUTION_PAIRING_GATE | production / 生产 | - | - | - | MOD-GOV_RULE_EXECUTION_PAIRING_GATE | production / 生产 | stable | - |
| JOB-709530 | MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE | production / 生产 | - | - | - | MOD-GOV_RULE_FOUR_WAY_ALIGNMENT_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709531 | MOD-GOV_RULE_PATTERNS | production / 生产 | - | - | - | MOD-GOV_RULE_PATTERNS | production / 生产 | stable | - |
| JOB-709532 | MOD-GOV_RULING_REFERENCE_GATE | production / 生产 | - | - | - | MOD-GOV_RULING_REFERENCE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709533 | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | production / 生产 | - | - | - | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT | production / 生产 | stable | - |
| JOB-709534 | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | production / 生产 | - | - | - | MOD-GOV_RUNTIME_VIOLATION_SNAPSHOT_RECONCILER | production / 生产 | stable | - |
| JOB-709535 | MOD-GOV_SCAN_CONSUMERS_ACCURACY | production / 生产 | - | - | - | MOD-GOV_SCAN_CONSUMERS_ACCURACY | production / 生产 | generated / 已生成 | - |
| JOB-709536 | MOD-GOV_SCAN_DEBT | production / 生产 | - | - | - | MOD-GOV_SCAN_DEBT | production / 生产 | generated / 已生成 | - |
| JOB-709537 | MOD-GOV_SCRIPTS | production / 生产 | - | - | - | MOD-GOV_SCRIPTS | production / 生产 | generated / 已生成 | - |
| JOB-709538 | MOD-GOV_SCRIPTS_ARCH | production / 生产 | - | - | - | MOD-GOV_SCRIPTS_ARCH | production / 生产 | stable | - |
| JOB-709539 | MOD-GOV_SECURITY_GOVERNANCE | production / 生产 | - | - | - | MOD-GOV_SECURITY_GOVERNANCE | production / 生产 | generated / 已生成 | - |
| JOB-709540 | MOD-GOV_SESSION_CLAIM | production / 生产 | - | - | - | MOD-GOV_SESSION_CLAIM | production / 生产 | generated / 已生成 | - |
| JOB-709541 | MOD-GOV_SESSION_REQUIRED_GATE | production / 生产 | - | - | - | MOD-GOV_SESSION_REQUIRED_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709542 | MOD-GOV_SESSION_WORKTREE | production / 生产 | - | - | - | MOD-GOV_SESSION_WORKTREE | production / 生产 | stable | - |
| JOB-709543 | MOD-GOV_SILENT_FAILURE_REGRESSION | production / 生产 | - | - | - | MOD-GOV_SILENT_FAILURE_REGRESSION | production / 生产 | generated / 已生成 | - |
| JOB-709544 | MOD-GOV_SSOT_REDEFINITION_GATE | production / 生产 | - | - | - | MOD-GOV_SSOT_REDEFINITION_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709545 | MOD-GOV_SYNC_PANORAMA | production / 生产 | - | - | - | MOD-GOV_SYNC_PANORAMA | production / 生产 | generated / 已生成 | - |
| JOB-709546 | MOD-GOV_SYNC_SAVEPOINT_TEST | production / 生产 | - | - | - | MOD-GOV_SYNC_SAVEPOINT_TEST | production / 生产 | generated / 已生成 | - |
| JOB-709547 | MOD-GOV_TASK_SYSTEM_RED_TEAM | production / 生产 | - | - | - | MOD-GOV_TASK_SYSTEM_RED_TEAM | production / 生产 | generated / 已生成 | - |
| JOB-709548 | MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | production / 生产 | - | - | - | MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | production / 生产 | generated / 已生成 | - |
| JOB-709549 | MOD-GOV_TEST_EMERGENCY_COMMIT | production / 生产 | - | - | - | MOD-GOV_TEST_EMERGENCY_COMMIT | production / 生产 | generated / 已生成 | - |
| JOB-709550 | MOD-GOV_TEST_RECONCILE_ASYNC | production / 生产 | - | - | - | MOD-GOV_TEST_RECONCILE_ASYNC | production / 生产 | generated / 已生成 | - |
| JOB-709551 | MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | production / 生产 | - | - | - | MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | production / 生产 | generated / 已生成 | - |
| JOB-709552 | MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE | production / 生产 | - | - | - | MOD-GOV_TEST_SOURCE_CONSISTENCY_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709553 | MOD-GOV_VERIFY_KEY_IMPORTS | production / 生产 | - | - | - | MOD-GOV_VERIFY_KEY_IMPORTS | production / 生产 | generated / 已生成 | - |
| JOB-709554 | MOD-GOV_VOCAB_HARDCODE_GATE | production / 生产 | - | - | - | MOD-GOV_VOCAB_HARDCODE_GATE | production / 生产 | generated / 已生成 | - |
| JOB-709555 | MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | production / 生产 | - | - | - | MOD-GOV_WORKSPACE_HYGIENE_RECONCILER | production / 生产 | stable | - |
| JOB-709556 | MOD-GOV_WORKTREE_MANAGER | production / 生产 | - | - | - | MOD-GOV_WORKTREE_MANAGER | production / 生产 | stable | - |
| JOB-709557 | MOD-GOV_YAML_SYNC_ERROR_CLASS | production / 生产 | - | - | - | MOD-GOV_YAML_SYNC_ERROR_CLASS | production / 生产 | generated / 已生成 | - |
| JOB-321362 | MOD-GOV_blueprint_status_transition_reconciler | production / 生产 | - | - | - | MOD-GOV_blueprint_status_transition_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-321311 | MOD-GOV_cross_layer_contract_signature_reconciler | production / 生产 | - | - | - | MOD-GOV_cross_layer_contract_signature_reconciler | design / 设计 | generated / 已生成 | - |
| JOB-709558 | MOD-INF-001 | production / 生产 | - | - | - | MOD-INF-001 | production / 生产 | generated / 已生成 | - |
| JOB-709559 | MOD-INF-002 | production / 生产 | - | - | - | MOD-INF-002 | production / 生产 | generated / 已生成 | - |
| JOB-709560 | MOD-INF-003 | production / 生产 | - | - | - | MOD-INF-003 | production / 生产 | stable | - |
| JOB-36357 | MOD-INF-005 | production / 生产 | - | - | - | MOD-INF-005 | design / 设计 | planned | - |
| JOB-37139 | MOD-INF-009 | production / 生产 | - | - | - | MOD-INF-009 | design / 设计 | planned | - |
| JOB-35565 | MOD-INF-011 | production / 生产 | - | - | - | MOD-INF-011 | design / 设计 | planned | - |
| JOB-709564 | MOD-INF-013 | production / 生产 | - | - | - | MOD-INF-013 | production / 生产 | generated / 已生成 | - |
| JOB-709565 | MOD-INF-014 | production / 生产 | - | - | - | MOD-INF-014 | production / 生产 | stable | - |
| JOB-709566 | MOD-INF-015 | production / 生产 | - | - | - | MOD-INF-015 | production / 生产 | stable | - |
| JOB-35954 | MOD-INF-016 | production / 生产 | - | - | - | MOD-INF-016 | design / 设计 | planned | - |
| JOB-36274 | MOD-INF-017 | production / 生产 | - | - | - | MOD-INF-017 | design / 设计 | planned | - |
| JOB-709569 | MOD-INF-018 | production / 生产 | - | - | - | MOD-INF-018 | production / 生产 | generated / 已生成 | - |
| JOB-37172 | MOD-INF-019 | production / 生产 | - | - | - | MOD-INF-019 | design / 设计 | planned | - |
| JOB-36050 | MOD-INF-020 | production / 生产 | - | - | - | MOD-INF-020 | design / 设计 | planned | - |
| JOB-35903 | MOD-INF-021 | production / 生产 | - | - | - | MOD-INF-021 | design / 设计 | planned | - |
| JOB-36400 | MOD-INF-022 | production / 生产 | - | - | - | MOD-INF-022 | design / 设计 | planned | - |
| JOB-35522 | MOD-INF-023 | production / 生产 | - | - | - | MOD-INF-023 | design / 设计 | planned | - |
| JOB-37193 | MOD-INF-024 | production / 生产 | - | - | - | MOD-INF-024 | design / 设计 | generated / 已生成 | - |
| JOB-709576 | MOD-INF-025 | production / 生产 | - | - | - | MOD-INF-025 | production / 生产 | generated / 已生成 | - |
| JOB-709577 | MOD-INF-026 | production / 生产 | - | - | - | MOD-INF-026 | production / 生产 | stable | - |
| JOB-35574 | MOD-INF-027 | production / 生产 | - | - | - | MOD-INF-027 | design / 设计 | planned | - |
| JOB-36222 | MOD-INF-028 | production / 生产 | - | - | - | MOD-INF-028 | design / 设计 | planned | - |
| JOB-35930 | MOD-INF-029 | production / 生产 | - | - | - | MOD-INF-029 | design / 设计 | planned | - |
| JOB-37217 | MOD-INF-030 | production / 生产 | - | - | - | MOD-INF-030 | design / 设计 | planned | - |
| JOB-37220 | MOD-INF-031 | production / 生产 | - | - | - | MOD-INF-031 | design / 设计 | planned | - |
| JOB-36336 | MOD-INF-033 | production / 生产 | - | - | - | MOD-INF-033 | design / 设计 | planned | - |
| JOB-35554 | MOD-INF-034 | production / 生产 | - | - | - | MOD-INF-034 | design / 设计 | planned | - |
| JOB-709585 | MOD-INF-035 | production / 生产 | - | - | - | MOD-INF-035 | production / 生产 | generated / 已生成 | - |
| JOB-37237 | MOD-INF-036 | production / 生产 | - | - | - | MOD-INF-036 | design / 设计 | planned | - |
| JOB-35538 | MOD-INF-037 | production / 生产 | - | - | - | MOD-INF-037 | design / 设计 | planned | - |
| JOB-709588 | MOD-INF-038 | production / 生产 | - | - | - | MOD-INF-038 | production / 生产 | stable | - |
| JOB-36080 | MOD-INF-039 | production / 生产 | - | - | - | MOD-INF-039 | design / 设计 | planned | - |
| JOB-709590 | MOD-INF-040 | production / 生产 | - | - | - | MOD-INF-040 | production / 生产 | generated / 已生成 | - |
| JOB-709591 | MOD-INF-042 | production / 生产 | - | - | - | MOD-INF-042 | production / 生产 | generated / 已生成 | - |
| JOB-709592 | MOD-INF-043 | production / 生产 | - | - | - | MOD-INF-043 | production / 生产 | generated / 已生成 | - |
| JOB-709593 | MOD-INF-044 | production / 生产 | - | - | - | MOD-INF-044 | production / 生产 | stable | - |
| JOB-35939 | MOD-INFRA_OPS | production / 生产 | - | - | - | MOD-INFRA_OPS | design / 设计 | planned | - |
| JOB-709594 | MOD-INFRA_RUNTIME | production / 生产 | - | - | - | MOD-INFRA_RUNTIME | production / 生产 | generated / 已生成 | - |
| JOB-709595 | MOD-INF_GOV | production / 生产 | - | - | - | MOD-INF_GOV | production / 生产 | generated / 已生成 | - |
| JOB-709596 | MOD-INTEGRATION | production / 生产 | - | - | - | MOD-INTEGRATION | production / 生产 | generated / 已生成 | - |
| JOB-709597 | MOD-L00-001 | production / 生产 | - | - | - | MOD-L00-001 | production / 生产 | generated / 已生成 | - |
| JOB-36157 | MOD-L00-002 | production / 生产 | - | - | - | MOD-L00-002 | design / 设计 | stable | - |
| JOB-35520 | MOD-L00-003 | production / 生产 | - | - | - | MOD-L00-003 | design / 设计 | stable | - |
| JOB-61876 | MOD-L00-004 | production / 生产 | - | - | - | MOD-L00-004 | design / 设计 | generated / 已生成 | - |
| JOB-709599 | MOD-L00-005 | production / 生产 | - | - | - | MOD-L00-005 | production / 生产 | generated / 已生成 | - |
| JOB-709600 | MOD-L00-006 | production / 生产 | - | - | - | MOD-L00-006 | production / 生产 | stable | - |
| JOB-709601 | MOD-L00-007 | production / 生产 | - | - | - | MOD-L00-007 | production / 生产 | generated / 已生成 | - |
| JOB-551909 | MOD-L02-001 | production / 生产 | - | - | - | MOD-L02-001 | design / 设计 | stable | - |
| JOB-709603 | MOD-L02-002 | production / 生产 | - | - | - | MOD-L02-002 | production / 生产 | stable | - |
| JOB-709604 | MOD-L02-003 | production / 生产 | - | - | - | MOD-L02-003 | production / 生产 | stable | - |
| JOB-709605 | MOD-L02-004 | production / 生产 | - | - | - | MOD-L02-004 | production / 生产 | stable | - |
| JOB-709606 | MOD-L02-005 | production / 生产 | - | - | - | MOD-L02-005 | production / 生产 | stable | - |
| JOB-709607 | MOD-L02-006 | production / 生产 | - | - | - | MOD-L02-006 | production / 生产 | stable | - |
| JOB-709608 | MOD-L02-007 | production / 生产 | - | - | - | MOD-L02-007 | production / 生产 | generated / 已生成 | - |
| JOB-709609 | MOD-L02-008 | production / 生产 | - | - | - | MOD-L02-008 | production / 生产 | generated / 已生成 | - |
| JOB-709610 | MOD-L02-009 | production / 生产 | - | - | - | MOD-L02-009 | production / 生产 | generated / 已生成 | - |
| JOB-709611 | MOD-L02-010 | production / 生产 | - | - | - | MOD-L02-010 | production / 生产 | generated / 已生成 | - |
| JOB-709612 | MOD-L02-011 | production / 生产 | - | - | - | MOD-L02-011 | production / 生产 | generated / 已生成 | - |
| JOB-709613 | MOD-L02-012 | production / 生产 | - | - | - | MOD-L02-012 | production / 生产 | generated / 已生成 | - |
| JOB-709614 | MOD-L02-013 | production / 生产 | - | - | - | MOD-L02-013 | production / 生产 | stable | - |
| JOB-709615 | MOD-L02-014 | production / 生产 | - | - | - | MOD-L02-014 | production / 生产 | stable | - |
| JOB-709616 | MOD-L02-015 | production / 生产 | - | - | - | MOD-L02-015 | production / 生产 | stable | - |
| JOB-709617 | MOD-L02-016 | production / 生产 | - | - | - | MOD-L02-016 | production / 生产 | stable | - |
| JOB-709618 | MOD-L02-017 | production / 生产 | - | - | - | MOD-L02-017 | production / 生产 | stable | - |
| JOB-709619 | MOD-L02-018 | production / 生产 | - | - | - | MOD-L02-018 | production / 生产 | stable | - |
| JOB-709620 | MOD-L02-024 | production / 生产 | - | - | - | MOD-L02-024 | production / 生产 | generated / 已生成 | - |
| JOB-709621 | MOD-L02-025 | production / 生产 | - | - | - | MOD-L02-025 | production / 生产 | generated / 已生成 | - |
| JOB-709622 | MOD-L02-ANA | production / 生产 | - | - | - | MOD-L02-ANA | production / 生产 | stable | - |
| JOB-709623 | MOD-L02-GOV | production / 生产 | - | - | - | MOD-L02-GOV | production / 生产 | generated / 已生成 | - |
| JOB-709624 | MOD-L03-001 | production / 生产 | - | - | - | MOD-L03-001 | production / 生产 | generated / 已生成 | - |
| JOB-688297 | MOD-L04-001 | production / 生产 | - | - | - | MOD-L04-001 | design / 设计 | generated / 已生成 | - |
| JOB-709626 | MOD-L04-002 | production / 生产 | - | - | - | MOD-L04-002 | production / 生产 | generated / 已生成 | - |
| JOB-709627 | MOD-L05-001 | production / 生产 | - | - | - | MOD-L05-001 | production / 生产 | generated / 已生成 | - |
| JOB-709628 | MOD-L06-001 | production / 生产 | - | - | - | MOD-L06-001 | production / 生产 | stable | - |
| JOB-709629 | MOD-L07-001 | production / 生产 | - | - | - | MOD-L07-001 | production / 生产 | generated / 已生成 | - |
| JOB-709630 | MOD-L08-001 | production / 生产 | - | - | - | MOD-L08-001 | production / 生产 | generated / 已生成 | - |
| JOB-709631 | MOD-L09-001 | production / 生产 | - | - | - | MOD-L09-001 | production / 生产 | generated / 已生成 | - |
| JOB-709632 | MOD-L10-001 | production / 生产 | - | - | - | MOD-L10-001 | production / 生产 | generated / 已生成 | - |
| JOB-709633 | MOD-L11-001 | production / 生产 | - | - | - | MOD-L11-001 | production / 生产 | generated / 已生成 | - |
| JOB-709634 | MOD-L13-001 | production / 生产 | - | - | - | MOD-L13-001 | production / 生产 | generated / 已生成 | - |
| JOB-709635 | MOD-LLM_SECURITY | production / 生产 | - | - | - | MOD-LLM_SECURITY | production / 生产 | generated / 已生成 | - |
| JOB-36390 | MOD-MASTER-001 | production / 生产 | - | - | - | MOD-MASTER-001 | design / 设计 | stable | - |
| JOB-35517 | MOD-MASTER-002 | production / 生产 | - | - | - | MOD-MASTER-002 | design / 设计 | stable | - |
| JOB-36344 | MOD-MASTER-003 | production / 生产 | - | - | - | MOD-MASTER-003 | design / 设计 | planned | - |
| JOB-35528 | MOD-MASTER_BLUEPRINT | production / 生产 | - | - | - | MOD-MASTER_BLUEPRINT | design / 设计 | deprecated | - |
| JOB-711884 | MOD-MKT-001 | production / 生产 | - | - | - | MOD-MKT-001 | design / 设计 | planned | - |
| JOB-711954 | MOD-MKT-002 | production / 生产 | - | - | - | MOD-MKT-002 | design / 设计 | planned | - |
| JOB-712012 | MOD-MKT-003 | production / 生产 | - | - | - | MOD-MKT-003 | design / 设计 | planned | - |
| JOB-709637 | MOD-MKT_DATA | production / 生产 | - | - | - | MOD-MKT_DATA | production / 生产 | generated / 已生成 | - |
| JOB-709638 | MOD-ML_SERVE | production / 生产 | - | - | - | MOD-ML_SERVE | production / 生产 | generated / 已生成 | - |
| JOB-709639 | MOD-OPS-018 | production / 生产 | - | - | - | MOD-OPS-018 | production / 生产 | generated / 已生成 | - |
| JOB-36113 | MOD-PF_ALLOC | production / 生产 | - | - | - | MOD-PF_ALLOC | design / 设计 | planned | - |
| JOB-709640 | MOD-REMEDIATION_PROGRESS | production / 生产 | - | - | - | MOD-REMEDIATION_PROGRESS | production / 生产 | generated / 已生成 | - |
| JOB-709641 | MOD-REMEDIATION_PROGRESS_SMOKE | production / 生产 | - | - | - | MOD-REMEDIATION_PROGRESS_SMOKE | production / 生产 | generated / 已生成 | - |
| JOB-35898 | MOD-RESOURCE_OPTIMIZATION_ENGINE | production / 生产 | - | - | - | MOD-RESOURCE_OPTIMIZATION_ENGINE | design / 设计 | planned | - |
| JOB-709643 | MOD-RULE_ENGINE | production / 生产 | - | - | - | MOD-RULE_ENGINE | production / 生产 | generated / 已生成 | - |
| JOB-709644 | MOD-SCRIPTS-006 | production / 生产 | - | - | - | MOD-SCRIPTS-006 | production / 生产 | generated / 已生成 | - |
| JOB-709645 | MOD-SEC-030 | production / 生产 | - | - | - | MOD-SEC-030 | production / 生产 | generated / 已生成 | - |
| JOB-709646 | MOD-SEC_IMMUTABLE_CORE | production / 生产 | - | - | - | MOD-SEC_IMMUTABLE_CORE | production / 生产 | generated / 已生成 | - |
| JOB-709647 | MOD-SELL_DECISION | production / 生产 | - | - | - | MOD-SELL_DECISION | production / 生产 | generated / 已生成 | - |
| JOB-709648 | MOD-SHARED-001 | production / 生产 | - | - | - | MOD-SHARED-001 | production / 生产 | generated / 已生成 | - |
| JOB-709649 | MOD-SHARED-002 | production / 生产 | - | - | - | MOD-SHARED-002 | production / 生产 | generated / 已生成 | - |
| JOB-709650 | MOD-SHR_CONVERTERS | production / 生产 | - | - | - | MOD-SHR_CONVERTERS | production / 生产 | stable | - |
| JOB-709651 | MOD-SHR_IO_YAML | production / 生产 | - | - | - | MOD-SHR_IO_YAML | production / 生产 | generated / 已生成 | - |
| JOB-709652 | MOD-SIGNAL_ASHARE | production / 生产 | - | - | - | MOD-SIGNAL_ASHARE | production / 生产 | generated / 已生成 | - |
| JOB-709653 | MOD-SIGQC-001 | production / 生产 | - | - | - | MOD-SIGQC-001 | production / 生产 | generated / 已生成 | - |
| JOB-35600 | MOD-SIMULATION | production / 生产 | - | - | - | MOD-SIMULATION | design / 设计 | planned | - |
| JOB-119053 | MOD-SMOKE-TEST | production / 生产 | - | - | - | MOD-SMOKE-TEST | design / 设计 | planned | - |
| JOB-709654 | MOD-TASK_SYSTEM | production / 生产 | - | - | - | MOD-TASK_SYSTEM | production / 生产 | generated / 已生成 | - |
| JOB-118981 | MOD-TEST | production / 生产 | - | - | - | MOD-TEST | design / 设计 | planned | - |
| JOB-709656 | MOD-TEST-202 | production / 生产 | - | - | - | MOD-TEST-202 | production / 生产 | generated / 已生成 | - |
| JOB-709657 | MOD-TEST-203 | production / 生产 | - | - | - | MOD-TEST-203 | production / 生产 | generated / 已生成 | - |
| JOB-709658 | MOD-TEST-204 | production / 生产 | - | - | - | MOD-TEST-204 | production / 生产 | generated / 已生成 | - |
| JOB-709659 | MOD-TEST-205 | production / 生产 | - | - | - | MOD-TEST-205 | production / 生产 | generated / 已生成 | - |
| JOB-709660 | MOD-TEST-206 | production / 生产 | - | - | - | MOD-TEST-206 | production / 生产 | generated / 已生成 | - |
| JOB-709661 | MOD-TEST-210 | production / 生产 | - | - | - | MOD-TEST-210 | production / 生产 | generated / 已生成 | - |
| JOB-709662 | MOD-TEST-211 | production / 生产 | - | - | - | MOD-TEST-211 | production / 生产 | generated / 已生成 | - |
| JOB-709663 | MOD-TEST-212 | production / 生产 | - | - | - | MOD-TEST-212 | production / 生产 | generated / 已生成 | - |
| JOB-709664 | MOD-TEST-213 | production / 生产 | - | - | - | MOD-TEST-213 | production / 生产 | generated / 已生成 | - |
| JOB-709665 | MOD-TEST-215 | production / 生产 | - | - | - | MOD-TEST-215 | production / 生产 | generated / 已生成 | - |
| JOB-709666 | MOD-TEST-216 | production / 生产 | - | - | - | MOD-TEST-216 | production / 生产 | generated / 已生成 | - |
| JOB-709667 | MOD-TEST-217 | production / 生产 | - | - | - | MOD-TEST-217 | production / 生产 | generated / 已生成 | - |
| JOB-709668 | MOD-TEST-218 | production / 生产 | - | - | - | MOD-TEST-218 | production / 生产 | generated / 已生成 | - |
| JOB-709669 | MOD-TEST-219 | production / 生产 | - | - | - | MOD-TEST-219 | production / 生产 | generated / 已生成 | - |
| JOB-709670 | MOD-TEST-220 | production / 生产 | - | - | - | MOD-TEST-220 | production / 生产 | generated / 已生成 | - |
| JOB-709671 | MOD-TEST-221 | production / 生产 | - | - | - | MOD-TEST-221 | production / 生产 | generated / 已生成 | - |
| JOB-709672 | MOD-TEST-222 | production / 生产 | - | - | - | MOD-TEST-222 | production / 生产 | generated / 已生成 | - |
| JOB-709673 | MOD-TEST-223 | production / 生产 | - | - | - | MOD-TEST-223 | production / 生产 | generated / 已生成 | - |
| JOB-709674 | MOD-TEST-224 | production / 生产 | - | - | - | MOD-TEST-224 | production / 生产 | generated / 已生成 | - |
| JOB-709675 | MOD-TEST-225 | production / 生产 | - | - | - | MOD-TEST-225 | production / 生产 | generated / 已生成 | - |
| JOB-709676 | MOD-TEST-226 | production / 生产 | - | - | - | MOD-TEST-226 | production / 生产 | generated / 已生成 | - |
| JOB-709677 | MOD-TEST-227 | production / 生产 | - | - | - | MOD-TEST-227 | production / 生产 | generated / 已生成 | - |
| JOB-709678 | MOD-TEST-228 | production / 生产 | - | - | - | MOD-TEST-228 | production / 生产 | generated / 已生成 | - |
| JOB-709679 | MOD-TEST-229 | production / 生产 | - | - | - | MOD-TEST-229 | production / 生产 | generated / 已生成 | - |
| JOB-709680 | MOD-TEST-230 | production / 生产 | - | - | - | MOD-TEST-230 | production / 生产 | generated / 已生成 | - |
| JOB-709681 | MOD-TEST-231 | production / 生产 | - | - | - | MOD-TEST-231 | production / 生产 | generated / 已生成 | - |
| JOB-709682 | MOD-TEST-232 | production / 生产 | - | - | - | MOD-TEST-232 | production / 生产 | generated / 已生成 | - |
| JOB-709683 | MOD-TEST-233 | production / 生产 | - | - | - | MOD-TEST-233 | production / 生产 | generated / 已生成 | - |
| JOB-709684 | MOD-TEST-234 | production / 生产 | - | - | - | MOD-TEST-234 | production / 生产 | generated / 已生成 | - |
| JOB-709685 | MOD-TEST-235 | production / 生产 | - | - | - | MOD-TEST-235 | production / 生产 | generated / 已生成 | - |
| JOB-709686 | MOD-TEST-236 | production / 生产 | - | - | - | MOD-TEST-236 | production / 生产 | generated / 已生成 | - |
| JOB-709687 | MOD-TEST-237 | production / 生产 | - | - | - | MOD-TEST-237 | production / 生产 | generated / 已生成 | - |
| JOB-709688 | MOD-TEST-238 | production / 生产 | - | - | - | MOD-TEST-238 | production / 生产 | generated / 已生成 | - |
| JOB-709689 | MOD-TEST-239 | production / 生产 | - | - | - | MOD-TEST-239 | production / 生产 | generated / 已生成 | - |
| JOB-709690 | MOD-TEST-240 | production / 生产 | - | - | - | MOD-TEST-240 | production / 生产 | generated / 已生成 | - |
| JOB-709691 | MOD-TEST-241 | production / 生产 | - | - | - | MOD-TEST-241 | production / 生产 | generated / 已生成 | - |
| JOB-709692 | MOD-TEST-242 | production / 生产 | - | - | - | MOD-TEST-242 | production / 生产 | generated / 已生成 | - |
| JOB-709693 | MOD-TEST-246 | production / 生产 | - | - | - | MOD-TEST-246 | production / 生产 | generated / 已生成 | - |
| JOB-709694 | MOD-TEST-247 | production / 生产 | - | - | - | MOD-TEST-247 | production / 生产 | generated / 已生成 | - |
| JOB-709695 | MOD-TEST-248 | production / 生产 | - | - | - | MOD-TEST-248 | production / 生产 | generated / 已生成 | - |
| JOB-709696 | MOD-TEST-250 | production / 生产 | - | - | - | MOD-TEST-250 | production / 生产 | generated / 已生成 | - |
| JOB-709697 | MOD-TEST-251 | production / 生产 | - | - | - | MOD-TEST-251 | production / 生产 | generated / 已生成 | - |
| JOB-709698 | MOD-TEST-252 | production / 生产 | - | - | - | MOD-TEST-252 | production / 生产 | generated / 已生成 | - |
| JOB-709699 | MOD-TEST-253 | production / 生产 | - | - | - | MOD-TEST-253 | production / 生产 | generated / 已生成 | - |
| JOB-709700 | MOD-TEST-254 | production / 生产 | - | - | - | MOD-TEST-254 | production / 生产 | generated / 已生成 | - |
| JOB-709701 | MOD-TEST-255 | production / 生产 | - | - | - | MOD-TEST-255 | production / 生产 | generated / 已生成 | - |
| JOB-709702 | MOD-TEST-256 | production / 生产 | - | - | - | MOD-TEST-256 | production / 生产 | generated / 已生成 | - |
| JOB-709703 | MOD-TEST-257 | production / 生产 | - | - | - | MOD-TEST-257 | production / 生产 | generated / 已生成 | - |
| JOB-709704 | MOD-TEST-258 | production / 生产 | - | - | - | MOD-TEST-258 | production / 生产 | generated / 已生成 | - |
| JOB-709705 | MOD-TEST-260 | production / 生产 | - | - | - | MOD-TEST-260 | production / 生产 | generated / 已生成 | - |
| JOB-709706 | MOD-TEST-261 | production / 生产 | - | - | - | MOD-TEST-261 | production / 生产 | generated / 已生成 | - |
| JOB-709707 | MOD-TEST-262 | production / 生产 | - | - | - | MOD-TEST-262 | production / 生产 | generated / 已生成 | - |
| JOB-709708 | MOD-TEST-263 | production / 生产 | - | - | - | MOD-TEST-263 | production / 生产 | generated / 已生成 | - |
| JOB-709709 | MOD-TEST-264 | production / 生产 | - | - | - | MOD-TEST-264 | production / 生产 | generated / 已生成 | - |
| JOB-709710 | MOD-TEST-265 | production / 生产 | - | - | - | MOD-TEST-265 | production / 生产 | generated / 已生成 | - |
| JOB-709711 | MOD-TEST-266 | production / 生产 | - | - | - | MOD-TEST-266 | production / 生产 | generated / 已生成 | - |
| JOB-709712 | MOD-TEST-268 | production / 生产 | - | - | - | MOD-TEST-268 | production / 生产 | generated / 已生成 | - |
| JOB-709713 | MOD-TEST-272 | production / 生产 | - | - | - | MOD-TEST-272 | production / 生产 | generated / 已生成 | - |
| JOB-709714 | MOD-TEST-273 | production / 生产 | - | - | - | MOD-TEST-273 | production / 生产 | generated / 已生成 | - |
| JOB-709715 | MOD-TEST-274 | production / 生产 | - | - | - | MOD-TEST-274 | production / 生产 | generated / 已生成 | - |
| JOB-709716 | MOD-TEST-275 | production / 生产 | - | - | - | MOD-TEST-275 | production / 生产 | generated / 已生成 | - |
| JOB-709717 | MOD-TEST-276 | production / 生产 | - | - | - | MOD-TEST-276 | production / 生产 | generated / 已生成 | - |
| JOB-709718 | MOD-TEST-277 | production / 生产 | - | - | - | MOD-TEST-277 | production / 生产 | generated / 已生成 | - |
| JOB-709719 | MOD-TEST-278 | production / 生产 | - | - | - | MOD-TEST-278 | production / 生产 | generated / 已生成 | - |
| JOB-709720 | MOD-TEST-279 | production / 生产 | - | - | - | MOD-TEST-279 | production / 生产 | generated / 已生成 | - |
| JOB-709721 | MOD-TEST-280 | production / 生产 | - | - | - | MOD-TEST-280 | production / 生产 | generated / 已生成 | - |
| JOB-709722 | MOD-TEST-281 | production / 生产 | - | - | - | MOD-TEST-281 | production / 生产 | generated / 已生成 | - |
| JOB-709723 | MOD-TEST-282 | production / 生产 | - | - | - | MOD-TEST-282 | production / 生产 | generated / 已生成 | - |
| JOB-709724 | MOD-TEST-283 | production / 生产 | - | - | - | MOD-TEST-283 | production / 生产 | generated / 已生成 | - |
| JOB-709725 | MOD-TEST-284 | production / 生产 | - | - | - | MOD-TEST-284 | production / 生产 | generated / 已生成 | - |
| JOB-709726 | MOD-TEST-285 | production / 生产 | - | - | - | MOD-TEST-285 | production / 生产 | generated / 已生成 | - |
| JOB-709727 | MOD-TEST-286 | production / 生产 | - | - | - | MOD-TEST-286 | production / 生产 | generated / 已生成 | - |
| JOB-709728 | MOD-TEST-287 | production / 生产 | - | - | - | MOD-TEST-287 | production / 生产 | generated / 已生成 | - |
| JOB-709729 | MOD-TEST-288 | production / 生产 | - | - | - | MOD-TEST-288 | production / 生产 | generated / 已生成 | - |
| JOB-709730 | MOD-TEST-289 | production / 生产 | - | - | - | MOD-TEST-289 | production / 生产 | generated / 已生成 | - |
| JOB-709731 | MOD-TEST-290 | production / 生产 | - | - | - | MOD-TEST-290 | production / 生产 | generated / 已生成 | - |
| JOB-709732 | MOD-TEST-291 | production / 生产 | - | - | - | MOD-TEST-291 | production / 生产 | generated / 已生成 | - |
| JOB-709733 | MOD-TEST-292 | production / 生产 | - | - | - | MOD-TEST-292 | production / 生产 | generated / 已生成 | - |
| JOB-709734 | MOD-TEST-293 | production / 生产 | - | - | - | MOD-TEST-293 | production / 生产 | generated / 已生成 | - |
| JOB-709735 | MOD-TEST-294 | production / 生产 | - | - | - | MOD-TEST-294 | production / 生产 | generated / 已生成 | - |
| JOB-709736 | MOD-TEST-295 | production / 生产 | - | - | - | MOD-TEST-295 | production / 生产 | generated / 已生成 | - |
| JOB-709737 | MOD-TEST-296 | production / 生产 | - | - | - | MOD-TEST-296 | production / 生产 | generated / 已生成 | - |
| JOB-709738 | MOD-TEST-297 | production / 生产 | - | - | - | MOD-TEST-297 | production / 生产 | generated / 已生成 | - |
| JOB-709739 | MOD-TEST-298 | production / 生产 | - | - | - | MOD-TEST-298 | production / 生产 | generated / 已生成 | - |
| JOB-709740 | MOD-TEST-299 | production / 生产 | - | - | - | MOD-TEST-299 | production / 生产 | generated / 已生成 | - |
| JOB-709741 | MOD-TEST-300 | production / 生产 | - | - | - | MOD-TEST-300 | production / 生产 | generated / 已生成 | - |
| JOB-709742 | MOD-TEST-301 | production / 生产 | - | - | - | MOD-TEST-301 | production / 生产 | generated / 已生成 | - |
| JOB-709743 | MOD-TEST-302 | production / 生产 | - | - | - | MOD-TEST-302 | production / 生产 | generated / 已生成 | - |
| JOB-709744 | MOD-TEST-303 | production / 生产 | - | - | - | MOD-TEST-303 | production / 生产 | generated / 已生成 | - |
| JOB-709745 | MOD-TEST-304 | production / 生产 | - | - | - | MOD-TEST-304 | production / 生产 | generated / 已生成 | - |
| JOB-709746 | MOD-TEST-305 | production / 生产 | - | - | - | MOD-TEST-305 | production / 生产 | generated / 已生成 | - |
| JOB-709747 | MOD-TEST-306 | production / 生产 | - | - | - | MOD-TEST-306 | production / 生产 | generated / 已生成 | - |
| JOB-709748 | MOD-TEST-307 | production / 生产 | - | - | - | MOD-TEST-307 | production / 生产 | generated / 已生成 | - |
| JOB-709749 | MOD-TEST-308 | production / 生产 | - | - | - | MOD-TEST-308 | production / 生产 | generated / 已生成 | - |
| JOB-709750 | MOD-TEST-309 | production / 生产 | - | - | - | MOD-TEST-309 | production / 生产 | generated / 已生成 | - |
| JOB-709751 | MOD-TEST-310 | production / 生产 | - | - | - | MOD-TEST-310 | production / 生产 | generated / 已生成 | - |
| JOB-709752 | MOD-TEST-311 | production / 生产 | - | - | - | MOD-TEST-311 | production / 生产 | generated / 已生成 | - |
| JOB-709753 | MOD-TEST-312 | production / 生产 | - | - | - | MOD-TEST-312 | production / 生产 | generated / 已生成 | - |
| JOB-709754 | MOD-TEST-313 | production / 生产 | - | - | - | MOD-TEST-313 | production / 生产 | generated / 已生成 | - |
| JOB-709755 | MOD-TEST-314 | production / 生产 | - | - | - | MOD-TEST-314 | production / 生产 | generated / 已生成 | - |
| JOB-709756 | MOD-TEST-315 | production / 生产 | - | - | - | MOD-TEST-315 | production / 生产 | generated / 已生成 | - |
| JOB-709757 | MOD-TEST-316 | production / 生产 | - | - | - | MOD-TEST-316 | production / 生产 | generated / 已生成 | - |
| JOB-709758 | MOD-TEST-319 | production / 生产 | - | - | - | MOD-TEST-319 | production / 生产 | generated / 已生成 | - |
| JOB-709759 | MOD-TEST-320 | production / 生产 | - | - | - | MOD-TEST-320 | production / 生产 | generated / 已生成 | - |
| JOB-709760 | MOD-TEST-322 | production / 生产 | - | - | - | MOD-TEST-322 | production / 生产 | generated / 已生成 | - |
| JOB-709761 | MOD-TEST-323 | production / 生产 | - | - | - | MOD-TEST-323 | production / 生产 | generated / 已生成 | - |
| JOB-709762 | MOD-TEST-324 | production / 生产 | - | - | - | MOD-TEST-324 | production / 生产 | generated / 已生成 | - |
| JOB-709763 | MOD-TEST-325 | production / 生产 | - | - | - | MOD-TEST-325 | production / 生产 | generated / 已生成 | - |
| JOB-709764 | MOD-TEST-326 | production / 生产 | - | - | - | MOD-TEST-326 | production / 生产 | generated / 已生成 | - |
| JOB-709765 | MOD-TEST-328 | production / 生产 | - | - | - | MOD-TEST-328 | production / 生产 | generated / 已生成 | - |
| JOB-709766 | MOD-TEST-329 | production / 生产 | - | - | - | MOD-TEST-329 | production / 生产 | generated / 已生成 | - |
| JOB-709767 | MOD-TEST-330 | production / 生产 | - | - | - | MOD-TEST-330 | production / 生产 | generated / 已生成 | - |
| JOB-709768 | MOD-TEST-331 | production / 生产 | - | - | - | MOD-TEST-331 | production / 生产 | generated / 已生成 | - |
| JOB-709769 | MOD-TEST-332 | production / 生产 | - | - | - | MOD-TEST-332 | production / 生产 | generated / 已生成 | - |
| JOB-709770 | MOD-TEST-333 | production / 生产 | - | - | - | MOD-TEST-333 | production / 生产 | generated / 已生成 | - |
| JOB-709771 | MOD-TEST-334 | production / 生产 | - | - | - | MOD-TEST-334 | production / 生产 | generated / 已生成 | - |
| JOB-709772 | MOD-TEST-335 | production / 生产 | - | - | - | MOD-TEST-335 | production / 生产 | generated / 已生成 | - |
| JOB-709773 | MOD-TEST-336 | production / 生产 | - | - | - | MOD-TEST-336 | production / 生产 | generated / 已生成 | - |
| JOB-709774 | MOD-TEST-337 | production / 生产 | - | - | - | MOD-TEST-337 | production / 生产 | generated / 已生成 | - |
| JOB-709775 | MOD-TEST-338 | production / 生产 | - | - | - | MOD-TEST-338 | production / 生产 | generated / 已生成 | - |
| JOB-709776 | MOD-TEST-339 | production / 生产 | - | - | - | MOD-TEST-339 | production / 生产 | generated / 已生成 | - |
| JOB-709777 | MOD-TEST-340 | production / 生产 | - | - | - | MOD-TEST-340 | production / 生产 | generated / 已生成 | - |
| JOB-709778 | MOD-TEST-342 | production / 生产 | - | - | - | MOD-TEST-342 | production / 生产 | generated / 已生成 | - |
| JOB-709779 | MOD-TEST-343 | production / 生产 | - | - | - | MOD-TEST-343 | production / 生产 | generated / 已生成 | - |
| JOB-709780 | MOD-TEST-344 | production / 生产 | - | - | - | MOD-TEST-344 | production / 生产 | generated / 已生成 | - |
| JOB-709781 | MOD-TEST-345 | production / 生产 | - | - | - | MOD-TEST-345 | production / 生产 | generated / 已生成 | - |
| JOB-709782 | MOD-TEST-346 | production / 生产 | - | - | - | MOD-TEST-346 | production / 生产 | generated / 已生成 | - |
| JOB-709783 | MOD-TEST-347 | production / 生产 | - | - | - | MOD-TEST-347 | production / 生产 | generated / 已生成 | - |
| JOB-709784 | MOD-TEST-348 | production / 生产 | - | - | - | MOD-TEST-348 | production / 生产 | generated / 已生成 | - |
| JOB-709785 | MOD-TEST-349 | production / 生产 | - | - | - | MOD-TEST-349 | production / 生产 | generated / 已生成 | - |
| JOB-709786 | MOD-TEST-350 | production / 生产 | - | - | - | MOD-TEST-350 | production / 生产 | generated / 已生成 | - |
| JOB-709787 | MOD-TEST-351 | production / 生产 | - | - | - | MOD-TEST-351 | production / 生产 | generated / 已生成 | - |
| JOB-709788 | MOD-TEST-354 | production / 生产 | - | - | - | MOD-TEST-354 | production / 生产 | generated / 已生成 | - |
| JOB-709789 | MOD-TEST-355 | production / 生产 | - | - | - | MOD-TEST-355 | production / 生产 | generated / 已生成 | - |
| JOB-709790 | MOD-TEST-356 | production / 生产 | - | - | - | MOD-TEST-356 | production / 生产 | generated / 已生成 | - |
| JOB-709791 | MOD-TEST-357 | production / 生产 | - | - | - | MOD-TEST-357 | production / 生产 | generated / 已生成 | - |
| JOB-709792 | MOD-TEST-358 | production / 生产 | - | - | - | MOD-TEST-358 | production / 生产 | generated / 已生成 | - |
| JOB-709793 | MOD-TEST-359 | production / 生产 | - | - | - | MOD-TEST-359 | production / 生产 | generated / 已生成 | - |
| JOB-709794 | MOD-TEST-360 | production / 生产 | - | - | - | MOD-TEST-360 | production / 生产 | generated / 已生成 | - |
| JOB-709795 | MOD-TEST-361 | production / 生产 | - | - | - | MOD-TEST-361 | production / 生产 | generated / 已生成 | - |
| JOB-709796 | MOD-TEST-362 | production / 生产 | - | - | - | MOD-TEST-362 | production / 生产 | generated / 已生成 | - |
| JOB-709797 | MOD-TEST-363 | production / 生产 | - | - | - | MOD-TEST-363 | production / 生产 | generated / 已生成 | - |
| JOB-709798 | MOD-TEST-364 | production / 生产 | - | - | - | MOD-TEST-364 | production / 生产 | generated / 已生成 | - |
| JOB-709799 | MOD-TEST-365 | production / 生产 | - | - | - | MOD-TEST-365 | production / 生产 | generated / 已生成 | - |
| JOB-709800 | MOD-TEST-366 | production / 生产 | - | - | - | MOD-TEST-366 | production / 生产 | generated / 已生成 | - |
| JOB-709801 | MOD-TEST-367 | production / 生产 | - | - | - | MOD-TEST-367 | production / 生产 | generated / 已生成 | - |
| JOB-709802 | MOD-TEST-368 | production / 生产 | - | - | - | MOD-TEST-368 | production / 生产 | generated / 已生成 | - |
| JOB-709803 | MOD-TEST-369 | production / 生产 | - | - | - | MOD-TEST-369 | production / 生产 | generated / 已生成 | - |
| JOB-709804 | MOD-TEST-370 | production / 生产 | - | - | - | MOD-TEST-370 | production / 生产 | generated / 已生成 | - |
| JOB-709805 | MOD-TEST-371 | production / 生产 | - | - | - | MOD-TEST-371 | production / 生产 | generated / 已生成 | - |
| JOB-709806 | MOD-TEST-372 | production / 生产 | - | - | - | MOD-TEST-372 | production / 生产 | generated / 已生成 | - |
| JOB-709807 | MOD-TEST-373 | production / 生产 | - | - | - | MOD-TEST-373 | production / 生产 | generated / 已生成 | - |
| JOB-709808 | MOD-TEST-374 | production / 生产 | - | - | - | MOD-TEST-374 | production / 生产 | generated / 已生成 | - |
| JOB-709809 | MOD-TEST-375 | production / 生产 | - | - | - | MOD-TEST-375 | production / 生产 | generated / 已生成 | - |
| JOB-709810 | MOD-TEST-376 | production / 生产 | - | - | - | MOD-TEST-376 | production / 生产 | generated / 已生成 | - |
| JOB-709811 | MOD-TEST-377 | production / 生产 | - | - | - | MOD-TEST-377 | production / 生产 | generated / 已生成 | - |
| JOB-709812 | MOD-TEST-378 | production / 生产 | - | - | - | MOD-TEST-378 | production / 生产 | generated / 已生成 | - |
| JOB-709813 | MOD-TEST-379 | production / 生产 | - | - | - | MOD-TEST-379 | production / 生产 | generated / 已生成 | - |
| JOB-709814 | MOD-TEST-380 | production / 生产 | - | - | - | MOD-TEST-380 | production / 生产 | generated / 已生成 | - |
| JOB-709815 | MOD-TEST-381 | production / 生产 | - | - | - | MOD-TEST-381 | production / 生产 | generated / 已生成 | - |
| JOB-709816 | MOD-TEST-382 | production / 生产 | - | - | - | MOD-TEST-382 | production / 生产 | generated / 已生成 | - |
| JOB-709817 | MOD-TEST-383 | production / 生产 | - | - | - | MOD-TEST-383 | production / 生产 | generated / 已生成 | - |
| JOB-709818 | MOD-TEST-384 | production / 生产 | - | - | - | MOD-TEST-384 | production / 生产 | generated / 已生成 | - |
| JOB-709819 | MOD-TEST-385 | production / 生产 | - | - | - | MOD-TEST-385 | production / 生产 | generated / 已生成 | - |
| JOB-709820 | MOD-TEST-386 | production / 生产 | - | - | - | MOD-TEST-386 | production / 生产 | generated / 已生成 | - |
| JOB-709821 | MOD-TEST-387 | production / 生产 | - | - | - | MOD-TEST-387 | production / 生产 | generated / 已生成 | - |
| JOB-709822 | MOD-TEST-388 | production / 生产 | - | - | - | MOD-TEST-388 | production / 生产 | generated / 已生成 | - |
| JOB-709823 | MOD-TEST-389 | production / 生产 | - | - | - | MOD-TEST-389 | production / 生产 | generated / 已生成 | - |
| JOB-709824 | MOD-TEST-390 | production / 生产 | - | - | - | MOD-TEST-390 | production / 生产 | generated / 已生成 | - |
| JOB-709825 | MOD-TEST-391 | production / 生产 | - | - | - | MOD-TEST-391 | production / 生产 | generated / 已生成 | - |
| JOB-709826 | MOD-TEST-392 | production / 生产 | - | - | - | MOD-TEST-392 | production / 生产 | generated / 已生成 | - |
| JOB-709827 | MOD-TEST-393 | production / 生产 | - | - | - | MOD-TEST-393 | production / 生产 | generated / 已生成 | - |
| JOB-709828 | MOD-TEST-394 | production / 生产 | - | - | - | MOD-TEST-394 | production / 生产 | generated / 已生成 | - |
| JOB-709829 | MOD-TEST-395 | production / 生产 | - | - | - | MOD-TEST-395 | production / 生产 | generated / 已生成 | - |
| JOB-709830 | MOD-TEST-396 | production / 生产 | - | - | - | MOD-TEST-396 | production / 生产 | generated / 已生成 | - |
| JOB-709831 | MOD-TEST-397 | production / 生产 | - | - | - | MOD-TEST-397 | production / 生产 | generated / 已生成 | - |
| JOB-709832 | MOD-TEST-402 | production / 生产 | - | - | - | MOD-TEST-402 | production / 生产 | generated / 已生成 | - |
| JOB-709833 | MOD-TEST-403 | production / 生产 | - | - | - | MOD-TEST-403 | production / 生产 | generated / 已生成 | - |
| JOB-709834 | MOD-TEST-404 | production / 生产 | - | - | - | MOD-TEST-404 | production / 生产 | generated / 已生成 | - |
| JOB-709835 | MOD-TEST-406 | production / 生产 | - | - | - | MOD-TEST-406 | production / 生产 | generated / 已生成 | - |
| JOB-709836 | MOD-TEST-407 | production / 生产 | - | - | - | MOD-TEST-407 | production / 生产 | generated / 已生成 | - |
| JOB-709837 | MOD-TEST-408 | production / 生产 | - | - | - | MOD-TEST-408 | production / 生产 | generated / 已生成 | - |
| JOB-709838 | MOD-TEST-409 | production / 生产 | - | - | - | MOD-TEST-409 | production / 生产 | generated / 已生成 | - |
| JOB-709839 | MOD-TEST-410 | production / 生产 | - | - | - | MOD-TEST-410 | production / 生产 | generated / 已生成 | - |
| JOB-709840 | MOD-TEST-411 | production / 生产 | - | - | - | MOD-TEST-411 | production / 生产 | generated / 已生成 | - |
| JOB-709841 | MOD-TEST-412 | production / 生产 | - | - | - | MOD-TEST-412 | production / 生产 | generated / 已生成 | - |
| JOB-709842 | MOD-TEST-413 | production / 生产 | - | - | - | MOD-TEST-413 | production / 生产 | generated / 已生成 | - |
| JOB-709843 | MOD-TEST-414 | production / 生产 | - | - | - | MOD-TEST-414 | production / 生产 | generated / 已生成 | - |
| JOB-709844 | MOD-TEST-415 | production / 生产 | - | - | - | MOD-TEST-415 | production / 生产 | generated / 已生成 | - |
| JOB-709845 | MOD-TEST-416 | production / 生产 | - | - | - | MOD-TEST-416 | production / 生产 | generated / 已生成 | - |
| JOB-709846 | MOD-TEST-417 | production / 生产 | - | - | - | MOD-TEST-417 | production / 生产 | generated / 已生成 | - |
| JOB-709847 | MOD-TEST-418 | production / 生产 | - | - | - | MOD-TEST-418 | production / 生产 | generated / 已生成 | - |
| JOB-709848 | MOD-TEST-419 | production / 生产 | - | - | - | MOD-TEST-419 | production / 生产 | generated / 已生成 | - |
| JOB-709849 | MOD-TEST-420 | production / 生产 | - | - | - | MOD-TEST-420 | production / 生产 | generated / 已生成 | - |
| JOB-709850 | MOD-TEST-421 | production / 生产 | - | - | - | MOD-TEST-421 | production / 生产 | generated / 已生成 | - |
| JOB-709851 | MOD-TEST-422 | production / 生产 | - | - | - | MOD-TEST-422 | production / 生产 | generated / 已生成 | - |
| JOB-709852 | MOD-TEST-423 | production / 生产 | - | - | - | MOD-TEST-423 | production / 生产 | generated / 已生成 | - |
| JOB-709853 | MOD-TEST-424 | production / 生产 | - | - | - | MOD-TEST-424 | production / 生产 | generated / 已生成 | - |
| JOB-709854 | MOD-TEST-425 | production / 生产 | - | - | - | MOD-TEST-425 | production / 生产 | generated / 已生成 | - |
| JOB-709855 | MOD-TEST-426 | production / 生产 | - | - | - | MOD-TEST-426 | production / 生产 | generated / 已生成 | - |
| JOB-709856 | MOD-TEST-427 | production / 生产 | - | - | - | MOD-TEST-427 | production / 生产 | generated / 已生成 | - |
| JOB-709857 | MOD-TEST-428 | production / 生产 | - | - | - | MOD-TEST-428 | production / 生产 | generated / 已生成 | - |
| JOB-709858 | MOD-TEST-429 | production / 生产 | - | - | - | MOD-TEST-429 | production / 生产 | generated / 已生成 | - |
| JOB-709859 | MOD-TEST-430 | production / 生产 | - | - | - | MOD-TEST-430 | production / 生产 | generated / 已生成 | - |
| JOB-709860 | MOD-TEST-431 | production / 生产 | - | - | - | MOD-TEST-431 | production / 生产 | generated / 已生成 | - |
| JOB-709861 | MOD-TEST-432 | production / 生产 | - | - | - | MOD-TEST-432 | production / 生产 | generated / 已生成 | - |
| JOB-709862 | MOD-TEST-433 | production / 生产 | - | - | - | MOD-TEST-433 | production / 生产 | generated / 已生成 | - |
| JOB-709863 | MOD-TEST-434 | production / 生产 | - | - | - | MOD-TEST-434 | production / 生产 | generated / 已生成 | - |
| JOB-709864 | MOD-TEST-435 | production / 生产 | - | - | - | MOD-TEST-435 | production / 生产 | generated / 已生成 | - |
| JOB-709865 | MOD-TEST-436 | production / 生产 | - | - | - | MOD-TEST-436 | production / 生产 | generated / 已生成 | - |
| JOB-709866 | MOD-TEST-437 | production / 生产 | - | - | - | MOD-TEST-437 | production / 生产 | generated / 已生成 | - |
| JOB-709867 | MOD-TEST-438 | production / 生产 | - | - | - | MOD-TEST-438 | production / 生产 | generated / 已生成 | - |
| JOB-709868 | MOD-TEST-439 | production / 生产 | - | - | - | MOD-TEST-439 | production / 生产 | generated / 已生成 | - |
| JOB-709869 | MOD-TEST-440 | production / 生产 | - | - | - | MOD-TEST-440 | production / 生产 | generated / 已生成 | - |
| JOB-709870 | MOD-TEST-441 | production / 生产 | - | - | - | MOD-TEST-441 | production / 生产 | generated / 已生成 | - |
| JOB-709871 | MOD-TEST-444 | production / 生产 | - | - | - | MOD-TEST-444 | production / 生产 | generated / 已生成 | - |
| JOB-709872 | MOD-TEST-447 | production / 生产 | - | - | - | MOD-TEST-447 | production / 生产 | generated / 已生成 | - |
| JOB-709873 | MOD-TEST-449 | production / 生产 | - | - | - | MOD-TEST-449 | production / 生产 | generated / 已生成 | - |
| JOB-709874 | MOD-TEST-450 | production / 生产 | - | - | - | MOD-TEST-450 | production / 生产 | generated / 已生成 | - |
| JOB-709875 | MOD-TEST-452 | production / 生产 | - | - | - | MOD-TEST-452 | production / 生产 | generated / 已生成 | - |
| JOB-709876 | MOD-TEST-454 | production / 生产 | - | - | - | MOD-TEST-454 | production / 生产 | generated / 已生成 | - |
| JOB-709877 | MOD-TEST-455 | production / 生产 | - | - | - | MOD-TEST-455 | production / 生产 | generated / 已生成 | - |
| JOB-709878 | MOD-TEST-456 | production / 生产 | - | - | - | MOD-TEST-456 | production / 生产 | generated / 已生成 | - |
| JOB-709879 | MOD-TEST-457 | production / 生产 | - | - | - | MOD-TEST-457 | production / 生产 | generated / 已生成 | - |
| JOB-709880 | MOD-TEST-459 | production / 生产 | - | - | - | MOD-TEST-459 | production / 生产 | generated / 已生成 | - |
| JOB-709881 | MOD-TEST-460 | production / 生产 | - | - | - | MOD-TEST-460 | production / 生产 | generated / 已生成 | - |
| JOB-709882 | MOD-TEST-461 | production / 生产 | - | - | - | MOD-TEST-461 | production / 生产 | generated / 已生成 | - |
| JOB-709883 | MOD-TEST-462 | production / 生产 | - | - | - | MOD-TEST-462 | production / 生产 | generated / 已生成 | - |
| JOB-709884 | MOD-TEST-463 | production / 生产 | - | - | - | MOD-TEST-463 | production / 生产 | generated / 已生成 | - |
| JOB-709885 | MOD-TEST-464 | production / 生产 | - | - | - | MOD-TEST-464 | production / 生产 | generated / 已生成 | - |
| JOB-709886 | MOD-TEST-466 | production / 生产 | - | - | - | MOD-TEST-466 | production / 生产 | generated / 已生成 | - |
| JOB-709887 | MOD-TEST-467 | production / 生产 | - | - | - | MOD-TEST-467 | production / 生产 | generated / 已生成 | - |
| JOB-709888 | MOD-TEST-468 | production / 生产 | - | - | - | MOD-TEST-468 | production / 生产 | generated / 已生成 | - |
| JOB-709889 | MOD-TEST-469 | production / 生产 | - | - | - | MOD-TEST-469 | production / 生产 | generated / 已生成 | - |
| JOB-709890 | MOD-TEST-470 | production / 生产 | - | - | - | MOD-TEST-470 | production / 生产 | generated / 已生成 | - |
| JOB-709891 | MOD-TEST-471 | production / 生产 | - | - | - | MOD-TEST-471 | production / 生产 | generated / 已生成 | - |
| JOB-709892 | MOD-TEST-472 | production / 生产 | - | - | - | MOD-TEST-472 | production / 生产 | generated / 已生成 | - |
| JOB-709893 | MOD-TEST-473 | production / 生产 | - | - | - | MOD-TEST-473 | production / 生产 | generated / 已生成 | - |
| JOB-709894 | MOD-TEST-475 | production / 生产 | - | - | - | MOD-TEST-475 | production / 生产 | generated / 已生成 | - |
| JOB-709895 | MOD-TEST-476 | production / 生产 | - | - | - | MOD-TEST-476 | production / 生产 | generated / 已生成 | - |
| JOB-709896 | MOD-TEST-477 | production / 生产 | - | - | - | MOD-TEST-477 | production / 生产 | generated / 已生成 | - |
| JOB-709897 | MOD-TEST-479 | production / 生产 | - | - | - | MOD-TEST-479 | production / 生产 | generated / 已生成 | - |
| JOB-709898 | MOD-TEST-481 | production / 生产 | - | - | - | MOD-TEST-481 | production / 生产 | generated / 已生成 | - |
| JOB-709899 | MOD-TEST-482 | production / 生产 | - | - | - | MOD-TEST-482 | production / 生产 | generated / 已生成 | - |
| JOB-709900 | MOD-TEST-484 | production / 生产 | - | - | - | MOD-TEST-484 | production / 生产 | generated / 已生成 | - |
| JOB-709901 | MOD-TEST-485 | production / 生产 | - | - | - | MOD-TEST-485 | production / 生产 | generated / 已生成 | - |
| JOB-709902 | MOD-TEST-487 | production / 生产 | - | - | - | MOD-TEST-487 | production / 生产 | generated / 已生成 | - |
| JOB-709903 | MOD-TEST-488 | production / 生产 | - | - | - | MOD-TEST-488 | production / 生产 | generated / 已生成 | - |
| JOB-709904 | MOD-TEST-489 | production / 生产 | - | - | - | MOD-TEST-489 | production / 生产 | generated / 已生成 | - |
| JOB-709905 | MOD-TEST-490 | production / 生产 | - | - | - | MOD-TEST-490 | production / 生产 | generated / 已生成 | - |
| JOB-709906 | MOD-TEST-491 | production / 生产 | - | - | - | MOD-TEST-491 | production / 生产 | generated / 已生成 | - |
| JOB-709907 | MOD-TEST-492 | production / 生产 | - | - | - | MOD-TEST-492 | production / 生产 | generated / 已生成 | - |
| JOB-709908 | MOD-TEST-494 | production / 生产 | - | - | - | MOD-TEST-494 | production / 生产 | generated / 已生成 | - |
| JOB-709909 | MOD-TEST-495 | production / 生产 | - | - | - | MOD-TEST-495 | production / 生产 | generated / 已生成 | - |
| JOB-709910 | MOD-TEST-496 | production / 生产 | - | - | - | MOD-TEST-496 | production / 生产 | generated / 已生成 | - |
| JOB-709911 | MOD-TEST-497 | production / 生产 | - | - | - | MOD-TEST-497 | production / 生产 | generated / 已生成 | - |
| JOB-709912 | MOD-TEST-498 | production / 生产 | - | - | - | MOD-TEST-498 | production / 生产 | generated / 已生成 | - |
| JOB-709913 | MOD-TEST-499 | production / 生产 | - | - | - | MOD-TEST-499 | production / 生产 | generated / 已生成 | - |
| JOB-709914 | MOD-TEST-501 | production / 生产 | - | - | - | MOD-TEST-501 | production / 生产 | generated / 已生成 | - |
| JOB-709915 | MOD-TEST-502 | production / 生产 | - | - | - | MOD-TEST-502 | production / 生产 | generated / 已生成 | - |
| JOB-709916 | MOD-TEST-504 | production / 生产 | - | - | - | MOD-TEST-504 | production / 生产 | generated / 已生成 | - |
| JOB-709917 | MOD-TEST-505 | production / 生产 | - | - | - | MOD-TEST-505 | production / 生产 | generated / 已生成 | - |
| JOB-709918 | MOD-TEST-506 | production / 生产 | - | - | - | MOD-TEST-506 | production / 生产 | generated / 已生成 | - |
| JOB-709919 | MOD-TEST-508 | production / 生产 | - | - | - | MOD-TEST-508 | production / 生产 | generated / 已生成 | - |
| JOB-709920 | MOD-TEST-509 | production / 生产 | - | - | - | MOD-TEST-509 | production / 生产 | generated / 已生成 | - |
| JOB-709921 | MOD-TEST-510 | production / 生产 | - | - | - | MOD-TEST-510 | production / 生产 | generated / 已生成 | - |
| JOB-709922 | MOD-TEST-511 | production / 生产 | - | - | - | MOD-TEST-511 | production / 生产 | generated / 已生成 | - |
| JOB-709923 | MOD-TEST-512 | production / 生产 | - | - | - | MOD-TEST-512 | production / 生产 | generated / 已生成 | - |
| JOB-709924 | MOD-TEST-513 | production / 生产 | - | - | - | MOD-TEST-513 | production / 生产 | generated / 已生成 | - |
| JOB-709925 | MOD-TEST-514 | production / 生产 | - | - | - | MOD-TEST-514 | production / 生产 | generated / 已生成 | - |
| JOB-709926 | MOD-TEST-528 | production / 生产 | - | - | - | MOD-TEST-528 | production / 生产 | generated / 已生成 | - |
| JOB-709927 | MOD-TEST-529 | production / 生产 | - | - | - | MOD-TEST-529 | production / 生产 | generated / 已生成 | - |
| JOB-709928 | MOD-TEST-530 | production / 生产 | - | - | - | MOD-TEST-530 | production / 生产 | generated / 已生成 | - |
| JOB-709929 | MOD-TEST-532 | production / 生产 | - | - | - | MOD-TEST-532 | production / 生产 | generated / 已生成 | - |
| JOB-709930 | MOD-TEST-533 | production / 生产 | - | - | - | MOD-TEST-533 | production / 生产 | generated / 已生成 | - |
| JOB-709931 | MOD-TEST-534 | production / 生产 | - | - | - | MOD-TEST-534 | production / 生产 | generated / 已生成 | - |
| JOB-709932 | MOD-TEST-535 | production / 生产 | - | - | - | MOD-TEST-535 | production / 生产 | generated / 已生成 | - |
| JOB-709933 | MOD-TEST-536 | production / 生产 | - | - | - | MOD-TEST-536 | production / 生产 | generated / 已生成 | - |
| JOB-709934 | MOD-TEST-537 | production / 生产 | - | - | - | MOD-TEST-537 | production / 生产 | generated / 已生成 | - |
| JOB-709935 | MOD-TEST-538 | production / 生产 | - | - | - | MOD-TEST-538 | production / 生产 | generated / 已生成 | - |
| JOB-709936 | MOD-TEST-539 | production / 生产 | - | - | - | MOD-TEST-539 | production / 生产 | generated / 已生成 | - |
| JOB-709937 | MOD-TEST-540 | production / 生产 | - | - | - | MOD-TEST-540 | production / 生产 | generated / 已生成 | - |
| JOB-709938 | MOD-TEST-541 | production / 生产 | - | - | - | MOD-TEST-541 | production / 生产 | generated / 已生成 | - |
| JOB-709939 | MOD-TEST-543 | production / 生产 | - | - | - | MOD-TEST-543 | production / 生产 | generated / 已生成 | - |
| JOB-709940 | MOD-TEST-544 | production / 生产 | - | - | - | MOD-TEST-544 | production / 生产 | generated / 已生成 | - |
| JOB-709941 | MOD-TEST-545 | production / 生产 | - | - | - | MOD-TEST-545 | production / 生产 | generated / 已生成 | - |
| JOB-709942 | MOD-TEST-547 | production / 生产 | - | - | - | MOD-TEST-547 | production / 生产 | generated / 已生成 | - |
| JOB-709943 | MOD-TEST-548 | production / 生产 | - | - | - | MOD-TEST-548 | production / 生产 | generated / 已生成 | - |
| JOB-709944 | MOD-TEST-549 | production / 生产 | - | - | - | MOD-TEST-549 | production / 生产 | generated / 已生成 | - |
| JOB-709945 | MOD-TEST-550 | production / 生产 | - | - | - | MOD-TEST-550 | production / 生产 | generated / 已生成 | - |
| JOB-709946 | MOD-TEST-551 | production / 生产 | - | - | - | MOD-TEST-551 | production / 生产 | generated / 已生成 | - |
| JOB-709947 | MOD-TEST-552 | production / 生产 | - | - | - | MOD-TEST-552 | production / 生产 | generated / 已生成 | - |
| JOB-709948 | MOD-TEST-553 | production / 生产 | - | - | - | MOD-TEST-553 | production / 生产 | generated / 已生成 | - |
| JOB-709949 | MOD-TEST-554 | production / 生产 | - | - | - | MOD-TEST-554 | production / 生产 | generated / 已生成 | - |
| JOB-709950 | MOD-TEST-555 | production / 生产 | - | - | - | MOD-TEST-555 | production / 生产 | generated / 已生成 | - |
| JOB-709951 | MOD-TEST-557 | production / 生产 | - | - | - | MOD-TEST-557 | production / 生产 | generated / 已生成 | - |
| JOB-709952 | MOD-TEST-558 | production / 生产 | - | - | - | MOD-TEST-558 | production / 生产 | generated / 已生成 | - |
| JOB-709953 | MOD-TEST-559 | production / 生产 | - | - | - | MOD-TEST-559 | production / 生产 | generated / 已生成 | - |
| JOB-709954 | MOD-TEST-560 | production / 生产 | - | - | - | MOD-TEST-560 | production / 生产 | generated / 已生成 | - |
| JOB-709955 | MOD-TEST-561 | production / 生产 | - | - | - | MOD-TEST-561 | production / 生产 | generated / 已生成 | - |
| JOB-709956 | MOD-TEST-562 | production / 生产 | - | - | - | MOD-TEST-562 | production / 生产 | generated / 已生成 | - |
| JOB-709957 | MOD-TEST-563 | production / 生产 | - | - | - | MOD-TEST-563 | production / 生产 | generated / 已生成 | - |
| JOB-709958 | MOD-TEST-564 | production / 生产 | - | - | - | MOD-TEST-564 | production / 生产 | generated / 已生成 | - |
| JOB-709959 | MOD-TEST-565 | production / 生产 | - | - | - | MOD-TEST-565 | production / 生产 | generated / 已生成 | - |
| JOB-709960 | MOD-TEST-566 | production / 生产 | - | - | - | MOD-TEST-566 | production / 生产 | generated / 已生成 | - |
| JOB-709961 | MOD-TEST-567 | production / 生产 | - | - | - | MOD-TEST-567 | production / 生产 | generated / 已生成 | - |
| JOB-709962 | MOD-TEST-568 | production / 生产 | - | - | - | MOD-TEST-568 | production / 生产 | generated / 已生成 | - |
| JOB-709963 | MOD-TEST-569 | production / 生产 | - | - | - | MOD-TEST-569 | production / 生产 | generated / 已生成 | - |
| JOB-709964 | MOD-TEST-570 | production / 生产 | - | - | - | MOD-TEST-570 | production / 生产 | generated / 已生成 | - |
| JOB-709965 | MOD-TEST-571 | production / 生产 | - | - | - | MOD-TEST-571 | production / 生产 | generated / 已生成 | - |
| JOB-709966 | MOD-TEST-572 | production / 生产 | - | - | - | MOD-TEST-572 | production / 生产 | generated / 已生成 | - |
| JOB-709967 | MOD-TEST-573 | production / 生产 | - | - | - | MOD-TEST-573 | production / 生产 | generated / 已生成 | - |
| JOB-709968 | MOD-TEST-574 | production / 生产 | - | - | - | MOD-TEST-574 | production / 生产 | generated / 已生成 | - |
| JOB-709969 | MOD-TEST-575 | production / 生产 | - | - | - | MOD-TEST-575 | production / 生产 | generated / 已生成 | - |
| JOB-709970 | MOD-TEST-576 | production / 生产 | - | - | - | MOD-TEST-576 | production / 生产 | generated / 已生成 | - |
| JOB-709971 | MOD-TEST-577 | production / 生产 | - | - | - | MOD-TEST-577 | production / 生产 | generated / 已生成 | - |
| JOB-709972 | MOD-TEST-579 | production / 生产 | - | - | - | MOD-TEST-579 | production / 生产 | generated / 已生成 | - |
| JOB-709973 | MOD-TEST-580 | production / 生产 | - | - | - | MOD-TEST-580 | production / 生产 | generated / 已生成 | - |
| JOB-709974 | MOD-TEST-582 | production / 生产 | - | - | - | MOD-TEST-582 | production / 生产 | generated / 已生成 | - |
| JOB-709975 | MOD-TEST-583 | production / 生产 | - | - | - | MOD-TEST-583 | production / 生产 | generated / 已生成 | - |
| JOB-709976 | MOD-TEST-584 | production / 生产 | - | - | - | MOD-TEST-584 | production / 生产 | generated / 已生成 | - |
| JOB-709977 | MOD-TEST-585 | production / 生产 | - | - | - | MOD-TEST-585 | production / 生产 | generated / 已生成 | - |
| JOB-709978 | MOD-TEST-586 | production / 生产 | - | - | - | MOD-TEST-586 | production / 生产 | generated / 已生成 | - |
| JOB-709979 | MOD-TEST-587 | production / 生产 | - | - | - | MOD-TEST-587 | production / 生产 | generated / 已生成 | - |
| JOB-709980 | MOD-TEST-588 | production / 生产 | - | - | - | MOD-TEST-588 | production / 生产 | generated / 已生成 | - |
| JOB-709981 | MOD-TEST-590 | production / 生产 | - | - | - | MOD-TEST-590 | production / 生产 | generated / 已生成 | - |
| JOB-709982 | MOD-TEST-591 | production / 生产 | - | - | - | MOD-TEST-591 | production / 生产 | generated / 已生成 | - |
| JOB-709983 | MOD-TEST-592 | production / 生产 | - | - | - | MOD-TEST-592 | production / 生产 | generated / 已生成 | - |
| JOB-709984 | MOD-TEST-593 | production / 生产 | - | - | - | MOD-TEST-593 | production / 生产 | generated / 已生成 | - |
| JOB-709985 | MOD-TEST-594 | production / 生产 | - | - | - | MOD-TEST-594 | production / 生产 | generated / 已生成 | - |
| JOB-709986 | MOD-TEST-595 | production / 生产 | - | - | - | MOD-TEST-595 | production / 生产 | generated / 已生成 | - |
| JOB-709987 | MOD-TEST-597 | production / 生产 | - | - | - | MOD-TEST-597 | production / 生产 | generated / 已生成 | - |
| JOB-709988 | MOD-TEST-598 | production / 生产 | - | - | - | MOD-TEST-598 | production / 生产 | generated / 已生成 | - |
| JOB-709989 | MOD-TEST-599 | production / 生产 | - | - | - | MOD-TEST-599 | production / 生产 | generated / 已生成 | - |
| JOB-709990 | MOD-TEST-600 | production / 生产 | - | - | - | MOD-TEST-600 | production / 生产 | generated / 已生成 | - |
| JOB-709991 | MOD-TEST-601 | production / 生产 | - | - | - | MOD-TEST-601 | production / 生产 | generated / 已生成 | - |
| JOB-709992 | MOD-TEST-602 | production / 生产 | - | - | - | MOD-TEST-602 | production / 生产 | generated / 已生成 | - |
| JOB-709993 | MOD-TEST-603 | production / 生产 | - | - | - | MOD-TEST-603 | production / 生产 | generated / 已生成 | - |
| JOB-709994 | MOD-TEST-604 | production / 生产 | - | - | - | MOD-TEST-604 | production / 生产 | generated / 已生成 | - |
| JOB-709995 | MOD-TEST-605 | production / 生产 | - | - | - | MOD-TEST-605 | production / 生产 | generated / 已生成 | - |
| JOB-709996 | MOD-TEST-606 | production / 生产 | - | - | - | MOD-TEST-606 | production / 生产 | generated / 已生成 | - |
| JOB-709997 | MOD-TEST-607 | production / 生产 | - | - | - | MOD-TEST-607 | production / 生产 | generated / 已生成 | - |
| JOB-709998 | MOD-TEST-608 | production / 生产 | - | - | - | MOD-TEST-608 | production / 生产 | generated / 已生成 | - |
| JOB-709999 | MOD-TEST-609 | production / 生产 | - | - | - | MOD-TEST-609 | production / 生产 | generated / 已生成 | - |
| JOB-710000 | MOD-TEST-610 | production / 生产 | - | - | - | MOD-TEST-610 | production / 生产 | generated / 已生成 | - |
| JOB-710001 | MOD-TEST-611 | production / 生产 | - | - | - | MOD-TEST-611 | production / 生产 | generated / 已生成 | - |
| JOB-710002 | MOD-TEST-612 | production / 生产 | - | - | - | MOD-TEST-612 | production / 生产 | generated / 已生成 | - |
| JOB-710003 | MOD-TEST-613 | production / 生产 | - | - | - | MOD-TEST-613 | production / 生产 | generated / 已生成 | - |
| JOB-710004 | MOD-TEST-614 | production / 生产 | - | - | - | MOD-TEST-614 | production / 生产 | generated / 已生成 | - |
| JOB-710005 | MOD-TEST-616 | production / 生产 | - | - | - | MOD-TEST-616 | production / 生产 | generated / 已生成 | - |
| JOB-710006 | MOD-TEST-617 | production / 生产 | - | - | - | MOD-TEST-617 | production / 生产 | generated / 已生成 | - |
| JOB-710007 | MOD-TEST-618 | production / 生产 | - | - | - | MOD-TEST-618 | production / 生产 | generated / 已生成 | - |
| JOB-710008 | MOD-TEST-619 | production / 生产 | - | - | - | MOD-TEST-619 | production / 生产 | generated / 已生成 | - |
| JOB-710009 | MOD-TEST-620 | production / 生产 | - | - | - | MOD-TEST-620 | production / 生产 | generated / 已生成 | - |
| JOB-710010 | MOD-TEST-621 | production / 生产 | - | - | - | MOD-TEST-621 | production / 生产 | generated / 已生成 | - |
| JOB-710011 | MOD-TEST-622 | production / 生产 | - | - | - | MOD-TEST-622 | production / 生产 | generated / 已生成 | - |
| JOB-710012 | MOD-TEST-623 | production / 生产 | - | - | - | MOD-TEST-623 | production / 生产 | generated / 已生成 | - |
| JOB-710013 | MOD-TEST-624 | production / 生产 | - | - | - | MOD-TEST-624 | production / 生产 | generated / 已生成 | - |
| JOB-710014 | MOD-TEST-625 | production / 生产 | - | - | - | MOD-TEST-625 | production / 生产 | generated / 已生成 | - |
| JOB-710015 | MOD-TEST-626 | production / 生产 | - | - | - | MOD-TEST-626 | production / 生产 | generated / 已生成 | - |
| JOB-710016 | MOD-TEST-627 | production / 生产 | - | - | - | MOD-TEST-627 | production / 生产 | generated / 已生成 | - |
| JOB-710017 | MOD-TEST-628 | production / 生产 | - | - | - | MOD-TEST-628 | production / 生产 | generated / 已生成 | - |
| JOB-710018 | MOD-TEST-629 | production / 生产 | - | - | - | MOD-TEST-629 | production / 生产 | generated / 已生成 | - |
| JOB-710019 | MOD-TEST-630 | production / 生产 | - | - | - | MOD-TEST-630 | production / 生产 | generated / 已生成 | - |
| JOB-710020 | MOD-TEST-631 | production / 生产 | - | - | - | MOD-TEST-631 | production / 生产 | generated / 已生成 | - |
| JOB-710021 | MOD-TEST-633 | production / 生产 | - | - | - | MOD-TEST-633 | production / 生产 | generated / 已生成 | - |
| JOB-710022 | MOD-TEST-634 | production / 生产 | - | - | - | MOD-TEST-634 | production / 生产 | generated / 已生成 | - |
| JOB-710023 | MOD-TEST-635 | production / 生产 | - | - | - | MOD-TEST-635 | production / 生产 | generated / 已生成 | - |
| JOB-710024 | MOD-TEST-636 | production / 生产 | - | - | - | MOD-TEST-636 | production / 生产 | generated / 已生成 | - |
| JOB-710025 | MOD-TEST-637 | production / 生产 | - | - | - | MOD-TEST-637 | production / 生产 | generated / 已生成 | - |
| JOB-710026 | MOD-TEST-639 | production / 生产 | - | - | - | MOD-TEST-639 | production / 生产 | generated / 已生成 | - |
| JOB-710027 | MOD-TEST-640 | production / 生产 | - | - | - | MOD-TEST-640 | production / 生产 | generated / 已生成 | - |
| JOB-710028 | MOD-TEST-641 | production / 生产 | - | - | - | MOD-TEST-641 | production / 生产 | generated / 已生成 | - |
| JOB-710029 | MOD-TEST-642 | production / 生产 | - | - | - | MOD-TEST-642 | production / 生产 | generated / 已生成 | - |
| JOB-710030 | MOD-TEST-643 | production / 生产 | - | - | - | MOD-TEST-643 | production / 生产 | generated / 已生成 | - |
| JOB-710031 | MOD-TEST-644 | production / 生产 | - | - | - | MOD-TEST-644 | production / 生产 | generated / 已生成 | - |
| JOB-710032 | MOD-TEST-646 | production / 生产 | - | - | - | MOD-TEST-646 | production / 生产 | generated / 已生成 | - |
| JOB-710033 | MOD-TEST-647 | production / 生产 | - | - | - | MOD-TEST-647 | production / 生产 | generated / 已生成 | - |
| JOB-710034 | MOD-TEST-648 | production / 生产 | - | - | - | MOD-TEST-648 | production / 生产 | generated / 已生成 | - |
| JOB-710035 | MOD-TEST-649 | production / 生产 | - | - | - | MOD-TEST-649 | production / 生产 | generated / 已生成 | - |
| JOB-710036 | MOD-TEST-651 | production / 生产 | - | - | - | MOD-TEST-651 | production / 生产 | generated / 已生成 | - |
| JOB-710037 | MOD-TEST-652 | production / 生产 | - | - | - | MOD-TEST-652 | production / 生产 | generated / 已生成 | - |
| JOB-710038 | MOD-TEST-653 | production / 生产 | - | - | - | MOD-TEST-653 | production / 生产 | generated / 已生成 | - |
| JOB-710039 | MOD-TEST-654 | production / 生产 | - | - | - | MOD-TEST-654 | production / 生产 | generated / 已生成 | - |
| JOB-710040 | MOD-TEST-655 | production / 生产 | - | - | - | MOD-TEST-655 | production / 生产 | generated / 已生成 | - |
| JOB-710041 | MOD-TEST-660 | production / 生产 | - | - | - | MOD-TEST-660 | production / 生产 | generated / 已生成 | - |
| JOB-710042 | MOD-TEST-661 | production / 生产 | - | - | - | MOD-TEST-661 | production / 生产 | generated / 已生成 | - |
| JOB-710043 | MOD-TEST-662 | production / 生产 | - | - | - | MOD-TEST-662 | production / 生产 | generated / 已生成 | - |
| JOB-710044 | MOD-TEST-663 | production / 生产 | - | - | - | MOD-TEST-663 | production / 生产 | generated / 已生成 | - |
| JOB-710045 | MOD-TEST-664 | production / 生产 | - | - | - | MOD-TEST-664 | production / 生产 | generated / 已生成 | - |
| JOB-710046 | MOD-TEST-665 | production / 生产 | - | - | - | MOD-TEST-665 | production / 生产 | generated / 已生成 | - |
| JOB-710047 | MOD-TEST-668 | production / 生产 | - | - | - | MOD-TEST-668 | production / 生产 | generated / 已生成 | - |
| JOB-710048 | MOD-TEST-669 | production / 生产 | - | - | - | MOD-TEST-669 | production / 生产 | generated / 已生成 | - |
| JOB-710049 | MOD-TEST-670 | production / 生产 | - | - | - | MOD-TEST-670 | production / 生产 | generated / 已生成 | - |
| JOB-710050 | MOD-TEST-671 | production / 生产 | - | - | - | MOD-TEST-671 | production / 生产 | generated / 已生成 | - |
| JOB-710051 | MOD-TEST-672 | production / 生产 | - | - | - | MOD-TEST-672 | production / 生产 | generated / 已生成 | - |
| JOB-710052 | MOD-TEST-673 | production / 生产 | - | - | - | MOD-TEST-673 | production / 生产 | generated / 已生成 | - |
| JOB-710053 | MOD-TEST-674 | production / 生产 | - | - | - | MOD-TEST-674 | production / 生产 | generated / 已生成 | - |
| JOB-710054 | MOD-TEST-675 | production / 生产 | - | - | - | MOD-TEST-675 | production / 生产 | generated / 已生成 | - |
| JOB-710055 | MOD-TEST-676 | production / 生产 | - | - | - | MOD-TEST-676 | production / 生产 | generated / 已生成 | - |
| JOB-710056 | MOD-TEST-677 | production / 生产 | - | - | - | MOD-TEST-677 | production / 生产 | generated / 已生成 | - |
| JOB-710057 | MOD-TEST-678 | production / 生产 | - | - | - | MOD-TEST-678 | production / 生产 | generated / 已生成 | - |
| JOB-710058 | MOD-TEST-679 | production / 生产 | - | - | - | MOD-TEST-679 | production / 生产 | generated / 已生成 | - |
| JOB-710059 | MOD-TEST-680 | production / 生产 | - | - | - | MOD-TEST-680 | production / 生产 | generated / 已生成 | - |
| JOB-710060 | MOD-TEST-681 | production / 生产 | - | - | - | MOD-TEST-681 | production / 生产 | generated / 已生成 | - |
| JOB-710061 | MOD-TEST-682 | production / 生产 | - | - | - | MOD-TEST-682 | production / 生产 | generated / 已生成 | - |
| JOB-710062 | MOD-TEST-683 | production / 生产 | - | - | - | MOD-TEST-683 | production / 生产 | generated / 已生成 | - |
| JOB-710063 | MOD-TEST-684 | production / 生产 | - | - | - | MOD-TEST-684 | production / 生产 | generated / 已生成 | - |
| JOB-710064 | MOD-TEST-685 | production / 生产 | - | - | - | MOD-TEST-685 | production / 生产 | generated / 已生成 | - |
| JOB-710065 | MOD-TEST-686 | production / 生产 | - | - | - | MOD-TEST-686 | production / 生产 | generated / 已生成 | - |
| JOB-710066 | MOD-TEST-687 | production / 生产 | - | - | - | MOD-TEST-687 | production / 生产 | generated / 已生成 | - |
| JOB-710067 | MOD-TEST-688 | production / 生产 | - | - | - | MOD-TEST-688 | production / 生产 | generated / 已生成 | - |
| JOB-710068 | MOD-TEST-689 | production / 生产 | - | - | - | MOD-TEST-689 | production / 生产 | generated / 已生成 | - |
| JOB-710069 | MOD-TEST-690 | production / 生产 | - | - | - | MOD-TEST-690 | production / 生产 | generated / 已生成 | - |
| JOB-710070 | MOD-TEST-691 | production / 生产 | - | - | - | MOD-TEST-691 | production / 生产 | generated / 已生成 | - |
| JOB-710071 | MOD-TEST-692 | production / 生产 | - | - | - | MOD-TEST-692 | production / 生产 | generated / 已生成 | - |
| JOB-710072 | MOD-TEST-693 | production / 生产 | - | - | - | MOD-TEST-693 | production / 生产 | generated / 已生成 | - |
| JOB-710073 | MOD-TEST-694 | production / 生产 | - | - | - | MOD-TEST-694 | production / 生产 | generated / 已生成 | - |
| JOB-710074 | MOD-TEST-695 | production / 生产 | - | - | - | MOD-TEST-695 | production / 生产 | generated / 已生成 | - |
| JOB-710075 | MOD-TEST-696 | production / 生产 | - | - | - | MOD-TEST-696 | production / 生产 | generated / 已生成 | - |
| JOB-710076 | MOD-TEST-697 | production / 生产 | - | - | - | MOD-TEST-697 | production / 生产 | generated / 已生成 | - |
| JOB-710077 | MOD-TEST-698 | production / 生产 | - | - | - | MOD-TEST-698 | production / 生产 | generated / 已生成 | - |
| JOB-710078 | MOD-TEST-699 | production / 生产 | - | - | - | MOD-TEST-699 | production / 生产 | generated / 已生成 | - |
| JOB-710079 | MOD-TEST-700 | production / 生产 | - | - | - | MOD-TEST-700 | production / 生产 | generated / 已生成 | - |
| JOB-710080 | MOD-TEST-701 | production / 生产 | - | - | - | MOD-TEST-701 | production / 生产 | generated / 已生成 | - |
| JOB-710081 | MOD-TEST-702 | production / 生产 | - | - | - | MOD-TEST-702 | production / 生产 | generated / 已生成 | - |
| JOB-710082 | MOD-TEST-703 | production / 生产 | - | - | - | MOD-TEST-703 | production / 生产 | generated / 已生成 | - |
| JOB-710083 | MOD-TEST-704 | production / 生产 | - | - | - | MOD-TEST-704 | production / 生产 | generated / 已生成 | - |
| JOB-710084 | MOD-TEST-705 | production / 生产 | - | - | - | MOD-TEST-705 | production / 生产 | generated / 已生成 | - |
| JOB-710085 | MOD-TEST-706 | production / 生产 | - | - | - | MOD-TEST-706 | production / 生产 | generated / 已生成 | - |
| JOB-710086 | MOD-TEST-708 | production / 生产 | - | - | - | MOD-TEST-708 | production / 生产 | generated / 已生成 | - |
| JOB-710087 | MOD-TEST-710 | production / 生产 | - | - | - | MOD-TEST-710 | production / 生产 | generated / 已生成 | - |
| JOB-710088 | MOD-TRADING-001 | production / 生产 | - | - | - | MOD-TRADING-001 | production / 生产 | generated / 已生成 | - |
| JOB-710089 | MOD-WORKSPACE_TELEMETRY | production / 生产 | - | - | - | MOD-WORKSPACE_TELEMETRY | production / 生产 | generated / 已生成 | - |
| JOB-710090 | MOD-XLR-003 | production / 生产 | - | - | - | MOD-XLR-003 | production / 生产 | generated / 已生成 | - |
| JOB-710091 | MOD-metric_count_drift | production / 生产 | - | - | - | MOD-metric_count_drift | production / 生产 | generated / 已生成 | - |
| JOB-710092 | MOD-migrate_sqlite_to_pg | production / 生产 | - | - | - | MOD-migrate_sqlite_to_pg | production / 生产 | generated / 已生成 | - |
| JOB-710093 | MOD-readme_version_sync | production / 生产 | - | - | - | MOD-readme_version_sync | production / 生产 | generated / 已生成 | - |
| JOB-35838 | PLACEHOLDER-MOD-GOV-SYNC-PANORAMA | production / 生产 | - | - | - | PLACEHOLDER-MOD-GOV-SYNC-PANORAMA | design / 设计 | planned | - |
| JOB-35636 | SH-DB-001 | production / 生产 | - | - | - | SH-DB-001 | design / 设计 | planned | - |
| JOB-710095 | SH-DB-002 | production / 生产 | - | - | - | SH-DB-002 | production / 生产 | stable | - |
| JOB-591654 | SH-GOV-001 | production / 生产 | - | - | - | SH-GOV-001 | design / 设计 | generated / 已生成 | - |
| JOB-710097 | SH-GOV-003 | production / 生产 | - | - | - | SH-GOV-003 | production / 生产 | generated / 已生成 | - |
| JOB-710098 | SH-GOV-004 | production / 生产 | - | - | - | SH-GOV-004 | production / 生产 | generated / 已生成 | - |
| JOB-710099 | SH-MAIN-001 | production / 生产 | - | - | - | SH-MAIN-001 | production / 生产 | stable | - |
| JOB-37268 | SYS-MASTER-001 | production / 生产 | - | - | - | SYS-MASTER-001 | design / 设计 | stable | - |
| JOB-709367 | aggregate.ohlc_bar / 聚合.OHLC K线 | production / 生产 | src/zephyr/data/aggregator.py | event_driven / 事件驱动 | production / 生产 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 将Tick数据聚合为OHLC K线（1m/5m/日线），产出DS-002 market_data.ohlc_bar |
| JOB-709371 | check.risk_limits / 检查.风险限额 | production / 生产 | src/zephyr/risk/risk_checker.py | event_driven / 事件驱动 | production / 生产 | MOD-L04-001 | production / 生产 | generated / 已生成 | 风险限额检查（持仓/回撤/暴露度），产出DS-006 risk.limits |
| JOB-709369 | compute.momentum_20d / 计算.20日动量 | production / 生产 | src/zephyr/factor/momentum.py | event_driven / 事件驱动 | production / 生产 | MOD-L02-001 | production / 生产 | generated / 已生成 | 计算20日动量因子（收益率/相对强度），产出DS-004 factor.momentum_20d |
| JOB-709368 | compute.value_factor / 计算.价值因子 | production / 生产 | src/zephyr/factor/value_factor.py | event_driven / 事件驱动 | production / 生产 | MOD-L02-001 | production / 生产 | generated / 已生成 | 计算价值因子（PE/PB/股息率等），产出DS-003 factor.value_factor |
| JOB-709373 | execute.order / 执行.订单 | production / 生产 | src/zephyr/ex_core/executor.py | event_driven / 事件驱动 | production / 生产 | MOD-L06-001 | production / 生产 | generated / 已生成 | 执行订单（实盘/模拟），产出DS-008 fill.executed + DS-009 position.snapshot |
| JOB-709372 | generate.order / 生成.订单 | production / 生产 | src/zephyr/pf_core/order_generator.py | event_driven / 事件驱动 | production / 生产 | MOD-L05-001 | production / 生产 | generated / 已生成 | 根据信号+风险限额生成目标订单，产出DS-007 order.target |
| JOB-709366 | ingest.ifind_kline / 采集.iFind行情 | production / 生产 | src/zephyr/data/ingest_ifind.py | scheduled / 定时 | production / 生产 | MOD-MKT_DATA | production / 生产 | generated / 已生成 | 从同花顺iFind THS_RQ接口采集K线/Tick行情数据，写入DS-001 market_data.tick |
| JOB-709370 | synthesize.signal / 合成.信号 | production / 生产 | src/zephyr/signal_ashare/synthesizer.py | event_driven / 事件驱动 | production / 生产 | - | production / 生产 | generated / 已生成 | 合成多因子信号（加权/截面排名/置信度），产出DS-005 signal.composite |
