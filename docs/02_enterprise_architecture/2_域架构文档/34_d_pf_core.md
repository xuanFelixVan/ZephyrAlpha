---
doc_type: domain_architecture_doc
title: D-PF_CORE 组合核心架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 34_d_pf_core 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 34 | Number | 34 |
| 域ID | D-PF_CORE | Domain ID | D-PF_CORE |
| 域名称 | 组合核心 | Domain Name | 组合核心 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 202 | Module Count | 202 |
| 域内依赖 | 152 | Internal Dependencies | 152 |
| 跨域入边 | 168 | Cross-domain Incoming | 168 |
| 跨域出边 | 153 | Cross-domain Outgoing | 153 |
| 设计态模块 | 183 | Design Modules | 183 |
| 原型态模块 | 7 | Prototype Modules | 7 |
| 生产态模块 | 6 | Production Modules | 6 |
| 容量 | 202/150 (超容) | Capacity | 202/150 (超容) |
| 描述 | 组合核心域。负责投资组合核心引擎，包括组合优化器、风险预算分配、基准跟踪、再平衡引擎。 | Description | 组合核心域。负责投资组合核心引擎，包括组合优化器、风险预算分配、基准跟踪、再平衡引擎。 |

## 模块清单 / Module List

共 202 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
|  | A-001 | design | active |  | A-001 | design | active |
|  | MS-02 | design | unbuilt |  | MS-02 | design | unbuilt |
|  | MT-02 | design | unbuilt |  | MT-02 | design | unbuilt |
|  | MS-04 | design | unbuilt |  | MS-04 | design | unbuilt |
|  | MT-03 | design | unbuilt |  | MT-03 | design | unbuilt |
|  | MS-03 | design | unbuilt |  | MS-03 | design | unbuilt |
|  | MS-05 | design | unbuilt |  | MS-05 | design | unbuilt |
|  | MT-05 | design | unbuilt |  | MT-05 | design | unbuilt |
|  | MT-04 | design | unbuilt |  | MT-04 | design | unbuilt |
|  | D-ALT-DATA-03 | design | unbuilt |  | D-ALT-DATA-03 | design | unbuilt |
|  | D-ALT-DATA-11 | design | unbuilt |  | D-ALT-DATA-11 | design | unbuilt |
|  | D-ALT-DATA-06 | design | unbuilt |  | D-ALT-DATA-06 | design | unbuilt |
|  | D-ALT-DATA-07 | design | unbuilt |  | D-ALT-DATA-07 | design | unbuilt |
|  | D-ALT-DATA-09 | design | unbuilt |  | D-ALT-DATA-09 | design | unbuilt |
|  | D-ALT-DATA-10 | design | unbuilt |  | D-ALT-DATA-10 | design | unbuilt |
|  | D-ALT-DATA-13 | design | unbuilt |  | D-ALT-DATA-13 | design | unbuilt |
|  | D-ALT-DATA-15 | design | unbuilt |  | D-ALT-DATA-15 | design | unbuilt |
|  | D-ALT-DATA-17 | design | unbuilt |  | D-ALT-DATA-17 | design | unbuilt |
|  | D-ALT-DATA-06扩展 | design | unbuilt |  | D-ALT-DATA-06扩展 | design | unbuilt |
|  | D-ALT-DATA-14 | design | unbuilt |  | D-ALT-DATA-14 | design | unbuilt |
|  | D-CROSS-ASSET-03 | design | unbuilt |  | D-CROSS-ASSET-03 | design | unbuilt |
|  | D-CROSS-ASSET-13 | design | unbuilt |  | D-CROSS-ASSET-13 | design | unbuilt |
|  | AP-07 | design | unbuilt |  | AP-07 | design | unbuilt |
|  | AP-09 | design | unbuilt |  | AP-09 | design | unbuilt |
|  | RK-10 | design | unbuilt |  | RK-10 | design | unbuilt |
|  | PA-01 | design | unbuilt |  | PA-01 | design | unbuilt |
| D-PF-CORE/19.2 Ensemble-HMM增强框架 | 19.2 Ensemble-HMM增强框架 | design | design_only | D-PF-CORE/19.2 Ensemble-HMM增强框架 | 19.2 Ensemble-HMM增强框架 | design | design_only |
| ...26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules | 26.5 逆势资金流与已有模块的联动 26.5 Contrarian Ca... | design | design_only | ...26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules | 26.5 逆势资金流与已有模块的联动 26.5 Contrarian Ca... | design | design_only |
| D-PF-CORE/28.5 与已有模块的联动 28.5 Linkage with Existing Modules | 28.5 与已有模块的联动 28.5 Linkage with Exist... | design | design_only | D-PF-CORE/28.5 与已有模块的联动 28.5 Linkage with Existing Modules | 28.5 与已有模块的联动 28.5 Linkage with Exist... | design | design_only |
| D-PF-CORE/31.3 高级协同检测（基于ESMA MABUM框架） | 31.3 高级协同检测（基于ESMA MABUM框架） | design | design_only | D-PF-CORE/31.3 高级协同检测（基于ESMA MABUM框架） | 31.3 高级协同检测（基于ESMA MABUM框架） | design | design_only |
| D-PF-CORE/A Share Trading Discipline A股交易纪律 | A Share Trading Discipline A股交易纪律 | design | design_only | D-PF-CORE/A Share Trading Discipline A股交易纪律 | A Share Trading Discipline A股交易纪律 | design | design_only |
| D-PF-CORE/Auto Down-Weight 自动降权 | Auto Down-Weight 自动降权 | design | design_only | D-PF-CORE/Auto Down-Weight 自动降权 | Auto Down-Weight 自动降权 | design | design_only |
| D-PF-CORE/Automatic Strategy Discovery 自动策略发现 | Automatic Strategy Discovery 自动策略发现 | design | design_only | D-PF-CORE/Automatic Strategy Discovery 自动策略发现 | Automatic Strategy Discovery 自动策略发现 | design | design_only |
| D-PF-CORE/Benchmark Manager 基准管理器 | Benchmark Manager 基准管理器 | design | design_only | D-PF-CORE/Benchmark Manager 基准管理器 | Benchmark Manager 基准管理器 | design | design_only |
| D-PF-CORE/BuyDecided 买入决策事件 | BuyDecided 买入决策事件 | design | design_only | D-PF-CORE/BuyDecided 买入决策事件 | BuyDecided 买入决策事件 | design | design_only |
| D-PF-CORE/BuyDecision 买入决策契约 | BuyDecision 买入决策契约 | design | design_only | D-PF-CORE/BuyDecision 买入决策契约 | BuyDecision 买入决策契约 | design | design_only |
| D-PF-CORE/C-006：策略工厂 | C-006：策略工厂 | design | design_only | D-PF-CORE/C-006：策略工厂 | C-006：策略工厂 | design | design_only |
| D-PF-CORE/C-016：知识图谱引擎 | C-016：知识图谱引擎 | design | design_only | D-PF-CORE/C-016：知识图谱引擎 | C-016：知识图谱引擎 | design | design_only |
| D-PF-CORE/C-027：因子工厂（P0） | C-027：因子工厂（P0） | design | design_only | D-PF-CORE/C-027：因子工厂（P0） | C-027：因子工厂（P0） | design | design_only |
| D-PF-CORE/C-028：信号工厂（P0） | C-028：信号工厂（P0） | design | design_only | D-PF-CORE/C-028：信号工厂（P0） | C-028：信号工厂（P0） | design | design_only |
| D-PF-CORE/C-033：过拟合系统性防护 | C-033：过拟合系统性防护 | design | design_only | D-PF-CORE/C-033：过拟合系统性防护 | C-033：过拟合系统性防护 | design | design_only |
| D-PF-CORE/C-040：系统性压力测试 | C-040：系统性压力测试 | design | design_only | D-PF-CORE/C-040：系统性压力测试 | C-040：系统性压力测试 | design | design_only |
| D-PF-CORE/C-047：仓位管理唯一裁决中心 | C-047：仓位管理唯一裁决中心 | design | design_only | D-PF-CORE/C-047：仓位管理唯一裁决中心 | C-047：仓位管理唯一裁决中心 | design | design_only |
| D-PF-CORE/CTR-P1-006 StrategyLifecycleEvent CTR-P1-006 StrategyLifecycleEvent契约 | CTR-P1-006 StrategyLifecycleEvent CTR... | design | design_only | D-PF-CORE/CTR-P1-006 StrategyLifecycleEvent CTR-P1-006 StrategyLifecycleEvent契约 | CTR-P1-006 StrategyLifecycleEvent CTR... | design | design_only |
| D-PF-CORE/Carbon Footprint Calculator碳足迹计算器 | Carbon Footprint Calculator碳足迹计算器 | design | design_only | D-PF-CORE/Carbon Footprint Calculator碳足迹计算器 | Carbon Footprint Calculator碳足迹计算器 | design | design_only |
| D-PF-CORE/Carbon Footprint 碳足迹 | Carbon Footprint 碳足迹 | design | design_only | D-PF-CORE/Carbon Footprint 碳足迹 | Carbon Footprint 碳足迹 | design | design_only |
| D-PF-CORE/Cash Flow Manager资金流管理器 | Cash Flow Manager资金流管理器 | design | design_only | D-PF-CORE/Cash Flow Manager资金流管理器 | Cash Flow Manager资金流管理器 | design | design_only |
| D-PF-CORE/Constraint Solver约束求解器 | Constraint Solver约束求解器 | design | design_only | D-PF-CORE/Constraint Solver约束求解器 | Constraint Solver约束求解器 | design | design_only |
| D-PF-CORE/Decision Orchestrator 决策编排器 | Decision Orchestrator 决策编排器 | design | design_only | D-PF-CORE/Decision Orchestrator 决策编排器 | Decision Orchestrator 决策编排器 | design | design_only |
| D-PF-CORE/Decision Orchestrator 决策编排器——缺失功能模块 | Decision Orchestrator 决策编排器——缺失功能模块 | design | design_only | D-PF-CORE/Decision Orchestrator 决策编排器——缺失功能模块 | Decision Orchestrator 决策编排器——缺失功能模块 | design | design_only |
| D-PF-CORE/E-PF-01 PortfolioRebalanced E-PF-01 PortfolioRebalanced事件 | E-PF-01 PortfolioRebalanced E-PF-01 P... | design | design_only | D-PF-CORE/E-PF-01 PortfolioRebalanced E-PF-01 PortfolioRebalanced事件 | E-PF-01 PortfolioRebalanced E-PF-01 P... | design | design_only |
| D-PF-CORE/E-SIM-01 SimulationCompleted 仿真完成 | E-SIM-01 SimulationCompleted 仿真完成 | design | design_only | D-PF-CORE/E-SIM-01 SimulationCompleted 仿真完成 | E-SIM-01 SimulationCompleted 仿真完成 | design | design_only |
| D-PF-CORE/Event Bus §2.2 事件总线事件分类 | Event Bus §2.2 事件总线事件分类 | design | design_only | D-PF-CORE/Event Bus §2.2 事件总线事件分类 | Event Bus §2.2 事件总线事件分类 | design | design_only |
| D-PF-CORE/Event Sourcing 事件溯源 | Event Sourcing 事件溯源 | design | design_only | D-PF-CORE/Event Sourcing 事件溯源 | Event Sourcing 事件溯源 | design | design_only |
| D-PF-CORE/Execution to L5 Closed Loop 执行→L5闭环优化 | Execution to L5 Closed Loop 执行→L5闭环优化 | design | design_only | D-PF-CORE/Execution to L5 Closed Loop 执行→L5闭环优化 | Execution to L5 Closed Loop 执行→L5闭环优化 | design | design_only |
| D-PF-CORE/Explainability 决策可解释性与溯源 | Explainability 决策可解释性与溯源 | design | design_only | D-PF-CORE/Explainability 决策可解释性与溯源 | Explainability 决策可解释性与溯源 | design | design_only |
| D-PF-CORE/Factor Direct Layer 因子直通层 | Factor Direct Layer 因子直通层 | design | design_only | D-PF-CORE/Factor Direct Layer 因子直通层 | Factor Direct Layer 因子直通层 | design | design_only |
| D-PF-CORE/Factor Exposure Manager因子敞口管理器 | Factor Exposure Manager因子敞口管理器 | design | design_only | D-PF-CORE/Factor Exposure Manager因子敞口管理器 | Factor Exposure Manager因子敞口管理器 | design | design_only |
| D-PF-CORE/Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 | Factor/Strategy Crowding Deep Detecti... | design | design_only | D-PF-CORE/Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 | Factor/Strategy Crowding Deep Detecti... | design | design_only |
| D-PF-CORE/Governance Domain §30.6 运维安全治理域缺失模块 | Governance Domain §30.6 运维安全治理域缺失模块 | design | design_only | D-PF-CORE/Governance Domain §30.6 运维安全治理域缺失模块 | Governance Domain §30.6 运维安全治理域缺失模块 | design | design_only |
| D-PF-CORE/HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 | HRP/Black-Litterman Portfolio Optimiz... | design | design_only | D-PF-CORE/HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 | HRP/Black-Litterman Portfolio Optimiz... | design | design_only |
| D-PF-CORE/HoldDecided 持有决策事件 | HoldDecided 持有决策事件 | design | design_only | D-PF-CORE/HoldDecided 持有决策事件 | HoldDecided 持有决策事件 | design | design_only |
| D-PF-CORE/L2 to L3 Strategy Decision L2→L3策略决策 | L2 to L3 Strategy Decision L2→L3策略决策 | design | design_only | D-PF-CORE/L2 to L3 Strategy Decision L2→L3策略决策 | L2 to L3 Strategy Decision L2→L3策略决策 | design | design_only |
| D-PF-CORE/L3-L6 决策/仓位/风控/执行/闭环数据 | L3-L6 决策/仓位/风控/执行/闭环数据 | design | design_only | D-PF-CORE/L3-L6 决策/仓位/风控/执行/闭环数据 | L3-L6 决策/仓位/风控/执行/闭环数据 | design | design_only |
| D-PF-CORE/LLM Evolutionary Strategy Search LLM进化式策略搜索 | LLM Evolutionary Strategy Search LLM进... | design | design_only | D-PF-CORE/LLM Evolutionary Strategy Search LLM进化式策略搜索 | LLM Evolutionary Strategy Search LLM进... | design | design_only |
| D-PF-CORE/Liquidity Estimator 流动性估算器 | Liquidity Estimator 流动性估算器 | design | design_only | D-PF-CORE/Liquidity Estimator 流动性估算器 | Liquidity Estimator 流动性估算器 | design | design_only |
| D-PF-CORE/Liquidity Estimator流动性估计器 | Liquidity Estimator流动性估计器 | design | design_only | D-PF-CORE/Liquidity Estimator流动性估计器 | Liquidity Estimator流动性估计器 | design | design_only |
| D-PF-CORE/MTF Four-Track Fusion 四轨融合器 | MTF Four-Track Fusion 四轨融合器 | design | design_only | D-PF-CORE/MTF Four-Track Fusion 四轨融合器 | MTF Four-Track Fusion 四轨融合器 | design | design_only |
| D-PF-CORE/Multi-Objective Optimizer多目标优化器 | Multi-Objective Optimizer多目标优化器 | design | design_only | D-PF-CORE/Multi-Objective Optimizer多目标优化器 | Multi-Objective Optimizer多目标优化器 | design | design_only |
| D-PF-CORE/Multi-Scenario Response & Contingency 多情景对策与预案 | Multi-Scenario Response & Contingency... | design | design_only | D-PF-CORE/Multi-Scenario Response & Contingency 多情景对策与预案 | Multi-Scenario Response & Contingency... | design | design_only |
| D-PF-CORE/Multi-Strategy Allocator 多策略分配器 | Multi-Strategy Allocator 多策略分配器 | design | design_only | D-PF-CORE/Multi-Strategy Allocator 多策略分配器 | Multi-Strategy Allocator 多策略分配器 | design | design_only |
| D-PF-CORE/Multi-Strategy Resonance Fusion 多策略共振融合层 | Multi-Strategy Resonance Fusion 多策略共振融合层 | design | design_only | D-PF-CORE/Multi-Strategy Resonance Fusion 多策略共振融合层 | Multi-Strategy Resonance Fusion 多策略共振融合层 | design | design_only |
| D-PF-CORE/Multi-Track Fusion 四轨融合器 | Multi-Track Fusion 四轨融合器 | design | design_only | D-PF-CORE/Multi-Track Fusion 四轨融合器 | Multi-Track Fusion 四轨融合器 | design | design_only |
| D-PF-CORE/P0 模块明细 | P0 模块明细 | design | design_only | D-PF-CORE/P0 模块明细 | P0 模块明细 | design | design_only |
| D-PF-CORE/P1 模块分类汇总（14个） | P1 模块分类汇总（14个） | design | design_only | D-PF-CORE/P1 模块分类汇总（14个） | P1 模块分类汇总（14个） | design | design_only |
| D-PF-CORE/P1 模块分类汇总（5个） | P1 模块分类汇总（5个） | design | design_only | D-PF-CORE/P1 模块分类汇总（5个） | P1 模块分类汇总（5个） | design | design_only |
| D-PF-CORE/P1 模块分类汇总（7个） | P1 模块分类汇总（7个） | design | design_only | D-PF-CORE/P1 模块分类汇总（7个） | P1 模块分类汇总（7个） | design | design_only |
| D-PF-CORE/P1 模块分类汇总（85个） | P1 模块分类汇总（85个） | design | design_only | D-PF-CORE/P1 模块分类汇总（85个） | P1 模块分类汇总（85个） | design | design_only |
| D-PF-CORE/P1 模块分类汇总（92个） | P1 模块分类汇总（92个） | design | design_only | D-PF-CORE/P1 模块分类汇总（92个） | P1 模块分类汇总（92个） | design | design_only |
| D-PF-CORE/P1 模块分类汇总（99个） | P1 模块分类汇总（99个） | design | design_only | D-PF-CORE/P1 模块分类汇总（99个） | P1 模块分类汇总（99个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（11个） | P2 模块分类汇总（11个） | design | design_only | D-PF-CORE/P2 模块分类汇总（11个） | P2 模块分类汇总（11个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（17个） | P2 模块分类汇总（17个） | design | design_only | D-PF-CORE/P2 模块分类汇总（17个） | P2 模块分类汇总（17个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（29个） | P2 模块分类汇总（29个） | design | design_only | D-PF-CORE/P2 模块分类汇总（29个） | P2 模块分类汇总（29个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（30个） | P2 模块分类汇总（30个） | design | design_only | D-PF-CORE/P2 模块分类汇总（30个） | P2 模块分类汇总（30个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（62个） | P2 模块分类汇总（62个） | design | design_only | D-PF-CORE/P2 模块分类汇总（62个） | P2 模块分类汇总（62个） | design | design_only |
| D-PF-CORE/P2 模块分类汇总（7个） | P2 模块分类汇总（7个） | design | design_only | D-PF-CORE/P2 模块分类汇总（7个） | P2 模块分类汇总（7个） | design | design_only |
| D-PF-CORE/P3 模块分类汇总（1个） | P3 模块分类汇总（1个） | design | design_only | D-PF-CORE/P3 模块分类汇总（1个） | P3 模块分类汇总（1个） | design | design_only |
| D-PF-CORE/P3 模块分类汇总（3个） | P3 模块分类汇总（3个） | design | design_only | D-PF-CORE/P3 模块分类汇总（3个） | P3 模块分类汇总（3个） | design | design_only |
| D-PF-CORE/Percentage 百分比 | Percentage 百分比 | design | design_only | D-PF-CORE/Percentage 百分比 | Percentage 百分比 | design | design_only |
| D-PF-CORE/Performance Attribution Engine绩效归因引擎 | Performance Attribution Engine绩效归因引擎 | design | design_only | D-PF-CORE/Performance Attribution Engine绩效归因引擎 | Performance Attribution Engine绩效归因引擎 | design | design_only |
| D-PF-CORE/Portfolio Benchmark Manager组合基准管理器 | Portfolio Benchmark Manager组合基准管理器 | design | design_only | D-PF-CORE/Portfolio Benchmark Manager组合基准管理器 | Portfolio Benchmark Manager组合基准管理器 | design | design_only |
| D-PF-CORE/Portfolio Construction Engine 组合构建引擎 | Portfolio Construction Engine 组合构建引擎 | design | design_only | D-PF-CORE/Portfolio Construction Engine 组合构建引擎 | Portfolio Construction Engine 组合构建引擎 | design | design_only |
| D-PF-CORE/Portfolio Core 组合核心 | Portfolio Core 组合核心 | design | design_only | D-PF-CORE/Portfolio Core 组合核心 | Portfolio Core 组合核心 | design | design_only |
| D-PF-CORE/Portfolio Drift Monitor组合漂移监控器 | Portfolio Drift Monitor组合漂移监控器 | design | design_only | D-PF-CORE/Portfolio Drift Monitor组合漂移监控器 | Portfolio Drift Monitor组合漂移监控器 | design | design_only |
| D-PF-CORE/Portfolio Optimization Engine 组合优化引擎 | Portfolio Optimization Engine 组合优化引擎 | design | design_only | D-PF-CORE/Portfolio Optimization Engine 组合优化引擎 | Portfolio Optimization Engine 组合优化引擎 | design | design_only |
| D-PF-CORE/Portfolio Optimizer组合优化器 | Portfolio Optimizer组合优化器 | design | design_only | D-PF-CORE/Portfolio Optimizer组合优化器 | Portfolio Optimizer组合优化器 | design | design_only |
| D-PF-CORE/Portfolio Rebalancer 组合再平衡器 | Portfolio Rebalancer 组合再平衡器 | design | design_only | D-PF-CORE/Portfolio Rebalancer 组合再平衡器 | Portfolio Rebalancer 组合再平衡器 | design | design_only |
| D-PF-CORE/Portfolio Risk Decomposer 组合风险分解器 | Portfolio Risk Decomposer 组合风险分解器 | design | design_only | D-PF-CORE/Portfolio Risk Decomposer 组合风险分解器 | Portfolio Risk Decomposer 组合风险分解器 | design | design_only |
| D-PF-CORE/Portfolio State 组合状态检查点 | Portfolio State 组合状态检查点 | design | design_only | D-PF-CORE/Portfolio State 组合状态检查点 | Portfolio State 组合状态检查点 | design | design_only |
| D-PF-CORE/Portfolio Stress Tester组合压力测试器 | Portfolio Stress Tester组合压力测试器 | design | design_only | D-PF-CORE/Portfolio Stress Tester组合压力测试器 | Portfolio Stress Tester组合压力测试器 | design | design_only |
| D-PF-CORE/Portfolio 组合 | Portfolio 组合 | design | design_only | D-PF-CORE/Portfolio 组合 | Portfolio 组合 | design | design_only |
| D-PF-CORE/Portfolio 组合聚合根 | Portfolio 组合聚合根 | design | design_only | D-PF-CORE/Portfolio 组合聚合根 | Portfolio 组合聚合根 | design | design_only |
| D-PF-CORE/PortfolioRebalanced 组合已再平衡 | PortfolioRebalanced 组合已再平衡 | design | design_only | D-PF-CORE/PortfolioRebalanced 组合已再平衡 | PortfolioRebalanced 组合已再平衡 | design | design_only |
| D-PF-CORE/Rebalance Cost Analyzer再平衡成本分析器 | Rebalance Cost Analyzer再平衡成本分析器 | design | design_only | D-PF-CORE/Rebalance Cost Analyzer再平衡成本分析器 | Rebalance Cost Analyzer再平衡成本分析器 | design | design_only |
| D-PF-CORE/Rebalance Full Flow Saga 再平衡全流程Saga | Rebalance Full Flow Saga 再平衡全流程Saga | design | design_only | D-PF-CORE/Rebalance Full Flow Saga 再平衡全流程Saga | Rebalance Full Flow Saga 再平衡全流程Saga | design | design_only |
| D-PF-CORE/Rebalance Scheduler再平衡调度器 | Rebalance Scheduler再平衡调度器 | design | design_only | D-PF-CORE/Rebalance Scheduler再平衡调度器 | Rebalance Scheduler再平衡调度器 | design | design_only |
| D-PF-CORE/Risk Parity Engine风险平价引擎 | Risk Parity Engine风险平价引擎 | design | design_only | D-PF-CORE/Risk Parity Engine风险平价引擎 | Risk Parity Engine风险平价引擎 | design | design_only |
| D-PF-CORE/SHAP LIME Dual Attribution SHAP LIME双归因 | SHAP LIME Dual Attribution SHAP LIME双归因 | design | design_only | D-PF-CORE/SHAP LIME Dual Attribution SHAP LIME双归因 | SHAP LIME Dual Attribution SHAP LIME双归因 | design | design_only |
| D-PF-CORE/Sector Exposure Manager行业敞口管理器 | Sector Exposure Manager行业敞口管理器 | design | design_only | D-PF-CORE/Sector Exposure Manager行业敞口管理器 | Sector Exposure Manager行业敞口管理器 | design | design_only |
| D-PF-CORE/Sell Decision Engine 卖出决策引擎 | Sell Decision Engine 卖出决策引擎 | design | design_only | D-PF-CORE/Sell Decision Engine 卖出决策引擎 | Sell Decision Engine 卖出决策引擎 | design | design_only |
| D-PF-CORE/Signal Factory §4.1 信号工厂九大子阶段 | Signal Factory §4.1 信号工厂九大子阶段 | design | design_only | D-PF-CORE/Signal Factory §4.1 信号工厂九大子阶段 | Signal Factory §4.1 信号工厂九大子阶段 | design | design_only |
| D-PF-CORE/Strategy Capacity Estimator策略容量估计器 | Strategy Capacity Estimator策略容量估计器 | design | design_only | D-PF-CORE/Strategy Capacity Estimator策略容量估计器 | Strategy Capacity Estimator策略容量估计器 | design | design_only |
| D-PF-CORE/Strategy Capacity Modeling 策略容量建模 | Strategy Capacity Modeling 策略容量建模 | design | design_only | D-PF-CORE/Strategy Capacity Modeling 策略容量建模 | Strategy Capacity Modeling 策略容量建模 | design | design_only |
| D-PF-CORE/Strategy Engine策略引擎 | Strategy Engine策略引擎 | design | design_only | D-PF-CORE/Strategy Engine策略引擎 | Strategy Engine策略引擎 | design | design_only |
| D-PF-CORE/Strategy Factory 策略工厂 | Strategy Factory 策略工厂 | design | design_only | D-PF-CORE/Strategy Factory 策略工厂 | Strategy Factory 策略工厂 | design | design_only |
| D-PF-CORE/Strategy Portfolio 策略组合 | Strategy Portfolio 策略组合 | design | design_only | D-PF-CORE/Strategy Portfolio 策略组合 | Strategy Portfolio 策略组合 | design | design_only |
| D-PF-CORE/Strategy Signal Router 策略信号路由器 | Strategy Signal Router 策略信号路由器 | design | design_only | D-PF-CORE/Strategy Signal Router 策略信号路由器 | Strategy Signal Router 策略信号路由器 | design | design_only |
| D-PF-CORE/StrategyLifecycleEvent 策略生命周期事件 | StrategyLifecycleEvent 策略生命周期事件 | design | design_only | D-PF-CORE/StrategyLifecycleEvent 策略生命周期事件 | StrategyLifecycleEvent 策略生命周期事件 | design | design_only |
| D-PF-CORE/StrategyRegistry 策略注册表 | StrategyRegistry 策略注册表 | design | design_only | D-PF-CORE/StrategyRegistry 策略注册表 | StrategyRegistry 策略注册表 | design | design_only |
| D-PF-CORE/Tax Loss Harvester税损收割器 | Tax Loss Harvester税损收割器 | design | design_only | D-PF-CORE/Tax Loss Harvester税损收割器 | Tax Loss Harvester税损收割器 | design | design_only |
| D-PF-CORE/XS-EXT 模块分类汇总（5个） | XS-EXT 模块分类汇总（5个） | design | design_only | D-PF-CORE/XS-EXT 模块分类汇总（5个） | XS-EXT 模块分类汇总（5个） | design | design_only |
| D-PF-CORE/§12.4 C-033 过拟合系统性防护 | §12.4 C-033 过拟合系统性防护 | design | design_only | D-PF-CORE/§12.4 C-033 过拟合系统性防护 | §12.4 C-033 过拟合系统性防护 | design | design_only |
| D-PF-CORE/§2.1 多源数据接入与分层存储架构 Data Ingestion Storage | §2.1 多源数据接入与分层存储架构 Data Ingestion Sto... | design | design_only | D-PF-CORE/§2.1 多源数据接入与分层存储架构 Data Ingestion Storage | §2.1 多源数据接入与分层存储架构 Data Ingestion Sto... | design | design_only |
| D-PF-CORE/§20.8 方法论约束八：训练-服务一致性(Feature Store) | §20.8 方法论约束八：训练-服务一致性(Feature Store) | design | design_only | D-PF-CORE/§20.8 方法论约束八：训练-服务一致性(Feature Store) | §20.8 方法论约束八：训练-服务一致性(Feature Store) | design | design_only |
| D-PF-CORE/§24 外部系统交互引用 External | §24 外部系统交互引用 External | design | design_only | D-PF-CORE/§24 外部系统交互引用 External | §24 外部系统交互引用 External | design | design_only |
| D-PF-CORE/§24.1 外部系统交互矩阵 External | §24.1 外部系统交互矩阵 External | design | design_only | D-PF-CORE/§24.1 外部系统交互矩阵 External | §24.1 外部系统交互矩阵 External | design | design_only |
| D-PF-CORE/§27 系统级成功指标引用 | §27 系统级成功指标引用 | design | design_only | D-PF-CORE/§27 系统级成功指标引用 | §27 系统级成功指标引用 | design | design_only |
| D-PF-CORE/§29.1 多进程隔离与运行时架构（→A9运维架构） | §29.1 多进程隔离与运行时架构（→A9运维架构） | design | design_only | D-PF-CORE/§29.1 多进程隔离与运行时架构（→A9运维架构） | §29.1 多进程隔离与运行时架构（→A9运维架构） | design | design_only |
| D-PF-CORE/§29.10 盘中即时反应决策引擎 Engine | §29.10 盘中即时反应决策引擎 Engine | design | design_only | D-PF-CORE/§29.10 盘中即时反应决策引擎 Engine | §29.10 盘中即时反应决策引擎 Engine | design | design_only |
| D-PF-CORE/§29.2 特征存储 (Feature Store) | §29.2 特征存储 (Feature Store) | design | design_only | D-PF-CORE/§29.2 特征存储 (Feature Store) | §29.2 特征存储 (Feature Store) | design | design_only |
| D-PF-CORE/§29.21 学习系统桥接声明 | §29.21 学习系统桥接声明 | design | design_only | D-PF-CORE/§29.21 学习系统桥接声明 | §29.21 学习系统桥接声明 | design | design_only |
| D-PF-CORE/§29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | design | design_only | D-PF-CORE/§29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | design | design_only |
| D-PF-CORE/§29.35 持续学习抗遗忘框架（v6.0新增） | §29.35 持续学习抗遗忘框架（v6.0新增） | design | design_only | D-PF-CORE/§29.35 持续学习抗遗忘框架（v6.0新增） | §29.35 持续学习抗遗忘框架（v6.0新增） | design | design_only |
| D-PF-CORE/§29.4 时序数据库与分层存储架构（→A3数据架构） | §29.4 时序数据库与分层存储架构（→A3数据架构） | design | design_only | D-PF-CORE/§29.4 时序数据库与分层存储架构（→A3数据架构） | §29.4 时序数据库与分层存储架构（→A3数据架构） | design | design_only |
| D-PF-CORE/§30 场外草稿区缺失模块补充 | §30 场外草稿区缺失模块补充 | design | design_only | D-PF-CORE/§30 场外草稿区缺失模块补充 | §30 场外草稿区缺失模块补充 | design | design_only |
| D-PF-CORE/§30.1 核心价值链域缺失模块 Core | §30.1 核心价值链域缺失模块 Core | design | design_only | D-PF-CORE/§30.1 核心价值链域缺失模块 Core | §30.1 核心价值链域缺失模块 Core | design | design_only |
| D-PF-CORE/§30.1.3 D-PF-CORE 组合核心域（18个模块） | §30.1.3 D-PF-CORE 组合核心域（18个模块） | design | design_only | D-PF-CORE/§30.1.3 D-PF-CORE 组合核心域（18个模块） | §30.1.3 D-PF-CORE 组合核心域（18个模块） | design | design_only |
| D-PF-CORE/§30.2 增强与扩展域缺失模块 | §30.2 增强与扩展域缺失模块 | design | design_only | D-PF-CORE/§30.2 增强与扩展域缺失模块 | §30.2 增强与扩展域缺失模块 | design | design_only |
| D-PF-CORE/§30.3 核心交易链域缺失模块 Core | §30.3 核心交易链域缺失模块 Core | design | design_only | D-PF-CORE/§30.3 核心交易链域缺失模块 Core | §30.3 核心交易链域缺失模块 Core | design | design_only |
| D-PF-CORE/§30.4 ML与数据工程域缺失模块 | §30.4 ML与数据工程域缺失模块 | design | design_only | D-PF-CORE/§30.4 ML与数据工程域缺失模块 | §30.4 ML与数据工程域缺失模块 | design | design_only |
| D-PF-CORE/§30.5 自治与基础设施域缺失模块 Base | §30.5 自治与基础设施域缺失模块 Base | design | design_only | D-PF-CORE/§30.5 自治与基础设施域缺失模块 Base | §30.5 自治与基础设施域缺失模块 Base | design | design_only |
| D-PF-CORE/§4.4 信号聚合器架构 Signal Aggregator | §4.4 信号聚合器架构 Signal Aggregator | design | design_only | D-PF-CORE/§4.4 信号聚合器架构 Signal Aggregator | §4.4 信号聚合器架构 Signal Aggregator | design | design_only |
| D-PF-CORE/§8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | design | design_only | D-PF-CORE/§8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | design | design_only |
| D-PF-CORE/§8.5 组合优化引擎 Portfolio Engine | §8.5 组合优化引擎 Portfolio Engine | design | design_only | D-PF-CORE/§8.5 组合优化引擎 Portfolio Engine | §8.5 组合优化引擎 Portfolio Engine | design | design_only |
| D-PF-CORE/❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution | ❌不能建模块门禁条件分布 Cannot Build Module Gate... | design | design_only | D-PF-CORE/❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution | ❌不能建模块门禁条件分布 Cannot Build Module Gate... | design | design_only |
| D-PF-CORE/再平衡全流程Saga Rebalancing Saga | 再平衡全流程Saga Rebalancing Saga | design | design_only | D-PF-CORE/再平衡全流程Saga Rebalancing Saga | 再平衡全流程Saga Rebalancing Saga | design | design_only |
| D-PF-CORE/决策四：模型/策略漂移检测框架 Strategy Model | 决策四：模型/策略漂移检测框架 Strategy Model | design | design_only | D-PF-CORE/决策四：模型/策略漂移检测框架 Strategy Model | 决策四：模型/策略漂移检测框架 Strategy Model | design | design_only |
| D-PF-CORE/多账户多策略 Strategy | 多账户多策略 Strategy | design | design_only | D-PF-CORE/多账户多策略 Strategy | 多账户多策略 Strategy | design | design_only |
| D-PF-CORE/模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | 模块10 动量领导因子与涨停板生态模型（Momentum Leadersh... | design | design_only | D-PF-CORE/模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | 模块10 动量领导因子与涨停板生态模型（Momentum Leadersh... | design | design_only |
| D-PF-CORE/模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | 模块11 动量层级与板块持续性模型（Momentum Hierarchy ... | design | design_only | D-PF-CORE/模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | 模块11 动量层级与板块持续性模型（Momentum Hierarchy ... | design | design_only |
| D-PF-CORE/模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow M... | design | design_only | D-PF-CORE/模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow M... | design | design_only |
| D-PF-CORE/模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | 模块15 假突破与诱多检测模型（False Breakout & Bull... | design | design_only | D-PF-CORE/模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | 模块15 假突破与诱多检测模型（False Breakout & Bull... | design | design_only |
| D-PF-CORE/模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | 模块16 情绪-价格背离指数模型（Sentiment-Price Dive... | design | design_only | D-PF-CORE/模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | 模块16 情绪-价格背离指数模型（Sentiment-Price Dive... | design | design_only |
| D-PF-CORE/模块19 市场体制转换模型（Regime-Switching Model） | 模块19 市场体制转换模型（Regime-Switching Model） | design | design_only | D-PF-CORE/模块19 市场体制转换模型（Regime-Switching Model） | 模块19 市场体制转换模型（Regime-Switching Model） | design | design_only |
| D-PF-CORE/模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | 模块23 量能体制自适应策略模型（Volume Regime Adapti... | design | design_only | D-PF-CORE/模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | 模块23 量能体制自适应策略模型（Volume Regime Adapti... | design | design_only |
| D-PF-CORE/模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | 模块24 核心-卫星仓位管理模型（Core-Satellite Posit... | design | design_only | D-PF-CORE/模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | 模块24 核心-卫星仓位管理模型（Core-Satellite Posit... | design | design_only |
| ...E/模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification | 模块26 3秒级逆势资金流识别模块 Module 26 3-Second ... | design | design_only | ...E/模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification | 模块26 3秒级逆势资金流识别模块 Module 26 3-Second ... | design | design_only |
| ...码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification | 模块27 主力假动作与筹码派发识别模块 Module 27 Main Fo... | design | design_only | ...码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification | 模块27 主力假动作与筹码派发识别模块 Module 27 Main Fo... | design | design_only |
| ...8 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) | 模块28 利好落地变利空（预期透支）模块 Module 28 Good N... | design | design_only | ...8 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) | 模块28 利好落地变利空（预期透支）模块 Module 28 Good N... | design | design_only |
| ...-CORE/模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold | 模块29 次日上涨概率统一门槛模块 Module 29 Next-Day ... | design | design_only | ...-CORE/模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold | 模块29 次日上涨概率统一门槛模块 Module 29 Next-Day ... | design | design_only |
| D-PF-CORE/模块3 缺口回补概率模型（Gap Fill Probability Model） | 模块3 缺口回补概率模型（Gap Fill Probability Model） | design | design_only | D-PF-CORE/模块3 缺口回补概率模型（Gap Fill Probability Model） | 模块3 缺口回补概率模型（Gap Fill Probability Model） | design | design_only |
| D-PF-CORE/模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | 模块31 协同交易行为检测模型（Coordinated Trading D... | design | design_only | D-PF-CORE/模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | 模块31 协同交易行为检测模型（Coordinated Trading D... | design | design_only |
| D-PF-CORE/模块32 市场风格体制识别模型（Market Style Regime Identification Model） | 模块32 市场风格体制识别模型（Market Style Regime I... | design | design_only | D-PF-CORE/模块32 市场风格体制识别模型（Market Style Regime Identification Model） | 模块32 市场风格体制识别模型（Market Style Regime I... | design | design_only |
| D-PF-CORE/模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | 模块34 异质参与者互动模型（Heterogeneous Agent In... | design | design_only | D-PF-CORE/模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | 模块34 异质参与者互动模型（Heterogeneous Agent In... | design | design_only |
| D-PF-CORE/模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | 模块39 多因子选股评分模型（Multi-Factor Stock Sel... | design | design_only | D-PF-CORE/模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） | 模块39 多因子选股评分模型（Multi-Factor Stock Sel... | design | design_only |
| D-PF-CORE/模块4 逼空行情检测模型（Short Squeeze Detection Model） | 模块4 逼空行情检测模型（Short Squeeze Detection ... | design | design_only | D-PF-CORE/模块4 逼空行情检测模型（Short Squeeze Detection Model） | 模块4 逼空行情检测模型（Short Squeeze Detection ... | design | design_only |
| D-PF-CORE/模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | 模块51 波动率压缩与突破模型（Volatility Compressio... | design | design_only | D-PF-CORE/模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | 模块51 波动率压缩与突破模型（Volatility Compressio... | design | design_only |
| ...更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) | 模块52 汇总：缺失模块与建议归属层映射（更新版） Module 52 S... | design | design_only | ...更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) | 模块52 汇总：缺失模块与建议归属层映射（更新版） Module 52 S... | design | design_only |
| D-PF-CORE/模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） | 模块57 多因子叠加择时模型（Multi-Factor Overlay T... | design | design_only | D-PF-CORE/模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） | 模块57 多因子叠加择时模型（Multi-Factor Overlay T... | design | design_only |
| .../模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 ... | design | design_only | .../模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 ... | design | design_only |
| ...架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture | 模块58 附录：已有架构覆盖的功能（不重复列出） Module 58 Ap... | design | design_only | ...架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture | 模块58 附录：已有架构覆盖的功能（不重复列出） Module 58 Ap... | design | design_only |
| D-PF-CORE/模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | 模块7 多指标背离检测模型（Multi-Indicator Diverge... | design | design_only | D-PF-CORE/模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | 模块7 多指标背离检测模型（Multi-Indicator Diverge... | design | design_only |
| D-PF-CORE/模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | 模块8 板块资金流再配置模型（Sector Flow Reallocati... | design | design_only | D-PF-CORE/模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | 模块8 板块资金流再配置模型（Sector Flow Reallocati... | design | design_only |
| D-PF-CORE/裁定15: FinRL-X模块化交易基础设施 | 裁定15: FinRL-X模块化交易基础设施 | design | design_only | D-PF-CORE/裁定15: FinRL-X模块化交易基础设施 | 裁定15: FinRL-X模块化交易基础设施 | design | design_only |
| D-PF-CORE/裁定18: 中金Quant 4.0框架对齐 | 裁定18: 中金Quant 4.0框架对齐 | design | design_only | D-PF-CORE/裁定18: 中金Quant 4.0框架对齐 | 裁定18: 中金Quant 4.0框架对齐 | design | design_only |
| ...架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) | 裁定22: 持续学习抗遗忘框架（§29.35） Decision 22: ... | design | design_only | ...架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) | 裁定22: 持续学习抗遗忘框架（§29.35） Decision 22: ... | design | design_only |
| D-PF-CORE/账户状态物化视图 Account Status View | 账户状态物化视图 Account Status View | design | design_only | D-PF-CORE/账户状态物化视图 Account Status View | 账户状态物化视图 Account Status View | design | design_only |
| D-PF-CORE/🟡 健康线（Healthy）—— 系统运行良好，可以放心 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | design | design_only | D-PF-CORE/🟡 健康线（Healthy）—— 系统运行良好，可以放心 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | design | design_only |
| D-PF-CORE/🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收... | design | design_only | D-PF-CORE/🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收... | design | design_only |
| src/zephyr/pf_core/__init__.py |  | prototype | draft | src/zephyr/pf_core/__init__.py |  | prototype | draft |
| src/zephyr/pf_core/_extensions/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/analytics_base.py |  | production | draft | src/zephyr/pf_core/analytics_base.py |  | production | draft |
| src/zephyr/pf_core/api/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/compliance_rule.py |  | production | draft | src/zephyr/pf_core/compliance_rule.py |  | production | draft |
| src/zephyr/pf_core/core/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/default_attribution_engine.py |  | production | draft | src/zephyr/pf_core/default_attribution_engine.py |  | production | draft |
| src/zephyr/pf_core/default_tca_engine.py |  | production | draft | src/zephyr/pf_core/default_tca_engine.py |  | production | draft |
| src/zephyr/pf_core/infrastructure/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/models/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/performance_attribution_engine/__init__.py |  | prototype | draft | src/zephyr/pf_core/performance_attribution_engine/__init__.py |  | prototype | draft |
| src/zephyr/pf_core/performance_attribution_report.py |  | production | draft | src/zephyr/pf_core/performance_attribution_report.py |  | production | draft |
| src/zephyr/pf_core/risk_limits.py |  | prototype | draft | src/zephyr/pf_core/risk_limits.py |  | prototype | draft |
| src/zephyr/pf_core/services/__init__.py |  | scaffold_placeholder | orphan | src/zephyr/pf_core/services/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_core/strategies/__init__.py |  | prototype | draft | src/zephyr/pf_core/strategies/__init__.py |  | prototype | draft |
| src/zephyr/pf_core/strategies/default_equity_strategy.py |  | prototype | draft | src/zephyr/pf_core/strategies/default_equity_strategy.py |  | prototype | draft |
| src/zephyr/pf_core/strategy_base.py |  | production | draft | src/zephyr/pf_core/strategy_base.py |  | production | draft |
| src/zephyr/pf_core/strategy_engine/__init__.py |  | prototype | draft | src/zephyr/pf_core/strategy_engine/__init__.py |  | prototype | draft |
| src/zephyr/pf_core/strategy_registry.py |  | prototype | draft | src/zephyr/pf_core/strategy_registry.py |  | prototype | draft |
| 另类数据域缩写，D-ALT-02=SentimentEngine | D-ALT-DATA-02 | design | design_only | 另类数据域缩写，D-ALT-02=SentimentEngine | D-ALT-DATA-02 | design | design_only |
| 推理域缩写，D-ML-02=ModelRegistry→归入MS-01 | MS-01 | design | design_only | 推理域缩写，D-ML-02=ModelRegistry→归入MS-01 | MS-01 | design | design_only |

