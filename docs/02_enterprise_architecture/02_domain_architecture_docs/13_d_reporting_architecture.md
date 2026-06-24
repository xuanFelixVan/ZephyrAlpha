---
doc_type: domain_architecture_diagram
title: D-REPORTING 报告架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 13_d_reporting / 报告 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示报告（D-REPORTING）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 报告（D-REPORTING）的模块分布。共 132 个模块 / 132 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (4 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   Report Watermark Tracker  [design]                             │
│   Report Publisher  [design]                                     │
│   Risk Report Engine  [design]                                   │
│   Regulatory Report Generator  [design]                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (15 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   Differential Privacy ε=1.0 差分隐私ε=1.0  [design]             │
│   src/zephyr/reporting/__init__.py  [prototype]                  │
│   src/zephyr/reporting/__init___from_obs.py  [prototype]         │
│   src/zephyr/reporting/_extensions/__init__.py  [scaffold_pla... │
│   src/zephyr/reporting/analytics_base.py  [prototype]            │
│   src/zephyr/reporting/api/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/reporting/core/__init__.py  [scaffold_placeholder]  │
│   src/zephyr/reporting/default_attribution_engine.py  [protot... │
│   src/zephyr/reporting/default_tca_engine.py  [prototype]        │
│   src/zephyr/reporting/implementations/__init__.py  [prototype]  │
│   src/zephyr/reporting/implementations/default_attribution_en... │
│   src/zephyr/reporting/implementations/default_tca_engine.py ... │
│   src/zephyr/reporting/infrastructure/__init__.py  [scaffold_... │
│   src/zephyr/reporting/models/__init__.py  [scaffold_placehol... │
│   src/zephyr/reporting/services/__init__.py  [scaffold_placeh... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (113 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   A-Share Performance Audit & Optimization Trigger A股绩效审...  │
│   A-Share Trading Record Template Engine A股交易记录模板引擎 ... │
│   A-Share Trading Review Engine A股交易复盘引擎  [design]        │
│   A-Share Trading Review Engine 引擎视图  [design]               │
│   Abnormal Decision Detection 异常决策检测  [design]             │
│   All Submodules Converge to Publisher Hub 所有子模块汇聚至Pu... │
│   Attribution Analysis 归因分析  [design]                        │
│   Attribution Engine 引擎  [design]                              │
│   Attribution Engine 绩效归因引擎  [design]                      │
│   Attribution Model Brinson First 多因子后期 归因模型Brinson...  │
│   Attributor Agent Consumption Mapping 归因Agent消费映射  [de... │
│   Attributor Agent 归因Agent  [design]                           │
│   Audit Historical State Reconstruction 审计历史状态重建  [de... │
│   Audit Log Append-Only 审计日志append-only  [design]            │
│   Audit Log Classification & Retention 审计日志分类与保留  [d... │
│   Audit Log Query & Verification 审计日志查询与校验  [design]    │
│   A股交易记录模板引擎 A-Share Trade Record Template Engine  [... │
│   BacktestCompleted 回测完成  [design]                           │
│   ...还有 95 个模块 / 95 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 132 个模块 / 132 modules）。

### L1 基础层 / Foundation Layer (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 报告域-水印追踪/D-REPORTING-17 | Report Watermark Tracker | design | design_only |
| 2 | 报告域/D-REPORTING-03 | Report Publisher | design | design_only |
| 3 | 报告域/D-REPORTING-08 | Risk Report Engine | design | design_only |
| 4 | 监管报告生成器(证监会/交易所报告+数据完整性校验)/D-REPORT... | Regulatory Report Generator | design | design_only |

### L2 领域层 / Domain Layer (15 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 |  | Differential Privacy ε=1.0 差分隐私ε=1.0 | design | path_invalid |
| 2 | src/zephyr/reporting/__init__.py | src/zephyr/reporting/__init__.py | prototype | draft |
| 3 | src/zephyr/reporting/__init___from_obs.py | src/zephyr/reporting/__init___from_ob... | prototype | draft |
| 4 | src/zephyr/reporting/_extensions/__init__.py | src/zephyr/reporting/_extensions/__in... | scaffold_placeholder | orphan |
| 5 | src/zephyr/reporting/analytics_base.py | src/zephyr/reporting/analytics_base.py | prototype | draft |
| 6 | src/zephyr/reporting/api/__init__.py | src/zephyr/reporting/api/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/reporting/core/__init__.py | src/zephyr/reporting/core/__init__.py | scaffold_placeholder | orphan |
| 8 | src/zephyr/reporting/default_attribution_engine.py | src/zephyr/reporting/default_attribut... | prototype | draft |
| 9 | src/zephyr/reporting/default_tca_engine.py | src/zephyr/reporting/default_tca_engi... | prototype | draft |
| 10 | src/zephyr/reporting/implementations/__init__.py | src/zephyr/reporting/implementations/... | prototype | draft |
| 11 | src/zephyr/reporting/implementations/default_attribution_... | src/zephyr/reporting/implementations/... | prototype | draft |
| 12 | src/zephyr/reporting/implementations/default_tca_engine.py | src/zephyr/reporting/implementations/... | prototype | draft |
| 13 | src/zephyr/reporting/infrastructure/__init__.py | src/zephyr/reporting/infrastructure/_... | scaffold_placeholder | orphan |
| 14 | src/zephyr/reporting/models/__init__.py | src/zephyr/reporting/models/__init__.py | scaffold_placeholder | orphan |
| 15 | src/zephyr/reporting/services/__init__.py | src/zephyr/reporting/services/__init_... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (113 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-REPORTING/A-Share Performance Audit & Optimization Trig... | A-Share Performance Audit & Optimizat... | design | design_only |
| 2 | D-REPORTING/A-Share Trading Record Template Engine A股交... | A-Share Trading Record Template Engin... | design | design_only |
| 3 | D-REPORTING/A-Share Trading Review Engine A股交易复盘引擎 | A-Share Trading Review Engine A股交易... | design | design_only |
| 4 | D-REPORTING/A-Share Trading Review Engine 引擎视图 | A-Share Trading Review Engine 引擎视图 | design | design_only |
| 5 | D-REPORTING/Abnormal Decision Detection 异常决策检测 | Abnormal Decision Detection 异常决策检测 | design | design_only |
| 6 | D-REPORTING/All Submodules Converge to Publisher Hub 所有... | All Submodules Converge to Publisher ... | design | design_only |
| 7 | D-REPORTING/Attribution Analysis 归因分析 | Attribution Analysis 归因分析 | design | design_only |
| 8 | D-REPORTING/Attribution Engine 引擎 | Attribution Engine 引擎 | design | design_only |
| 9 | D-REPORTING/Attribution Engine 绩效归因引擎 | Attribution Engine 绩效归因引擎 | design | design_only |
| 10 | D-REPORTING/Attribution Model Brinson First 多因子后期 归... | Attribution Model Brinson First 多因... | design | design_only |
| 11 | D-REPORTING/Attributor Agent Consumption Mapping 归因Agen... | Attributor Agent Consumption Mapping ... | design | design_only |
| 12 | D-REPORTING/Attributor Agent 归因Agent | Attributor Agent 归因Agent | design | design_only |
| 13 | D-REPORTING/Audit Historical State Reconstruction 审计历... | Audit Historical State Reconstruction... | design | design_only |
| 14 | D-REPORTING/Audit Log Append-Only 审计日志append-only | Audit Log Append-Only 审计日志append-... | design | design_only |
| 15 | D-REPORTING/Audit Log Classification & Retention 审计日志... | Audit Log Classification & Retention ... | design | design_only |
| 16 | D-REPORTING/Audit Log Query & Verification 审计日志查询与... | Audit Log Query & Verification 审计日... | design | design_only |
| 17 | D-REPORTING/A股交易记录模板引擎 A-Share Trade Record Temp... | A股交易记录模板引擎 A-Share Trade Rec... | design | design_only |
| 18 | D-REPORTING/BacktestCompleted 回测完成 | BacktestCompleted 回测完成 | design | design_only |
| 19 | D-REPORTING/Brinson Model Brinson归因模型 | Brinson Model Brinson归因模型 | design | design_only |
| 20 | D-REPORTING/Brinson Model Brinson模型 | Brinson Model Brinson模型 | design | design_only |
| 21 | D-REPORTING/CTR-P1-009 PerformanceAttributionReport CTR-P... | CTR-P1-009 PerformanceAttributionRepo... | design | design_only |
| 22 | D-REPORTING/Capital Curve Analyzer Consumes D-RISK Capita... | Capital Curve Analyzer Consumes D-RIS... | design | design_only |
| 23 | D-REPORTING/Capital Curve Analyzer 资金曲线分析器 | Capital Curve Analyzer 资金曲线分析器 | design | design_only |
| 24 | D-REPORTING/Causal SHAP 因果SHAP | Causal SHAP 因果SHAP | design | design_only |
| 25 | D-REPORTING/Clock Synchronization 时钟同步 | Clock Synchronization 时钟同步 | design | design_only |
| 26 | D-REPORTING/Compliance Reporter 合规报告器 | Compliance Reporter 合规报告器 | design | design_only |
| 27 | D-REPORTING/Concept-Based Explanation 概念级解释 | Concept-Based Explanation 概念级解释 | design | design_only |
| 28 | D-REPORTING/D-REPORTING 报告 | D-REPORTING 报告 | design | design_only |
| 29 | D-REPORTING/D-REPORTING-03 Report Publisher D-REPORTING-0... | D-REPORTING-03 Report Publisher D-REP... | design | design_only |
| 30 | D-REPORTING/D-REPORTING-13 Report Version Manager D-REPOR... | D-REPORTING-13 Report Version Manager... | design | design_only |
| 31 | D-REPORTING/D-REPORTING-27 A-Share Trading Record Templat... | D-REPORTING-27 A-Share Trading Record... | design | design_only |
| 32 | D-REPORTING/Dashboard Engine 仪表盘引擎 | Dashboard Engine 仪表盘引擎 | design | design_only |
| 33 | D-REPORTING/Data Lineage MVP SQLite 血缘MVP用SQLite存储血缘 | Data Lineage MVP SQLite 血缘MVP用SQLi... | design | design_only |
| 34 | D-REPORTING/DateRange 日期范围 | DateRange 日期范围 | design | design_only |
| 35 | D-REPORTING/Day Trade Strategy Attribution Report 做T策略... | Day Trade Strategy Attribution Report... | design | design_only |
| 36 | D-REPORTING/Decision Trace Chain 决策溯源链 | Decision Trace Chain 决策溯源链 | design | design_only |
| 37 | D-REPORTING/Decision Trace Collector Independent Submodul... | Decision Trace Collector Independent ... | design | design_only |
| 38 | D-REPORTING/Decision Trace Collector 决策溯源收集器 | Decision Trace Collector 决策溯源收集器 | design | design_only |
| 39 | D-REPORTING/Decision Trace 决策溯源链 | Decision Trace 决策溯源链 | design | design_only |
| 40 | D-REPORTING/Degradation Strategy C-017 Not Ready PnL No F... | Degradation Strategy C-017 Not Ready ... | design | design_only |
| 41 | D-REPORTING/Differential Privacy ε=1.0 差分隐私ε=1.0 | Differential Privacy ε=1.0 差分隐私ε=1.0 | design | design_only |
| 42 | D-REPORTING/Differential Privacy 差分隐私 | Differential Privacy 差分隐私 | design | design_only |
| 43 | D-REPORTING/Event Subscription via ACL 事件订阅走ACL防腐层 | Event Subscription via ACL 事件订阅走... | design | design_only |
| 44 | D-REPORTING/Evidence Auto Collection 证据自动采集 | Evidence Auto Collection 证据自动采集 | design | design_only |
| 45 | D-REPORTING/Evidence Chain Integrity Verification 证据链... | Evidence Chain Integrity Verification... | design | design_only |
| 46 | D-REPORTING/Evidence Graph Model 证据图模型 | Evidence Graph Model 证据图模型 | design | design_only |
| 47 | D-REPORTING/Execution Quality Report 执行质量报告 | Execution Quality Report 执行质量报告 | design | design_only |
| 48 | D-REPORTING/Explainability Gating 可解释性门控 | Explainability Gating 可解释性门控 | design | design_only |
| 49 | D-REPORTING/Explainability Guarantee 可解释性保障 | Explainability Guarantee 可解释性保障 | design | design_only |
| 50 | D-REPORTING/Hard Dependency D-AUTONOMY-CORE D-DATA 硬依赖 | Hard Dependency D-AUTONOMY-CORE D-DAT... | design | design_only |
| 51 | D-REPORTING/Hash Chain 哈希链 | Hash Chain 哈希链 | design | design_only |
| 52 | D-REPORTING/Historical Failure Mode Library 历史失效模式库 | Historical Failure Mode Library 历史... | design | design_only |
| 53 | D-REPORTING/L1 Event Integrity L1事件完整性 | L1 Event Integrity L1事件完整性 | design | design_only |
| 54 | D-REPORTING/L1 Event Integrity Restricted L1事件完整性受限 | L1 Event Integrity Restricted L1事件... | design | design_only |
| 55 | D-REPORTING/L2 Set Integrity Construction Status L2集合完... | L2 Set Integrity Construction Status ... | design | design_only |
| 56 | D-REPORTING/L2 Set Integrity L2集合完整性 | L2 Set Integrity L2集合完整性 | design | design_only |
| 57 | D-REPORTING/L3 External Verifiability L3外部可验证性 | L3 External Verifiability L3外部可验证性 | design | design_only |
| 58 | D-REPORTING/L3 External Verifiability Restricted L3外部可... | L3 External Verifiability Restricted ... | design | design_only |
| 59 | D-REPORTING/L5 to L6 Explainability L5→L6可解释性 | L5 to L6 Explainability L5→L6可解释性 | design | design_only |
| 60 | D-REPORTING/LIME LIME局部可解释模型 | LIME LIME局部可解释模型 | design | design_only |
| 61 | D-REPORTING/LLM Self-Evaluation LLM自评估 | LLM Self-Evaluation LLM自评估 | design | design_only |
| 62 | D-REPORTING/LLM Summary LLM摘要 | LLM Summary LLM摘要 | design | design_only |
| 63 | D-REPORTING/LLM-as-Explainer 自然语言解释 | LLM-as-Explainer 自然语言解释 | design | design_only |
| 64 | D-REPORTING/LP-007 Attribution Agent V3 归因Agent V3上线 | LP-007 Attribution Agent V3 归因Agent... | design | design_only |
| 65 | D-REPORTING/Man Group AlphaGPT Man Group AlphaGPT实践 | Man Group AlphaGPT Man Group AlphaGPT... | design | design_only |
| 66 | D-REPORTING/Merkle Tree Merkle树 | Merkle Tree Merkle树 | design | design_only |
| 67 | D-REPORTING/Multi-Dimensional Quantitative Health Indicat... | Multi-Dimensional Quantitative Health... | design | design_only |
| 68 | D-REPORTING/Multimodal Financial Reasoning 多模态金融推理 | Multimodal Financial Reasoning 多模态... | design | design_only |
| 69 | D-REPORTING/Neo4j Graph Database Neo4j图数据库 | Neo4j Graph Database Neo4j图数据库 | design | design_only |
| 70 | D-REPORTING/No Domain Event Published 不发布领域事件 | No Domain Event Published 不发布领域事件 | design | design_only |
| 71 | D-REPORTING/P3-Low P3低优先级指令 | P3-Low P3低优先级指令 | design | design_only |
| 72 | D-REPORTING/PerformanceAttributionReport 归因报告 | PerformanceAttributionReport 归因报告 | design | design_only |
| 73 | D-REPORTING/PerformanceAttributionReport 绩效归因报告 | PerformanceAttributionReport 绩效归因... | design | design_only |
| 74 | D-REPORTING/Phase 1 Activation Phase 1激活阶段 | Phase 1 Activation Phase 1激活阶段 | design | design_only |
| 75 | D-REPORTING/Phase 2 Activation Phase 2激活阶段 | Phase 2 Activation Phase 2激活阶段 | design | design_only |
| 76 | D-REPORTING/Phase 3 Activation Phase 3激活阶段 | Phase 3 Activation Phase 3激活阶段 | design | design_only |
| 77 | D-REPORTING/Phase 4 Activation Phase 4激活阶段 | Phase 4 Activation Phase 4激活阶段 | design | design_only |
| 78 | D-REPORTING/Post Trade Analytics Core 交易后分析核心 | Post Trade Analytics Core 交易后分析核心 | design | design_only |
| 79 | D-REPORTING/Post-Market Report Local LLM 盘后报告走本地LLM | Post-Market Report Local LLM 盘后报告... | design | design_only |
| 80 | D-REPORTING/Publisher Hub 发布枢纽 | Publisher Hub 发布枢纽 | design | design_only |
| 81 | D-REPORTING/Real-time P&L Dashboard 实时盈亏仪表盘 | Real-time P&L Dashboard 实时盈亏仪表盘 | design | design_only |
| 82 | D-REPORTING/Report Data Consistency 1 Hour SLA 报告数据一... | Report Data Consistency 1 Hour SLA 报... | design | design_only |
| 83 | D-REPORTING/Report Publisher 发布者报告 | Report Publisher 发布者报告 | design | design_only |
| 84 | D-REPORTING/Report Publisher 报告发布器 | Report Publisher 报告发布器 | design | design_only |
| 85 | D-REPORTING/Report Storage SQLite Parquet Archive 报告存... | Report Storage SQLite Parquet Archive... | design | design_only |
| 86 | D-REPORTING/Report Version Manager 报告版本管理器 | Report Version Manager 报告版本管理器 | design | design_only |
| 87 | D-REPORTING/Report Watermark Tracker 报告水印追踪器 | Report Watermark Tracker 报告水印追踪器 | design | design_only |
| 88 | D-REPORTING/SHAP SHAP沙普利加性解释 | SHAP SHAP沙普利加性解释 | design | design_only |
| 89 | D-REPORTING/SHAP+LIME Dual Attribution SHAP+LIME双归因架构 | SHAP+LIME Dual Attribution SHAP+LIME... | design | design_only |
| 90 | D-REPORTING/SQLite report_archive SQLite报告归档 | SQLite report_archive SQLite报告归档 | design | design_only |
| 91 | D-REPORTING/Sentinel Hallucination Detector Sentinel幻觉... | Sentinel Hallucination Detector Senti... | design | design_only |
| 92 | D-REPORTING/Soft Dependency D-INFRA-RUNTIME 软依赖 | Soft Dependency D-INFRA-RUNTIME 软依赖 | design | design_only |
| 93 | D-REPORTING/SpectralGuardrails 谱分析幻觉检测 | SpectralGuardrails 谱分析幻觉检测 | design | design_only |
| 94 | D-REPORTING/Strategy Degradation Detection 策略退化检测 | Strategy Degradation Detection 策略退... | design | design_only |
| 95 | D-REPORTING/Strategy Explainability Reporter 策略可解释性... | Strategy Explainability Reporter 策略... | design | design_only |
| 96 | D-REPORTING/Strategy Health Score 策略健康评分 | Strategy Health Score 策略健康评分 | design | design_only |
| 97 | D-REPORTING/Submodule Skeleton Thickness 子模块骨架厚度 | Submodule Skeleton Thickness 子模块骨... | design | design_only |
| 98 | D-REPORTING/TCA Engine TCA交易成本分析引擎 | TCA Engine TCA交易成本分析引擎 | design | design_only |
| 99 | D-REPORTING/TCA Engine 引擎 | TCA Engine 引擎 | design | design_only |
| 100 | D-REPORTING/Tax Report 税务报告生成器 | Tax Report 税务报告生成器 | design | design_only |
| 101 | D-REPORTING/Temporal Consistency Verification 时序一致性验证 | Temporal Consistency Verification 时... | design | design_only |
| 102 | D-REPORTING/Three-Layer Audit Architecture 三层审计架构 | Three-Layer Audit Architecture 三层审... | design | design_only |
| 103 | D-REPORTING/TraceCompleteness Indicator TraceCompleteness... | TraceCompleteness Indicator TraceComp... | design | design_only |
| 104 | D-REPORTING/VCP v1.1 Crypto-Shredding PoC VCP v1.1 Crypto... | VCP v1.1 Crypto-Shredding PoC VCP v1.... | design | design_only |
| 105 | D-REPORTING/VCP v1.1 VCP v1.1完整性架构 | VCP v1.1 VCP v1.1完整性架构 | design | design_only |
| 106 | D-REPORTING/VeNRA Double-Lock Zero Hallucination VeNRA双... | VeNRA Double-Lock Zero Hallucination ... | design | design_only |
| 107 | D-REPORTING/attribution-analysis 归因分析 | attribution-analysis 归因分析 | design | design_only |
| 108 | D-REPORTING/strategic-attributor Agent Card strategic-att... | strategic-attributor Agent Card strat... | design | design_only |
| 109 | D-REPORTING/strategy-health-score 策略健康评分 | strategy-health-score 策略健康评分 | design | design_only |
| 110 | D-REPORTING/v4.0+ Success Criteria v4.0+成功标准 | v4.0+ Success Criteria v4.0+成功标准 | design | design_only |
| 111 | D-REPORTING/交易绩效归因模型 Performance Attribution Model | 交易绩效归因模型 Performance Attribut... | design | design_only |
| 112 | D-REPORTING/因子归因 Factor Attribution | 因子归因 Factor Attribution | design | design_only |
| 113 | D-REPORTING/风险归因 Risk Attribution | 风险归因 Risk Attribution | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 114 条 / 114 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 114 条 / 114 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 91 条 / edges                                │
│   [runtime]: 15 条 / edges                                       │
│   [event]: 4 条 / edges                                          │
│   [contract]: 2 条 / edges                                       │
│   [config_depends]: 1 条 / edges                                 │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (91 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-REPORTING 报告 → TCA Engine 引擎                             │
│   TCA Engine 引擎 → Attribution Engine 引擎                      │
│   Attribution Engine 引擎 → Report Publisher 发布者报告          │
│   Report Publisher 发布者报告 → A-Share Trading Review En...     │
│   A-Share Trading Review En... → Report Version Manager 报...    │
│   Report Version Manager 报... → A股交易记录模板引擎 A-Sha...    │
│   A股交易记录模板引擎 A-Sha... → Dashboard Engine 仪表盘引擎     │
│   Dashboard Engine 仪表盘引擎 → Compliance Reporter 合规...      │
│   Compliance Reporter 合规... → Strategy Explainability R...     │
│   Strategy Explainability R... → Report Watermark Tracker ...    │
│   Report Watermark Tracker ... → A-Share Performance Audit...    │
│   A-Share Performance Audit... → Attributor Agent 归因Agent      │
│   Attributor Agent 归因Agent → Attribution Analysis 归因...      │
│   Attributor Agent 归因Agent → VCP v1.1 Crypto-Shredding...      │
│   Attribution Analysis 归因... → Strategy Health Score 策...     │
│   Strategy Health Score 策... → Explainability Guarantee ...     │
│   Explainability Guarantee ... → SHAP SHAP沙普利加性解释         │
│   SHAP SHAP沙普利加性解释 → LIME LIME局部可解释模型              │
│   LIME LIME局部可解释模型 → Brinson Model Brinson模型            │
│   Brinson Model Brinson模型 → Merkle Tree Merkle树               │
│   Merkle Tree Merkle树 → Hash Chain 哈希链                       │
│   Merkle Tree Merkle树 → Man Group AlphaGPT Man Gr...            │
│   Hash Chain 哈希链 → SQLite report_archive SQL...               │
│   SQLite report_archive SQL... → LLM Summary LLM摘要             │
│   LLM Summary LLM摘要 → Neo4j Graph Database Neo4...             │
│   Neo4j Graph Database Neo4... → Differential Privacy 差分...    │
│   Differential Privacy 差分... → Decision Trace Chain 决策...    │
│   Decision Trace Chain 决策... → TraceCompleteness Indicat...    │
│   TraceCompleteness Indicat... → Evidence Graph Model 证据...    │
│   Evidence Graph Model 证据... → Decision Trace Collector ...    │
│   Decision Trace Collector ... → Capital Curve Analyzer 资...    │
│   Capital Curve Analyzer 资... → Publisher Hub 发布枢纽          │
│   Capital Curve Analyzer 资... → LP-007 Attribution Agent ...    │
│   Publisher Hub 发布枢纽 → Evidence Chain Integrity ...          │
│   Evidence Chain Integrity ... → Evidence Auto Collection ...    │
│   Evidence Auto Collection ... → Temporal Consistency Veri...    │
│   Temporal Consistency Veri... → Day Trade Strategy Attrib...    │
│   Day Trade Strategy Attrib... → Execution Quality Report ...    │
│   Execution Quality Report ... → Multi-Dimensional Quantit...    │
│   Multi-Dimensional Quantit... → Historical Failure Mode L...    │
│   Historical Failure Mode L... → Abnormal Decision Detecti...    │
│   Abnormal Decision Detecti... → Causal SHAP 因果SHAP            │
│   Causal SHAP 因果SHAP → Concept-Based Explanation...            │
│   Concept-Based Explanation... → LLM-as-Explainer 自然语言...    │
│   LLM-as-Explainer 自然语言... → L2 Set Integrity L2集合完...    │
│   L2 Set Integrity L2集合完... → L3 External Verifiability...    │
│   L3 External Verifiability... → strategic-attributor Agen...    │
│   strategic-attributor Agen... → attribution-analysis 归因...    │
│   attribution-analysis 归因... → strategy-health-score 策...     │
│   ...还有 42 条 / 42 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[runtime]** (15 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (1 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 114 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `13_d_reporting_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
