---
doc_type: domain_architecture_diagram
title: D-SIMULATION 仿真架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 42_d_simulation / 仿真 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示仿真（D-SIMULATION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 仿真（D-SIMULATION）的模块分布。共 128 个模块 / 128 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (23 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   仿真核心域  [design]                                           │
│   src/zephyr/simulation/__init__.py  [prototype]                 │
│   src/zephyr/simulation/__init___from_resear.py  [prototype]     │
│   src/zephyr/simulation/_extensions/__init__.py  [scaffold_pl... │
│   src/zephyr/simulation/api/__init__.py  [scaffold_placeholder]  │
│   src/zephyr/simulation/backtest_base.py  [production]           │
│   src/zephyr/simulation/backtest_base_from_resear.py  [protot... │
│   src/zephyr/simulation/core/__init__.py  [scaffold_placeholder] │
│   src/zephyr/simulation/default_backtest_engine.py  [production] │
│   src/zephyr/simulation/default_backtest_engine_from_resear.p... │
│   仿真引擎  [design]                                             │
│   src/zephyr/simulation/implementations/__init__.py  [prototype] │
│   src/zephyr/simulation/implementations/__init___from_resear.... │
│   src/zephyr/simulation/implementations/default_experiment_pi... │
│   src/zephyr/simulation/implementations/default_experiment_pi... │
│   src/zephyr/simulation/infrastructure/__init__.py  [scaffold... │
│   市场仿真器  [design]                                           │
│   src/zephyr/simulation/models/__init__.py  [scaffold_placeho... │
│   ...还有 5 个模块 / 5 more modules                              │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (105 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   ADR Decision Simulator ADR决策仿真器  [design]                 │
│   Agent-Based Market Model 基于Agent的市场模型  [design]         │
│   Approval Gate Dependency Extractor Enhancer 审批门依赖提取...  │
│   Approval Gate Dependency Extractor 审批门依赖提取器  [design]  │
│   Architecture Anti-Pattern Topology Detector 架构反模式拓扑...  │
│   Architecture Anti-Pattern Topology Enhancer 架构反模式拓扑...  │
│   Argus Dependency-First Mutation Tester Argus依赖优先变异测...  │
│   Argus Mutation Enhancer Argus变异增强器  [design]              │
│   Auto Backtest Scheduler 自动回测调度器  [design]               │
│   Automated Overfitting Detector 自动化过拟合检测  [design]      │
│   Backtest Acceleration Module 回测加速模块  [design]            │
│   Backtest Anomaly Diagnoser 回测异常诊断  [design]              │
│   Backtest Cache Manager 回测缓存管理器  [design]                │
│   Backtest Data Quality Checker 回测数据质量检查器  [design]     │
│   Backtest Overfitting Detector回测过拟合检测  [design]          │
│   Backtest Pipeline Orchestrator 回测流水线编排器  [design]      │
│   Backtest Report Auto Generator 回测报告自动生成  [design]      │
│   Backtest Result Comparator 回测结果对比  [design]              │
│   ...还有 87 个模块 / 87 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 128 个模块 / 128 modules）。

### L2 领域层 / Domain Layer (23 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/simulation/ | 仿真核心域 | design | design_only |
| 2 | src/zephyr/simulation/__init__.py | src/zephyr/simulation/__init__.py | prototype | draft |
| 3 | src/zephyr/simulation/__init___from_resear.py | src/zephyr/simulation/__init___from_r... | prototype | draft |
| 4 | src/zephyr/simulation/_extensions/__init__.py | src/zephyr/simulation/_extensions/__i... | scaffold_placeholder | orphan |
| 5 | src/zephyr/simulation/api/__init__.py | src/zephyr/simulation/api/__init__.py | scaffold_placeholder | orphan |
| 6 | src/zephyr/simulation/backtest_base.py | src/zephyr/simulation/backtest_base.py | production | draft |
| 7 | src/zephyr/simulation/backtest_base_from_resear.py | src/zephyr/simulation/backtest_base_f... | prototype | draft |
| 8 | src/zephyr/simulation/core/__init__.py | src/zephyr/simulation/core/__init__.py | scaffold_placeholder | orphan |
| 9 | src/zephyr/simulation/default_backtest_engine.py | src/zephyr/simulation/default_backtes... | production | draft |
| 10 | src/zephyr/simulation/default_backtest_engine_from_resear.py | src/zephyr/simulation/default_backtes... | prototype | draft |
| 11 | src/zephyr/simulation/engine/ | 仿真引擎 | design | design_only |
| 12 | src/zephyr/simulation/implementations/__init__.py | src/zephyr/simulation/implementations... | prototype | draft |
| 13 | src/zephyr/simulation/implementations/__init___from_resea... | src/zephyr/simulation/implementations... | prototype | draft |
| 14 | src/zephyr/simulation/implementations/default_experiment_... | src/zephyr/simulation/implementations... | production | draft |
| 15 | src/zephyr/simulation/implementations/default_experiment_... | src/zephyr/simulation/implementations... | prototype | draft |
| 16 | src/zephyr/simulation/infrastructure/__init__.py | src/zephyr/simulation/infrastructure/... | scaffold_placeholder | orphan |
| 17 | src/zephyr/simulation/market_sim/ | 市场仿真器 | design | design_only |
| 18 | src/zephyr/simulation/models/__init__.py | src/zephyr/simulation/models/__init__.py | scaffold_placeholder | orphan |
| 19 | src/zephyr/simulation/pipeline_base.py | src/zephyr/simulation/pipeline_base.py | production | draft |
| 20 | src/zephyr/simulation/pipeline_base_from_resear.py | src/zephyr/simulation/pipeline_base_f... | prototype | draft |
| 21 | src/zephyr/simulation/result/ | 仿真结果分析 | design | design_only |
| 22 | src/zephyr/simulation/scenario/ | 场景管理器 | design | design_only |
| 23 | src/zephyr/simulation/services/__init__.py | src/zephyr/simulation/services/__init... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (105 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-SIMULATION/ADR Decision Simulator ADR决策仿真器 | ADR Decision Simulator ADR决策仿真器 | design | design_only |
| 2 | D-SIMULATION/Agent-Based Market Model 基于Agent的市场模型 | Agent-Based Market Model 基于Agent的... | design | design_only |
| 3 | D-SIMULATION/Approval Gate Dependency Extractor Enhancer ... | Approval Gate Dependency Extractor En... | design | design_only |
| 4 | D-SIMULATION/Approval Gate Dependency Extractor 审批门依... | Approval Gate Dependency Extractor 审... | design | design_only |
| 5 | D-SIMULATION/Architecture Anti-Pattern Topology Detector ... | Architecture Anti-Pattern Topology De... | design | design_only |
| 6 | D-SIMULATION/Architecture Anti-Pattern Topology Enhancer ... | Architecture Anti-Pattern Topology En... | design | design_only |
| 7 | D-SIMULATION/Argus Dependency-First Mutation Tester Argus... | Argus Dependency-First Mutation Teste... | design | design_only |
| 8 | D-SIMULATION/Argus Mutation Enhancer Argus变异增强器 | Argus Mutation Enhancer Argus变异增强器 | design | design_only |
| 9 | D-SIMULATION/Auto Backtest Scheduler 自动回测调度器 | Auto Backtest Scheduler 自动回测调度器 | design | design_only |
| 10 | D-SIMULATION/Automated Overfitting Detector 自动化过拟合检测 | Automated Overfitting Detector 自动化... | design | design_only |
| 11 | D-SIMULATION/Backtest Acceleration Module 回测加速模块 | Backtest Acceleration Module 回测加速... | design | design_only |
| 12 | D-SIMULATION/Backtest Anomaly Diagnoser 回测异常诊断 | Backtest Anomaly Diagnoser 回测异常诊断 | design | design_only |
| 13 | D-SIMULATION/Backtest Cache Manager 回测缓存管理器 | Backtest Cache Manager 回测缓存管理器 | design | design_only |
| 14 | D-SIMULATION/Backtest Data Quality Checker 回测数据质量检... | Backtest Data Quality Checker 回测数... | design | design_only |
| 15 | D-SIMULATION/Backtest Overfitting Detector回测过拟合检测 | Backtest Overfitting Detector回测过拟... | design | design_only |
| 16 | D-SIMULATION/Backtest Pipeline Orchestrator 回测流水线编排器 | Backtest Pipeline Orchestrator 回测流... | design | design_only |
| 17 | D-SIMULATION/Backtest Report Auto Generator 回测报告自动生成 | Backtest Report Auto Generator 回测报... | design | design_only |
| 18 | D-SIMULATION/Backtest Result Comparator 回测结果对比 | Backtest Result Comparator 回测结果对比 | design | design_only |
| 19 | D-SIMULATION/Backtest Result One-Click Deployer 回测结果... | Backtest Result One-Click Deployer 回... | design | design_only |
| 20 | D-SIMULATION/Backtest Result Statistical Significance Tes... | Backtest Result Statistical Significa... | design | design_only |
| 21 | D-SIMULATION/Capital Group Ecology & Multi-Party Game Sim... | Capital Group Ecology & Multi-Party G... | design | design_only |
| 22 | D-SIMULATION/Carbon Intensity Queryer 碳强度查询器 | Carbon Intensity Queryer 碳强度查询器 | design | design_only |
| 23 | D-SIMULATION/Carbon-Aware Scheduler Optimizer 碳感知调度... | Carbon-Aware Scheduler Optimizer 碳感... | design | design_only |
| 24 | D-SIMULATION/Chaos Engineering Environment 混沌工程环境 | Chaos Engineering Environment 混沌工... | design | design_only |
| 25 | D-SIMULATION/Chaos Experiment Auto-Generator 混沌实验自动... | Chaos Experiment Auto-Generator 混沌... | design | design_only |
| 26 | D-SIMULATION/Convexity Budget Framework 凸性预算框架 | Convexity Budget Framework 凸性预算框架 | design | design_only |
| 27 | D-SIMULATION/Correlation Regime Shift 相关性体制转换 | Correlation Regime Shift 相关性体制转换 | design | design_only |
| 28 | D-SIMULATION/Counterparty Simulator 对手仿真器 | Counterparty Simulator 对手仿真器 | design | design_only |
| 29 | D-SIMULATION/Cross-Engine Backtest Result Comparator 跨引... | Cross-Engine Backtest Result Comparat... | design | design_only |
| 30 | D-SIMULATION/Cross-Env Dependency Diff Analyzer 跨环境依... | Cross-Env Dependency Diff Analyzer 跨... | design | design_only |
| 31 | D-SIMULATION/D-SIMULATION 仿真 | D-SIMULATION 仿真 | design | design_only |
| 32 | D-SIMULATION/DANTE Dependency-Aware Test Generator DANTE... | DANTE Dependency-Aware Test Generator... | design | design_only |
| 33 | D-SIMULATION/DANTE Test Generation Enhancer DANTE测试生成... | DANTE Test Generation Enhancer DANTE... | design | design_only |
| 34 | D-SIMULATION/Deflated Sharpe Ratio Calculator DSR计算器 | Deflated Sharpe Ratio Calculator DSR... | design | design_only |
| 35 | D-SIMULATION/Dependency Chain Carbon Footprint Attributor... | Dependency Chain Carbon Footprint Att... | design | design_only |
| 36 | D-SIMULATION/Dependency Graph Digital Twin 依赖图数字孪生 | Dependency Graph Digital Twin 依赖图... | design | design_only |
| 37 | D-SIMULATION/Dependency Graph Real-time Twin Engine 依赖... | Dependency Graph Real-time Twin Engin... | design | design_only |
| 38 | D-SIMULATION/Dependency Hell 5-Dimension Detection Enhanc... | Dependency Hell 5-Dimension Detection... | design | design_only |
| 39 | D-SIMULATION/Digital Twin Market Simulation 数字孪生市场仿真 | Digital Twin Market Simulation 数字孪... | design | design_only |
| 40 | D-SIMULATION/Dual-Mode Backtest Engine双模式回测引擎 | Dual-Mode Backtest Engine双模式回测引擎 | design | design_only |
| 41 | D-SIMULATION/Energy Consumption Collector 能耗采集器 | Energy Consumption Collector 能耗采集器 | design | design_only |
| 42 | D-SIMULATION/Event-Driven Backtester 事件驱动回测器 | Event-Driven Backtester 事件驱动回测器 | design | design_only |
| 43 | D-SIMULATION/Extreme Event Simulator 极端事件仿真器 | Extreme Event Simulator 极端事件仿真器 | design | design_only |
| 44 | D-SIMULATION/FeatureStore PIT Feature Store时点特征 | FeatureStore PIT Feature Store时点特征 | design | design_only |
| 45 | D-SIMULATION/Greek Trilemma希腊三难困境 | Greek Trilemma希腊三难困境 | design | design_only |
| 46 | D-SIMULATION/History Replay Engine历史重放引擎 | History Replay Engine历史重放引擎 | design | design_only |
| 47 | D-SIMULATION/Indicator NaN Processor 指标NaN处理器 | Indicator NaN Processor 指标NaN处理器 | design | design_only |
| 48 | D-SIMULATION/Liquidity Model & Slippage Simulator 流动性... | Liquidity Model & Slippage Simulator ... | design | design_only |
| 49 | D-SIMULATION/Liquidity Simulator 流动性仿真器 | Liquidity Simulator 流动性仿真器 | design | design_only |
| 50 | D-SIMULATION/Live Environment Simulator实盘环境模拟 | Live Environment Simulator实盘环境模拟 | design | design_only |
| 51 | D-SIMULATION/Look-Ahead Bias Detector未来函数风险检测 | Look-Ahead Bias Detector未来函数风险检测 | design | design_only |
| 52 | D-SIMULATION/Market Simulator市场仿真器 | Market Simulator市场仿真器 | design | design_only |
| 53 | D-SIMULATION/Monte Carlo Engine蒙特卡洛模拟 | Monte Carlo Engine蒙特卡洛模拟 | design | design_only |
| 54 | D-SIMULATION/Multi-Strategy Backtest Comparator 多策略回... | Multi-Strategy Backtest Comparator 多... | design | design_only |
| 55 | D-SIMULATION/Mutation Score Dependency Gate 变异评分依赖门禁 | Mutation Score Dependency Gate 变异评... | design | design_only |
| 56 | D-SIMULATION/NozyIO Backtest Visual Reporter NozyIO回测可... | NozyIO Backtest Visual Reporter NozyI... | design | design_only |
| 57 | D-SIMULATION/Order Matching Engine 订单撮合引擎 | Order Matching Engine 订单撮合引擎 | design | design_only |
| 58 | D-SIMULATION/Overfitting Detector 过拟合检验器 | Overfitting Detector 过拟合检验器 | design | design_only |
| 59 | D-SIMULATION/OverfittingDetected 过拟合检测触发 | OverfittingDetected 过拟合检测触发 | design | design_only |
| 60 | D-SIMULATION/Parameter Optimization Result Analyzer 参数... | Parameter Optimization Result Analyze... | design | design_only |
| 61 | D-SIMULATION/Parameter Robustness Tester 参数鲁棒性测试器 | Parameter Robustness Tester 参数鲁棒... | design | design_only |
| 62 | D-SIMULATION/Parameter Sensitivity Analyzer 参数灵敏度分析器 | Parameter Sensitivity Analyzer 参数灵... | design | design_only |
| 63 | D-SIMULATION/Performance Regression Dependency Gate 性能... | Performance Regression Dependency Gat... | design | design_only |
| 64 | D-SIMULATION/Pipeline DAG Scheduler 管线DAG调度器 | Pipeline DAG Scheduler 管线DAG调度器 | design | design_only |
| 65 | D-SIMULATION/Pipeline DAG Scheduling Enhancer Pipeline DA... | Pipeline DAG Scheduling Enhancer Pipe... | design | design_only |
| 66 | D-SIMULATION/Qlib Walk-Forward Simplified Version Integra... | Qlib Walk-Forward Simplified Version ... | design | design_only |
| 67 | D-SIMULATION/Real-time DT Synchronizer 实时数字孪生同步器 | Real-time DT Synchronizer 实时数字孪... | design | design_only |
| 68 | D-SIMULATION/Risk Simulator风控仿真器 | Risk Simulator风控仿真器 | design | design_only |
| 69 | D-SIMULATION/SCI Calculator SCI计算器 | SCI Calculator SCI计算器 | design | design_only |
| 70 | D-SIMULATION/Scenario Generator场景生成器 | Scenario Generator场景生成器 | design | design_only |
| 71 | D-SIMULATION/ScenarioGenerated 场景生成完成 | ScenarioGenerated 场景生成完成 | design | design_only |
| 72 | D-SIMULATION/Semantic-Level Diff Understanding 语义级差异... | Semantic-Level Diff Understanding 语... | design | design_only |
| 73 | D-SIMULATION/Sharpe Calculator Fixer Sharpe计算修正器 | Sharpe Calculator Fixer Sharpe计算修正器 | design | design_only |
| 74 | D-SIMULATION/Simulation Profitability Evaluator 模拟盘盈... | Simulation Profitability Evaluator 模... | design | design_only |
| 75 | D-SIMULATION/Simulation Result Analyzer 仿真结果分析器 | Simulation Result Analyzer 仿真结果分... | design | design_only |
| 76 | D-SIMULATION/SimulationCompleted 仿真完成 | SimulationCompleted 仿真完成 | design | design_only |
| 77 | D-SIMULATION/SimulationResult Interface 仿真结果接口 | SimulationResult Interface 仿真结果接口 | design | design_only |
| 78 | D-SIMULATION/SimulationScenario 仿真场景 | SimulationScenario 仿真场景 | design | design_only |
| 79 | D-SIMULATION/Strategy Decay Monitor Alerter 策略衰减监控... | Strategy Decay Monitor Alerter 策略衰... | design | design_only |
| 80 | D-SIMULATION/Strategy Simulator策略仿真器 | Strategy Simulator策略仿真器 | design | design_only |
| 81 | D-SIMULATION/StressTestResult 压力测试结果 | StressTestResult 压力测试结果 | design | design_only |
| 82 | D-SIMULATION/Technical Analysis Backtest Validator 技术分... | Technical Analysis Backtest Validator... | design | design_only |
| 83 | D-SIMULATION/Test Data Factory 测试数据工厂 | Test Data Factory 测试数据工厂 | design | design_only |
| 84 | D-SIMULATION/Test Environment Orchestrator 测试环境编排器 | Test Environment Orchestrator 测试环... | design | design_only |
| 85 | D-SIMULATION/Test Impact Analyzer 测试影响分析器 | Test Impact Analyzer 测试影响分析器 | design | design_only |
| 86 | D-SIMULATION/Validation Automation Pipeline验证自动化流水线 | Validation Automation Pipeline验证自... | design | design_only |
| 87 | D-SIMULATION/Walk-Forward Analyzer Walk-Forward分析 | Walk-Forward Analyzer Walk-Forward分析 | design | design_only |
| 88 | D-SIMULATION/Walk-Forward Optimization Engine WFO引擎 | Walk-Forward Optimization Engine WFO引擎 | design | design_only |
| 89 | D-SIMULATION/empyrical Integrator empyrical集成器 | empyrical Integrator empyrical集成器 | design | design_only |
| 90 | D-SIMULATION/quantstats Integrator quantstats集成器 | quantstats Integrator quantstats集成器 | design | design_only |
| 91 | D-SIMULATION/vectorbt Vectorized Backtest Integrator vect... | vectorbt Vectorized Backtest Integrat... | design | design_only |
| 92 | D-SIMULATION/仿真域监控指标采集适配器 Adapter Monitoring ... | 仿真域监控指标采集适配器 Adapter Moni... | design | design_only |
| 93 | D-SIMULATION/仿真域配置热更新适配器 Adapter Simulation Co... | 仿真域配置热更新适配器 Adapter Simula... | design | design_only |
| 94 | D-SIMULATION/参数优化结果分析器 Analyzer Parameter | 参数优化结果分析器 Analyzer Parameter | design | design_only |
| 95 | D-SIMULATION/回测仿真 Walk-Forward回测 | 回测仿真 Walk-Forward回测 | design | design_only |
| 96 | D-SIMULATION/回测异常诊断 Backtest | 回测异常诊断 Backtest | design | design_only |
| 97 | D-SIMULATION/回测数据质量检查器 Data Quality Backtest | 回测数据质量检查器 Data Quality Backtest | design | design_only |
| 98 | D-SIMULATION/回测流水线执行记录查询与回放器 Execution Bac... | 回测流水线执行记录查询与回放器 Execut... | design | design_only |
| 99 | D-SIMULATION/回测结果一键部署 Backtest | 回测结果一键部署 Backtest | design | design_only |
| 100 | D-SIMULATION/回测结果对比 Backtest | 回测结果对比 Backtest | design | design_only |
| 101 | D-SIMULATION/回测缓存管理器 Backtest Management Cache | 回测缓存管理器 Backtest Management Cache | design | design_only |
| 102 | D-SIMULATION/指标计算NaN处理器 | 指标计算NaN处理器 | design | design_only |
| 103 | D-SIMULATION/自动化过拟合检测 Automated Overfitting Detec... | 自动化过拟合检测 Automated Overfittin... | design | design_only |
| 104 | D-SIMULATION/集成测试任务 Integration Task | 集成测试任务 Integration Task | design | design_only |
| 105 | D-SIMULATION/验收标准自动化测试与判定器 Acceptance Criter... | 验收标准自动化测试与判定器 Acceptance... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 114 条 / 114 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 114 条 / 114 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 104 条 / edges                               │
│   [config_depends]: 5 条 / edges                                 │
│   [event]: 4 条 / edges                                          │
│   [contract]: 1 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (104 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   default_backtest_engine.py → __init__.py                       │
│   default_backtest_engine_f... → __init__.py                     │
│   __init___from_resear.py → backtest_base.py                     │
│   __init___from_resear.py → default_backtest_engine.py           │
│   __init___from_resear.py → pipeline_base.py                     │
│   default_experiment_pipeli... → __init__.py                     │
│   default_experiment_pipeli... → __init__.py                     │
│   Capital Group Ecology & M... → Carbon Intensity Queryer ...    │
│   D-SIMULATION 仿真 → Market Simulator市场仿真器                 │
│   Market Simulator市场仿真器 → Strategy Simulator策略仿真器      │
│   Strategy Simulator策略仿真器 → Risk Simulator风控仿真器        │
│   Risk Simulator风控仿真器 → Scenario Generator场景生成器        │
│   Scenario Generator场景生成器 → Monte Carlo Engine蒙特卡...     │
│   Monte Carlo Engine蒙特卡... → History Replay Engine历史...     │
│   History Replay Engine历史... → Backtest Overfitting Dete...    │
│   Backtest Overfitting Dete... → Walk-Forward Analyzer Wal...    │
│   Walk-Forward Analyzer Wal... → Look-Ahead Bias Detector...     │
│   Walk-Forward Analyzer Wal... → Convexity Budget Framewor...    │
│   Look-Ahead Bias Detector... → Validation Automation Pip...     │
│   Validation Automation Pip... → Dual-Mode Backtest Engine...    │
│   Dual-Mode Backtest Engine... → Live Environment Simulato...    │
│   Live Environment Simulato... → Counterparty Simulator 对...    │
│   Counterparty Simulator 对... → Liquidity Simulator 流动...     │
│   Counterparty Simulator 对... → Correlation Regime Shift ...    │
│   Liquidity Simulator 流动... → Extreme Event Simulator ...      │
│   Extreme Event Simulator ... → Agent-Based Market Model ...     │
│   Agent-Based Market Model ... → Simulation Result Analyze...    │
│   Simulation Result Analyze... → Dependency Graph Digital ...    │
│   Dependency Graph Digital ... → Real-time DT Synchronizer...    │
│   Real-time DT Synchronizer... → Chaos Experiment Auto-Gen...    │
│   Chaos Experiment Auto-Gen... → ADR Decision Simulator AD...    │
│   ADR Decision Simulator AD... → Dependency Graph Real-tim...    │
│   Dependency Graph Real-tim... → Event-Driven Backtester ...     │
│   Event-Driven Backtester ... → Parameter Robustness Test...     │
│   Parameter Robustness Test... → Sharpe Calculator Fixer S...    │
│   Sharpe Calculator Fixer S... → Deflated Sharpe Ratio Cal...    │
│   Deflated Sharpe Ratio Cal... → Walk-Forward Optimization...    │
│   Walk-Forward Optimization... → Auto Backtest Scheduler ...     │
│   Auto Backtest Scheduler ... → Strategy Decay Monitor Al...     │
│   Strategy Decay Monitor Al... → empyrical Integrator empy...    │
│   empyrical Integrator empy... → quantstats Integrator qua...    │
│   quantstats Integrator qua... → vectorbt Vectorized Backt...    │
│   vectorbt Vectorized Backt... → Qlib Walk-Forward Simplif...    │
│   Qlib Walk-Forward Simplif... → Parameter Sensitivity Ana...    │
│   Parameter Sensitivity Ana... → Order Matching Engine 订...     │
│   Order Matching Engine 订... → Simulation Profitability ...     │
│   Simulation Profitability ... → NozyIO Backtest Visual Re...    │
│   NozyIO Backtest Visual Re... → Backtest Pipeline Orchest...    │
│   Backtest Pipeline Orchest... → Overfitting Detector 过拟...    │
│   ...还有 55 条 / 55 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (5 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 114 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `42_d_simulation_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