> (仅显示前 200 个模块，共 202 个)

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_PF_CORE["D-PF_CORE 组合核心"]
        A_001["A-001 design"]
        MS_02["MS-02 design"]
        MT_02["MT-02 design"]
        MS_04["MS-04 design"]
        MT_03["MT-03 design"]
        MS_03["MS-03 design"]
        MS_05["MS-05 design"]
        MT_05["MT-05 design"]
        MT_04["MT-04 design"]
        D_ALT_DATA_03["D-ALT-DATA-03 design"]
        D_ALT_DATA_11["D-ALT-DATA-11 design"]
        D_ALT_DATA_06["D-ALT-DATA-06 design"]
        D_ALT_DATA_07["D-ALT-DATA-07 design"]
        D_ALT_DATA_09["D-ALT-DATA-09 design"]
        D_ALT_DATA_10["D-ALT-DATA-10 design"]
        D_ALT_DATA_13["D-ALT-DATA-13 design"]
        D_ALT_DATA_15["D-ALT-DATA-15 design"]
        D_ALT_DATA_17["D-ALT-DATA-17 design"]
        D_ALT_DATA_06_1["D-ALT-DATA-06扩展 design"]
        D_ALT_DATA_14["D-ALT-DATA-14 design"]
        D_CROSS_ASSET_03["D-CROSS-ASSET-03 design"]
        D_CROSS_ASSET_13["D-CROSS-ASSET-13 design"]
        AP_07["AP-07 design"]
        AP_09["AP-09 design"]
        RK_10["RK-10 design"]
        PA_01["PA-01 design"]
        D_PF_CORE_19_2_Ensemble_HMM["19.2 Ensemble-HMM增强框架 design"]
        D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules["26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow... design"]
        D_PF_CORE_28_5_28_5_Linkage_with_Existing_Modules["28.5 与已有模块的联动 28.5 Linkage with Existing Modules design"]
        D_PF_CORE_31_3_ESMA_MABUM["31.3 高级协同检测（基于ESMA MABUM框架） design"]
    end
    D_TRADING["D-TRADING design"]
    D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules -.->|data| D_TRADING
    D_EX_CORE["D-EX_CORE design"]
    D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules -.->|config_depends| D_EX_CORE
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_PF_CORE_31_3_ESMA_MABUM -.->|event| D_INFRA_RUNTIME
    D_SIGNAL["D-SIGNAL design"]
    D_PF_CORE_31_3_ESMA_MABUM -.->|contract| D_SIGNAL
    D_RISK["D-RISK design"]
    D_PF_CORE_28_5_28_5_Linkage_with_Existing_Modules -.->|data| D_RISK
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_INTELLIGENCE -.->|event| D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|event| D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|contract| D_PF_CORE_31_3_ESMA_MABUM
    D_INFRA_OPS -.->|contract| D_PF_CORE_31_3_ESMA_MABUM
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|event| D_PF_CORE_31_3_ESMA_MABUM
    D_INTEGRATION["D-INTEGRATION design"]
    D_INTEGRATION -.->|data| D_PF_CORE_31_3_ESMA_MABUM
    D_REPORTING["D-REPORTING design"]
    D_REPORTING -.->|event| D_PF_CORE_28_5_28_5_Linkage_with_Existing_Modules
    D_COMPLIANCE -.->|event| D_PF_CORE_28_5_28_5_Linkage_with_Existing_Modules
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class A_001,MS_02,MT_02,MS_04,MT_03,MS_03,MS_05,MT_05,MT_04,D_ALT_DATA_03,D_ALT_DATA_11,D_ALT_DATA_06,D_ALT_DATA_07,D_ALT_DATA_09,D_ALT_DATA_10,D_ALT_DATA_13,D_ALT_DATA_15,D_ALT_DATA_17,D_ALT_DATA_06_1,D_ALT_DATA_14,D_CROSS_ASSET_03,D_CROSS_ASSET_13,AP_07,AP_09,RK_10,PA_01,D_PF_CORE_19_2_Ensemble_HMM,D_PF_CORE_26_5_26_5_Contrarian_Capital_Flow_Linkage_with_Existing_Modules,D_PF_CORE_28_5_28_5_Linkage_with_Existing_Modules,D_PF_CORE_31_3_ESMA_MABUM design
    class D_TRADING,D_EX_CORE,D_INFRA_RUNTIME,D_SIGNAL,D_RISK,D_INTELLIGENCE,D_AUTONOMY_CORE,D_INFRA_OPS,D_COMPLIANCE,D_INTEGRATION,D_REPORTING external_design
