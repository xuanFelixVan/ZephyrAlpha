---
ttl: task_bound
title: "幽灵13项三段挖掘报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# 幽灵13项三段挖掘报告（EXEC-D6）

> 勘察窗口：2026-10-04；方法=CH system.tables 全库扫描（只读）+ 全仓 grep + registry 字段核 + depgraph PG 实测（只读 count）+ WebSearch 业界对标。
> 结论先行：**13 项无一属于"应建未建的 CH 表"**。11 张 factor_analysis 是"模块能力被误登为数据集"（设计态内存计算件，代码与消费方均存活）；DS-224 数据在 depgraph PG 存活且大幅增长（非幽灵）；DS-225 是设计态无表派生流（端点存活）。总裁定=13/13 口径纠正，0 建表、0 删码。

## 一、第一段：项目内漂移查（逐张证据）

### 1.1 CH 全库同名/改名表扫描（第一段①）

对 correlation / decay / attribution / optimiz / ic / layered / synthes / judgment / industry / chain_impact / chain / factor 共 12 个关键词 ILIKE 扫 `system.tables`（剔除 system 库），命中 21 张**全部为无关表**（sim_attribution_daily、judgment_daily_plan、industry_class、technical_indicator 等）。**factor_analysis 族 11 张、ig_* 族、chain_impact 在 CH 全库零同名/零改名/零别名表**。无"表被删"痕迹，也无 SQL 消费（全仓 `FROM/INTO factor_analysis` 零命中）——即从不存在"代码在读一个未来才存在的表"的漂移。

### 1.2 消费代码核（第一段②）

11 个模块全部物理存活于 `src/zephyr/factor/analysis/`（27 个文件），且**域外消费方真实存在**：

| 模块 | 域外消费方（节选） |
|------|------|
| correlation_dedup | signal_quality/signal_dedup.py |
| ic_decay | risk/core/model_risk_audit.py、decay_monitor |
| ic_ir_calc | pf_core/strategies/multifactor_sleeve_strategy.py、autonomy_core/agents/_g04_ops_check.py |
| multifactor_synthesis | ex_core/signal_providers.py、governance/consumption/consumption_census.py、factor_optimization |
| three_level_judgment | factor/analysis/factor_lifecycle_runner.py（周扫） |
| 其余 6 张 | 域内互调 + governance 登记脚本 |

DS-225：`api_server.py:4786 /api/chain-impact-stream` 端点存活，实现真源 zephyr.intelligence.chain_impact_stream 三件套在位。

### 1.3 registry 字段核（第一段③）

`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`：DS-029~DS-039 的 **physical_type 登记的是模块路径**（如 `src/zephyr/factor/analysis/ic_decay.py`），非 CH 表名；produced_by_job=JOB-028~JOB-038（trigger_type=manual，source_code_ref=同一模块，inputs=DS-003/DS-004 因子信号）；2026-08-13 由 `scripts/governance/oneoff/factor_design_state_complete.py` 批量登记，degradation_note 自认"仅设计态，CH 无物理表，降级待物化"。**即：登记当时就没打算落 CH 表，"幽灵"是登记口径产物，不是数据丢失。**

### 1.4 DS-224 depgraph PG 真相（第一段④）

