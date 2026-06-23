---
doc_type: domain_architecture_doc
title: D-SIMULATION 仿真架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SIMULATION 仿真架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SIMULATION |
| 域名称 | 仿真 |
| 架构层 | L2_domain |
| 模块总数 | 128 |
| 设计态模块 | 110 |
| 原型态模块 | 8 |
| 生产态模块 | 4 |
| 容量 | 4/150 (正常) |
| 描述 | 仿真引擎、场景生成、蒙特卡洛、回测模拟。策略验证沙箱。 |

## 模块清单

共 128 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-SIMULATION/ADR Decision Simulator ADR决策仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Agent-Based Market Model 基于Agent的市场模型 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Approval Gate Dependency Extractor Enhancer 审批门依赖提取器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Approval Gate Dependency Extractor 审批门依赖提取器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Architecture Anti-Pattern Topology Detector 架构反模式拓扑检测器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Architecture Anti-Pattern Topology Enhancer 架构反模式拓扑增强器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Argus Dependency-First Mutation Tester Argus依赖优先变异测试器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Argus Mutation Enhancer Argus变异增强器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Auto Backtest Scheduler 自动回测调度器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Automated Overfitting Detector 自动化过拟合检测 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Acceleration Module 回测加速模块 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Anomaly Diagnoser 回测异常诊断 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Cache Manager 回测缓存管理器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Data Quality Checker 回测数据质量检查器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Overfitting Detector回测过拟合检测 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Pipeline Orchestrator 回测流水线编排器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Report Auto Generator 回测报告自动生成 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Result Comparator 回测结果对比 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Result One-Click Deployer 回测结果一键部署 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Backtest Result Statistical Significance Tester 回测结果统计显著性检验 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Capital Group Ecology & Multi-Party Game Simulation 资金群体生态与多方博弈模拟 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Carbon Intensity Queryer 碳强度查询器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Carbon-Aware Scheduler Optimizer 碳感知调度优化器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Chaos Engineering Environment 混沌工程环境 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Chaos Experiment Auto-Generator 混沌实验自动生成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Convexity Budget Framework 凸性预算框架 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Correlation Regime Shift 相关性体制转换 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Counterparty Simulator 对手仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Cross-Engine Backtest Result Comparator 跨引擎回测结果比较器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Cross-Env Dependency Diff Analyzer 跨环境依赖差异分析器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/D-SIMULATION 仿真 |  | design_only | design | 0 | 0 |
| D-SIMULATION/DANTE Dependency-Aware Test Generator DANTE依赖感知测试生成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/DANTE Test Generation Enhancer DANTE测试生成增强器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Deflated Sharpe Ratio Calculator DSR计算器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Dependency Chain Carbon Footprint Attributor 依赖链碳足迹归因器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Dependency Graph Digital Twin 依赖图数字孪生 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Dependency Graph Real-time Twin Engine 依赖图实时孪生引擎 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Dependency Hell 5-Dimension Detection Enhancer 依赖地狱5维检测增强器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Digital Twin Market Simulation 数字孪生市场仿真 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Dual-Mode Backtest Engine双模式回测引擎 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Energy Consumption Collector 能耗采集器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Event-Driven Backtester 事件驱动回测器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Extreme Event Simulator 极端事件仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/FeatureStore PIT Feature Store时点特征 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Greek Trilemma希腊三难困境 |  | design_only | design | 0 | 0 |
| D-SIMULATION/History Replay Engine历史重放引擎 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Indicator NaN Processor 指标NaN处理器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Liquidity Model & Slippage Simulator 流动性模型与滑点模拟器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Liquidity Simulator 流动性仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Live Environment Simulator实盘环境模拟 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Look-Ahead Bias Detector未来函数风险检测 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Market Simulator市场仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Monte Carlo Engine蒙特卡洛模拟 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Multi-Strategy Backtest Comparator 多策略回测对比 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Mutation Score Dependency Gate 变异评分依赖门禁 |  | design_only | design | 0 | 0 |
| D-SIMULATION/NozyIO Backtest Visual Reporter NozyIO回测可视化报告器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Order Matching Engine 订单撮合引擎 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Overfitting Detector 过拟合检验器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/OverfittingDetected 过拟合检测触发 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Parameter Optimization Result Analyzer 参数优化结果分析器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Parameter Robustness Tester 参数鲁棒性测试器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Parameter Sensitivity Analyzer 参数灵敏度分析器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Performance Regression Dependency Gate 性能回归依赖门禁 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Pipeline DAG Scheduler 管线DAG调度器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Pipeline DAG Scheduling Enhancer Pipeline DAG调度增强器 |  | design_only | design | 0 | 0 |
| ...ATION/Qlib Walk-Forward Simplified Version Integrator Qlib Walk-Forward简化版集成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Real-time DT Synchronizer 实时数字孪生同步器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Risk Simulator风控仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/SCI Calculator SCI计算器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Scenario Generator场景生成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/ScenarioGenerated 场景生成完成 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Semantic-Level Diff Understanding 语义级差异理解器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Sharpe Calculator Fixer Sharpe计算修正器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Simulation Profitability Evaluator 模拟盘盈利评估器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Simulation Result Analyzer 仿真结果分析器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/SimulationCompleted 仿真完成 |  | design_only | design | 0 | 0 |
| D-SIMULATION/SimulationResult Interface 仿真结果接口 |  | design_only | design | 0 | 0 |
| D-SIMULATION/SimulationScenario 仿真场景 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Strategy Decay Monitor Alerter 策略衰减监控告警器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Strategy Simulator策略仿真器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/StressTestResult 压力测试结果 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Technical Analysis Backtest Validator 技术分析回测验证器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Test Data Factory 测试数据工厂 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Test Environment Orchestrator 测试环境编排器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Test Impact Analyzer 测试影响分析器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Validation Automation Pipeline验证自动化流水线 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Walk-Forward Analyzer Walk-Forward分析 |  | design_only | design | 0 | 0 |
| D-SIMULATION/Walk-Forward Optimization Engine WFO引擎 |  | design_only | design | 0 | 0 |
| D-SIMULATION/empyrical Integrator empyrical集成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/quantstats Integrator quantstats集成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/vectorbt Vectorized Backtest Integrator vectorbt向量化回测集成器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/仿真域监控指标采集适配器 Adapter Monitoring Simulation |  | design_only | design | 0 | 0 |
| D-SIMULATION/仿真域配置热更新适配器 Adapter Simulation Config |  | design_only | design | 0 | 0 |
| D-SIMULATION/参数优化结果分析器 Analyzer Parameter |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测仿真 Walk-Forward回测 |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测异常诊断 Backtest |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测数据质量检查器 Data Quality Backtest |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测流水线执行记录查询与回放器 Execution Backtest Query |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测结果一键部署 Backtest |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测结果对比 Backtest |  | design_only | design | 0 | 0 |
| D-SIMULATION/回测缓存管理器 Backtest Management Cache |  | design_only | design | 0 | 0 |
| D-SIMULATION/指标计算NaN处理器 |  | design_only | design | 0 | 0 |
| D-SIMULATION/自动化过拟合检测 Automated Overfitting Detection |  | design_only | design | 0 | 0 |
| D-SIMULATION/集成测试任务 Integration Task |  | design_only | design | 0 | 0 |
| D-SIMULATION/验收标准自动化测试与判定器 Acceptance Criteria Automated Testing and Judger |  | design_only | design | 0 | 0 |
| src/zephyr/simulation/ | MOD-SIMULATION | design_only | design | 0 | 0 |
| src/zephyr/simulation/__init__.py | MOD-L13-001 | draft | prototype | 10 | 0 |
| src/zephyr/simulation/__init___from_resear.py | MOD-SIMULATION | draft | prototype | 0 | 3 |
| src/zephyr/simulation/_extensions/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/simulation/api/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/simulation/backtest_base.py | MOD-L09-001 | draft | production | 4 | 0 |
| src/zephyr/simulation/backtest_base_from_resear.py | MOD-L09-001 | draft | prototype | 0 | 1 |
| src/zephyr/simulation/core/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/simulation/default_backtest_engine.py | MOD-L09-001 | draft | production | 4 | 1 |
| src/zephyr/simulation/default_backtest_engine_from_resear.py | MOD-L09-001 | draft | prototype | 0 | 1 |
| src/zephyr/simulation/engine/ | MOD-SIMULATION | design_only | design | 0 | 0 |
| src/zephyr/simulation/implementations/__init__.py | MOD-L13-001 | draft | prototype | 1 | 1 |
| src/zephyr/simulation/implementations/__init___from_resear.py | MOD-L13-001 | draft | prototype | 0 | 1 |
| src/zephyr/simulation/implementations/default_experiment_pipeline.py | MOD-L13-001 | draft | production | 3 | 1 |
| src/zephyr/simulation/implementations/default_experiment_pipeline_from_resear.py | MOD-L13-001 | draft | prototype | 1 | 1 |
| src/zephyr/simulation/infrastructure/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/simulation/market_sim/ | MOD-SIMULATION | design_only | design | 0 | 0 |
| src/zephyr/simulation/models/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/simulation/pipeline_base.py | MOD-L13-001 | draft | production | 5 | 1 |
| src/zephyr/simulation/pipeline_base_from_resear.py | MOD-L13-001 | draft | prototype | 0 | 1 |
| src/zephyr/simulation/result/ | MOD-SIMULATION | design_only | design | 0 | 0 |
| src/zephyr/simulation/scenario/ | MOD-SIMULATION | design_only | design | 0 | 0 |
| src/zephyr/simulation/services/__init__.py | MOD-SIMULATION | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 19 | contract,event,data,config_depends |
| D-SIGNAL | 17 | data,config_depends,contract,event |
| D-SECURITY | 16 | contract,data,config_depends |
| D-INTEGRATION | 15 | contract,import_depends,data,config_depends,event |
| D-FACTOR | 14 | contract,event,data |
| D-MKT_DATA | 10 | domain_dependency,contract,event,data |
| D-INTELLIGENCE | 9 | data,event,contract |
| D-EX_CORE | 7 | contract,event,data |
| D-AUTONOMY_PERM | 7 | data,contract,config_depends |
| D-INFRA_RUNTIME | 6 | event,contract |
| D-PF_CORE | 4 | data,event,contract |
| D-DATA_ENG | 4 | data,contract,event |
| D-EX_SOR | 3 | data |
| D-TRADING | 2 | data,event |
| D-ML_TRAIN | 2 | data,event |
| D-KNOWLEDGE | 2 | event,contract |
| D-ML_SERVE | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 28 | test_depends,import_depends,event,contract,data |
| D-COMPLIANCE | 20 | config_depends,contract,data,event |
| D-AUTONOMY_CORE | 8 | contract,data,config_depends |
| D-OPS | 7 | contract,event,data |
| D-FRONTEND | 7 | data,contract,config_depends |
| D-INFRA_OPS | 6 | data,contract,event |
| D-PF_ALLOC | 3 | event,config_depends |
| D-INTELLIGENCE | 3 | import_depends |
| D-CROSS_ASSET | 3 | contract,data |
| D-REPORTING | 2 | data,event |
| D-ALT_DATA | 2 | contract,config_depends |
| D-SHARED | 1 | import_depends |
| D-DATA_SEC | 1 | data |
| D-BACKTEST | 1 | contract |

## 域内依赖图

详见 [d_simulation_dependency.mmd](d_simulation_dependency.mmd)