```

> (依赖图最多显示前 30 个节点，共 202 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-RISK | 27 | data,contract,config_depends,event | D-RISK | 27 | data,contract,config_depends,event |
| D-SIGNAL | 22 | contract,data,event,config_depends | D-SIGNAL | 22 | contract,data,event,config_depends |
| D-SECURITY | 22 | event,contract,data | D-SECURITY | 22 | event,contract,data |
| D-INFRA_RUNTIME | 15 | data,event,contract,config_depends | D-INFRA_RUNTIME | 15 | data,event,contract,config_depends |
| D-GOVERNANCE | 12 | contract,import_depends | D-GOVERNANCE | 12 | contract,import_depends |
| D-EX_CORE | 9 | event,config_depends,contract | D-EX_CORE | 9 | event,config_depends,contract |
| D-DATA_ENG | 9 | config_depends,event,data,contract | D-DATA_ENG | 9 | config_depends,event,data,contract |
| D-MKT_DATA | 8 | event,contract,data | D-MKT_DATA | 8 | event,contract,data |
| D-FACTOR | 8 | event,contract,data | D-FACTOR | 8 | event,contract,data |
| D-TRADING | 4 | import_depends,contract,event,data | D-TRADING | 4 | import_depends,contract,event,data |
| D-ML_SERVE | 4 | data,event,contract | D-ML_SERVE | 4 | data,event,contract |
| D-KNOWLEDGE | 4 | event,contract,config_depends | D-KNOWLEDGE | 4 | event,contract,config_depends |
| D-EX_SOR | 4 | event,config_depends,data | D-EX_SOR | 4 | event,config_depends,data |
| D-POSITION | 2 | contract | D-POSITION | 2 | contract |
| D-ML_TRAIN | 2 | data | D-ML_TRAIN | 2 | data |
| D-REPORTING | 1 | import_depends | D-REPORTING | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 30 | test_depends,data,event,contract,config_depends | D-GOVERNANCE | 30 | test_depends,data,event,contract,config_depends |
| D-COMPLIANCE | 30 | event,data,config_depends,contract | D-COMPLIANCE | 30 | event,data,config_depends,contract |
| D-INFRA_OPS | 19 | contract,config_depends,event,data | D-INFRA_OPS | 19 | contract,config_depends,event,data |
| D-INTEGRATION | 18 | contract,data,config_depends,event | D-INTEGRATION | 18 | contract,data,config_depends,event |
| D-AUTONOMY_CORE | 15 | contract,data,event,config_depends | D-AUTONOMY_CORE | 15 | contract,data,event,config_depends |
| D-FRONTEND | 11 | contract,data,event,config_depends | D-FRONTEND | 11 | contract,data,event,config_depends |
| D-REPORTING | 7 | config_depends,contract,event,data | D-REPORTING | 7 | config_depends,contract,event,data |
| D-OPS | 7 | contract,event,data | D-OPS | 7 | contract,event,data |
| D-INTELLIGENCE | 7 | contract,data,event,config_depends | D-INTELLIGENCE | 7 | contract,data,event,config_depends |
| D-PF_ALLOC | 6 | data,contract,event | D-PF_ALLOC | 6 | data,contract,event |
| D-SIMULATION | 4 | event,data,contract | D-SIMULATION | 4 | event,data,contract |
| D-CROSS_ASSET | 4 | data,event,contract | D-CROSS_ASSET | 4 | data,event,contract |
| D-SELL_DECISION | 3 | event,data,contract | D-SELL_DECISION | 3 | event,data,contract |
| D-DATA_GOV | 3 | contract,event,data | D-DATA_GOV | 3 | contract,event,data |
| D-AUTONOMY_PERM | 3 | contract,data | D-AUTONOMY_PERM | 3 | contract,data |
| D-ALT_DATA | 1 | event | D-ALT_DATA | 1 | event |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
