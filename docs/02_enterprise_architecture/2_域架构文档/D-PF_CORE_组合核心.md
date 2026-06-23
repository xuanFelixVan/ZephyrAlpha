---
doc_type: domain_architecture_doc
title: D-PF_CORE 组合核心架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-PF_CORE 组合核心架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-PF_CORE |
| 域名称 | 组合核心 |
| 架构层 | L2_domain |
| 模块总数 | 202 |
| 设计态模块 | 183 |
| 原型态模块 | 7 |
| 生产态模块 | 6 |
| 容量 | 7/150 (正常) |
| 描述 | 组合核心域。负责投资组合核心引擎，包括组合优化器、风险预算分配、基准跟踪、再平衡引擎。 |

## 模块清单

共 202 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
|  | MOD-PORTFOLIO_CORE | active | design | 0 | 10 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
|  | MOD-PF_CORE | unbuilt | design | 0 | 0 |
| D-PF-CORE/19.2 Ensemble-HMM增强框架 |  | design_only | design | 0 | 0 |
| ...26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules |  | design_only | design | 0 | 0 |
| D-PF-CORE/28.5 与已有模块的联动 28.5 Linkage with Existing Modules |  | design_only | design | 0 | 0 |
| D-PF-CORE/31.3 高级协同检测（基于ESMA MABUM框架） |  | design_only | design | 0 | 0 |
| D-PF-CORE/A Share Trading Discipline A股交易纪律 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Auto Down-Weight 自动降权 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Automatic Strategy Discovery 自动策略发现 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Benchmark Manager 基准管理器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/BuyDecided 买入决策事件 |  | design_only | design | 0 | 0 |
| D-PF-CORE/BuyDecision 买入决策契约 |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-006：策略工厂 |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-016：知识图谱引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-027：因子工厂（P0） |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-028：信号工厂（P0） |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-033：过拟合系统性防护 |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-040：系统性压力测试 |  | design_only | design | 0 | 0 |
| D-PF-CORE/C-047：仓位管理唯一裁决中心 |  | design_only | design | 0 | 0 |
| D-PF-CORE/CTR-P1-006 StrategyLifecycleEvent CTR-P1-006 StrategyLifecycleEvent契约 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Carbon Footprint Calculator碳足迹计算器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Carbon Footprint 碳足迹 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Cash Flow Manager资金流管理器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Constraint Solver约束求解器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Decision Orchestrator 决策编排器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Decision Orchestrator 决策编排器——缺失功能模块 |  | design_only | design | 0 | 0 |
| D-PF-CORE/E-PF-01 PortfolioRebalanced E-PF-01 PortfolioRebalanced事件 |  | design_only | design | 0 | 0 |
| D-PF-CORE/E-SIM-01 SimulationCompleted 仿真完成 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Event Bus §2.2 事件总线事件分类 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Event Sourcing 事件溯源 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Execution to L5 Closed Loop 执行→L5闭环优化 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Explainability 决策可解释性与溯源 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Factor Direct Layer 因子直通层 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Factor Exposure Manager因子敞口管理器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Governance Domain §30.6 运维安全治理域缺失模块 |  | design_only | design | 0 | 0 |
| D-PF-CORE/HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 |  | design_only | design | 0 | 0 |
| D-PF-CORE/HoldDecided 持有决策事件 |  | design_only | design | 0 | 0 |
| D-PF-CORE/L2 to L3 Strategy Decision L2→L3策略决策 |  | design_only | design | 0 | 0 |
| D-PF-CORE/L3-L6 决策/仓位/风控/执行/闭环数据 |  | design_only | design | 0 | 0 |
| D-PF-CORE/LLM Evolutionary Strategy Search LLM进化式策略搜索 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Liquidity Estimator 流动性估算器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Liquidity Estimator流动性估计器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/MTF Four-Track Fusion 四轨融合器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Multi-Objective Optimizer多目标优化器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Multi-Scenario Response & Contingency 多情景对策与预案 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Multi-Strategy Allocator 多策略分配器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Multi-Strategy Resonance Fusion 多策略共振融合层 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Multi-Track Fusion 四轨融合器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/P0 模块明细 |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（14个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（5个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（7个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（85个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（92个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P1 模块分类汇总（99个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（11个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（17个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（29个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（30个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（62个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P2 模块分类汇总（7个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P3 模块分类汇总（1个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/P3 模块分类汇总（3个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/Percentage 百分比 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Performance Attribution Engine绩效归因引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Benchmark Manager组合基准管理器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Construction Engine 组合构建引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Core 组合核心 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Drift Monitor组合漂移监控器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Optimization Engine 组合优化引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Optimizer组合优化器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Rebalancer 组合再平衡器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Risk Decomposer 组合风险分解器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio State 组合状态检查点 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio Stress Tester组合压力测试器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio 组合 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Portfolio 组合聚合根 |  | design_only | design | 0 | 0 |
| D-PF-CORE/PortfolioRebalanced 组合已再平衡 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Rebalance Cost Analyzer再平衡成本分析器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Rebalance Full Flow Saga 再平衡全流程Saga |  | design_only | design | 0 | 0 |
| D-PF-CORE/Rebalance Scheduler再平衡调度器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Risk Parity Engine风险平价引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/SHAP LIME Dual Attribution SHAP LIME双归因 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Sector Exposure Manager行业敞口管理器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Sell Decision Engine 卖出决策引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Signal Factory §4.1 信号工厂九大子阶段 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Capacity Estimator策略容量估计器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Capacity Modeling 策略容量建模 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Engine策略引擎 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Factory 策略工厂 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Portfolio 策略组合 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Strategy Signal Router 策略信号路由器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/StrategyLifecycleEvent 策略生命周期事件 |  | design_only | design | 0 | 0 |
| D-PF-CORE/StrategyRegistry 策略注册表 |  | design_only | design | 0 | 0 |
| D-PF-CORE/Tax Loss Harvester税损收割器 |  | design_only | design | 0 | 0 |
| D-PF-CORE/XS-EXT 模块分类汇总（5个） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§12.4 C-033 过拟合系统性防护 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§2.1 多源数据接入与分层存储架构 Data Ingestion Storage |  | design_only | design | 0 | 0 |
| D-PF-CORE/§20.8 方法论约束八：训练-服务一致性(Feature Store) |  | design_only | design | 0 | 0 |
| D-PF-CORE/§24 外部系统交互引用 External |  | design_only | design | 0 | 0 |
| D-PF-CORE/§24.1 外部系统交互矩阵 External |  | design_only | design | 0 | 0 |
| D-PF-CORE/§27 系统级成功指标引用 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.1 多进程隔离与运行时架构（→A9运维架构） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.10 盘中即时反应决策引擎 Engine |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.2 特征存储 (Feature Store) |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.21 学习系统桥接声明 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.35 持续学习抗遗忘框架（v6.0新增） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§29.4 时序数据库与分层存储架构（→A3数据架构） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30 场外草稿区缺失模块补充 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.1 核心价值链域缺失模块 Core |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.1.3 D-PF-CORE 组合核心域（18个模块） |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.2 增强与扩展域缺失模块 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.3 核心交易链域缺失模块 Core |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.4 ML与数据工程域缺失模块 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§30.5 自治与基础设施域缺失模块 Base |  | design_only | design | 0 | 0 |
| D-PF-CORE/§4.4 信号聚合器架构 Signal Aggregator |  | design_only | design | 0 | 0 |
| D-PF-CORE/§8.1 策略工厂(C-006)与信号工厂(C-028)的协作 |  | design_only | design | 0 | 0 |
| D-PF-CORE/§8.5 组合优化引擎 Portfolio Engine |  | design_only | design | 0 | 0 |
| D-PF-CORE/❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution |  | design_only | design | 0 | 0 |
| D-PF-CORE/再平衡全流程Saga Rebalancing Saga |  | design_only | design | 0 | 0 |
| D-PF-CORE/决策四：模型/策略漂移检测框架 Strategy Model |  | design_only | design | 0 | 0 |
| D-PF-CORE/多账户多策略 Strategy |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块19 市场体制转换模型（Regime-Switching Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） |  | design_only | design | 0 | 0 |
| ...E/模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification |  | design_only | design | 0 | 0 |
| ...码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification |  | design_only | design | 0 | 0 |
| ...8 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) |  | design_only | design | 0 | 0 |
| ...-CORE/模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块3 缺口回补概率模型（Gap Fill Probability Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块31 协同交易行为检测模型（Coordinated Trading Detection Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块32 市场风格体制识别模型（Market Style Regime Identification Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块39 多因子选股评分模型（Multi-Factor Stock Selection Scoring Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块4 逼空行情检测模型（Short Squeeze Detection Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） |  | design_only | design | 0 | 0 |
| ...更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） |  | design_only | design | 0 | 0 |
| .../模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description |  | design_only | design | 0 | 0 |
| ...架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/模块8 板块资金流再配置模型（Sector Flow Reallocation Model） |  | design_only | design | 0 | 0 |
| D-PF-CORE/裁定15: FinRL-X模块化交易基础设施 |  | design_only | design | 0 | 0 |
| D-PF-CORE/裁定18: 中金Quant 4.0框架对齐 |  | design_only | design | 0 | 0 |
| ...架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) |  | design_only | design | 0 | 0 |
| D-PF-CORE/账户状态物化视图 Account Status View |  | design_only | design | 0 | 0 |
| D-PF-CORE/🟡 健康线（Healthy）—— 系统运行良好，可以放心 |  | design_only | design | 0 | 0 |
| D-PF-CORE/🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 |  | design_only | design | 0 | 0 |
| src/zephyr/pf_core/__init__.py | MOD-L05-001 | draft | prototype | 1 | 0 |
| src/zephyr/pf_core/_extensions/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/analytics_base.py | MOD-PF_CORE | draft | production | 2 | 1 |
| src/zephyr/pf_core/api/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/compliance_rule.py | MOD-PF_CORE | draft | production | 1 | 1 |
| src/zephyr/pf_core/core/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/default_attribution_engine.py | MOD-PF_CORE | draft | production | 1 | 1 |
| src/zephyr/pf_core/default_tca_engine.py | MOD-PF_CORE | draft | production | 3 | 1 |
| src/zephyr/pf_core/infrastructure/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/models/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/performance_attribution_engine/__init__.py | MOD-PF_CORE | draft | prototype | 0 | 1 |
| src/zephyr/pf_core/performance_attribution_report.py | MOD-PF_CORE | draft | production | 1 | 1 |
| src/zephyr/pf_core/risk_limits.py | MOD-PF_CORE | draft | prototype | 0 | 1 |
| src/zephyr/pf_core/services/__init__.py | MOD-PF_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_core/strategies/__init__.py | MOD-PF_CORE | draft | prototype | 0 | 1 |
| src/zephyr/pf_core/strategies/default_equity_strategy.py | MOD-L05-001 | draft | prototype | 0 | 2 |
| src/zephyr/pf_core/strategy_base.py | MOD-PF_CORE | draft | production | 1 | 1 |
| src/zephyr/pf_core/strategy_engine/__init__.py | MOD-PF_CORE | draft | prototype | 0 | 1 |
| src/zephyr/pf_core/strategy_registry.py | MOD-PF_CORE | draft | prototype | 0 | 1 |
| 另类数据域缩写，D-ALT-02=SentimentEngine | MOD-PF_CORE | design_only | design | 0 | 0 |
| 推理域缩写，D-ML-02=ModelRegistry→归入MS-01 | MOD-PF_CORE | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 202 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 27 | data,contract,config_depends,event |
| D-SIGNAL | 22 | contract,data,event,config_depends |
| D-SECURITY | 22 | event,contract,data |
| D-INFRA_RUNTIME | 15 | data,event,contract,config_depends |
| D-GOVERNANCE | 12 | contract,import_depends |
| D-EX_CORE | 9 | event,config_depends,contract |
| D-DATA_ENG | 9 | config_depends,event,data,contract |
| D-MKT_DATA | 8 | event,contract,data |
| D-FACTOR | 8 | event,contract,data |
| D-TRADING | 4 | import_depends,contract,event,data |
| D-ML_SERVE | 4 | data,event,contract |
| D-KNOWLEDGE | 4 | event,contract,config_depends |
| D-EX_SOR | 4 | event,config_depends,data |
| D-POSITION | 2 | contract |
| D-ML_TRAIN | 2 | data |
| D-REPORTING | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 30 | test_depends,data,event,contract,config_depends |
| D-COMPLIANCE | 30 | event,data,config_depends,contract |
| D-INFRA_OPS | 19 | contract,config_depends,event,data |
| D-INTEGRATION | 18 | contract,data,config_depends,event |
| D-AUTONOMY_CORE | 15 | contract,data,event,config_depends |
| D-FRONTEND | 11 | contract,data,event,config_depends |
| D-REPORTING | 7 | config_depends,contract,event,data |
| D-OPS | 7 | contract,event,data |
| D-INTELLIGENCE | 7 | contract,data,event,config_depends |
| D-PF_ALLOC | 6 | data,contract,event |
| D-SIMULATION | 4 | event,data,contract |
| D-CROSS_ASSET | 4 | data,event,contract |
| D-SELL_DECISION | 3 | event,data,contract |
| D-DATA_GOV | 3 | contract,event,data |
| D-AUTONOMY_PERM | 3 | contract,data |
| D-ALT_DATA | 1 | event |

## 域内依赖图

详见 [d_pf_core_dependency.mmd](d_pf_core_dependency.mmd)