用 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection` 实测（只读 count）：

| 表 | 2026-09-11 快照 | 2026-10-04 实测 |
|----|------|------|
| ig_chain | 830 | 873 |
| ig_node | 3328 | 5560 |
| ig_edge | 1378 | 1726 |
| ig_node_company | 16900 | 25559 |

且四表族已扩张为 **13 表**（新增 ig_fact 264072 行、ig_io_edge 16859、ig_product_revenue 165255、ig_company_metric 235392、ig_company_edge 58207、ig_document、ig_chunk、ig_entity_code_map、ig_unlisted_entity）。api_server cm_* 通道（:3854 等）持续活查 ig_node_company/ig_node/ig_chain。**DS-224 数据活着且在增长——是"数据在 PG 不在 CH"的登记口径错位， AUDIT 判断证实。**

## 二、第二段：数据源/产线定位

- 产线判定：这 11 张对应的**不是某条产线的应然落库输出**。`sop/mining_sop/factor_mining_sop_policy.md` 的 S0-S7 八段产线，其落库点只有两处——**S7 因子回写 factor_registry 的 ic/ir/decay 字段 + 考试台账行**（§S7："输出=注册表变更（走 GitCommitGateway）+ 台账行"）。IC 大海选（S2）、沙箱三关/E4 正考（S4/S5，layered_backtest/ic_ir）、组队备料（S6，correlation_dedup/multifactor_synthesis）都是**工序工具**，中间产物即算即弃。
- 代码实证：11 个模块全是纯计算函数（返回 pandas Series/DataFrame，零 CH 写入）；域内真正的落库件是 `factor_production_pipeline.py` + `feature_store_writer.py`（写 c1_market.factor_feature_value），与这 11 张分属两条线。
- 消费现状：factor_lifecycle_runner（trading_lifecycle_weekly 周扫）把 decay_state 回写 factor_registry（文件行级替换），three_level_judgment 的判定结果**有落点**，落点是注册表不是 CH 表。

## 三、第三段：业界对标（WebSearch，3 轮，搜索服务重度限流 429，以下为三轮结果汇合口径）

- **Alphalens**（业界因子分析事实标准）：纯即算即弃分析库，tearsheet 从因子 DataFrame 现算 IC/分位收益/衰减，**无任何内建持久化**。
- **Qlib**：IC 每次回测现算，经 MLflow 实验跟踪留痕，**不落关系表**。
- **生产化平台惯例**：持久化的是**因子值**（storage 层：Arctic/ClickHouse/Parquet 长表），分析指标（IC/衰减/ICIR）默认现算；仅当中台需要监控仪表盘/告警时才选择性物化一张小型 factor_metrics 快照表（混合模式）。
- 结论：业界**不为**相关矩阵/衰减曲线/分层回测/多因子合成各建一张表。本仓现状（因子值落库 + 分析即算）与业界主流同构。

## 四、逐张总裁定（三选一：恢复建表/删除降级/口径纠正）

| DS | entity_name | 三段摘要 | 裁定 |
|----|------|------|------|
| DS-029 | correlation_analyzer | 模块活/消费活/CH 无表且从未有 | 口径纠正 |
| DS-030 | correlation_dedup | 同上，signal_quality 在用 | 口径纠正 |
| DS-031 | decay_monitor | 域内互调活 | 口径纠正 |
| DS-032 | factor_attribution | 模块活，仅域内+登记脚本消费 | 口径纠正 |
| DS-033 | factor_optimization | _g04_ops_check 在用 | 口径纠正 |
| DS-034 | ic_decay | model_risk_audit 在用 | 口径纠正 |
| DS-035 | ic_ir_calc | pf_core 策略+自治体检在用 | 口径纠正 |
| DS-036 | ic_ir_evaluator | 模块活 | 口径纠正 |
| DS-037 | layered_backtest | 模块活 | 口径纠正 |
| DS-038 | multifactor_synthesis | ex_core/census 在用 | 口径纠正 |
| DS-039 | three_level_judgment | lifecycle 周扫在用 | 口径纠正 |
| DS-224 | ig_industry_graph | **PG 13 表存活且增长，cm_* 活查** | 口径纠正→**可复评 active**（physical_type=postgres_table 已对，补"CH 不含、depgraph PG 只读四表族已扩 13 表"注记；满足其 degradation_note 自设回升条件） |
| DS-225 | chain_impact_stream | 派生流设计态无表，端点 :4786 活 | 口径纠正（按其自设 note：改登 job/endpoint 资产，或保留 candidate 永久标注"无物理表为设计态"） |

口径纠正的具体动作建议（供 Owner/后续会话执行，本任务未改任何文件）：
1. 11 张 factor_analysis：physical_type 语义从"模块路径冒充表"改为显式 `in_memory_compute`（或退役 dataset 条目、能力挂 MOD-L02-* 模块注册表，消灭 dataset 幽灵身份）；produced_by_job 的 JOB-028~038（manual 触发的"任务"实为函数调用）同批复核口径。
2. 唯一值得讨论的物化例外：若未来监控仪表盘需要 IC/衰减历史曲线，按业界混合模式**单张** factor_metrics 快照表（键=factor_id×date）即可覆盖 11 张的需求，无需 11 张。
3. DS-224：回升 active 走既定复评通道（PG 复验证据本报告 §1.4）。
4. DS-225：按其 degradation_note 自设路径改登 endpoint/job 资产。

## 附：勘察命令与真源锚点

- CH 扫描：`get_db_service().get_clickhouse_conn()` + `system.tables ILIKE`（只读）；PG 实测：`get_depgraph_pg_connection(read_only=True)`。
- 登记真源：`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（DS-029@L1800~DS-039@L2170、DS-224@L9545、DS-225@L9589；JOB-028@L14180）。
- 产线真源：`docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md` §S7。
- 消费端点：`src/zephyr/frontend/dashboard/api_server.py:4786`（chain-impact-stream）、`:3854`（ig_* 活查）。
