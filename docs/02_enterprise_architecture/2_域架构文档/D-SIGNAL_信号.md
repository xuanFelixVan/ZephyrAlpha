---
doc_type: domain_architecture_doc
title: D-SIGNAL 信号架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SIGNAL 信号架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SIGNAL |
| 域名称 | 信号 |
| 架构层 | L2_domain |
| 模块总数 | 476 |
| 设计态模块 | 474 |
| 原型态模块 | 1 |
| 生产态模块 | 1 |
| 容量 | 1/150 (正常) |
| 描述 | 信号生成、信号组合、信号过滤、信号优先级。交易信号引擎。 |

## 模块清单

共 476 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-SIGNAL/36-Step Decision Framework Implementer 36环节决策框架实现器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/3秒级逆势资金流识别个股级 Stock Contrarian Flow |  | design_only | design | 0 | 0 |
| D-SIGNAL/3秒级逆势资金流识别概念/板块级 Sector Contrarian Flow |  | design_only | design | 0 | 0 |
| D-SIGNAL/3秒级逆势资金流识别模块 Contrarian Flow Detector |  | design_only | design | 0 | 0 |
| D-SIGNAL/4-Min Aggregation vs 3-Sec Tick 4分钟聚合版本vs3秒Tick版 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share 4-Min Surge Anomaly Detector A股4分钟涨速异常探测器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Auction Session Analyzer A股集合竞价分析器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Auction Weak-to-Strong Detector A股竞价弱转强检测器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Broken Board Definer A股烂板定义判定器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Capital Flow Pattern A股资金流模式 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Capital Flow Signal A股资金流向信号 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Capital-Force Conflict Arbiter A股主力游资冲突仲裁器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Capital-Force Conflict Observer A股主力游资打架观察器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Contrarian Capital 5-Day Tracker A股逆势资金5日连续跟踪排名器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Contrarian Signal Phase Filter A股逆势信号市场阶段过滤器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Contrarian Signal Sensitivity Configurator A股逆势信号灵敏度配置器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Decision Priority Engine A股决策优先级引擎 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Dual-Engine 5-Type Decision Mapper A股双引擎融合5类操作映射器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Dual-Engine Fusion 引擎 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Emergency Opportunity Evaluator A股应急机会5分钟快速评估器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Emotion Cycle 4+1 Stage Action Mapper A股情绪周期4+1阶段操作映射器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Emotion Ladder Classifier A股情绪梯队自动分类器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Gap Support-Pressure Converter A股跳空缺口支撑压力转换器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Institutional Behavior A股机构行为 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Intraday Buy/Sell Point A股日内买卖点 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Intraday Pattern Analyzer A股分时形态分析器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share KDJ-MACD Multi-Period Screener A股KDJ三周期+MACD多头确认筛选器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Limit-Up Gene Evaluator A股涨停基因4维评估器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Market Breadth Monitor A股市场真实广度监控器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Market Direction Predictor A股大盘方向预测器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Market Microstructure Signal A股微观结构信号 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Market Phase Threshold Classifier A股市场阶段阈值分类器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Market Sentiment A股市场情绪 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Multi-Concept Overlay Bonus Calculator A股多概念叠加加分计算器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Multi-Day Breakdown Confirmer A股有效跌破多日确认器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Multi-Index Decline Period Detector A股多指数下跌时段识别器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share National Team Dual-Mode Identifier A股国家队操纵双模式识别器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Order Book Microstructure Analyzer A股盘口微观结构分析器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Plan Conformity Evaluator A股计划吻合度量化评估器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Policy Signal A股政策信号 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Post-Buy Quick Diagnostician A股买入后5-15分钟诊断器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Quant Short-term Strength A股量化短线强度 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Rotation Warning Signaler A股轮动预警信号器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Seal Order Level Jump Detector A股封单级别跃变检测器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Sector Analyzer 分析器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Sector Capital Rotation Timeline A股板块资金轮动时间线生成器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Sector Dual-List Cross Filter A股板块双榜交叉筛选器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Short-term Stock Selector A股短线选股器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Signal Post-Rise Filter A股信号后涨幅过滤器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Unexpected Strength/Weakness Detector A股该弱不弱/该强不强检测器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A-Share Youzi Relay Emotion A股游资接力情绪 |  | design_only | design | 0 | 0 |
| D-SIGNAL/AST Sandbox AST沙箱三层安全 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Agent Hallucination Output Agent输出异常幻觉 |  | design_only | design | 0 | 0 |
| D-SIGNAL/AgentFeedbackRound Agent反馈轮次 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Aggregator Base GRE基础 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Analyst Agent Feedback Loop 分析师Agent反馈循环 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Atomic Strategy Module Library 原子化策略模块库 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Auction Direction Prediction 竞价方向预测 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Auction Microstructure Signal Module 竞价微结构信号模块 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Auction Trap 竞价陷阱 |  | design_only | design | 0 | 0 |
| D-SIGNAL/A股信号子域 |  | design_only | design | 0 | 0 |
| D-SIGNAL/BMA Bayesian Model Averaging BMA贝叶斯模型平均 |  | design_only | design | 0 | 0 |
| D-SIGNAL/BVC Method BVC统计推断方法 |  | design_only | design | 0 | 0 |
| D-SIGNAL/BayesianModelAveraging BMA贝叶斯模型平均 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Behavioral Bias Engine 行为偏差引擎 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Book Imbalance 订单簿不平衡 |  | design_only | design | 0 | 0 |
| D-SIGNAL/BullTrapQuantified 诱多量化 |  | design_only | design | 0 | 0 |
| D-SIGNAL/BuySignal 买入信号契约 |  | design_only | design | 0 | 0 |
| D-SIGNAL/C-011 主力行为识别 Main Force Behavior Recognition |  | design_only | design | 0 | 0 |
| D-SIGNAL/C-014 大盘预测 Market Prediction |  | design_only | design | 0 | 0 |
| D-SIGNAL/C-021 市场状态 Market State |  | design_only | design | 0 | 0 |
| D-SIGNAL/C-034 主力画像 Main Force Profile |  | design_only | design | 0 | 0 |
| D-SIGNAL/C-039 跨市场传导 Cross-market Transmission |  | design_only | design | 0 | 0 |
| D-SIGNAL/CTR-002消费契约适配器 CTR-002 Contract Adapter |  | design_only | design | 0 | 0 |
| D-SIGNAL/CTR-TRACE-001 TraceContext传播器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Calendar Constraint Layer 日历约束层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Candlestick Pattern Recognizer 蜡烛图模式识别器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Canvas Drag-Connect Engine 画布拖拽连线引擎 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Capital Allocation Constraint Validator 资本分配约束校验器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Capital Allocator 资金分配器 |  | design_only | design | 0 | 0 |
| ...italAllocationResult CTR-P1-003 Builder CapitalAllocationResult CTR-P1-003构建器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CapitulationBottom 投降底部 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Causal KG 因果知识图谱 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Causal Relationship Extraction 因果关系提取 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CausalKGEdge Causal KG因果方向标注 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CausalML 因果机器学习 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CausalPrior LLM引导因果发现先验 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CausalRL CausalRL因果约束强化学习 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Chan Theory Pen-Segment-Pivot Recognizer 缠论笔段中枢识别器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Chart Pattern Recognition Algorithm Library 图形形态识别算法库 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Click First or Last 早晚下单策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Code Generation Flow Orchestrator 代码生成流程编排器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CompositeSignal 复合信号契约 |  | design_only | design | 0 | 0 |
| D-SIGNAL/CompositeSignal 复合信号聚合根 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Concept Net Inflow Aggregation 概念级资金净流入聚合 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Conditional Density Prediction 收益率条件密度预测 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Conflict Detection 矛盾检测 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contradictory Signal Processing 矛盾信号处理 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contradictory Signal Resolver 矛盾信号解决器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian Capital Flow Signal Module 逆势资金流信号模块 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian Fund Flow Identification 逆势资金流识别模型 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-L2B Linkage 逆势资金流与L2-B主力行为层联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-L2C Linkage 逆势资金流与L2-C市场状态层联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-L3 Linkage 逆势资金流与L3策略工厂联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-L3.5 Linkage 逆势资金流与L3.5仓位管理联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-L4 Linkage 逆势资金流与L4风控层联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Contrarian-Stock Selection Linkage 逆势资金流与选股决策流联动 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Correlation Structure Collapse 相关性结构崩塌 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Create New 新建信号模块模式 |  | design_only | design | 0 | 0 |
| D-SIGNAL/D-L0 Degradation Level 0 降级等级0 |  | design_only | design | 0 | 0 |
| D-SIGNAL/D-L1 Degradation Level 1 降级等级1 |  | design_only | design | 0 | 0 |
| D-SIGNAL/D-L2 Degradation Level 2 降级等级2 |  | design_only | design | 0 | 0 |
| D-SIGNAL/D-L3 Degradation Level 3 降级等级3 |  | design_only | design | 0 | 0 |
| D-SIGNAL/DataIngestionFailed 数据接入失败事件 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Decision Step Dependency Graph 决策环节依赖图 |  | design_only | design | 0 | 0 |
| D-SIGNAL/DecisionEvent 决策事件 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Degradation Monitor 监控器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Degradation Notification Downstream Manager 降级通知下游管理器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/DivergenceDetection 背离检测 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dual-Engine Fusion Decision 双引擎融合决策 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Conditional Correlation 动态条件相关 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Signal Weighting Model 动态信号权重模型 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Take-Profit Strategy Library 动态止盈策略库 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Weight Allocation 动态权重分配 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Weight Allocator 动态权重分配器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Dynamic Weight Synthesis 动态权重合成策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/E-SG-01 D-SIGNAL→PA-02事件 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Empty Signal NEUTRAL Strategy Manager 空信号NEUTRAL策略管理器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Equal Weight Allocation 等权分配策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Equal Weight Synthesis 等权合成策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Evening Research Pipeline 晚间研究流水线 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Event-Driven Distribution Filter 事件驱动分布筛选 |  | design_only | design | 0 | 0 |
| D-SIGNAL/EvolutionRound 进化轮次 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Evolutionary Code Generation 进化式代码生成 |  | design_only | design | 0 | 0 |
| D-SIGNAL/ExecutionEvent 执行事件 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Explainable Design Constraint 可解释设计约束 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Extend Module 信号模块扩展模式 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor Consistency Confidence Calculator 因子一致性置信度计算器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor DSL 因子DSL约束 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor Decay Linkage Degradation Handler 因子衰减联动降级器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor IC Collective Decay 因子IC集体衰减 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor Missing Ratio Calculator 因子缺失比例计算器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Factor Validity Filter 因子有效性过滤器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/FactorMAD Debate FactorMAD双Agent辩论 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Fund Source Identification 资金来源识别 |  | design_only | design | 0 | 0 |
| D-SIGNAL/GARCHVolatilityForecast GARCH波动率预测 |  | design_only | design | 0 | 0 |
| D-SIGNAL/GNN Stock Relationship Modeling GNN股票关系建模 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Game Theory Knowledge 博弈知识 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Gap Pattern Recognizer 缺口形态识别器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/GlobalMarketContagion 全球市场传染 |  | design_only | design | 0 | 0 |
| D-SIGNAL/GraphRAG 图谱 |  | design_only | design | 0 | 0 |
| D-SIGNAL/HMMGMMRegimeDetection HMM/GMM体制识别 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Herd Effect Critical State 散户羊群效应临界态 |  | design_only | design | 0 | 0 |
| D-SIGNAL/High Open Strength 高开强度 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Hoeting Bayesian Model Averaging Hoeting贝叶斯模型平均 |  | design_only | design | 0 | 0 |
| D-SIGNAL/IC Weighted Synthesis IC加权合成策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/IC Weighted Synthesis Strategist IC加权合成策略器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/IRCF Revision List IRCF因子补充修订清单 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Incremental Factor Calculation 增量因子计算 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Institutional Retail Contrarian Flow IRCF因子 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Interactive Time Series Annotation Tool 交互式时间序列标注工具 |  | design_only | design | 0 | 0 |
| D-SIGNAL/InterventionCausalEdge 带干预的时序因果发现结果 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Intraday Auction Strategy 日内竞价策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Intraday Real-time Pipeline 盘中实时流水线 |  | design_only | design | 0 | 0 |
| D-SIGNAL/K-Line Chart Interactive Toolset K线图交互工具集 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Knowledge Type Classification 知识类型分类 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Kronos TSFM Kronos时序基础模型 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L03 Predictions L03预测子模块 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L03 Signals Default L03默认信号子模块 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L1 to L2-B Main Force Behavior L1→L2-B主力行为 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L1 to L2-C Market State L1→L2-C市场状态 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-A Signal Layer 信号层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-A 信号数据 Signal Data |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-B Main Force Behavior Layer 主力行为层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-B 主力行为 Main Force Behavior |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-C Market State Layer 市场状态层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/L2-C 市场状态与宏观 Market State & Macro |  | design_only | design | 0 | 0 |
| D-SIGNAL/L3.5 Position Management Layer 仓位管理层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/LLM Guided Causal Discovery LLM引导因果发现 |  | design_only | design | 0 | 0 |
| D-SIGNAL/LLM Semantic Understanding LLM语义理解 |  | design_only | design | 0 | 0 |
| D-SIGNAL/LLM Strategy Agent LLM策略Agent |  | design_only | design | 0 | 0 |
| D-SIGNAL/Late Session Contrarian Filter 尾盘逆势过滤 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Lee-Ready Algorithm Lee-Ready算法 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Lesson Learned Knowledge 教训知识 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Limit-Up Contrarian Filter 涨停板逆势过滤 |  | design_only | design | 0 | 0 |
| D-SIGNAL/LineageRoot 血缘根 |  | design_only | design | 0 | 0 |
| D-SIGNAL/ML Enhanced Classification ML增强分类 |  | design_only | design | 0 | 0 |
| D-SIGNAL/ML Weight Synthesis ML权重合成策略 |  | design_only | design | 0 | 0 |
| D-SIGNAL/ML Weight Synthesis Strategist ML权重合成策略器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Macro Signal Generator 宏观信号生成器 |  | design_only | design | 0 | 0 |
| D-SIGNAL/MacroCausalEdge 宏观因果传导路径 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Market Crash Signal Enhancement 大盘急跌时信号增强 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Market State Agent 状态 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Market State Determination 市场状态判定 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Market State Knowledge 市场状态知识 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Model-Free Factor Fusion 因子直通层 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Module Factory Dependency Graph 模块工厂依赖图 |  | design_only | design | 0 | 0 |
| D-SIGNAL/Module Registry 信号模块注册表 |  | design_only | design | 0 | 0 |
| D-SIGNAL/MomentumBreadth 动量广度 |  | design_only | design | 0 | 0 |
| D-SIGNAL/MomentumLeadership 动量领导力 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 476 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-FACTOR | 40 | data,contract,config_depends,event,domain_dependency |
| D-MKT_DATA | 37 | data,contract,event,config_depends,domain_dependency |
| D-INFRA_RUNTIME | 27 | data,contract,event,config_depends |
| D-EX_CORE | 15 | event,config_depends,contract,data |
| D-TRADING | 14 | import_depends,event,config_depends,data,contract |
| D-EX_SOR | 13 | contract,event,data,config_depends |
| D-DATA_ENG | 13 | event,data,contract |
| D-ML_TRAIN | 11 | event,data,contract |
| D-POSITION | 4 | data,contract,event |
| D-GOVERNANCE | 2 | contract,import_depends |
| D-SIGNAL_FUNDAMENTAL | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 93 | contract,config_depends,data,event |
| D-RISK | 71 | contract,data,config_depends,event |
| D-SECURITY | 62 | event,config_depends,data,contract |
| D-GOVERNANCE | 57 | test_depends,import_depends,contract,event,data,config_depends |
| D-AUTONOMY_CORE | 53 | config_depends,data,event,contract |
| D-INTEGRATION | 41 | contract,data,event,config_depends |
| D-INFRA_OPS | 39 | event,contract,data,config_depends |
| D-FRONTEND | 28 | data,event,contract,config_depends |
| D-OPS | 25 | event,contract,data,config_depends |
| D-PF_CORE | 22 | contract,data,event,config_depends |
| D-INTELLIGENCE | 22 | contract,config_depends,event,data |
| D-SIMULATION | 17 | event,contract,data,config_depends |
| D-AUTONOMY_PERM | 15 | contract,event,data,config_depends |
| D-PF_ALLOC | 13 | config_depends,event,data,contract |
| D-REPORTING | 11 | data,contract,event |
| D-KNOWLEDGE | 10 | contract,config_depends,event,data |
| D-CROSS_ASSET | 10 | event,contract,domain_dependency,config_depends,data |
| D-ALT_DATA | 8 | data,event,contract |
| D-ML_SERVE | 6 | contract,event,data,config_depends |
| D-DATA_GOV | 5 | contract,data |
| D-SELL_DECISION | 4 | contract,config_depends |
| D-DATA_SEC | 3 | contract,event,data |
| D-FACTOR | 2 | contract,import_depends |
| D-BACKTEST | 1 | contract |

## 域内依赖图

详见 [d_signal_dependency.mmd](d_signal_dependency.mmd)
