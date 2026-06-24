---
doc_type: domain_architecture_diagram
title: D-PF_CORE 组合核心架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 34_d_pf_core / 组合核心 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示组合核心（D-PF_CORE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 组合核心（D-PF_CORE）的模块分布。共 201 个模块 / 201 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (48 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   A-001  [design]                                                │
│   MS-02  [design]                                                │
│   MT-02  [design]                                                │
│   MS-04  [design]                                                │
│   MT-03  [design]                                                │
│   MS-03  [design]                                                │
│   MS-05  [design]                                                │
│   MT-05  [design]                                                │
│   MT-04  [design]                                                │
│   D-ALT-DATA-03  [design]                                        │
│   D-ALT-DATA-11  [design]                                        │
│   D-ALT-DATA-06  [design]                                        │
│   D-ALT-DATA-07  [design]                                        │
│   D-ALT-DATA-09  [design]                                        │
│   D-ALT-DATA-10  [design]                                        │
│   D-ALT-DATA-13  [design]                                        │
│   D-ALT-DATA-15  [design]                                        │
│   D-ALT-DATA-17  [design]                                        │
│   ...还有 30 个模块 / 30 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (153 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   19.2 Ensemble-HMM增强框架  [design]                            │
│   26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flo... │
│   28.5 与已有模块的联动 28.5 Linkage with Existing Modules  [... │
│   31.3 高级协同检测（基于ESMA MABUM框架）  [design]              │
│   A Share Trading Discipline A股交易纪律  [design]               │
│   Auto Down-Weight 自动降权  [design]                            │
│   Automatic Strategy Discovery 自动策略发现  [design]            │
│   Benchmark Manager 基准管理器  [design]                         │
│   BuyDecided 买入决策事件  [design]                              │
│   BuyDecision 买入决策契约  [design]                             │
│   C-006：策略工厂  [design]                                      │
│   C-016：知识图谱引擎  [design]                                  │
│   C-027：因子工厂（P0）  [design]                                │
│   C-028：信号工厂（P0）  [design]                                │
│   C-033：过拟合系统性防护  [design]                              │
│   C-040：系统性压力测试  [design]                                │
│   C-047：仓位管理唯一裁决中心  [design]                          │
│   CTR-P1-006 StrategyLifecycleEvent CTR-P1-006 StrategyLifecy... │
│   ...还有 135 个模块 / 135 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 201 个模块 / 201 modules）。

### L2 领域层 / Domain Layer (48 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 |  | A-001 | design | active |
| 2 |  | MS-02 | design | unbuilt |
| 3 |  | MT-02 | design | unbuilt |
| 4 |  | MS-04 | design | unbuilt |
| 5 |  | MT-03 | design | unbuilt |
| 6 |  | MS-03 | design | unbuilt |
| 7 |  | MS-05 | design | unbuilt |
| 8 |  | MT-05 | design | unbuilt |
| 9 |  | MT-04 | design | unbuilt |
| 10 |  | D-ALT-DATA-03 | design | unbuilt |
| 11 |  | D-ALT-DATA-11 | design | unbuilt |
| 12 |  | D-ALT-DATA-06 | design | unbuilt |
| 13 |  | D-ALT-DATA-07 | design | unbuilt |
| 14 |  | D-ALT-DATA-09 | design | unbuilt |
| 15 |  | D-ALT-DATA-10 | design | unbuilt |
| 16 |  | D-ALT-DATA-13 | design | unbuilt |
| 17 |  | D-ALT-DATA-15 | design | unbuilt |
| 18 |  | D-ALT-DATA-17 | design | unbuilt |
| 19 |  | D-ALT-DATA-06扩展 | design | unbuilt |
| 20 |  | D-ALT-DATA-14 | design | unbuilt |
| 21 |  | D-CROSS-ASSET-03 | design | unbuilt |
| 22 |  | D-CROSS-ASSET-13 | design | unbuilt |
| 23 |  | AP-07 | design | unbuilt |
| 24 |  | AP-09 | design | unbuilt |
| 25 |  | RK-10 | design | unbuilt |
| 26 |  | PA-01 | design | unbuilt |
| 27 | src/zephyr/pf_core/__init__.py | src/zephyr/pf_core/__init__.py | prototype | draft |
| 28 | src/zephyr/pf_core/_extensions/__init__.py | src/zephyr/pf_core/_extensions/__init... | scaffold_placeholder | orphan |
| 29 | src/zephyr/pf_core/analytics_base.py | src/zephyr/pf_core/analytics_base.py | production | draft |
| 30 | src/zephyr/pf_core/api/__init__.py | src/zephyr/pf_core/api/__init__.py | scaffold_placeholder | orphan |
| 31 | src/zephyr/pf_core/compliance_rule.py | src/zephyr/pf_core/compliance_rule.py | production | draft |
| 32 | src/zephyr/pf_core/core/__init__.py | src/zephyr/pf_core/core/__init__.py | scaffold_placeholder | orphan |
| 33 | src/zephyr/pf_core/default_attribution_engine.py | src/zephyr/pf_core/default_attributio... | production | draft |
| 34 | src/zephyr/pf_core/default_tca_engine.py | src/zephyr/pf_core/default_tca_engine.py | production | draft |
| 35 | src/zephyr/pf_core/infrastructure/__init__.py | src/zephyr/pf_core/infrastructure/__i... | scaffold_placeholder | orphan |
| 36 | src/zephyr/pf_core/performance_attribution_engine/__init_... | src/zephyr/pf_core/performance_attrib... | prototype | draft |
| 37 | src/zephyr/pf_core/performance_attribution_report.py | src/zephyr/pf_core/performance_attrib... | production | draft |
| 38 | src/zephyr/pf_core/risk_limits.py | src/zephyr/pf_core/risk_limits.py | prototype | draft |
| 39 | src/zephyr/pf_core/services/__init__.py | src/zephyr/pf_core/services/__init__.py | scaffold_placeholder | orphan |
| 40 | src/zephyr/pf_core/strategies/__init__.py | src/zephyr/pf_core/strategies/__init_... | prototype | draft |
| 41 | src/zephyr/pf_core/strategies/default_equity_strategy.py | src/zephyr/pf_core/strategies/default... | prototype | draft |
| 42 | src/zephyr/pf_core/strategy_base.py | src/zephyr/pf_core/strategy_base.py | production | draft |
| 43 | src/zephyr/pf_core/strategy_engine/__init__.py | src/zephyr/pf_core/strategy_engine/__... | prototype | draft |
| 44 | src/zephyr/pf_core/strategy_registry.py | src/zephyr/pf_core/strategy_registry.py | prototype | draft |
| 45 | 另类数据域缩写，D-ALT-02=SentimentEngine | D-ALT-DATA-02 | design | design_only |
| 46 | 推理域缩写，D-ML-02=ModelRegistry→归入MS-01 | MS-01 | design | design_only |
| 47 | 训练域缩写，D-ML-01=TrainingPipeline→归入MT-01 | MT-01 | design | design_only |
| 48 | 跨资产域缩写，D-XA=D-CROSS-ASSET(CA) | D-CROSS-ASSET-01 | design | design_only |

### 未分类 / Unclassified (153 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-PF-CORE/19.2 Ensemble-HMM增强框架 | 19.2 Ensemble-HMM增强框架 | design | design_only |
| 2 | D-PF-CORE/26.5 逆势资金流与已有模块的联动 26.5 Contrarian... | 26.5 逆势资金流与已有模块的联动 26.5 ... | design | design_only |
| 3 | D-PF-CORE/28.5 与已有模块的联动 28.5 Linkage with Existin... | 28.5 与已有模块的联动 28.5 Linkage wi... | design | design_only |
| 4 | D-PF-CORE/31.3 高级协同检测（基于ESMA MABUM框架） | 31.3 高级协同检测（基于ESMA MABUM框架） | design | design_only |
| 5 | D-PF-CORE/A Share Trading Discipline A股交易纪律 | A Share Trading Discipline A股交易纪律 | design | design_only |
| 6 | D-PF-CORE/Auto Down-Weight 自动降权 | Auto Down-Weight 自动降权 | design | design_only |
| 7 | D-PF-CORE/Automatic Strategy Discovery 自动策略发现 | Automatic Strategy Discovery 自动策略... | design | design_only |
| 8 | D-PF-CORE/Benchmark Manager 基准管理器 | Benchmark Manager 基准管理器 | design | design_only |
| 9 | D-PF-CORE/BuyDecided 买入决策事件 | BuyDecided 买入决策事件 | design | design_only |
| 10 | D-PF-CORE/BuyDecision 买入决策契约 | BuyDecision 买入决策契约 | design | design_only |
| 11 | D-PF-CORE/C-006：策略工厂 | C-006：策略工厂 | design | design_only |
| 12 | D-PF-CORE/C-016：知识图谱引擎 | C-016：知识图谱引擎 | design | design_only |
| 13 | D-PF-CORE/C-027：因子工厂（P0） | C-027：因子工厂（P0） | design | design_only |
| 14 | D-PF-CORE/C-028：信号工厂（P0） | C-028：信号工厂（P0） | design | design_only |
| 15 | D-PF-CORE/C-033：过拟合系统性防护 | C-033：过拟合系统性防护 | design | design_only |
| 16 | D-PF-CORE/C-040：系统性压力测试 | C-040：系统性压力测试 | design | design_only |
| 17 | D-PF-CORE/C-047：仓位管理唯一裁决中心 | C-047：仓位管理唯一裁决中心 | design | design_only |
| 18 | D-PF-CORE/CTR-P1-006 StrategyLifecycleEvent CTR-P1-006 St... | CTR-P1-006 StrategyLifecycleEvent CTR... | design | design_only |
| 19 | D-PF-CORE/Carbon Footprint Calculator碳足迹计算器 | Carbon Footprint Calculator碳足迹计算器 | design | design_only |
| 20 | D-PF-CORE/Carbon Footprint 碳足迹 | Carbon Footprint 碳足迹 | design | design_only |
| 21 | D-PF-CORE/Cash Flow Manager资金流管理器 | Cash Flow Manager资金流管理器 | design | design_only |
| 22 | D-PF-CORE/Constraint Solver约束求解器 | Constraint Solver约束求解器 | design | design_only |
| 23 | D-PF-CORE/Decision Orchestrator 决策编排器 | Decision Orchestrator 决策编排器 | design | design_only |
| 24 | D-PF-CORE/Decision Orchestrator 决策编排器——缺失功能模块 | Decision Orchestrator 决策编排器——... | design | design_only |
| 25 | D-PF-CORE/E-PF-01 PortfolioRebalanced E-PF-01 PortfolioRe... | E-PF-01 PortfolioRebalanced E-PF-01 P... | design | design_only |
| 26 | D-PF-CORE/E-SIM-01 SimulationCompleted 仿真完成 | E-SIM-01 SimulationCompleted 仿真完成 | design | design_only |
| 27 | D-PF-CORE/Event Bus §2.2 事件总线事件分类 | Event Bus §2.2 事件总线事件分类 | design | design_only |
| 28 | D-PF-CORE/Event Sourcing 事件溯源 | Event Sourcing 事件溯源 | design | design_only |
| 29 | D-PF-CORE/Execution to L5 Closed Loop 执行→L5闭环优化 | Execution to L5 Closed Loop 执行→L5... | design | design_only |
| 30 | D-PF-CORE/Explainability 决策可解释性与溯源 | Explainability 决策可解释性与溯源 | design | design_only |
| 31 | D-PF-CORE/Factor Direct Layer 因子直通层 | Factor Direct Layer 因子直通层 | design | design_only |
| 32 | D-PF-CORE/Factor Exposure Manager因子敞口管理器 | Factor Exposure Manager因子敞口管理器 | design | design_only |
| 33 | D-PF-CORE/Factor/Strategy Crowding Deep Detection 因子/策... | Factor/Strategy Crowding Deep Detecti... | design | design_only |
| 34 | D-PF-CORE/Governance Domain §30.6 运维安全治理域缺失模块 | Governance Domain §30.6 运维安全治理... | design | design_only |
| 35 | D-PF-CORE/HRP/Black-Litterman Portfolio Optimization HRP/... | HRP/Black-Litterman Portfolio Optimiz... | design | design_only |
| 36 | D-PF-CORE/HoldDecided 持有决策事件 | HoldDecided 持有决策事件 | design | design_only |
| 37 | D-PF-CORE/L2 to L3 Strategy Decision L2→L3策略决策 | L2 to L3 Strategy Decision L2→L3策略决策 | design | design_only |
| 38 | D-PF-CORE/L3-L6 决策/仓位/风控/执行/闭环数据 | L3-L6 决策/仓位/风控/执行/闭环数据 | design | design_only |
| 39 | D-PF-CORE/LLM Evolutionary Strategy Search LLM进化式策略搜索 | LLM Evolutionary Strategy Search LLM... | design | design_only |
| 40 | D-PF-CORE/Liquidity Estimator 流动性估算器 | Liquidity Estimator 流动性估算器 | design | design_only |
| 41 | D-PF-CORE/Liquidity Estimator流动性估计器 | Liquidity Estimator流动性估计器 | design | design_only |
| 42 | D-PF-CORE/MTF Four-Track Fusion 四轨融合器 | MTF Four-Track Fusion 四轨融合器 | design | design_only |
| 43 | D-PF-CORE/Multi-Objective Optimizer多目标优化器 | Multi-Objective Optimizer多目标优化器 | design | design_only |
| 44 | D-PF-CORE/Multi-Scenario Response & Contingency 多情景对... | Multi-Scenario Response & Contingency... | design | design_only |
| 45 | D-PF-CORE/Multi-Strategy Allocator 多策略分配器 | Multi-Strategy Allocator 多策略分配器 | design | design_only |
| 46 | D-PF-CORE/Multi-Strategy Resonance Fusion 多策略共振融合层 | Multi-Strategy Resonance Fusion 多策... | design | design_only |
| 47 | D-PF-CORE/Multi-Track Fusion 四轨融合器 | Multi-Track Fusion 四轨融合器 | design | design_only |
| 48 | D-PF-CORE/P0 模块明细 | P0 模块明细 | design | design_only |
| 49 | D-PF-CORE/P1 模块分类汇总（14个） | P1 模块分类汇总（14个） | design | design_only |
| 50 | D-PF-CORE/P1 模块分类汇总（5个） | P1 模块分类汇总（5个） | design | design_only |
| 51 | D-PF-CORE/P1 模块分类汇总（7个） | P1 模块分类汇总（7个） | design | design_only |
| 52 | D-PF-CORE/P1 模块分类汇总（85个） | P1 模块分类汇总（85个） | design | design_only |
| 53 | D-PF-CORE/P1 模块分类汇总（92个） | P1 模块分类汇总（92个） | design | design_only |
| 54 | D-PF-CORE/P1 模块分类汇总（99个） | P1 模块分类汇总（99个） | design | design_only |
| 55 | D-PF-CORE/P2 模块分类汇总（11个） | P2 模块分类汇总（11个） | design | design_only |
| 56 | D-PF-CORE/P2 模块分类汇总（17个） | P2 模块分类汇总（17个） | design | design_only |
| 57 | D-PF-CORE/P2 模块分类汇总（29个） | P2 模块分类汇总（29个） | design | design_only |
| 58 | D-PF-CORE/P2 模块分类汇总（30个） | P2 模块分类汇总（30个） | design | design_only |
| 59 | D-PF-CORE/P2 模块分类汇总（62个） | P2 模块分类汇总（62个） | design | design_only |
| 60 | D-PF-CORE/P2 模块分类汇总（7个） | P2 模块分类汇总（7个） | design | design_only |
| 61 | D-PF-CORE/P3 模块分类汇总（1个） | P3 模块分类汇总（1个） | design | design_only |
| 62 | D-PF-CORE/P3 模块分类汇总（3个） | P3 模块分类汇总（3个） | design | design_only |
| 63 | D-PF-CORE/Percentage 百分比 | Percentage 百分比 | design | design_only |
| 64 | D-PF-CORE/Performance Attribution Engine绩效归因引擎 | Performance Attribution Engine绩效归... | design | design_only |
| 65 | D-PF-CORE/Portfolio Benchmark Manager组合基准管理器 | Portfolio Benchmark Manager组合基准管... | design | design_only |
| 66 | D-PF-CORE/Portfolio Construction Engine 组合构建引擎 | Portfolio Construction Engine 组合构... | design | design_only |
| 67 | D-PF-CORE/Portfolio Core 组合核心 | Portfolio Core 组合核心 | design | design_only |
| 68 | D-PF-CORE/Portfolio Drift Monitor组合漂移监控器 | Portfolio Drift Monitor组合漂移监控器 | design | design_only |
| 69 | D-PF-CORE/Portfolio Optimization Engine 组合优化引擎 | Portfolio Optimization Engine 组合优... | design | design_only |
| 70 | D-PF-CORE/Portfolio Optimizer组合优化器 | Portfolio Optimizer组合优化器 | design | design_only |
| 71 | D-PF-CORE/Portfolio Rebalancer 组合再平衡器 | Portfolio Rebalancer 组合再平衡器 | design | design_only |
| 72 | D-PF-CORE/Portfolio Risk Decomposer 组合风险分解器 | Portfolio Risk Decomposer 组合风险分解器 | design | design_only |
| 73 | D-PF-CORE/Portfolio State 组合状态检查点 | Portfolio State 组合状态检查点 | design | design_only |
| 74 | D-PF-CORE/Portfolio Stress Tester组合压力测试器 | Portfolio Stress Tester组合压力测试器 | design | design_only |
| 75 | D-PF-CORE/Portfolio 组合 | Portfolio 组合 | design | design_only |
| 76 | D-PF-CORE/Portfolio 组合聚合根 | Portfolio 组合聚合根 | design | design_only |
| 77 | D-PF-CORE/PortfolioRebalanced 组合已再平衡 | PortfolioRebalanced 组合已再平衡 | design | design_only |
| 78 | D-PF-CORE/Rebalance Cost Analyzer再平衡成本分析器 | Rebalance Cost Analyzer再平衡成本分析器 | design | design_only |
| 79 | D-PF-CORE/Rebalance Full Flow Saga 再平衡全流程Saga | Rebalance Full Flow Saga 再平衡全流程... | design | design_only |
| 80 | D-PF-CORE/Rebalance Scheduler再平衡调度器 | Rebalance Scheduler再平衡调度器 | design | design_only |
| 81 | D-PF-CORE/Risk Parity Engine风险平价引擎 | Risk Parity Engine风险平价引擎 | design | design_only |
| 82 | D-PF-CORE/SHAP LIME Dual Attribution SHAP LIME双归因 | SHAP LIME Dual Attribution SHAP LIME... | design | design_only |
| 83 | D-PF-CORE/Sector Exposure Manager行业敞口管理器 | Sector Exposure Manager行业敞口管理器 | design | design_only |
| 84 | D-PF-CORE/Sell Decision Engine 卖出决策引擎 | Sell Decision Engine 卖出决策引擎 | design | design_only |
| 85 | D-PF-CORE/Signal Factory §4.1 信号工厂九大子阶段 | Signal Factory §4.1 信号工厂九大子阶段 | design | design_only |
| 86 | D-PF-CORE/Strategy Capacity Estimator策略容量估计器 | Strategy Capacity Estimator策略容量估... | design | design_only |
| 87 | D-PF-CORE/Strategy Capacity Modeling 策略容量建模 | Strategy Capacity Modeling 策略容量建模 | design | design_only |
| 88 | D-PF-CORE/Strategy Engine策略引擎 | Strategy Engine策略引擎 | design | design_only |
| 89 | D-PF-CORE/Strategy Factory 策略工厂 | Strategy Factory 策略工厂 | design | design_only |
| 90 | D-PF-CORE/Strategy Portfolio 策略组合 | Strategy Portfolio 策略组合 | design | design_only |
| 91 | D-PF-CORE/Strategy Signal Router 策略信号路由器 | Strategy Signal Router 策略信号路由器 | design | design_only |
| 92 | D-PF-CORE/StrategyLifecycleEvent 策略生命周期事件 | StrategyLifecycleEvent 策略生命周期事件 | design | design_only |
| 93 | D-PF-CORE/StrategyRegistry 策略注册表 | StrategyRegistry 策略注册表 | design | design_only |
| 94 | D-PF-CORE/Tax Loss Harvester税损收割器 | Tax Loss Harvester税损收割器 | design | design_only |
| 95 | D-PF-CORE/XS-EXT 模块分类汇总（5个） | XS-EXT 模块分类汇总（5个） | design | design_only |
| 96 | D-PF-CORE/§12.4 C-033 过拟合系统性防护 | §12.4 C-033 过拟合系统性防护 | design | design_only |
| 97 | D-PF-CORE/§2.1 多源数据接入与分层存储架构 Data Ingestion... | §2.1 多源数据接入与分层存储架构 Data... | design | design_only |
| 98 | D-PF-CORE/§20.8 方法论约束八：训练-服务一致性(Feature Store) | §20.8 方法论约束八：训练-服务一致性(... | design | design_only |
| 99 | D-PF-CORE/§24 外部系统交互引用 External | §24 外部系统交互引用 External | design | design_only |
| 100 | D-PF-CORE/§24.1 外部系统交互矩阵 External | §24.1 外部系统交互矩阵 External | design | design_only |
| 101 | D-PF-CORE/§27 系统级成功指标引用 | §27 系统级成功指标引用 | design | design_only |
| 102 | D-PF-CORE/§29.1 多进程隔离与运行时架构（→A9运维架构） | §29.1 多进程隔离与运行时架构（→A9运... | design | design_only |
| 103 | D-PF-CORE/§29.10 盘中即时反应决策引擎 Engine | §29.10 盘中即时反应决策引擎 Engine | design | design_only |
| 104 | D-PF-CORE/§29.2 特征存储 (Feature Store) | §29.2 特征存储 (Feature Store) | design | design_only |
| 105 | D-PF-CORE/§29.21 学习系统桥接声明 | §29.21 学习系统桥接声明 | design | design_only |
| 106 | D-PF-CORE/§29.27 多智能体编排框架选型与MCP协议（→A7 Age... | §29.27 多智能体编排框架选型与MCP协议... | design | design_only |
| 107 | D-PF-CORE/§29.35 持续学习抗遗忘框架（v6.0新增） | §29.35 持续学习抗遗忘框架（v6.0新增） | design | design_only |
| 108 | D-PF-CORE/§29.4 时序数据库与分层存储架构（→A3数据架构） | §29.4 时序数据库与分层存储架构（→A3... | design | design_only |
| 109 | D-PF-CORE/§30 场外草稿区缺失模块补充 | §30 场外草稿区缺失模块补充 | design | design_only |
| 110 | D-PF-CORE/§30.1 核心价值链域缺失模块 Core | §30.1 核心价值链域缺失模块 Core | design | design_only |
| 111 | D-PF-CORE/§30.1.3 D-PF-CORE 组合核心域（18个模块） | §30.1.3 D-PF-CORE 组合核心域（18个模块） | design | design_only |
| 112 | D-PF-CORE/§30.2 增强与扩展域缺失模块 | §30.2 增强与扩展域缺失模块 | design | design_only |
| 113 | D-PF-CORE/§30.3 核心交易链域缺失模块 Core | §30.3 核心交易链域缺失模块 Core | design | design_only |
| 114 | D-PF-CORE/§30.4 ML与数据工程域缺失模块 | §30.4 ML与数据工程域缺失模块 | design | design_only |
| 115 | D-PF-CORE/§30.5 自治与基础设施域缺失模块 Base | §30.5 自治与基础设施域缺失模块 Base | design | design_only |
| 116 | D-PF-CORE/§4.4 信号聚合器架构 Signal Aggregator | §4.4 信号聚合器架构 Signal Aggregator | design | design_only |
| 117 | D-PF-CORE/§8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | §8.1 策略工厂(C-006)与信号工厂(C-028... | design | design_only |
| 118 | D-PF-CORE/§8.5 组合优化引擎 Portfolio Engine | §8.5 组合优化引擎 Portfolio Engine | design | design_only |
| 119 | D-PF-CORE/❌不能建模块门禁条件分布 Cannot Build Module Ga... | ❌不能建模块门禁条件分布 Cannot Build... | design | design_only |
| 120 | D-PF-CORE/再平衡全流程Saga Rebalancing Saga | 再平衡全流程Saga Rebalancing Saga | design | design_only |
| 121 | D-PF-CORE/决策四：模型/策略漂移检测框架 Strategy Model | 决策四：模型/策略漂移检测框架 Strateg... | design | design_only |
| 122 | D-PF-CORE/多账户多策略 Strategy | 多账户多策略 Strategy | design | design_only |
| 123 | D-PF-CORE/模块10 动量领导因子与涨停板生态模型（Momentum L... | 模块10 动量领导因子与涨停板生态模型（... | design | design_only |
| 124 | D-PF-CORE/模块11 动量层级与板块持续性模型（Momentum Hiera... | 模块11 动量层级与板块持续性模型（Mome... | design | design_only |
| 125 | D-PF-CORE/模块12 板块间资金流迁移检测模型（Inter-Sector F... | 模块12 板块间资金流迁移检测模型（Inte... | design | design_only |
| 126 | D-PF-CORE/模块15 假突破与诱多检测模型（False Breakout & B... | 模块15 假突破与诱多检测模型（False Br... | design | design_only |
| 127 | D-PF-CORE/模块16 情绪-价格背离指数模型（Sentiment-Price D... | 模块16 情绪-价格背离指数模型（Sentime... | design | design_only |
| 128 | D-PF-CORE/模块19 市场体制转换模型（Regime-Switching Model） | 模块19 市场体制转换模型（Regime-Switc... | design | design_only |
| 129 | D-PF-CORE/模块23 量能体制自适应策略模型（Volume Regime Ad... | 模块23 量能体制自适应策略模型（Volume... | design | design_only |
| 130 | D-PF-CORE/模块24 核心-卫星仓位管理模型（Core-Satellite Po... | 模块24 核心-卫星仓位管理模型（Core-Sa... | design | design_only |
| 131 | D-PF-CORE/模块26 3秒级逆势资金流识别模块 Module 26 3-Seco... | 模块26 3秒级逆势资金流识别模块 Module... | design | design_only |
| 132 | D-PF-CORE/模块27 主力假动作与筹码派发识别模块 Module 27 M... | 模块27 主力假动作与筹码派发识别模块 M... | design | design_only |
| 133 | D-PF-CORE/模块28 利好落地变利空（预期透支）模块 Module 28... | 模块28 利好落地变利空（预期透支）模块... | design | design_only |
| 134 | D-PF-CORE/模块29 次日上涨概率统一门槛模块 Module 29 Next-... | 模块29 次日上涨概率统一门槛模块 Modul... | design | design_only |
| 135 | D-PF-CORE/模块3 缺口回补概率模型（Gap Fill Probability Mo... | 模块3 缺口回补概率模型（Gap Fill Prob... | design | design_only |
| 136 | D-PF-CORE/模块31 协同交易行为检测模型（Coordinated Tradin... | 模块31 协同交易行为检测模型（Coordina... | design | design_only |
| 137 | D-PF-CORE/模块32 市场风格体制识别模型（Market Style Regim... | 模块32 市场风格体制识别模型（Market S... | design | design_only |
| 138 | D-PF-CORE/模块34 异质参与者互动模型（Heterogeneous Agent ... | 模块34 异质参与者互动模型（Heterogene... | design | design_only |
| 139 | D-PF-CORE/模块39 多因子选股评分模型（Multi-Factor Stock S... | 模块39 多因子选股评分模型（Multi-Fact... | design | design_only |
| 140 | D-PF-CORE/模块4 逼空行情检测模型（Short Squeeze Detection... | 模块4 逼空行情检测模型（Short Squeeze... | design | design_only |
| 141 | D-PF-CORE/模块51 波动率压缩与突破模型（Volatility Compres... | 模块51 波动率压缩与突破模型（Volatili... | design | design_only |
| 142 | D-PF-CORE/模块52 汇总：缺失模块与建议归属层映射（更新版）... | 模块52 汇总：缺失模块与建议归属层映射... | design | design_only |
| 143 | D-PF-CORE/模块57 多因子叠加择时模型（Multi-Factor Overlay... | 模块57 多因子叠加择时模型（Multi-Fact... | design | design_only |
| 144 | D-PF-CORE/模块58 附录二：已剔除模块说明（架构文档完全覆盖... | 模块58 附录二：已剔除模块说明（架构文... | design | design_only |
| 145 | D-PF-CORE/模块58 附录：已有架构覆盖的功能（不重复列出） M... | 模块58 附录：已有架构覆盖的功能（不重... | design | design_only |
| 146 | D-PF-CORE/模块7 多指标背离检测模型（Multi-Indicator Diver... | 模块7 多指标背离检测模型（Multi-Indic... | design | design_only |
| 147 | D-PF-CORE/模块8 板块资金流再配置模型（Sector Flow Realloc... | 模块8 板块资金流再配置模型（Sector Fl... | design | design_only |
| 148 | D-PF-CORE/裁定15: FinRL-X模块化交易基础设施 | 裁定15: FinRL-X模块化交易基础设施 | design | design_only |
| 149 | D-PF-CORE/裁定18: 中金Quant 4.0框架对齐 | 裁定18: 中金Quant 4.0框架对齐 | design | design_only |
| 150 | D-PF-CORE/裁定22: 持续学习抗遗忘框架（§29.35） Decision ... | 裁定22: 持续学习抗遗忘框架（§29.35）... | design | design_only |
| 151 | D-PF-CORE/账户状态物化视图 Account Status View | 账户状态物化视图 Account Status View | design | design_only |
| 152 | D-PF-CORE/🟡 健康线（Healthy）—— 系统运行良好，可以放心 | 🟡 健康线（Healthy）—— 系统运行良好... | design | design_only |
| 153 | D-PF-CORE/🟢 生存线（Survival）—— 低于此线系统进入警告... | 🟢 生存线（Survival）—— 低于此线系... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 152 条 / 152 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 152 条 / 152 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 139 条 / edges                               │
│   [event]: 8 条 / edges                                          │
│   [contract]: 3 条 / edges                                       │
│   [data]: 2 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (139 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Strategy Capacity Modelin... → §29.35 持续学习抗遗忘框...      │
│   Factor/Strategy Crowding ... → Signal Factory §4.1 信号...     │
│   Explainability 决策可解释... → §2.1 多源数据接入与分层...      │
│   多账户多策略 Strategy → Multi-Track Fusion 四轨融...           │
│   Strategy Engine策略引擎 → Portfolio Optimizer组合优...         │
│   Portfolio Optimizer组合优... → Rebalance Scheduler再平衡...    │
│   Rebalance Scheduler再平衡... → Constraint Solver约束求解器     │
│   Constraint Solver约束求解器 → Risk Parity Engine风险平...      │
│   Risk Parity Engine风险平... → Multi-Objective Optimizer...     │
│   Multi-Objective Optimizer... → Tax Loss Harvester税损收割器    │
│   Tax Loss Harvester税损收割器 → Portfolio Drift Monitor组...    │
│   Portfolio Drift Monitor组... → Cash Flow Manager资金流管...    │
│   Cash Flow Manager资金流管... → Rebalance Cost Analyzer再...    │
│   Cash Flow Manager资金流管... → Rebalance Full Flow Saga ...    │
│   Rebalance Cost Analyzer再... → Liquidity Estimator流动性...    │
│   Liquidity Estimator流动性... → Portfolio Stress Tester组...    │
│   Liquidity Estimator流动性... → Execution to L5 Closed Lo...    │
│   Portfolio Stress Tester组... → Sector Exposure Manager行...    │
│   Sector Exposure Manager行... → Factor Exposure Manager因...    │
│   Factor Exposure Manager因... → Portfolio Benchmark Manag...    │
│   Portfolio Benchmark Manag... → Carbon Footprint Calculat...    │
│   Carbon Footprint Calculat... → Strategy Capacity Estimat...    │
│   Strategy Capacity Estimat... → Performance Attribution E...    │
│   Performance Attribution E... → §2.1 多源数据接入与分层...      │
│   §2.1 多源数据接入与分层... → 模块3 缺口回补概率模型（G...      │
│   模块3 缺口回补概率模型（G... → 模块4 逼空行情检测模型（S...    │
│   模块4 逼空行情检测模型（S... → 模块7 多指标背离检测模型...     │
│   模块7 多指标背离检测模型... → 模块8 板块资金流再配置模...      │
│   模块8 板块资金流再配置模... → 模块10 动量领导因子与涨停...     │
│   模块10 动量领导因子与涨停... → 模块11 动量层级与板块持续...    │
│   模块11 动量层级与板块持续... → 模块12 板块间资金流迁移检...    │
│   模块11 动量层级与板块持续... → L2 to L3 Strategy Decisio...    │
│   模块12 板块间资金流迁移检... → 模块15 假突破与诱多检测模...    │
│   模块15 假突破与诱多检测模... → 模块16 情绪-价格背离指数...     │
│   模块16 情绪-价格背离指数... → 模块19 市场体制转换模型（...     │
│   模块16 情绪-价格背离指数... → Portfolio 组合                   │
│   模块19 市场体制转换模型（... → 19.2 Ensemble-HMM增强框架       │
│   19.2 Ensemble-HMM增强框架 → 模块26 3秒级逆势资金流识...        │
│   模块26 3秒级逆势资金流识... → 26.5 逆势资金流与已有模块...     │
│   26.5 逆势资金流与已有模块... → 模块31 协同交易行为检测模...    │
│   模块31 协同交易行为检测模... → 31.3 高级协同检测（基于ES...    │
│   31.3 高级协同检测（基于ES... → 模块34 异质参与者互动模型...    │
│   模块34 异质参与者互动模型... → 模块39 多因子选股评分模型...    │
│   模块39 多因子选股评分模型... → 模块51 波动率压缩与突破模...    │
│   模块39 多因子选股评分模型... → 再平衡全流程Saga Rebalanc...    │
│   模块51 波动率压缩与突破模... → 模块52 汇总：缺失模块与建...    │
│   模块52 汇总：缺失模块与建... → 模块58 附录：已有架构覆盖...    │
│   模块58 附录：已有架构覆盖... → 模块58 附录二：已剔除模块...    │
│   模块58 附录二：已剔除模块... → Signal Factory §4.1 信号...     │
│   ...还有 90 条 / 90 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[event]** (8 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (3 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (2 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 152 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `34_d_pf_core_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
