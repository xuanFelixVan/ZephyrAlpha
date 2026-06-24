---
doc_type: domain_architecture_diagram
title: D-COMPLIANCE 合规架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 18_d_compliance / 合规 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示合规（D-COMPLIANCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 合规（D-COMPLIANCE）的模块分布。共 916 个模块 / 916 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (30 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/compliance/__init__.py  [prototype]                 │
│   src/zephyr/compliance/_extensions/__init__.py  [scaffold_pl... │
│   src/zephyr/compliance/aisg_sandbox.py  [prototype]             │
│   src/zephyr/compliance/api/__init__.py  [scaffold_placeholder]  │
│   src/zephyr/compliance/artifact_scanner.py  [prototype]         │
│   src/zephyr/compliance/audit_orchestrator/__init__.py  [prot... │
│   src/zephyr/compliance/audit_trail/__init__.py  [prototype]     │
│   src/zephyr/compliance/audit_trail/bridges/__init__.py  [pro... │
│   src/zephyr/compliance/behavioral_admission/__init__.py  [pr... │
│   src/zephyr/compliance/behavioral_auditor/__init__.py  [prot... │
│   src/zephyr/compliance/compliance_gate_a6/__init__.py  [prot... │
│   src/zephyr/compliance/compliance_manager.py  [prototype]       │
│   src/zephyr/compliance/core/__init__.py  [scaffold_placeholder] │
│   src/zephyr/compliance/default_security_gateway.py  [prototype] │
│   src/zephyr/compliance/evidence_pack.py  [prototype]            │
│   src/zephyr/compliance/financial_compliance.py  [prototype]     │
│   src/zephyr/compliance/implementations/__init__.py  [prototype] │
│   src/zephyr/compliance/infrastructure/__init__.py  [scaffold... │
│   ...还有 12 个模块 / 12 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (886 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   2025.7.7 Programmatic Trading Rules 2025.7.7程序化交易管理...  │
│   2026 Year End Same Controller Account Supervision 2026年底...  │
│   2026-2027 T+0 Trial 2026-2027 T+0交易试点  [design]            │
│   2026.1.12 Stock Connect Report Guidance 2026.1.12沪深股通程... │
│   2026.4.7 New Implementation Rules 2026.4.7新版实施细则  [de... │
│   2026.5.15 Derivatives Trading Supervision 2026.5.15衍生品交... │
│   2026.5.8 Agent Application Opinion 2026.5.8智能体规范应用与... │
│   2026H2 Abnormal Trading Monitor Standard 2026H2程序化异常交... │
│   2026H2 HFT Differential Pricing 2026H2高频交易差异化收费  [... │
│   2026Q3-Q4 Northbound Regulation 2026Q3-Q4北向资金程序化交易... │
│   2027H1 Strategy Code Filing 2027H1量化策略代码报备与核查  [... │
│   27 Buildable Functions Implementation Order 27项能建功能实...  │
│   27 Buildable Functions Implementation Order 能建功能27项实...  │
│   47 Functions Binary Decision 47项功能二元裁定  [design]        │
│   47 Functions Binary Verdict 47项功能二元裁定  [design]         │
│   A Share Trading Discipline Compliance Check A股交易纪律合规... │
│   A Share Trading System A股交易制度  [design]                   │
│   A-Share Trading Discipline Checker A股交易纪律检查  [design]   │
│   ...还有 868 个模块 / 868 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 916 个模块 / 916 modules）。

### L2 领域层 / Domain Layer (30 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/compliance/__init__.py | src/zephyr/compliance/__init__.py | prototype | draft |
| 2 | src/zephyr/compliance/_extensions/__init__.py | src/zephyr/compliance/_extensions/__i... | scaffold_placeholder | orphan |
| 3 | src/zephyr/compliance/aisg_sandbox.py | src/zephyr/compliance/aisg_sandbox.py | prototype | draft |
| 4 | src/zephyr/compliance/api/__init__.py | src/zephyr/compliance/api/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/compliance/artifact_scanner.py | src/zephyr/compliance/artifact_scanne... | prototype | draft |
| 6 | src/zephyr/compliance/audit_orchestrator/__init__.py | src/zephyr/compliance/audit_orchestra... | prototype | draft |
| 7 | src/zephyr/compliance/audit_trail/__init__.py | src/zephyr/compliance/audit_trail/__i... | prototype | draft |
| 8 | src/zephyr/compliance/audit_trail/bridges/__init__.py | src/zephyr/compliance/audit_trail/bri... | prototype | draft |
| 9 | src/zephyr/compliance/behavioral_admission/__init__.py | src/zephyr/compliance/behavioral_admi... | prototype | draft |
| 10 | src/zephyr/compliance/behavioral_auditor/__init__.py | src/zephyr/compliance/behavioral_audi... | prototype | draft |
| 11 | src/zephyr/compliance/compliance_gate_a6/__init__.py | src/zephyr/compliance/compliance_gate... | prototype | draft |
| 12 | src/zephyr/compliance/compliance_manager.py | src/zephyr/compliance/compliance_mana... | prototype | draft |
| 13 | src/zephyr/compliance/core/__init__.py | src/zephyr/compliance/core/__init__.py | scaffold_placeholder | orphan |
| 14 | src/zephyr/compliance/default_security_gateway.py | src/zephyr/compliance/default_securit... | prototype | draft |
| 15 | src/zephyr/compliance/evidence_pack.py | src/zephyr/compliance/evidence_pack.py | prototype | draft |
| 16 | src/zephyr/compliance/financial_compliance.py | src/zephyr/compliance/financial_compl... | prototype | draft |
| 17 | src/zephyr/compliance/implementations/__init__.py | src/zephyr/compliance/implementations... | prototype | draft |
| 18 | src/zephyr/compliance/infrastructure/__init__.py | src/zephyr/compliance/infrastructure/... | scaffold_placeholder | orphan |
| 19 | src/zephyr/compliance/integrity.py | src/zephyr/compliance/integrity.py | prototype | draft |
| 20 | src/zephyr/compliance/merkle_hourly.py | src/zephyr/compliance/merkle_hourly.py | prototype | draft |
| 21 | src/zephyr/compliance/models/__init__.py | src/zephyr/compliance/models/__init__.py | scaffold_placeholder | orphan |
| 22 | src/zephyr/compliance/security_gateway_base.py | src/zephyr/compliance/security_gatewa... | prototype | draft |
| 23 | src/zephyr/compliance/semantic_auditor/__init__.py | src/zephyr/compliance/semantic_audito... | prototype | draft |
| 24 | src/zephyr/compliance/services/__init__.py | src/zephyr/compliance/services/__init... | scaffold_placeholder | orphan |
| 25 | src/zephyr/compliance/zero_knowledge_audit_stub/__init__.py | src/zephyr/compliance/zero_knowledge_... | prototype | draft |
| 26 | 交易监控规则引擎+监管报告生成器+身份验证集成器+风险管理集... | RegTech Compliance Automation Engine | design | design_only |
| 27 | 合规域-交易纪律/D-COMPLIANCE-23 | A-Share Trading Discipline Checker | design | design_only |
| 28 | 合规域-持续运营/D-COMPLIANCE-13 | AML/KYC Engine | design | design_only |
| 29 | 合规域-规则验证/D-COMPLIANCE-20 | Compliance Rule Backtester | design | design_only |
| 30 | 异常交易披露数据采集器(监管披露数据→统计因子)/D-DATA-89 | 龙虎榜 | design | design_only |

### 未分类 / Unclassified (886 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-COMPLIANCE/2025.7.7 Programmatic Trading Rules 2025.7.7... | 2025.7.7 Programmatic Trading Rules 2... | design | design_only |
| 2 | D-COMPLIANCE/2026 Year End Same Controller Account Superv... | 2026 Year End Same Controller Account... | design | design_only |
| 3 | D-COMPLIANCE/2026-2027 T+0 Trial 2026-2027 T+0交易试点 | 2026-2027 T+0 Trial 2026-2027 T+0交易... | design | design_only |
| 4 | D-COMPLIANCE/2026.1.12 Stock Connect Report Guidance 2026... | 2026.1.12 Stock Connect Report Guidan... | design | design_only |
| 5 | D-COMPLIANCE/2026.4.7 New Implementation Rules 2026.4.7新... | 2026.4.7 New Implementation Rules 202... | design | design_only |
| 6 | D-COMPLIANCE/2026.5.15 Derivatives Trading Supervision 20... | 2026.5.15 Derivatives Trading Supervi... | design | design_only |
| 7 | D-COMPLIANCE/2026.5.8 Agent Application Opinion 2026.5.8... | 2026.5.8 Agent Application Opinion 20... | design | design_only |
| 8 | D-COMPLIANCE/2026H2 Abnormal Trading Monitor Standard 202... | 2026H2 Abnormal Trading Monitor Stand... | design | design_only |
| 9 | D-COMPLIANCE/2026H2 HFT Differential Pricing 2026H2高频交... | 2026H2 HFT Differential Pricing 2026H... | design | design_only |
| 10 | D-COMPLIANCE/2026Q3-Q4 Northbound Regulation 2026Q3-Q4北... | 2026Q3-Q4 Northbound Regulation 2026Q... | design | design_only |
| 11 | D-COMPLIANCE/2027H1 Strategy Code Filing 2027H1量化策略代... | 2027H1 Strategy Code Filing 2027H1量... | design | design_only |
| 12 | D-COMPLIANCE/27 Buildable Functions Implementation Order ... | 27 Buildable Functions Implementation... | design | design_only |
| 13 | D-COMPLIANCE/27 Buildable Functions Implementation Order ... | 27 Buildable Functions Implementation... | design | design_only |
| 14 | D-COMPLIANCE/47 Functions Binary Decision 47项功能二元裁定 | 47 Functions Binary Decision 47项功能... | design | design_only |
| 15 | D-COMPLIANCE/47 Functions Binary Verdict 47项功能二元裁定 | 47 Functions Binary Verdict 47项功能... | design | design_only |
| 16 | D-COMPLIANCE/A Share Trading Discipline Compliance Check ... | A Share Trading Discipline Compliance... | design | design_only |
| 17 | D-COMPLIANCE/A Share Trading System A股交易制度 | A Share Trading System A股交易制度 | design | design_only |
| 18 | D-COMPLIANCE/A-Share Trading Discipline Checker A股交易纪... | A-Share Trading Discipline Checker A... | design | design_only |
| 19 | D-COMPLIANCE/A-Share Trading Discipline Compliance Check ... | A-Share Trading Discipline Compliance... | design | design_only |
| 20 | D-COMPLIANCE/A1 §29.25 Migration EU AI Act Compliance Ar... | A1 §29.25 Migration EU AI Act Compli... | design | design_only |
| 21 | D-COMPLIANCE/AI Act Compliance Gap Assessment AI Act合规... | AI Act Compliance Gap Assessment AI A... | design | design_only |
| 22 | D-COMPLIANCE/AI Act Compliance Metrics AI Act合规度量 | AI Act Compliance Metrics AI Act合规度量 | design | design_only |
| 23 | D-COMPLIANCE/AI Autonomous Spoofing AI自主发起spoofing | AI Autonomous Spoofing AI自主发起spoo... | design | design_only |
| 24 | D-COMPLIANCE/AI Compliance AI合规 | AI Compliance AI合规 | design | design_only |
| 25 | D-COMPLIANCE/AI Compliance AI合规层 | AI Compliance AI合规层 | design | design_only |
| 26 | D-COMPLIANCE/AI Compliance Explainability Human Oversight... | AI Compliance Explainability Human Ov... | design | design_only |
| 27 | D-COMPLIANCE/AI Compliance Rule Auto Extraction AI合规规... | AI Compliance Rule Auto Extraction AI... | design | design_only |
| 28 | D-COMPLIANCE/AI Compliance Rule Auto Extractor AI合规规则... | AI Compliance Rule Auto Extractor AI... | design | design_only |
| 29 | D-COMPLIANCE/AI Compliance Rule Auto Extractor AI合规规则... | AI Compliance Rule Auto Extractor AI... | design | design_only |
| 30 | D-COMPLIANCE/AI Compliance Suggestion Approval AI合规建议... | AI Compliance Suggestion Approval AI... | design | design_only |
| 31 | D-COMPLIANCE/AI Decision Process Log AI决策过程日志 | AI Decision Process Log AI决策过程日志 | design | design_only |
| 32 | D-COMPLIANCE/AI Decision Real-time Monitoring AI决策实时监控 | AI Decision Real-time Monitoring AI决... | design | design_only |
| 33 | D-COMPLIANCE/AI Ethics Statement Decision AI伦理声明裁定 | AI Ethics Statement Decision AI伦理声... | design | design_only |
| 34 | D-COMPLIANCE/AI Operational Risk Prediction AI操作风险预测 | AI Operational Risk Prediction AI操作... | design | design_only |
| 35 | D-COMPLIANCE/AI Risk Classification AI风险分类 | AI Risk Classification AI风险分类 | design | design_only |
| 36 | D-COMPLIANCE/AI Trading Regulation AI交易法规门禁 | AI Trading Regulation AI交易法规门禁 | design | design_only |
| 37 | D-COMPLIANCE/AI Training Data Audit AI训练数据审计 | AI Training Data Audit AI训练数据审计 | design | design_only |
| 38 | D-COMPLIANCE/AI Training Data Auditor AI训练数据审计 | AI Training Data Auditor AI训练数据审计 | design | design_only |
| 39 | D-COMPLIANCE/AI自主Spoofing防护 | AI自主Spoofing防护 | design | design_only |
| 40 | D-COMPLIANCE/AML KYC Engine AML KYC引擎 | AML KYC Engine AML KYC引擎 | design | design_only |
| 41 | D-COMPLIANCE/AML KYC Engine AML/KYC引擎 | AML KYC Engine AML/KYC引擎 | design | design_only |
| 42 | D-COMPLIANCE/AML Transaction Monitoring 反洗钱交易监控 | AML Transaction Monitoring 反洗钱交易... | design | design_only |
| 43 | D-COMPLIANCE/AML/KYC Engine反洗钱/客户识别 | AML/KYC Engine反洗钱/客户识别 | design | design_only |
| 44 | D-COMPLIANCE/AUM Threshold AUM门槛 | AUM Threshold AUM门槛 | design | design_only |
| 45 | D-COMPLIANCE/Abnormal Trading Detection Decision 异常交易... | Abnormal Trading Detection Decision ... | design | design_only |
| 46 | D-COMPLIANCE/Abnormal Trading Monitoring Supervision 异常... | Abnormal Trading Monitoring Supervisi... | design | design_only |
| 47 | D-COMPLIANCE/Abnormal Trading Monitoring 异常交易行为监控 | Abnormal Trading Monitoring 异常交易... | design | design_only |
| 48 | D-COMPLIANCE/Abnormal Trading Self Report 异常交易自报 | Abnormal Trading Self Report 异常交易... | design | design_only |
| 49 | D-COMPLIANCE/Abnormal Trading Self-Report 异常交易自报 | Abnormal Trading Self-Report 异常交易... | design | design_only |
| 50 | D-COMPLIANCE/Abnormal Volatility Trigger Detection 异常波... | Abnormal Volatility Trigger Detection... | design | design_only |
| 51 | D-COMPLIANCE/Abnormal Volatility Trigger 异常波动触发 | Abnormal Volatility Trigger 异常波动触发 | design | design_only |
| 52 | D-COMPLIANCE/Account Basic Info Report 账户基本信息报告 | Account Basic Info Report 账户基本信... | design | design_only |
| 53 | D-COMPLIANCE/Accountability 责任追究 | Accountability 责任追究 | design | design_only |
| 54 | D-COMPLIANCE/Accuracy Robustness Cybersecurity 准确性鲁棒... | Accuracy Robustness Cybersecurity 准... | design | design_only |
| 55 | D-COMPLIANCE/Action Conditional CP Application 交易决策安... | Action Conditional CP Application 交... | design | design_only |
| 56 | D-COMPLIANCE/Ad Hoc Report 临时报告 | Ad Hoc Report 临时报告 | design | design_only |
| 57 | D-COMPLIANCE/Adaptive Conformal Inference Application 非... | Adaptive Conformal Inference Applicat... | design | design_only |
| 58 | D-COMPLIANCE/Add Position 加仓行为 | Add Position 加仓行为 | design | design_only |
| 59 | D-COMPLIANCE/Advanced Coordinated Detection 高级协同检测 | Advanced Coordinated Detection 高级协... | design | design_only |
| 60 | D-COMPLIANCE/Advanced Coordination Detection 高级协同检测 | Advanced Coordination Detection 高级... | design | design_only |
| 61 | D-COMPLIANCE/Agent Identity Registration Agent身份注册 | Agent Identity Registration Agent身份... | design | design_only |
| 62 | D-COMPLIANCE/Agent Interoperability Standard Agent互操作... | Agent Interoperability Standard Agent... | design | design_only |
| 63 | D-COMPLIANCE/Agent Regulation Opinion 智能体规范意见 | Agent Regulation Opinion 智能体规范意见 | design | design_only |
| 64 | D-COMPLIANCE/Agentic Systemic Risk Agentic系统性风险 | Agentic Systemic Risk Agentic系统性风险 | design | design_only |
| 65 | D-COMPLIANCE/Almgren Chriss Impact Model 参与率冲击模型 | Almgren Chriss Impact Model 参与率冲... | design | design_only |
| 66 | D-COMPLIANCE/Annual Report Preview Deadline 年报预告截止日 | Annual Report Preview Deadline 年报预... | design | design_only |
| 67 | D-COMPLIANCE/Annual Report Preview Period 年报预告强制披露期 | Annual Report Preview Period 年报预告... | design | design_only |
| 68 | D-COMPLIANCE/Annual Report Q1 Deadline 年报+一季报截止日 | Annual Report Q1 Deadline 年报+一季报... | design | design_only |
| 69 | D-COMPLIANCE/Annual Report Q1 Disclosure Period 年报+一季... | Annual Report Q1 Disclosure Period 年... | design | design_only |
| 70 | D-COMPLIANCE/Annual Risk Assessment 年度风险评估 | Annual Risk Assessment 年度风险评估 | design | design_only |
| 71 | D-COMPLIANCE/Anti AI Arms Race 反对AI军备竞赛原则 | Anti AI Arms Race 反对AI军备竞赛原则 | design | design_only |
| 72 | D-COMPLIANCE/Association Analysis 关联分析 | Association Analysis 关联分析 | design | design_only |
| 73 | D-COMPLIANCE/Audit Evidence Chain Architecture 审计证据链... | Audit Evidence Chain Architecture 审... | design | design_only |
| 74 | D-COMPLIANCE/Audit Request Event 审计请求事件 | Audit Request Event 审计请求事件 | design | design_only |
| 75 | D-COMPLIANCE/Audit Trail Dependency Integrity Verifier 审... | Audit Trail Dependency Integrity Veri... | design | design_only |
| 76 | D-COMPLIANCE/Audit and Evidence Layer 审计与证据层 | Audit and Evidence Layer 审计与证据层 | design | design_only |
| 77 | D-COMPLIANCE/Auto Regulatory Report Interface Decision 自... | Auto Regulatory Report Interface Deci... | design | design_only |
| 78 | D-COMPLIANCE/Automatic Logging 自动日志记录 | Automatic Logging 自动日志记录 | design | design_only |
| 79 | D-COMPLIANCE/Batch Auditor 批量审计器 | Batch Auditor 批量审计器 | design | design_only |
| 80 | D-COMPLIANCE/Behavior Pattern Proof Decision 行为模式证明... | Behavior Pattern Proof Decision 行为... | design | design_only |
| 81 | D-COMPLIANCE/Behavior Pattern Proof 行为模式证明 | Behavior Pattern Proof 行为模式证明 | design | design_only |
| 82 | D-COMPLIANCE/Best Execution Documenter执行质量文档 | Best Execution Documenter执行质量文档 | design | design_only |
| 83 | D-COMPLIANCE/Bias Assessment Report 偏差评估报告 | Bias Assessment Report 偏差评估报告 | design | design_only |
| 84 | D-COMPLIANCE/Binary Verdict Principle 二元裁定原则 | Binary Verdict Principle 二元裁定原则 | design | design_only |
| 85 | D-COMPLIANCE/Bulletproofs Bulletproofs技术 | Bulletproofs Bulletproofs技术 | design | design_only |
| 86 | D-COMPLIANCE/CDD EDD Module CDD/EDD模块 | CDD EDD Module CDD/EDD模块 | design | design_only |
| 87 | D-COMPLIANCE/CER Cancellation to Execution Ratio 撤单执行比 | CER Cancellation to Execution Ratio ... | design | design_only |
| 88 | D-COMPLIANCE/CFFEX Programmatic Trading Rules 中金所程序... | CFFEX Programmatic Trading Rules 中金... | design | design_only |
| 89 | D-COMPLIANCE/CISA SBOM Minimum Element Check CISA SBOM最... | CISA SBOM Minimum Element Check CISA ... | design | design_only |
| 90 | D-COMPLIANCE/CISA SBOM合规检查器 | CISA SBOM合规检查器 | design | design_only |
| 91 | D-COMPLIANCE/CL0 Regulation Layer 法规与标准层 | CL0 Regulation Layer 法规与标准层 | design | design_only |
| 92 | D-COMPLIANCE/CL1 Compliance Rule Layer 合规规则层 | CL1 Compliance Rule Layer 合规规则层 | design | design_only |
| 93 | D-COMPLIANCE/CL2-A Trading Compliance Layer 交易合规层 | CL2-A Trading Compliance Layer 交易合... | design | design_only |
| 94 | D-COMPLIANCE/CL2-B Position Compliance Layer 持仓合规层 | CL2-B Position Compliance Layer 持仓... | design | design_only |
| 95 | D-COMPLIANCE/CL2-C AI Compliance Layer AI合规层 | CL2-C AI Compliance Layer AI合规层 | design | design_only |
| 96 | D-COMPLIANCE/CL2-D Information Operation Compliance Layer... | CL2-D Information Operation Complianc... | design | design_only |
| 97 | D-COMPLIANCE/CL3 Compliance Execution Layer 合规执行层 | CL3 Compliance Execution Layer 合规执... | design | design_only |
| 98 | D-COMPLIANCE/CL4 Audit Evidence Layer 审计与证据层 | CL4 Audit Evidence Layer 审计与证据层 | design | design_only |
| 99 | D-COMPLIANCE/CL5 Zero Knowledge Audit Layer 零知识审计层 | CL5 Zero Knowledge Audit Layer 零知识... | design | design_only |
| 100 | D-COMPLIANCE/CNN Spoofing Filter CNN实时Spoofing过滤器 | CNN Spoofing Filter CNN实时Spoofing过... | design | design_only |
| 101 | D-COMPLIANCE/CSRC 2026-2027 Regulatory Roadmap 证监会2026... | CSRC 2026-2027 Regulatory Roadmap 证... | design | design_only |
| 102 | D-COMPLIANCE/CSRC Programmatic Trading Regulation 证监会... | CSRC Programmatic Trading Regulation ... | design | design_only |
| 103 | D-COMPLIANCE/Cancel Rate Limit 15% 撤单率限制15% | Cancel Rate Limit 15% 撤单率限制15% | design | design_only |
| 104 | D-COMPLIANCE/Cancellation Rate Check Decision 撤单率检查裁定 | Cancellation Rate Check Decision 撤单... | design | design_only |
| 105 | D-COMPLIANCE/Cancellation Velocity 撤单速度 | Cancellation Velocity 撤单速度 | design | design_only |
| 106 | D-COMPLIANCE/Capital Flow 资金流向 | Capital Flow 资金流向 | design | design_only |
| 107 | D-COMPLIANCE/Cascade Contrastive Learning 级联对比学习 | Cascade Contrastive Learning 级联对比... | design | design_only |
| 108 | D-COMPLIANCE/Change Impact Analysis 变更影响分析 | Change Impact Analysis 变更影响分析 | design | design_only |
| 109 | D-COMPLIANCE/Change Report 变更报告 | Change Report 变更报告 | design | design_only |
| 110 | D-COMPLIANCE/Chase High 踏空追高 | Chase High 踏空追高 | design | design_only |
| 111 | D-COMPLIANCE/China Programmatic Trading Implementation Ru... | China Programmatic Trading Implementa... | design | design_only |
| 112 | D-COMPLIANCE/China Regulations 中国法规 | China Regulations 中国法规 | design | design_only |
| 113 | D-COMPLIANCE/China Regulations 中国法规映射 | China Regulations 中国法规映射 | design | design_only |
| 114 | D-COMPLIANCE/Chip Change 筹码变化 | Chip Change 筹码变化 | design | design_only |
| 115 | D-COMPLIANCE/Collection Integrity Merkle Tree 集合完整性M... | Collection Integrity Merkle Tree 集合... | design | design_only |
| 116 | D-COMPLIANCE/Communication Archive 通信存档 | Communication Archive 通信存档 | design | design_only |
| 117 | D-COMPLIANCE/Communication Collector 通信采集器 | Communication Collector 通信采集器 | design | design_only |
| 118 | D-COMPLIANCE/Communication Content NLP Analysis 通信内容N... | Communication Content NLP Analysis 通... | design | design_only |
| 119 | D-COMPLIANCE/Communication Monitoring 通信监控 | Communication Monitoring 通信监控 | design | design_only |
| 120 | D-COMPLIANCE/Communication Monitor通信监控 | Communication Monitor通信监控 | design | design_only |
| 121 | D-COMPLIANCE/Compatibility Check 兼容性检查 | Compatibility Check 兼容性检查 | design | design_only |
| 122 | D-COMPLIANCE/Complete Episode Proof 完整episode证明 | Complete Episode Proof 完整episode证明 | design | design_only |
| 123 | D-COMPLIANCE/Complete zkCA Layer Decision 完整zkCA层裁定 | Complete zkCA Layer Decision 完整zkCA... | design | design_only |
| 124 | D-COMPLIANCE/Compliance Agent 合规Agent | Compliance Agent 合规Agent | design | design_only |
| 125 | D-COMPLIANCE/Compliance Architecture A6 合规架构A6 | Compliance Architecture A6 合规架构A6 | design | design_only |
| 126 | D-COMPLIANCE/Compliance Assessment 合规性评估 | Compliance Assessment 合规性评估 | design | design_only |
| 127 | D-COMPLIANCE/Compliance Audit Log 合规审计日志 | Compliance Audit Log 合规审计日志 | design | design_only |
| 128 | D-COMPLIANCE/Compliance Backtest 合规回溯测试 | Compliance Backtest 合规回溯测试 | design | design_only |
| 129 | D-COMPLIANCE/Compliance Case Library 合规案例库 | Compliance Case Library 合规案例库 | design | design_only |
| 130 | D-COMPLIANCE/Compliance Certification Tracking 合规认证追踪 | Compliance Certification Tracking 合... | design | design_only |
| 131 | D-COMPLIANCE/Compliance Change Approval KPI Decision 合规... | Compliance Change Approval KPI Decisi... | design | design_only |
| 132 | D-COMPLIANCE/Compliance Change Approval 合规变更审批 | Compliance Change Approval 合规变更审批 | design | design_only |
| 133 | D-COMPLIANCE/Compliance Check Coverage Rate 合规检查覆盖率 | Compliance Check Coverage Rate 合规检... | design | design_only |
| 134 | D-COMPLIANCE/Compliance Check Event 合规检查事件 | Compliance Check Event 合规检查事件 | design | design_only |
| 135 | D-COMPLIANCE/Compliance Clause Dependency Chain Validator... | Compliance Clause Dependency Chain Va... | design | design_only |
| 136 | D-COMPLIANCE/Compliance Clause Dependency Chain Verificat... | Compliance Clause Dependency Chain Ve... | design | design_only |
| 137 | D-COMPLIANCE/Compliance Clause Dependency Chain Verificat... | Compliance Clause Dependency Chain Ve... | design | design_only |
| 138 | D-COMPLIANCE/Compliance Continuous Operations 合规持续运营 | Compliance Continuous Operations 合规... | design | design_only |
| 139 | D-COMPLIANCE/Compliance Core 合规核心 | Compliance Core 合规核心 | design | design_only |
| 140 | D-COMPLIANCE/Compliance Cross-Domain 合规跨域 | Compliance Cross-Domain 合规跨域 | design | design_only |
| 141 | D-COMPLIANCE/Compliance Dashboard 合规仪表盘 | Compliance Dashboard 合规仪表盘 | design | design_only |
| 142 | D-COMPLIANCE/Compliance Document Index 合规文档索引 | Compliance Document Index 合规文档索引 | design | design_only |
| 143 | D-COMPLIANCE/Compliance Document Package 合规文档包 | Compliance Document Package 合规文档包 | design | design_only |
| 144 | D-COMPLIANCE/Compliance Drift Detector 合规漂移检测器 | Compliance Drift Detector 合规漂移检测器 | design | design_only |
| 145 | D-COMPLIANCE/Compliance Engine Architecture Diagram 合规... | Compliance Engine Architecture Diagra... | design | design_only |
| 146 | D-COMPLIANCE/Compliance Engine Architecture 合规引擎架构 | Compliance Engine Architecture 合规引... | design | design_only |
| 147 | D-COMPLIANCE/Compliance Engine Architecture 合规引擎架构图 | Compliance Engine Architecture 合规引... | design | design_only |
| 148 | D-COMPLIANCE/Compliance Event Escalation 合规事件升级 | Compliance Event Escalation 合规事件升级 | design | design_only |
| 149 | D-COMPLIANCE/Compliance Event Escalator 合规事件升级器 | Compliance Event Escalator 合规事件升... | design | design_only |
| 150 | D-COMPLIANCE/Compliance Event Flow Decision 合规事件流裁定 | Compliance Event Flow Decision 合规事... | design | design_only |
| 151 | D-COMPLIANCE/Compliance Event Flow 合规事件流 | Compliance Event Flow 合规事件流 | design | design_only |
| 152 | D-COMPLIANCE/Compliance Evidence Chain Generator 合规证据... | Compliance Evidence Chain Generator ... | design | design_only |
| 153 | D-COMPLIANCE/Compliance Evidence Chain合规证据链 | Compliance Evidence Chain合规证据链 | design | design_only |
| 154 | D-COMPLIANCE/Compliance Evidence Graph 合规证据图 | Compliance Evidence Graph 合规证据图 | design | design_only |
| 155 | D-COMPLIANCE/Compliance Exception Application 合规例外申请 | Compliance Exception Application 合规... | design | design_only |
| 156 | D-COMPLIANCE/Compliance Exception Approval Flow 合规例外... | Compliance Exception Approval Flow 合... | design | design_only |
| 157 | D-COMPLIANCE/Compliance Exception Approval Flow 合规例外... | Compliance Exception Approval Flow 合... | design | design_only |
| 158 | D-COMPLIANCE/Compliance Exception Approval Workflow 合规... | Compliance Exception Approval Workflo... | design | design_only |
| 159 | D-COMPLIANCE/Compliance Exception Condition Management 合... | Compliance Exception Condition Manage... | design | design_only |
| 160 | D-COMPLIANCE/Compliance Exception Report 合规例外报告 | Compliance Exception Report 合规例外报告 | design | design_only |
| 161 | D-COMPLIANCE/Compliance Exception Tracking 合规例外追踪 | Compliance Exception Tracking 合规例... | design | design_only |
| 162 | D-COMPLIANCE/Compliance Execution Layer 合规执行层 | Compliance Execution Layer 合规执行层 | design | design_only |
| 163 | D-COMPLIANCE/Compliance Gap Report 合规差距报告 | Compliance Gap Report 合规差距报告 | design | design_only |
| 164 | D-COMPLIANCE/Compliance Governance Rule 合规治理规则 | Compliance Governance Rule 合规治理规则 | design | design_only |
| 165 | D-COMPLIANCE/Compliance Governance and KPI 合规治理与KPI | Compliance Governance and KPI 合规治... | design | design_only |
| 166 | D-COMPLIANCE/Compliance Governance 合规治理 | Compliance Governance 合规治理 | design | design_only |
| 167 | D-COMPLIANCE/Compliance Integration Test 合规集成测试 | Compliance Integration Test 合规集成测试 | design | design_only |
| 168 | D-COMPLIANCE/Compliance KPI 合规KPI | Compliance KPI 合规KPI | design | design_only |
| 169 | D-COMPLIANCE/Compliance Knowledge Accumulation 合规知识持... | Compliance Knowledge Accumulation 合... | design | design_only |
| 170 | D-COMPLIANCE/Compliance Knowledge Continuous Accumulation... | Compliance Knowledge Continuous Accum... | design | design_only |
| 171 | D-COMPLIANCE/Compliance Knowledge Distillation 合规知识蒸馏 | Compliance Knowledge Distillation 合... | design | design_only |
| 172 | D-COMPLIANCE/Compliance Knowledge Quality Scoring 合规知... | Compliance Knowledge Quality Scoring ... | design | design_only |
| 173 | D-COMPLIANCE/Compliance Log 合规日志 | Compliance Log 合规日志 | design | design_only |
| 174 | D-COMPLIANCE/Compliance Officer 合规官 | Compliance Officer 合规官 | design | design_only |
| 175 | D-COMPLIANCE/Compliance Parameter Tuning Approval 合规参... | Compliance Parameter Tuning Approval ... | design | design_only |
| 176 | D-COMPLIANCE/Compliance Penetration Test 合规穿透测试 | Compliance Penetration Test 合规穿透测试 | design | design_only |
| 177 | D-COMPLIANCE/Compliance Policy Drift Detection 合规策略漂... | Compliance Policy Drift Detection 合... | design | design_only |
| 178 | D-COMPLIANCE/Compliance Policy as Code Engine 合规策略即... | Compliance Policy as Code Engine 合规... | design | design_only |
| 179 | D-COMPLIANCE/Compliance Policy as Code 合规策略即代码 | Compliance Policy as Code 合规策略即代码 | design | design_only |
| 180 | D-COMPLIANCE/Compliance Policy-as-Code合规策略即代码 | Compliance Policy-as-Code合规策略即代码 | design | design_only |
| 181 | D-COMPLIANCE/Compliance Regulatory Domain 合规监管域 | Compliance Regulatory Domain 合规监管域 | design | design_only |
| 182 | D-COMPLIANCE/Compliance Report Timeliness 合规报告及时性 | Compliance Report Timeliness 合规报告... | design | design_only |
| 183 | D-COMPLIANCE/Compliance Review 合规评审 | Compliance Review 合规评审 | design | design_only |
| 184 | D-COMPLIANCE/Compliance Rule Backtester 合规规则回测器 | Compliance Rule Backtester 合规规则回... | design | design_only |
| 185 | D-COMPLIANCE/Compliance Rule DSL 合规规则DSL | Compliance Rule DSL 合规规则DSL | design | design_only |
| 186 | D-COMPLIANCE/Compliance Rule DSL 合规规则DSL设计 | Compliance Rule DSL 合规规则DSL设计 | design | design_only |
| 187 | D-COMPLIANCE/Compliance Rule Engine Decision 合规规则引擎... | Compliance Rule Engine Decision 合规... | design | design_only |
| 188 | D-COMPLIANCE/Compliance Rule Engine 合规规则引擎 | Compliance Rule Engine 合规规则引擎 | design | design_only |
| 189 | D-COMPLIANCE/Compliance Rule Layer 合规规则层 | Compliance Rule Layer 合规规则层 | design | design_only |
| 190 | D-COMPLIANCE/Compliance Rule Unit Test 合规规则单元测试 | Compliance Rule Unit Test 合规规则单... | design | design_only |
| 191 | D-COMPLIANCE/Compliance Rule Version Control and Backtest... | Compliance Rule Version Control and B... | design | design_only |
| 192 | D-COMPLIANCE/Compliance Rule Version Control 合规规则版本... | Compliance Rule Version Control 合规... | design | design_only |
| 193 | D-COMPLIANCE/Compliance Rule Version Controller合规规则版... | Compliance Rule Version Controller合... | design | design_only |
| 194 | D-COMPLIANCE/Compliance Rule 合规规则 | Compliance Rule 合规规则 | design | design_only |
| 195 | D-COMPLIANCE/Compliance Stress Test 合规压力测试 | Compliance Stress Test 合规压力测试 | design | design_only |
| 196 | D-COMPLIANCE/Compliance Technical Architecture 合规技术架构 | Compliance Technical Architecture 合... | design | design_only |
| 197 | D-COMPLIANCE/Compliance Technical Depth 合规技术深度 | Compliance Technical Depth 合规技术深度 | design | design_only |
| 198 | D-COMPLIANCE/Compliance Technology Architecture 合规技术架构 | Compliance Technology Architecture 合... | design | design_only |
| 199 | D-COMPLIANCE/Compliance Test Framework Decision 合规测试... | Compliance Test Framework Decision 合... | design | design_only |
| 200 | D-COMPLIANCE/Compliance Test Framework 合规测试框架 | Compliance Test Framework 合规测试框架 | design | design_only |

> (仅显示前 200 个模块，共 886 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 989 条 / 989 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 989 条 / 989 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 833 条 / edges                               │
│   [config_depends]: 53 条 / edges                                │
│   [event]: 44 条 / edges                                         │
│   [contract]: 33 条 / edges                                      │
│   [data]: 26 条 / edges                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (833 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → __init__.py                                      │
│   Trade Surveillance Engine... → Regulatory Reporter监管报...    │
│   Regulatory Reporter监管报... → Best Execution Documenter...    │
│   Best Execution Documenter... → Information Barrier信息隔...    │
│   Information Barrier信息隔... → Insider Trading Monitor内...    │
│   Insider Trading Monitor内... → Market Manipulation Detec...    │
│   Market Manipulation Detec... → Position Reporter持仓报告       │
│   Position Reporter持仓报告 → Communication Monitor通信...       │
│   Communication Monitor通信... → Program Trading Reporter...     │
│   Program Trading Reporter... → AML/KYC Engine反洗钱/客户...     │
│   Program Trading Reporter... → Compliance Rule Engine De...     │
│   AML/KYC Engine反洗钱/客户... → RegTech Compliance Automa...    │
│   RegTech Compliance Automa... → Compliance Evidence Chain...    │
│   Compliance Evidence Chain... → Compliance Policy-as-Code...    │
│   Compliance Policy-as-Code... → Compliance Rule Version C...    │
│   Compliance Rule Version C... → A-Share Trading Disciplin...    │
│   A-Share Trading Disciplin... → 信息隔离墙执行层 Execution      │
│   EU AI Act合规 EU AI Act C... → SBOM Drift Detector SBOM...     │
│   信息隔离墙执行层 Execution → 内幕交易监控器 Monitor            │
│   内幕交易监控器 Monitor → 市场操纵检测器 Detector               │
│   市场操纵检测器 Detector → EU AI Act合规自动化引擎              │
│   市场操纵检测器 Detector → Korea Extreme Market Prog...         │
│   EU AI Act合规自动化引擎 → 中国AI安全框架对齐器                 │
│   中国AI安全框架对齐器 → CISA SBOM合规检查器                     │
│   中国AI安全框架对齐器 → 47 Functions Binary Verdi...            │
│   CISA SBOM合规检查器 → EU CRA SBOM验证器                        │
│   EU CRA SBOM验证器 → Compliance Cross-Domain ...                │
│   Compliance Cross-Domain ... → Information Classificatio...     │
│   Information Classificatio... → Cross-Wall Approval Flow ...    │
│   Information Classificatio... → Volume Ratio Limit Decisi...    │
│   Cross-Wall Approval Flow ... → MNPI Flow Real-Time Monit...    │
│   MNPI Flow Real-Time Monit... → Whiteboard Time Manager ...     │
│   Whiteboard Time Manager ... → Information Window Manage...     │
│   Whiteboard Time Manager ... → Opacity 不透明性                 │
│   Whiteboard Time Manager ... → EU AI Act Transparency EU...     │
│   Information Window Manage... → Trading Pattern Matcher ...     │
│   Information Window Manage... → Compliance Officer 合规官       │
│   Trading Pattern Matcher ... → Related Party Identifier ...     │
│   Related Party Identifier ... → AI Training Data Auditor ...    │
│   Related Party Identifier ... → No Retail Exploitation 不...    │
│   AI Training Data Auditor ... → Rego/OPA Rule Engine Rego...    │
│   Rego/OPA Rule Engine Rego... → Policy Version Manager 策...    │
│   Rego/OPA Rule Engine Rego... → 2027H1 Strategy Code Fili...    │
│   Rego/OPA Rule Engine Rego... → US Stock Trading System ...     │
│   Policy Version Manager 策... → Policy Conflict Detector ...    │
│   Policy Version Manager 策... → CL4 Audit Evidence Layer ...    │
│   Policy Conflict Detector ... → AI Compliance Rule Auto E...    │
│   Policy Conflict Detector ... → Frequent Price Pushing 频...    │
│   AI Compliance Rule Auto E... → Compliance Exception Appr...    │
│   ...还有 784 条 / 784 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (53 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (44 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (33 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (26 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 989 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `18_d_compliance_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
