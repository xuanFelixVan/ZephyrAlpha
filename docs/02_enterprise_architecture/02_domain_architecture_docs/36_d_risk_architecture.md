---
doc_type: domain_architecture_diagram
title: D-RISK 风控架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 36_d_risk / 风控 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示风控（D-RISK）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 风控（D-RISK）的模块分布。共 774 个模块 / 774 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/oms_risk_engine.py  [prototype]                │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (81 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/__init__.py  [prototype]                       │
│   src/zephyr/risk/_extensions/__init__.py  [scaffold_placehol... │
│   src/zephyr/risk/api/__init__.py  [scaffold_placeholder]        │
│   src/zephyr/risk/core/__init__.py  [scaffold_placeholder]       │
│   src/zephyr/risk/cross_asset/__init__.py  [prototype]           │
│   src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/__i... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/__ini... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_ex... │
│   src/zephyr/risk/cross_asset/currency_hedger_and_fixed_incom... │
│   src/zephyr/risk/cross_asset/risk_manager.py  [prototype]       │
│   src/zephyr/risk/cross_asset/risk_manager_base.py  [prototype]  │
│   src/zephyr/risk/implementations/__init__.py  [prototype]       │
│   src/zephyr/risk/implementations/default_position_limit_chec... │
│   src/zephyr/risk/implementations/default_risk_limits_calcula... │
│   src/zephyr/risk/implementations/default_risk_manager_orches... │
│   src/zephyr/risk/implementations/default_risk_validator.py  ... │
│   src/zephyr/risk/implementations/default_stop_loss_engine.py... │
│   src/zephyr/risk/infrastructure/__init__.py  [scaffold_place... │
│   ...还有 63 个模块 / 63 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (692 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN  [design]            │
│   A Share Compliance Rule A股合规规则代管  [design]              │
│   A-Share 5-Signal Systemic Risk Scanner A股5信号系统性风险扫... │
│   A-Share Cascading Circuit Breaker A股级联熔断器  [design]      │
│   A-Share Compliance Custody A股合规代管  [design]               │
│   A-Share Contrarian Dedicated Stop-Loss A股逆向专用止损  [de... │
│   A-Share Contrarian Time-Based Stop-Loss A股逆向时间止损  [d... │
│   A-Share First-Minute Stop-Loss Executor A股首分钟止损执行器... │
│   A-Share Loss Limit Enforcer A股亏损限额强制执行  [design]      │
│   A-Share Multi-Level Loss Circuit Breaker A股多级亏损熔断器 ... │
│   A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自动对冲器 ... │
│   A-Share Stock Blacklist Manager A股股票黑名单管理器  [design]  │
│   A-Share Stop Loss 6 Patterns A股特色止损6种模式  [design]      │
│   A-Share Stop Loss A股止损  [design]                            │
│   A-Share Stop-Loss Rule Engine A股止损规则引擎  [design]        │
│   A-Share Stop-Loss Rule Engine A股特色止损  [design]            │
│   A-Share Stop-Loss/Circuit Breaker Series A股特色止损/熔断系... │
│   A-Share Systemic Risk 3-Level Alerter A股系统性风险三级告警... │
│   ...还有 674 个模块 / 674 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 774 个模块 / 774 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/oms_risk_engine.py | src/zephyr/risk/oms_risk_engine.py | prototype | draft |

### L2 领域层 / Domain Layer (81 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/__init__.py | src/zephyr/risk/__init__.py | prototype | draft |
| 2 | src/zephyr/risk/_extensions/__init__.py | src/zephyr/risk/_extensions/__init__.py | scaffold_placeholder | orphan |
| 3 | src/zephyr/risk/api/__init__.py | src/zephyr/risk/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/risk/core/__init__.py | src/zephyr/risk/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/risk/cross_asset/__init__.py | src/zephyr/risk/cross_asset/__init__.py | prototype | draft |
| 6 | src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/_... | src/zephyr/risk/cross_asset/cross_ass... | prototype | orphan |
| 7 | src/zephyr/risk/cross_asset/cross_market_data_adapter/__i... | src/zephyr/risk/cross_asset/cross_mar... | prototype | draft |
| 8 | src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_... | src/zephyr/risk/cross_asset/cross_mar... | prototype | draft |
| 9 | src/zephyr/risk/cross_asset/currency_hedger_and_fixed_inc... | src/zephyr/risk/cross_asset/currency_... | prototype | orphan |
| 10 | src/zephyr/risk/cross_asset/risk_manager.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | draft |
| 11 | src/zephyr/risk/cross_asset/risk_manager_base.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | draft |
| 12 | src/zephyr/risk/implementations/__init__.py | src/zephyr/risk/implementations/__ini... | prototype | draft |
| 13 | src/zephyr/risk/implementations/default_position_limit_ch... | src/zephyr/risk/implementations/defau... | production | draft |
| 14 | src/zephyr/risk/implementations/default_risk_limits_calcu... | src/zephyr/risk/implementations/defau... | production | draft |
| 15 | src/zephyr/risk/implementations/default_risk_manager_orch... | src/zephyr/risk/implementations/defau... | production | draft |
| 16 | src/zephyr/risk/implementations/default_risk_validator.py | src/zephyr/risk/implementations/defau... | production | draft |
| 17 | src/zephyr/risk/implementations/default_stop_loss_engine.py | src/zephyr/risk/implementations/defau... | production | draft |
| 18 | src/zephyr/risk/infrastructure/__init__.py | src/zephyr/risk/infrastructure/__init... | scaffold_placeholder | orphan |
| 19 | src/zephyr/risk/risk_limits.py | src/zephyr/risk/risk_limits.py | prototype | draft |
| 20 | src/zephyr/risk/risk_manager.py | src/zephyr/risk/risk_manager.py | production | draft |
| 21 | src/zephyr/risk/risk_manager_base.py | src/zephyr/risk/risk_manager_base.py | production | draft |
| 22 | src/zephyr/risk/risk_validator.py | src/zephyr/risk/risk_validator.py | production | draft |
| 23 | src/zephyr/risk/services/__init__.py | src/zephyr/risk/services/__init__.py | scaffold_placeholder | orphan |
| 24 | src/zephyr/risk/stop_loss.py | src/zephyr/risk/stop_loss.py | production | draft |
| 25 | 风控-策略管理/D-RISK-01 | Risk Policy Manager | design | design_only |
| 26 | 风控-组合监控/D-RISK-03 | Portfolio Risk Monitor | design | design_only |
| 27 | 风控域-A股特色/D-RISK-27 | A-Share Stop-Loss Rule Engine | design | design_only |
| 28 | 风控域-A股特色/D-RISK-29 | A-Share PDF Tail Risk Auto-Hedger | design | design_only |
| 29 | 风控域-A股特色/D-RISK-30 | A-Share Loss Limit Enforcer | design | design_only |
| 30 | 风控域-A股特色/D-RISK-32 | A-Share Contrarian Dedicated Stop-Loss | design | design_only |
| 31 | 风控域-A股特色/D-RISK-34 | A-Share First-Minute Stop-Loss Executor | design | design_only |
| 32 | 风控域-A股特色/D-RISK-36 | A-Share Multi-Level Loss Circuit Breaker | design | design_only |
| 33 | 风控域-A股特色/D-RISK-39 | A-Share Cascading Circuit Breaker | design | design_only |
| 34 | 风控域-Kill Switch/D-RISK-54 | Kill Switch Cooldown Manager | design | design_only |
| 35 | 风控域-Kill Switch/D-RISK-66 | Kill Switch Multi-Domain Notifier | design | design_only |
| 36 | 风控域-Kill Switch/D-RISK-83 | Kill Switch New Order Rejector | design | design_only |
| 37 | 风控域-VaR/D-RISK-07 | VaR Calculator | design | design_only |
| 38 | 风控域-VaR/D-RISK-41 | Historical Data Representativeness Va... | design | design_only |
| 39 | 风控域-VaR/D-RISK-43 | VaR Fast Pre-Screen Alerter | design | design_only |
| 40 | 风控域-VaR/D-RISK-45 | Two-Tier Alert Strategy Engine | design | design_only |
| 41 | 风控域-VaR/D-RISK-47 | VaR Cross-Validation Engine | design | design_only |
| 42 | 风控域-VaR/D-RISK-71 | VaR Phase Independence Guarantor | design | design_only |
| 43 | 风控域-VaR/D-RISK-73 | Monte Carlo Precision Level Manager | design | design_only |
| 44 | 风控域-分析引擎/D-RISK-06 | Scenario Analyzer | design | design_only |
| 45 | 风控域-分析引擎/D-RISK-103 | 风险预算调整器 | design | design_only |
| 46 | 风控域-分析引擎/D-RISK-16 | Counterfactual Analyzer | design | design_only |
| 47 | 风控域-回测/D-RISK-24 | Risk Policy Backtester | design | design_only |
| 48 | 风控域-基础设施/D-RISK-121 | 风控域仓储接口 | design | design_only |
| 49 | 风控域-基础设施/D-RISK-21 | Risk Rule DSL Compiler | design | design_only |
| 50 | 风控域-基础设施/D-RISK-50 | Position Write Authority Arbiter | design | design_only |
| 51 | 风控域-基础设施/D-RISK-56 | Rule Engine vs Statistical Engine Router | design | design_only |
| 52 | 风控域-基础设施/D-RISK-77 | Risk Policy SQLite Schema Designer | design | design_only |
| 53 | 风控域-契约/D-RISK-80 | CTR-006 PositionSnapshot Provider | design | design_only |
| 54 | 风控域-契约/D-RISK-87 | CTR-004 Order Consumer | design | design_only |
| 55 | 风控域-审计/D-RISK-15 | Risk Breach Logger | design | design_only |
| 56 | 风控域-报告/D-RISK-23 | Risk Report Auto-Generator | design | design_only |
| 57 | 风控域-止损/D-RISK-64 | ATR Dynamic Stop Loss Calculator | design | design_only |
| 58 | 风控域-盘中监控/D-RISK-08 | Liquidity Risk Monitor | design | design_only |
| 59 | 风控域-盘中监控/D-RISK-13 | Concentration Risk Monitor | design | design_only |
| 60 | 风控域-盘中监控/D-RISK-18 | Crowding Risk Monitor | design | design_only |
| 61 | 风控域-盘中监控/D-RISK-63 | Sector Concentration Real-Time Calcul... | design | design_only |
| 62 | 风控域-盘中监控/D-RISK-70 | Enforcement 3-Level Executor | design | design_only |
| 63 | 风控域-盘中监控/D-RISK-97 | 保证金比例安全检查器 | design | design_only |
| 64 | 风控域-盘中监控/D-RISK-99 | 动态仓位调整器 | design | design_only |
| 65 | 风控域-盘前拦截/D-RISK-53 | Pre-Trade Idempotency Guarantor | design | design_only |
| 66 | 风控域-盘前拦截/D-RISK-78 | Pre-Trade 50ms SLA Monitor | design | design_only |
| 67 | 风控域-规则引擎/D-RISK-105 | 风险规则用户配置器 | design | design_only |
| 68 | 风控域-规则引擎/D-RISK-109 | 风控规则验证与压力测试器 | design | design_only |
| 69 | 风控域-规则引擎/D-RISK-113 | 风控规则DSL引擎 | design | design_only |
| 70 | 风控域-规则引擎/D-RISK-117 | 风控规则版本化与热更新器 | design | design_only |
| 71 | 风控域-迁移/D-RISK-86 | DefaultRiskValidator to Configurable ... | design | design_only |
| 72 | 风控域-远期❌/D-RISK-09 | Counterparty Risk Manager | design | design_only |
| 73 | 风控域-远期❌/D-RISK-19 | Climate Risk Engine | design | design_only |
| 74 | 风控域-远期❌/D-RISK-48 | Monte Carlo Batch Backtester | design | design_only |
| 75 | 风控域-远期❌/D-RISK-95 | AI增强风控引擎 | design | design_only |
| 76 | 风控域-门禁/D-RISK-92 | Strategy Correlation Gate Checker | design | design_only |
| 77 | 风控域-预测/D-RISK-25 | Limit Consumption Predictor | design | design_only |
| 78 | 风控域-风险报告/D-RISK-101 | 每日风险报告生成器 | design | design_only |
| 79 | 风控域-风险报告/D-RISK-22 | Risk Dashboard Generator | design | design_only |
| 80 | 风控域-风险报告/D-RISK-90 | RiskDashboardSnapshot CTR-P1-008 Builder | design | design_only |
| 81 | 风控域-风险治理/D-RISK-49 | Risk Policy Persister | design | design_only |

### 未分类 / Unclassified (692 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-RISK/4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN | 4级风控决策 APPROVE/REDUCE/REJECT/FLA... | design | design_only |
| 2 | D-RISK/A Share Compliance Rule A股合规规则代管 | A Share Compliance Rule A股合规规则代管 | design | design_only |
| 3 | D-RISK/A-Share 5-Signal Systemic Risk Scanner A股5信号系... | A-Share 5-Signal Systemic Risk Scanne... | design | design_only |
| 4 | D-RISK/A-Share Cascading Circuit Breaker A股级联熔断器 | A-Share Cascading Circuit Breaker A股... | design | design_only |
| 5 | D-RISK/A-Share Compliance Custody A股合规代管 | A-Share Compliance Custody A股合规代管 | design | design_only |
| 6 | D-RISK/A-Share Contrarian Dedicated Stop-Loss A股逆向专用... | A-Share Contrarian Dedicated Stop-Los... | design | design_only |
| 7 | D-RISK/A-Share Contrarian Time-Based Stop-Loss A股逆向时... | A-Share Contrarian Time-Based Stop-Lo... | design | design_only |
| 8 | D-RISK/A-Share First-Minute Stop-Loss Executor A股首分钟... | A-Share First-Minute Stop-Loss Execut... | design | design_only |
| 9 | D-RISK/A-Share Loss Limit Enforcer A股亏损限额强制执行 | A-Share Loss Limit Enforcer A股亏损限... | design | design_only |
| 10 | D-RISK/A-Share Multi-Level Loss Circuit Breaker A股多级亏... | A-Share Multi-Level Loss Circuit Brea... | design | design_only |
| 11 | D-RISK/A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自... | A-Share PDF Tail Risk Auto-Hedger A股... | design | design_only |
| 12 | D-RISK/A-Share Stock Blacklist Manager A股股票黑名单管理器 | A-Share Stock Blacklist Manager A股股... | design | design_only |
| 13 | D-RISK/A-Share Stop Loss 6 Patterns A股特色止损6种模式 | A-Share Stop Loss 6 Patterns A股特色... | design | design_only |
| 14 | D-RISK/A-Share Stop Loss A股止损 | A-Share Stop Loss A股止损 | design | design_only |
| 15 | D-RISK/A-Share Stop-Loss Rule Engine A股止损规则引擎 | A-Share Stop-Loss Rule Engine A股止损... | design | design_only |
| 16 | D-RISK/A-Share Stop-Loss Rule Engine A股特色止损 | A-Share Stop-Loss Rule Engine A股特色... | design | design_only |
| 17 | D-RISK/A-Share Stop-Loss/Circuit Breaker Series A股特色止... | A-Share Stop-Loss/Circuit Breaker Ser... | design | design_only |
| 18 | D-RISK/A-Share Systemic Risk 3-Level Alerter A股系统性风... | A-Share Systemic Risk 3-Level Alerter... | design | design_only |
| 19 | D-RISK/A-Share Systemic Risk 5 Signals A股系统性风险5信号 | A-Share Systemic Risk 5 Signals A股系... | design | design_only |
| 20 | D-RISK/A-Share Systemic Risk Detector A股系统性风险检测 | A-Share Systemic Risk Detector A股系... | design | design_only |
| 21 | D-RISK/A-Share Systemic Risk Detector A股系统性风险检测器 | A-Share Systemic Risk Detector A股系... | design | design_only |
| 22 | D-RISK/A6合规架构何时激活 A6 Compliance Activation | A6合规架构何时激活 A6 Compliance Acti... | design | design_only |
| 23 | D-RISK/AI Agent Risk AI/Agent风险 | AI Agent Risk AI/Agent风险 | design | design_only |
| 24 | D-RISK/AI Agent Risk Governance AI/Agent风险治理 | AI Agent Risk Governance AI/Agent风险... | design | design_only |
| 25 | D-RISK/AI Agent Risk Governance Bounded Autonomy AI/Agent... | AI Agent Risk Governance Bounded Auto... | design | design_only |
| 26 | D-RISK/AI Agent Specific Risk AI/Agent特有风险 | AI Agent Specific Risk AI/Agent特有风险 | design | design_only |
| 27 | D-RISK/AI Cannot Directly Modify Risk Parameters AI不可直... | AI Cannot Directly Modify Risk Parame... | design | design_only |
| 28 | D-RISK/AI Risk Engine Implementer AI风控引擎实现器 | AI Risk Engine Implementer AI风控引擎... | design | design_only |
| 29 | D-RISK/AI-Enhanced Risk Engine AI增强风控引擎 | AI-Enhanced Risk Engine AI增强风控引擎 | design | design_only |
| 30 | D-RISK/AI/Agent Risk AI/Agent风险 | AI/Agent Risk AI/Agent风险 | design | design_only |
| 31 | D-RISK/AI/Agent特有风险 AI/Agent Specific Risk | AI/Agent特有风险 AI/Agent Specific Risk | design | design_only |
| 32 | D-RISK/AISG Regulatory Compliance Checker AISG监管合规检查器 | AISG Regulatory Compliance Checker AI... | design | design_only |
| 33 | D-RISK/AI自动触发 AI Auto Trigger | AI自动触发 AI Auto Trigger | design | design_only |
| 34 | D-RISK/APPROVE Risk Decision 风险 | APPROVE Risk Decision 风险 | design | design_only |
| 35 | D-RISK/ARA五项原则 ARA Five Principles | ARA五项原则 ARA Five Principles | design | design_only |
| 36 | D-RISK/ARA治理方程 ARA Governance Equation | ARA治理方程 ARA Governance Equation | design | design_only |
| 37 | D-RISK/ARS双轨结算模型 ARS Dual-Track Settlement | ARS双轨结算模型 ARS Dual-Track Settle... | design | design_only |
| 38 | D-RISK/ARS状态机语义 ARS State Machine Semantics | ARS状态机语义 ARS State Machine Seman... | design | design_only |
| 39 | D-RISK/ATR Dynamic Stop Loss Calculator ATR动态止损计算器 | ATR Dynamic Stop Loss Calculator ATR... | design | design_only |
| 40 | D-RISK/ATR动态止损与Bayesian参数优化模型 ATR Dynamic Stop... | ATR动态止损与Bayesian参数优化模型 ATR... | design | design_only |
| 41 | D-RISK/ATR动态止盈 ATR Dynamic Take Profit | ATR动态止盈 ATR Dynamic Take Profit | design | design_only |
| 42 | D-RISK/Abnormal Trade Detection Interceptor 异常交易检测... | Abnormal Trade Detection Interceptor ... | design | design_only |
| 43 | D-RISK/Agent Boundary Violation Agent越界行为 | Agent Boundary Violation Agent越界行为 | design | design_only |
| 44 | D-RISK/Agent Strategy Drift Must Be Detected Agent策略漂... | Agent Strategy Drift Must Be Detected... | design | design_only |
| 45 | D-RISK/Agent失控 Agent Out-of-Control | Agent失控 Agent Out-of-Control | design | design_only |
| 46 | D-RISK/Agent红队测试 Agent Red Team Testing | Agent红队测试 Agent Red Team Testing | design | design_only |
| 47 | D-RISK/Agent行为日志 Agent Behavior Log | Agent行为日志 Agent Behavior Log | design | design_only |
| 48 | D-RISK/Agent行为监控 Agent Behavior Monitor | Agent行为监控 Agent Behavior Monitor | design | design_only |
| 49 | D-RISK/Agent行为监控 Agent Behavior Monitoring | Agent行为监控 Agent Behavior Monitoring | design | design_only |
| 50 | D-RISK/Almgren-Chriss Impact Model Almgren-Chriss冲击模型 | Almgren-Chriss Impact Model Almgren-C... | design | design_only |
| 51 | D-RISK/Almgren-Chriss Optimal Execution Framework Almgren... | Almgren-Chriss Optimal Execution Fram... | design | design_only |
| 52 | D-RISK/Almgren-Chriss最优执行框架 Almgren-Chriss Optimal ... | Almgren-Chriss最优执行框架 Almgren-Ch... | design | design_only |
| 53 | D-RISK/Amihud ILLIQ Amihud非流动性指标 | Amihud ILLIQ Amihud非流动性指标 | design | design_only |
| 54 | D-RISK/Amihud ILLIQ 非流动性指标 | Amihud ILLIQ 非流动性指标 | design | design_only |
| 55 | D-RISK/Amihud Illiquidity Amihud非流动性指标 | Amihud Illiquidity Amihud非流动性指标 | design | design_only |
| 56 | D-RISK/Autoencoder重构异常检测 Autoencoder Anomaly Detection | Autoencoder重构异常检测 Autoencoder A... | design | design_only |
| 57 | D-RISK/A股风险日历 A-Share Risk Calendar | A股风险日历 A-Share Risk Calendar | design | design_only |
| 58 | D-RISK/BFSI领域自适应红队 FinRedTeamBench | BFSI领域自适应红队 FinRedTeamBench | design | design_only |
| 59 | D-RISK/Basel III Multiplier Factor Manager Basel III乘数... | Basel III Multiplier Factor Manager B... | design | design_only |
| 60 | D-RISK/Bayesian优化 Bayesian Optimization | Bayesian优化 Bayesian Optimization | design | design_only |
| 61 | D-RISK/Black Swan Pattern Library 黑天鹅模式库 | Black Swan Pattern Library 黑天鹅模式库 | design | design_only |
| 62 | D-RISK/Black Swan Pattern Library 黑天鹅模式库7种模式 | Black Swan Pattern Library 黑天鹅模式... | design | design_only |
| 63 | D-RISK/Brinson模型 Brinson Model | Brinson模型 Brinson Model | design | design_only |
| 64 | D-RISK/C-004 风控 Risk Control | C-004 风控 Risk Control | design | design_only |
| 65 | D-RISK/C-038 黑天鹅检测 Black Swan Detection | C-038 黑天鹅检测 Black Swan Detection | design | design_only |
| 66 | D-RISK/C/S Pattern C/S关系模式 | C/S Pattern C/S关系模式 | design | design_only |
| 67 | D-RISK/CER Cancellation-to-Execution Ratio 撤单成交比 | CER Cancellation-to-Execution Ratio ... | design | design_only |
| 68 | D-RISK/CTR-003 RiskLimits Producer CTR-003风险限额生产者 | CTR-003 RiskLimits Producer CTR-003风... | design | design_only |
| 69 | D-RISK/CTR-004 Order Consumer CTR-004订单消费者 | CTR-004 Order Consumer CTR-004订单消费者 | design | design_only |
| 70 | D-RISK/CTR-006 PositionSnapshot Provider CTR-006仓位快照... | CTR-006 PositionSnapshot Provider CTR... | design | design_only |
| 71 | D-RISK/CTR-P1-008 Risk Dashboard Snapshot CTR-P1-008风控... | CTR-P1-008 Risk Dashboard Snapshot CT... | design | design_only |
| 72 | D-RISK/CTR-P1-008 RiskDashboardSnapshot CTR-P1-008 RiskDa... | CTR-P1-008 RiskDashboardSnapshot CTR-... | design | design_only |
| 73 | D-RISK/CTR-P1-011 RiskMetricsReport CTR-P1-011 RiskMetric... | CTR-P1-011 RiskMetricsReport CTR-P1-0... | design | design_only |
| 74 | D-RISK/CUSUM控制图 CUSUM Control Chart | CUSUM控制图 CUSUM Control Chart | design | design_only |
| 75 | D-RISK/CVaR/ES条件风险价值 Conditional Value at Risk | CVaR/ES条件风险价值 Conditional Value... | design | design_only |
| 76 | D-RISK/Carry持有成本 Carry | Carry持有成本 Carry | design | design_only |
| 77 | D-RISK/CheckResult CheckResult结构 | CheckResult CheckResult结构 | design | design_only |
| 78 | D-RISK/CheckResult 检查结果 | CheckResult 检查结果 | design | design_only |
| 79 | D-RISK/Circuit Breaker Trigger 熔断触发 | Circuit Breaker Trigger 熔断触发 | design | design_only |
| 80 | D-RISK/CircuitBreaker 熔断事件 | CircuitBreaker 熔断事件 | design | design_only |
| 81 | D-RISK/Climate Risk Engine 气候风险引擎 | Climate Risk Engine 气候风险引擎 | design | design_only |
| 82 | D-RISK/CoVaR Cross-Market Contagion CoVaR跨市场传染 | CoVaR Cross-Market Contagion CoVaR跨... | design | design_only |
| 83 | D-RISK/CoVaR跨市场传染 | CoVaR跨市场传染 | design | design_only |
| 84 | D-RISK/CoVaR跨市场传染 CoVaR Cross-Market Contagion | CoVaR跨市场传染 CoVaR Cross-Market Co... | design | design_only |
| 85 | D-RISK/Collaborative Trading Behavior Detector 协同交易行... | Collaborative Trading Behavior Detect... | design | design_only |
| 86 | D-RISK/Compliance Rule 合规规则(代码实现) | Compliance Rule 合规规则(代码实现) | design | design_only |
| 87 | D-RISK/Concentration Exceeds Limit 集中度超限 | Concentration Exceeds Limit 集中度超限 | design | design_only |
| 88 | D-RISK/Concentration Limit Non-Breakable 集中度上限不可突破 | Concentration Limit Non-Breakable 集... | design | design_only |
| 89 | D-RISK/Concentration Risk Monitor 集中度风险监控器 | Concentration Risk Monitor 集中度风险... | design | design_only |
| 90 | D-RISK/Concentration Risk Monitor集中度风险监控 | Concentration Risk Monitor集中度风险监控 | design | design_only |
| 91 | D-RISK/Configurable Rule Engine 可配置规则引擎 | Configurable Rule Engine 可配置规则引擎 | design | design_only |
| 92 | D-RISK/Convexity凸性收益 Convexity | Convexity凸性收益 Convexity | design | design_only |
| 93 | D-RISK/Correlation Collapse 相关性崩塌 | Correlation Collapse 相关性崩塌 | design | design_only |
| 94 | D-RISK/Counterfactual Analyzer 反事实分析器 | Counterfactual Analyzer 反事实分析器 | design | design_only |
| 95 | D-RISK/Counterparty Risk Manager 交易对手风险管理器 | Counterparty Risk Manager 交易对手风... | design | design_only |
| 96 | D-RISK/Counterparty Risk 交易对手风险 | Counterparty Risk 交易对手风险 | design | design_only |
| 97 | D-RISK/Covariance Matrix Decomposer 协方差矩阵分解器 | Covariance Matrix Decomposer 协方差矩... | design | design_only |
| 98 | D-RISK/Credit Risk Engine信用风险引擎 | Credit Risk Engine信用风险引擎 | design | design_only |
| 99 | D-RISK/Credit Risk 信用风险 | Credit Risk 信用风险 | design | design_only |
| 100 | D-RISK/Cross-Market Contagion 跨市场传导 | Cross-Market Contagion 跨市场传导 | design | design_only |
| 101 | D-RISK/Crowding Risk Monitor 拥挤风险监控器 | Crowding Risk Monitor 拥挤风险监控器 | design | design_only |
| 102 | D-RISK/Cumulative Drawdown Exceeds Limit 累计回撤超限 | Cumulative Drawdown Exceeds Limit 累... | design | design_only |
| 103 | D-RISK/Custom Risk Report Generator 风险报告自定义生成器 | Custom Risk Report Generator 风险报告... | design | design_only |
| 104 | D-RISK/D-AUTONOMY Readiness D-AUTONOMY就绪前提 | D-AUTONOMY Readiness D-AUTONOMY就绪前提 | design | design_only |
| 105 | D-RISK/D-DATA Readiness D-DATA就绪前提 | D-DATA Readiness D-DATA就绪前提 | design | design_only |
| 106 | D-RISK/D-FACTOR Readiness D-FACTOR就绪前提 | D-FACTOR Readiness D-FACTOR就绪前提 | design | design_only |
| 107 | D-RISK/D-RISK 风险 | D-RISK 风险 | design | design_only |
| 108 | D-RISK/DPG七场景 DPG Seven Scenarios | DPG七场景 DPG Seven Scenarios | design | design_only |
| 109 | D-RISK/Daily Loss Exceeds Limit 单日亏损超限 | Daily Loss Exceeds Limit 单日亏损超限 | design | design_only |
| 110 | D-RISK/Daily Loss Limit Invariant 日损失限额不变量 | Daily Loss Limit Invariant 日损失限额... | design | design_only |
| 111 | D-RISK/Daily Risk Report Generator 每日风险报告生成器 | Daily Risk Report Generator 每日风险... | design | design_only |
| 112 | D-RISK/Default Position Limit Checker 默认持仓限额检查器(... | Default Position Limit Checker 默认持... | design | design_only |
| 113 | D-RISK/Default Risk Limits Calculator 默认风险限额计算器(... | Default Risk Limits Calculator 默认风... | design | design_only |
| 114 | D-RISK/Default Risk Manager Orchestrator 默认风控管理器编... | Default Risk Manager Orchestrator 默... | design | design_only |
| 115 | D-RISK/Default Risk Validator 默认风控校验器(代码实现) | Default Risk Validator 默认风控校验器... | design | design_only |
| 116 | D-RISK/Default Stop Loss Engine 默认止损引擎(代码实现) | Default Stop Loss Engine 默认止损引擎... | design | design_only |
| 117 | D-RISK/DefaultRiskValidator to Configurable Rule Engine M... | DefaultRiskValidator to Configurable ... | design | design_only |
| 118 | D-RISK/Degraded Liquidity Mode 降级流动性模式 | Degraded Liquidity Mode 降级流动性模式 | design | design_only |
| 119 | D-RISK/Degraded 风控降级事件 | Degraded 风控降级事件 | design | design_only |
| 120 | D-RISK/Distribution Fitting Engine 分布拟合引擎 | Distribution Fitting Engine 分布拟合引擎 | design | design_only |
| 121 | D-RISK/Dragon-Tiger List Verification 龙虎榜验证 | Dragon-Tiger List Verification 龙虎榜... | design | design_only |
| 122 | D-RISK/Drawdown Real-Time Tracker 回撤实时跟踪器 | Drawdown Real-Time Tracker 回撤实时跟... | design | design_only |
| 123 | D-RISK/DrawdownAlerted 回撤已告警 | DrawdownAlerted 回撤已告警 | design | design_only |
| 124 | D-RISK/Drift Detection Risk Closed Loop 漂移检测与风险闭环 | Drift Detection Risk Closed Loop 漂移... | design | design_only |
| 125 | D-RISK/Drift Exceeded Model Must Degrade 漂移超限模型必须... | Drift Exceeded Model Must Degrade 漂... | design | design_only |
| 126 | D-RISK/Drift Exceeds Limit 漂移超限 | Drift Exceeds Limit 漂移超限 | design | design_only |
| 127 | D-RISK/Dual-Engine Routing 双引擎路由 | Dual-Engine Routing 双引擎路由 | design | design_only |
| 128 | D-RISK/Dynamic Position Adjuster 动态仓位调整器 | Dynamic Position Adjuster 动态仓位调整器 | design | design_only |
| 129 | D-RISK/E-RK-01 D-RISK→间接经PC-04事件 | E-RK-01 D-RISK→间接经PC-04事件 | design | design_only |
| 130 | D-RISK/E-RK-03 DrawdownAlerted E-RK-03 DrawdownAlerted事件 | E-RK-03 DrawdownAlerted E-RK-03 Drawd... | design | design_only |
| 131 | D-RISK/E-SIM-03 StressTestResult 压力测试结果 | E-SIM-03 StressTestResult 压力测试结果 | design | design_only |
| 132 | D-RISK/ESG Risk ESG风险 | ESG Risk ESG风险 | design | design_only |
| 133 | D-RISK/ESRB 14个AI风险放大向量 ESRB 14 AI Risk Amplificat... | ESRB 14个AI风险放大向量 ESRB 14 AI Ri... | design | design_only |
| 134 | D-RISK/ESRB 2025系统性风险报告 | ESRB 2025系统性风险报告 | design | design_only |
| 135 | D-RISK/ESRB Concentration Risk Vector ESRB集中度风险向量 | ESRB Concentration Risk Vector ESRB集... | design | design_only |
| 136 | D-RISK/ESRB Data Dependency Vector ESRB数据依赖向量 | ESRB Data Dependency Vector ESRB数据... | design | design_only |
| 137 | D-RISK/ESRB Feedback Loop Vector ESRB反馈循环向量 | ESRB Feedback Loop Vector ESRB反馈循... | design | design_only |
| 138 | D-RISK/ESRB Interconnection Vector ESRB互联性向量 | ESRB Interconnection Vector ESRB互联... | design | design_only |
| 139 | D-RISK/ESRB Model Homogenization Vector ESRB模型同质化向量 | ESRB Model Homogenization Vector ESRB... | design | design_only |
| 140 | D-RISK/ESRB Network Vulnerability Vector ESRB网络漏洞向量 | ESRB Network Vulnerability Vector ESR... | design | design_only |
| 141 | D-RISK/ESRB Opacity Vector ESRB不透明性向量 | ESRB Opacity Vector ESRB不透明性向量 | design | design_only |
| 142 | D-RISK/ESRB Operational Risk Vector ESRB操作风险向量 | ESRB Operational Risk Vector ESRB操作... | design | design_only |
| 143 | D-RISK/ESRB Procyclicality Vector ESRB顺周期性向量 | ESRB Procyclicality Vector ESRB顺周期... | design | design_only |
| 144 | D-RISK/ESRB Regulatory Arbitrage Vector ESRB监管套利向量 | ESRB Regulatory Arbitrage Vector ESRB... | design | design_only |
| 145 | D-RISK/ESRB Speed Vector ESRB速度向量 | ESRB Speed Vector ESRB速度向量 | design | design_only |
| 146 | D-RISK/ESRB不透明性风险向量 ESRB Opacity | ESRB不透明性风险向量 ESRB Opacity | design | design_only |
| 147 | D-RISK/ESRB互联性风险向量 ESRB Interconnectedness | ESRB互联性风险向量 ESRB Interconnecte... | design | design_only |
| 148 | D-RISK/ESRB历史约束风险向量 ESRB History-Constrained | ESRB历史约束风险向量 ESRB History-Con... | design | design_only |
| 149 | D-RISK/ESRB市场操纵风险向量 ESRB Market Manipulation | ESRB市场操纵风险向量 ESRB Market Mani... | design | design_only |
| 150 | D-RISK/ESRB数据依赖风险向量 ESRB Data Dependency | ESRB数据依赖风险向量 ESRB Data Depend... | design | design_only |
| 151 | D-RISK/ESRB模型同质性风险向量 ESRB Model Homogeneity | ESRB模型同质性风险向量 ESRB Model Hom... | design | design_only |
| 152 | D-RISK/ESRB法律地位未定风险向量 ESRB Untested Legal Status | ESRB法律地位未定风险向量 ESRB Unteste... | design | design_only |
| 153 | D-RISK/ESRB监管套利风险向量 ESRB Regulatory Arbitrage | ESRB监管套利风险向量 ESRB Regulatory ... | design | design_only |
| 154 | D-RISK/ESRB网络脆弱性风险向量 ESRB Cyber Vulnerability | ESRB网络脆弱性风险向量 ESRB Cyber Vul... | design | design_only |
| 155 | D-RISK/ESRB过度信任风险向量 ESRB Overreliance | ESRB过度信任风险向量 ESRB Overreliance | design | design_only |
| 156 | D-RISK/ESRB运营风险向量 ESRB Operational Risk | ESRB运营风险向量 ESRB Operational Risk | design | design_only |
| 157 | D-RISK/ESRB速度风险向量 ESRB Speed | ESRB速度风险向量 ESRB Speed | design | design_only |
| 158 | D-RISK/ESRB集中风险向量 ESRB Concentration Risk | ESRB集中风险向量 ESRB Concentration Risk | design | design_only |
| 159 | D-RISK/ESRB顺周期性风险向量 ESRB Procyclicality | ESRB顺周期性风险向量 ESRB Procyclicality | design | design_only |
| 160 | D-RISK/EVT极值理论 | EVT极值理论 | design | design_only |
| 161 | D-RISK/Emergent Manipulation 涌现操纵模式 | Emergent Manipulation 涌现操纵模式 | design | design_only |
| 162 | D-RISK/Enforcement 3-Level Executor 执行3级执行器 | Enforcement 3-Level Executor 执行3级... | design | design_only |
| 163 | D-RISK/Enforcement Type 执行类型枚举 | Enforcement Type 执行类型枚举 | design | design_only |
| 164 | D-RISK/Execution Result Feedback Consumption Bridger 执行... | Execution Result Feedback Consumption... | design | design_only |
| 165 | D-RISK/Exit Time Risk 退出时间风险 | Exit Time Risk 退出时间风险 | design | design_only |
| 166 | D-RISK/Extreme Event Black Swan 极端事件与黑天鹅 | Extreme Event Black Swan 极端事件与黑... | design | design_only |
| 167 | D-RISK/Extreme Liquidity Mode 极端流动性模式 | Extreme Liquidity Mode 极端流动性模式 | design | design_only |
| 168 | D-RISK/FLATTEN Risk Decision 风险 | FLATTEN Risk Decision 风险 | design | design_only |
| 169 | D-RISK/Fail-Closed Degradation Handler Fail-Closed降级处理器 | Fail-Closed Degradation Handler Fail-... | design | design_only |
| 170 | D-RISK/Fail-Closed 引擎故障处置 | Fail-Closed 引擎故障处置 | design | design_only |
| 171 | D-RISK/Fake Move Identification Signal Engine 假动作识别... | Fake Move Identification Signal Engin... | design | design_only |
| 172 | D-RISK/Fake Rally Real Distribution 假拉升真出货 | Fake Rally Real Distribution 假拉升真... | design | design_only |
| 173 | D-RISK/Fake Rebound Real Distribution 假反弹真派发 | Fake Rebound Real Distribution 假反弹... | design | design_only |
| 174 | D-RISK/Fake Support Real Lure 假护盘真诱多 | Fake Support Real Lure 假护盘真诱多 | design | design_only |
| 175 | D-RISK/Fee Track费用轨道 Fee Track | Fee Track费用轨道 Fee Track | design | design_only |
| 176 | D-RISK/Frequent Instant Cancellation 频繁瞬时撤单 | Frequent Instant Cancellation 频繁瞬... | design | design_only |
| 177 | D-RISK/Frequent Push-Pull 频繁拉抬打压 | Frequent Push-Pull 频繁拉抬打压 | design | design_only |
| 178 | D-RISK/GAN对抗检测 GAN Adversarial Detection | GAN对抗检测 GAN Adversarial Detection | design | design_only |
| 179 | D-RISK/GATE-FPGA-01 AUM高频 | GATE-FPGA-01 AUM高频 | design | design_only |
| 180 | D-RISK/GATE-FPGA-02 共享内存延迟 | GATE-FPGA-02 共享内存延迟 | design | design_only |
| 181 | D-RISK/GATE-FUT-03 期货风控参数 | GATE-FUT-03 期货风控参数 | design | design_only |
| 182 | D-RISK/Gate/Dashboard/Profile/DSL/Warehouse Series 门禁/... | Gate/Dashboard/Profile/DSL/Warehouse ... | design | design_only |
| 183 | D-RISK/Grid Search 网格搜索 | Grid Search 网格搜索 | design | design_only |
| 184 | D-RISK/Grinold & Kahn容量公式 | Grinold & Kahn容量公式 | design | design_only |
| 185 | D-RISK/Hedge Execution 独立对冲执行 | Hedge Execution 独立对冲执行 | design | design_only |
| 186 | D-RISK/Hot Path No Python Invariant 热路径禁Python不变量 | Hot Path No Python Invariant 热路径禁... | design | design_only |
| 187 | D-RISK/IC衰减检测 IC Decay Detection | IC衰减检测 IC Decay Detection | design | design_only |
| 188 | D-RISK/INV-001 Kill Switch Response Time Kill Switch响应... | INV-001 Kill Switch Response Time Kil... | design | design_only |
| 189 | D-RISK/IV Parametric VaR to Historical Simulation Migrato... | IV Parametric VaR to Historical Simul... | design | design_only |
| 190 | D-RISK/Impact Cost Risk 冲击成本风险 | Impact Cost Risk 冲击成本风险 | design | design_only |
| 191 | D-RISK/Industry Concentration Compliance Detector 行业集... | Industry Concentration Compliance Det... | design | design_only |
| 192 | D-RISK/Industry Deviation Exceeds Limit 行业偏离超限 | Industry Deviation Exceeds Limit 行业... | design | design_only |
| 193 | D-RISK/Information Asymmetry Period Manipulation Detector... | Information Asymmetry Period Manipula... | design | design_only |
| 194 | D-RISK/Information Asymmetry Window 信息不对称空窗期 | Information Asymmetry Window 信息不对... | design | design_only |
| 195 | D-RISK/Instant Order Rate Anomaly 瞬时申报速率异常 | Instant Order Rate Anomaly 瞬时申报速... | design | design_only |
| 196 | D-RISK/Insufficient Liquidity 流动性不足 | Insufficient Liquidity 流动性不足 | design | design_only |
| 197 | D-RISK/Intraday Time-Varying Participation Rate 日内时变... | Intraday Time-Varying Participation R... | design | design_only |
| 198 | D-RISK/KS-L1 软暂停 Kill Switch | KS-L1 软暂停 Kill Switch | design | design_only |
| 199 | D-RISK/KS-L2 会话熔断 Kill Switch | KS-L2 会话熔断 Kill Switch | design | design_only |
| 200 | D-RISK/KS-L3 通道断开 Kill Switch | KS-L3 通道断开 Kill Switch | design | design_only |

> (仅显示前 200 个模块，共 692 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 770 条 / 770 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 770 条 / 770 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 579 条 / edges                               │
│   [config_depends]: 52 条 / edges                                │
│   [event]: 50 条 / edges                                         │
│   [contract]: 40 条 / edges                                      │
│   [runtime]: 35 条 / edges                                       │
│   [data]: 14 条 / edges                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (579 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → risk_manager.py                                  │
│   __init__.py → risk_manager_base.py                             │
│   default_position_limit_ch... → risk_manager.py                 │
│   default_position_limit_ch... → risk_manager_base.py            │
│   default_stop_loss_engine.py → risk_manager_base.py             │
│   default_risk_manager_orch... → risk_manager.py                 │
│   default_risk_manager_orch... → risk_manager_base.py            │
│   default_risk_manager_orch... → default_position_limit_ch...    │
│   default_risk_manager_orch... → default_stop_loss_engine.py     │
│   default_risk_manager_orch... → default_risk_validator.py       │
│   default_risk_manager_orch... → default_risk_limits_calcu...    │
│   default_risk_validator.py → risk_manager.py                    │
│   default_risk_validator.py → risk_validator.py                  │
│   default_risk_limits_calcu... → risk_manager.py                 │
│   Systematic Stress Testing... → Agent行为日志 Agent Behav...    │
│   Systematic Overfitting Pr... → 模型设定风险 Model Specif...    │
│   黑天鹅模式库与预判 Black ... → 风险否决权 Risk Veto Power      │
│   资金曲线自诊断与结构预警 ... → VaR Scheduling/Concentrat...    │
│   Risk Policy Manager风控策... → Pre-Trade Checker盘前检查       │
│   Pre-Trade Checker盘前检查 → Portfolio Risk Monitor持...        │
│   Portfolio Risk Monitor持... → Stop Loss Engine止损引擎         │
│   Stop Loss Engine止损引擎 → Stress Test Engine压力测...         │
│   Stop Loss Engine止损引擎 → ESRB Operational Risk Vec...        │
│   Stress Test Engine压力测... → VaR Calculator VaR计算器         │
│   VaR Calculator VaR计算器 → Risk Budget Allocator风险...        │
│   Risk Budget Allocator风险... → Risk Decomposition Engine...    │
│   Risk Decomposition Engine... → Concentration Risk Monito...    │
│   Concentration Risk Monito... → Risk Limit Manager风险限...     │
│   Risk Limit Manager风险限... → Credit Risk Engine信用风...      │
│   Credit Risk Engine信用风... → A-Share Stop-Loss Rule En...     │
│   A-Share Stop-Loss Rule En... → A-Share Systemic Risk Det...    │
│   A-Share Systemic Risk Det... → A-Share Loss Limit Enforc...    │
│   A-Share Loss Limit Enforc... → Stop-Loss Engine止损引擎        │
│   A-Share Loss Limit Enforc... → INV-001 Kill Switch Respo...    │
│   Stop-Loss Engine止损引擎 → 仓位限制预检器 Position             │
│   Stop-Loss Engine止损引擎 → AI Agent Risk Governance ...        │
│   仓位限制预检器 Position → 保证金比例安全检查器 Secu...         │
│   仓位限制预检器 Position → C/S Pattern C/S关系模式              │
│   保证金比例安全检查器 Secu... → 风险指标体系定义器 Risk         │
│   风险指标体系定义器 Risk → 紧急停止安全确认 Security            │
│   紧急停止安全确认 Security → VaR Compute Data Prefetch...       │
│   VaR Compute Data Prefetch... → 历史数据代表性验证器 Hist...    │
│   历史数据代表性验证器 Hist... → Risk Policy Persister 风...     │
│   Risk Policy Persister 风... → 双时态PositionSnapshot管...      │
│   双时态PositionSnapshot管... → VaR DuckDB历史模拟查询构...      │
│   VaR DuckDB历史模拟查询构... → 风险指标计算数据源依赖管...      │
│   风险指标计算数据源依赖管... → C-004 风控 Risk Control          │
│   C-004 风控 Risk Control → C-038 黑天鹅检测 Black Sw...         │
│   C-004 风控 Risk Control → Normal Liquidity Mode 正...          │
│   ...还有 530 条 / 530 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (52 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (50 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (40 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (35 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (14 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 770 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `36_d_risk_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
