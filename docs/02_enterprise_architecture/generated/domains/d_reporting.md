---
doc_type: domain_architecture_doc
title: D-REPORTING 报告架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-REPORTING 报告架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-REPORTING |
| 域名称 | 报告 |
| 架构层 | L1_platform |
| 模块总数 | 132 |
| 设计态模块 | 118 |
| 原型态模块 | 8 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 |

## 模块清单

共 132 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
|  | MOD-REPORTING | path_invalid | design | 0 | 0 |
| D-REPORTING/A-Share Performance Audit & Optimization Trigger A股绩效审计与优化触发器 |  | design_only | design | 0 | 0 |
| D-REPORTING/A-Share Trading Record Template Engine A股交易记录模板引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/A-Share Trading Review Engine A股交易复盘引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/A-Share Trading Review Engine 引擎视图 |  | design_only | design | 0 | 0 |
| D-REPORTING/Abnormal Decision Detection 异常决策检测 |  | design_only | design | 0 | 0 |
| D-REPORTING/All Submodules Converge to Publisher Hub 所有子模块汇聚至Publisher Hub |  | design_only | design | 0 | 0 |
| D-REPORTING/Attribution Analysis 归因分析 |  | design_only | design | 0 | 0 |
| D-REPORTING/Attribution Engine 引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/Attribution Engine 绩效归因引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/Attribution Model Brinson First 多因子后期 归因模型Brinson先行 |  | design_only | design | 0 | 0 |
| D-REPORTING/Attributor Agent Consumption Mapping 归因Agent消费映射 |  | design_only | design | 0 | 0 |
| D-REPORTING/Attributor Agent 归因Agent |  | design_only | design | 0 | 0 |
| D-REPORTING/Audit Historical State Reconstruction 审计历史状态重建 |  | design_only | design | 0 | 0 |
| D-REPORTING/Audit Log Append-Only 审计日志append-only |  | design_only | design | 0 | 0 |
| D-REPORTING/Audit Log Classification & Retention 审计日志分类与保留 |  | design_only | design | 0 | 0 |
| D-REPORTING/Audit Log Query & Verification 审计日志查询与校验 |  | design_only | design | 0 | 0 |
| D-REPORTING/A股交易记录模板引擎 A-Share Trade Record Template Engine |  | design_only | design | 0 | 0 |
| D-REPORTING/BacktestCompleted 回测完成 |  | design_only | design | 0 | 0 |
| D-REPORTING/Brinson Model Brinson归因模型 |  | design_only | design | 0 | 0 |
| D-REPORTING/Brinson Model Brinson模型 |  | design_only | design | 0 | 0 |
| ...P1-009 PerformanceAttributionReport CTR-P1-009 PerformanceAttributionReport契约 |  | design_only | design | 0 | 0 |
| ...ING/Capital Curve Analyzer Consumes D-RISK Capital Curve Analyzer消费D-RISK诊断结果 |  | design_only | design | 0 | 0 |
| D-REPORTING/Capital Curve Analyzer 资金曲线分析器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Causal SHAP 因果SHAP |  | design_only | design | 0 | 0 |
| D-REPORTING/Clock Synchronization 时钟同步 |  | design_only | design | 0 | 0 |
| D-REPORTING/Compliance Reporter 合规报告器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Concept-Based Explanation 概念级解释 |  | design_only | design | 0 | 0 |
| D-REPORTING/D-REPORTING 报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/D-REPORTING-03 Report Publisher D-REPORTING-03报告发布器 |  | design_only | design | 0 | 0 |
| D-REPORTING/D-REPORTING-13 Report Version Manager D-REPORTING-13报告版本管理器 |  | design_only | design | 0 | 0 |
| ...REPORTING-27 A-Share Trading Record Template Engine D-REPORTING-27 A股交易记录模板引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/Dashboard Engine 仪表盘引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/Data Lineage MVP SQLite 血缘MVP用SQLite存储血缘 |  | design_only | design | 0 | 0 |
| D-REPORTING/DateRange 日期范围 |  | design_only | design | 0 | 0 |
| D-REPORTING/Day Trade Strategy Attribution Report 做T策略归因报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/Decision Trace Chain 决策溯源链 |  | design_only | design | 0 | 0 |
| .../Decision Trace Collector Independent Submodule Decision Trace Collector独立子模块 |  | design_only | design | 0 | 0 |
| D-REPORTING/Decision Trace Collector 决策溯源收集器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Decision Trace 决策溯源链 |  | design_only | design | 0 | 0 |
| D-REPORTING/Degradation Strategy C-017 Not Ready PnL No Fee 降级策略C-017未就绪时PnL不含费率 |  | design_only | design | 0 | 0 |
| D-REPORTING/Differential Privacy ε=1.0 差分隐私ε=1.0 |  | design_only | design | 0 | 0 |
| D-REPORTING/Differential Privacy 差分隐私 |  | design_only | design | 0 | 0 |
| D-REPORTING/Event Subscription via ACL 事件订阅走ACL防腐层 |  | design_only | design | 0 | 0 |
| D-REPORTING/Evidence Auto Collection 证据自动采集 |  | design_only | design | 0 | 0 |
| D-REPORTING/Evidence Chain Integrity Verification 证据链完整性验证 |  | design_only | design | 0 | 0 |
| D-REPORTING/Evidence Graph Model 证据图模型 |  | design_only | design | 0 | 0 |
| D-REPORTING/Execution Quality Report 执行质量报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/Explainability Gating 可解释性门控 |  | design_only | design | 0 | 0 |
| D-REPORTING/Explainability Guarantee 可解释性保障 |  | design_only | design | 0 | 0 |
| D-REPORTING/Hard Dependency D-AUTONOMY-CORE D-DATA 硬依赖 |  | design_only | design | 0 | 0 |
| D-REPORTING/Hash Chain 哈希链 |  | design_only | design | 0 | 0 |
| D-REPORTING/Historical Failure Mode Library 历史失效模式库 |  | design_only | design | 0 | 0 |
| D-REPORTING/L1 Event Integrity L1事件完整性 |  | design_only | design | 0 | 0 |
| D-REPORTING/L1 Event Integrity Restricted L1事件完整性受限 |  | design_only | design | 0 | 0 |
| D-REPORTING/L2 Set Integrity Construction Status L2集合完整性建设状态 |  | design_only | design | 0 | 0 |
| D-REPORTING/L2 Set Integrity L2集合完整性 |  | design_only | design | 0 | 0 |
| D-REPORTING/L3 External Verifiability L3外部可验证性 |  | design_only | design | 0 | 0 |
| D-REPORTING/L3 External Verifiability Restricted L3外部可验证性受限 |  | design_only | design | 0 | 0 |
| D-REPORTING/L5 to L6 Explainability L5→L6可解释性 |  | design_only | design | 0 | 0 |
| D-REPORTING/LIME LIME局部可解释模型 |  | design_only | design | 0 | 0 |
| D-REPORTING/LLM Self-Evaluation LLM自评估 |  | design_only | design | 0 | 0 |
| D-REPORTING/LLM Summary LLM摘要 |  | design_only | design | 0 | 0 |
| D-REPORTING/LLM-as-Explainer 自然语言解释 |  | design_only | design | 0 | 0 |
| D-REPORTING/LP-007 Attribution Agent V3 归因Agent V3上线 |  | design_only | design | 0 | 0 |
| D-REPORTING/Man Group AlphaGPT Man Group AlphaGPT实践 |  | design_only | design | 0 | 0 |
| D-REPORTING/Merkle Tree Merkle树 |  | design_only | design | 0 | 0 |
| D-REPORTING/Multi-Dimensional Quantitative Health Indicator 多维量化健康指标 |  | design_only | design | 0 | 0 |
| D-REPORTING/Multimodal Financial Reasoning 多模态金融推理 |  | design_only | design | 0 | 0 |
| D-REPORTING/Neo4j Graph Database Neo4j图数据库 |  | design_only | design | 0 | 0 |
| D-REPORTING/No Domain Event Published 不发布领域事件 |  | design_only | design | 0 | 0 |
| D-REPORTING/P3-Low P3低优先级指令 |  | design_only | design | 0 | 0 |
| D-REPORTING/PerformanceAttributionReport 归因报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/PerformanceAttributionReport 绩效归因报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/Phase 1 Activation Phase 1激活阶段 |  | design_only | design | 0 | 0 |
| D-REPORTING/Phase 2 Activation Phase 2激活阶段 |  | design_only | design | 0 | 0 |
| D-REPORTING/Phase 3 Activation Phase 3激活阶段 |  | design_only | design | 0 | 0 |
| D-REPORTING/Phase 4 Activation Phase 4激活阶段 |  | design_only | design | 0 | 0 |
| D-REPORTING/Post Trade Analytics Core 交易后分析核心 |  | design_only | design | 0 | 0 |
| D-REPORTING/Post-Market Report Local LLM 盘后报告走本地LLM |  | design_only | design | 0 | 0 |
| D-REPORTING/Publisher Hub 发布枢纽 |  | design_only | design | 0 | 0 |
| D-REPORTING/Real-time P&L Dashboard 实时盈亏仪表盘 |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Data Consistency 1 Hour SLA 报告数据一致性1小时SLA |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Publisher 发布者报告 |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Publisher 报告发布器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Storage SQLite Parquet Archive 报告存储SQLite+Parquet归档 |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Version Manager 报告版本管理器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Report Watermark Tracker 报告水印追踪器 |  | design_only | design | 0 | 0 |
| D-REPORTING/SHAP SHAP沙普利加性解释 |  | design_only | design | 0 | 0 |
| D-REPORTING/SHAP+LIME Dual Attribution SHAP+LIME双归因架构 |  | design_only | design | 0 | 0 |
| D-REPORTING/SQLite report_archive SQLite报告归档 |  | design_only | design | 0 | 0 |
| D-REPORTING/Sentinel Hallucination Detector Sentinel幻觉检测器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Soft Dependency D-INFRA-RUNTIME 软依赖 |  | design_only | design | 0 | 0 |
| D-REPORTING/SpectralGuardrails 谱分析幻觉检测 |  | design_only | design | 0 | 0 |
| D-REPORTING/Strategy Degradation Detection 策略退化检测 |  | design_only | design | 0 | 0 |
| D-REPORTING/Strategy Explainability Reporter 策略可解释性报告器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Strategy Health Score 策略健康评分 |  | design_only | design | 0 | 0 |
| D-REPORTING/Submodule Skeleton Thickness 子模块骨架厚度 |  | design_only | design | 0 | 0 |
| D-REPORTING/TCA Engine TCA交易成本分析引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/TCA Engine 引擎 |  | design_only | design | 0 | 0 |
| D-REPORTING/Tax Report 税务报告生成器 |  | design_only | design | 0 | 0 |
| D-REPORTING/Temporal Consistency Verification 时序一致性验证 |  | design_only | design | 0 | 0 |
| D-REPORTING/Three-Layer Audit Architecture 三层审计架构 |  | design_only | design | 0 | 0 |
| D-REPORTING/TraceCompleteness Indicator TraceCompleteness指标 |  | design_only | design | 0 | 0 |
| D-REPORTING/VCP v1.1 Crypto-Shredding PoC VCP v1.1 Crypto-Shredding概念验证 |  | design_only | design | 0 | 0 |
| D-REPORTING/VCP v1.1 VCP v1.1完整性架构 |  | design_only | design | 0 | 0 |
| D-REPORTING/VeNRA Double-Lock Zero Hallucination VeNRA双锁零幻觉锚定 |  | design_only | design | 0 | 0 |
| D-REPORTING/attribution-analysis 归因分析 |  | design_only | design | 0 | 0 |
| D-REPORTING/strategic-attributor Agent Card strategic-attributor Agent卡片 |  | design_only | design | 0 | 0 |
| D-REPORTING/strategy-health-score 策略健康评分 |  | design_only | design | 0 | 0 |
| D-REPORTING/v4.0+ Success Criteria v4.0+成功标准 |  | design_only | design | 0 | 0 |
| D-REPORTING/交易绩效归因模型 Performance Attribution Model |  | design_only | design | 0 | 0 |
| D-REPORTING/因子归因 Factor Attribution |  | design_only | design | 0 | 0 |
| D-REPORTING/风险归因 Risk Attribution |  | design_only | design | 0 | 0 |
| src/zephyr/reporting/__init__.py | MOD-L07-001 | draft | prototype | 1 | 1 |
| src/zephyr/reporting/__init___from_obs.py | MOD-INF-026 | draft | prototype | 0 | 1 |
| src/zephyr/reporting/_extensions/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/reporting/analytics_base.py | MOD-L07-001 | draft | prototype | 3 | 4 |
| src/zephyr/reporting/api/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/reporting/core/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/reporting/default_attribution_engine.py | MOD-L07-001 | draft | prototype | 0 | 2 |
| src/zephyr/reporting/default_tca_engine.py | MOD-L07-001 | draft | prototype | 0 | 4 |
| src/zephyr/reporting/implementations/__init__.py | MOD-L07-001 | draft | prototype | 0 | 2 |
| src/zephyr/reporting/implementations/default_attribution_engine.py | MOD-L07-001 | draft | prototype | 0 | 2 |
| src/zephyr/reporting/implementations/default_tca_engine.py | MOD-L07-001 | draft | prototype | 0 | 4 |
| src/zephyr/reporting/infrastructure/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/reporting/models/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/reporting/services/__init__.py | MOD-REPORTING | orphan | scaffold_placeholder | 0 | 0 |
| 报告域-水印追踪/D-REPORTING-17 | MOD-REPORTING | design_only | design | 0 | 0 |
| 报告域/D-REPORTING-03 | MOD-REPORTING | design_only | design | 0 | 0 |
| 报告域/D-REPORTING-08 | MOD-REPORTING | design_only | design | 0 | 3 |
| 监管报告生成器(证监会/交易所报告+数据完整性校验)/D-REPORTING-06 | MOD-REPORTING | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 22 | contract,event,data,config_depends |
| D-SECURITY | 12 | config_depends,data,contract,event |
| D-TRADING | 11 | import_depends,contract,event |
| D-SIGNAL | 11 | contract,event,data |
| D-GOVERNANCE | 11 | contract,import_depends |
| D-INFRA_RUNTIME | 10 | config_depends,data,event,contract |
| D-MKT_DATA | 8 | data,event,contract |
| D-DATA_ENG | 8 | domain_dependency,contract,config_depends,event,data |
| D-PF_CORE | 7 | contract,data,config_depends,event |
| D-INTEGRATION | 7 | event,data |
| D-EX_SOR | 6 | contract,config_depends,data |
| D-POSITION | 5 | domain_dependency,contract,data,event |
| D-FACTOR | 5 | contract,data,event |
| D-EX_CORE | 5 | data,contract,event |
| D-ML_TRAIN | 4 | config_depends,contract,data |
| D-AUTONOMY_PERM | 4 | contract,data,config_depends,event |
| D-INTELLIGENCE | 3 | event,data |
| D-SIMULATION | 2 | data,event |
| D-ML_SERVE | 2 | config_depends |
| D-KNOWLEDGE | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 41 | contract,event,data,config_depends |
| D-GOVERNANCE | 17 | import_depends,data,contract,event,config_depends |
| D-INFRA_OPS | 12 | config_depends,data,contract,event |
| D-FRONTEND | 10 | domain_dependency,data,contract,config_depends,event |
| D-AUTONOMY_CORE | 10 | contract,config_depends,data,event |
| D-OPS | 5 | contract,data |
| D-SELL_DECISION | 4 | contract,data,config_depends |
| D-PF_ALLOC | 3 | data,contract |
| D-CROSS_ASSET | 3 | event,contract |
| D-ALT_DATA | 2 | data,contract |
| D-PF_CORE | 1 | import_depends |
| D-DATA_SEC | 1 | config_depends |
| D-DATA_GOV | 1 | event |

## 域内依赖图

详见 [d_reporting_dependency.mmd](d_reporting_dependency.mmd)
