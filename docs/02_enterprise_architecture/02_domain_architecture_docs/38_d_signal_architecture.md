---
doc_type: domain_architecture_diagram
title: D-SIGNAL 信号架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 38_d_signal / 信号 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示信号（D-SIGNAL）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 信号（D-SIGNAL）的模块分布。共 476 个模块 / 476 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (47 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/signal_fundamental/__init__.py  [prototype]         │
│   src/zephyr/signal_fundamental/pipeline.py  [production]        │
│   信号域仓储接口  [design]                                       │
│   策略框架升级迁移适配器  [design]                               │
│   Regime Sample Size Adequacy Checker  [design]                  │
│   Regime Signal Contextualizer  [design]                         │
│   Regime Failure Mode Diagnoser  [design]                        │
│   Regime Macro Indicator Driver  [design]                        │
│   Strategy Shared Kernel Synchronizer  [design]                  │
│   Strategy Historical Performance Data Provider  [design]        │
│   Risk Event E-RK-01 Consumer Handler  [design]                  │
│   策略引擎信号聚合  [design]                                     │
│   Capital Allocation Constraint Validator  [design]              │
│   Regime-Aware Market State Adaptive Synthesizer  [design]       │
│   ML Weight Synthesis Strategist  [design]                       │
│   SynthesizedSignal Event Publisher  [design]                    │
│   Sharpe Ratio Allocation Strategist  [design]                   │
│   CTR-TRACE-001 TraceContext传播器  [design]                     │
│   ...还有 29 个模块 / 29 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (429 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   36-Step Decision Framework Implementer 36环节决策框架实现器... │
│   3秒级逆势资金流识别个股级 Stock Contrarian Flow  [design]      │
│   3秒级逆势资金流识别概念/板块级 Sector Contrarian Flow  [des... │
│   3秒级逆势资金流识别模块 Contrarian Flow Detector  [design]     │
│   4-Min Aggregation vs 3-Sec Tick 4分钟聚合版本vs3秒Tick版  [... │
│   A-Share 4-Min Surge Anomaly Detector A股4分钟涨速异常探测器... │
│   A-Share Auction Session Analyzer A股集合竞价分析器  [design]   │
│   A-Share Auction Weak-to-Strong Detector A股竞价弱转强检测器... │
│   A-Share Broken Board Definer A股烂板定义判定器  [design]       │
│   A-Share Capital Flow Pattern A股资金流模式  [design]           │
│   A-Share Capital Flow Signal A股资金流向信号  [design]          │
│   A-Share Capital-Force Conflict Arbiter A股主力游资冲突仲裁...  │
│   A-Share Capital-Force Conflict Observer A股主力游资打架观察... │
│   A-Share Contrarian Capital 5-Day Tracker A股逆势资金5日连续... │
│   A-Share Contrarian Signal Phase Filter A股逆势信号市场阶段...  │
│   A-Share Contrarian Signal Sensitivity Configurator A股逆势...  │
│   A-Share Decision Priority Engine A股决策优先级引擎  [design]   │
│   A-Share Dual-Engine 5-Type Decision Mapper A股双引擎融合5类... │
│   ...还有 411 个模块 / 411 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 476 个模块 / 476 modules）。

### L2 领域层 / Domain Layer (47 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_fundamental/__init__.py | src/zephyr/signal_fundamental/__init_... | prototype | draft |
| 2 | src/zephyr/signal_fundamental/pipeline.py | src/zephyr/signal_fundamental/pipelin... | production | draft |
| 3 | 信号域-DDD契约/D-SIGNAL-160 | 信号域仓储接口 | design | design_only |
| 4 | 信号域-DDD契约/D-SIGNAL-162 | 策略框架升级迁移适配器 | design | design_only |
| 5 | 信号域-Regime/D-SIGNAL-65 | Regime Sample Size Adequacy Checker | design | design_only |
| 6 | 信号域-Regime/D-SIGNAL-67 | Regime Signal Contextualizer | design | design_only |
| 7 | 信号域-Regime/D-SIGNAL-74 | Regime Failure Mode Diagnoser | design | design_only |
| 8 | 信号域-Regime/D-SIGNAL-76 | Regime Macro Indicator Driver | design | design_only |
| 9 | 信号域-事件追踪/D-SIGNAL-101 | Strategy Shared Kernel Synchronizer | design | design_only |
| 10 | 信号域-事件追踪/D-SIGNAL-103 | Strategy Historical Performance Data ... | design | design_only |
| 11 | 信号域-事件追踪/D-SIGNAL-99 | Risk Event E-RK-01 Consumer Handler | design | design_only |
| 12 | 信号域-冲突融合/D-SIGNAL-134 | 策略引擎信号聚合 | design | design_only |
| 13 | 信号域-合成分配/D-SIGNAL-85 | Capital Allocation Constraint Validator | design | design_only |
| 14 | 信号域-合成分配/D-SIGNAL-87 | Regime-Aware Market State Adaptive Sy... | design | design_only |
| 15 | 信号域-合成分配/D-SIGNAL-90 | ML Weight Synthesis Strategist | design | design_only |
| 16 | 信号域-合成分配/D-SIGNAL-94 | SynthesizedSignal Event Publisher | design | design_only |
| 17 | 信号域-合成分配/D-SIGNAL-96 | Sharpe Ratio Allocation Strategist | design | design_only |
| 18 | 信号域-契约/D-SIGNAL-100 | CTR-TRACE-001 TraceContext传播器 | design | design_only |
| 19 | 信号域-契约/D-SIGNAL-158 | 因子计算结果消费桥接器 | design | design_only |
| 20 | 信号域-审计/D-SIGNAL-06 | Signal Audit Logger | design | design_only |
| 21 | 信号域-技术指标/D-SIGNAL-114 | 技术指标信号生成器 | design | design_only |
| 22 | 信号域-技术指标/D-SIGNAL-116 | 策略逻辑流程图生成器 | design | design_only |
| 23 | 信号域-技术指标/D-SIGNAL-120 | 统一策略接口定义器 | design | design_only |
| 24 | 信号域-技术指标/D-SIGNAL-122 | TA-Lib技术指标信号计算器 | design | design_only |
| 25 | 信号域-技术指标/D-SIGNAL-124 | 图形形态识别算法库 | design | design_only |
| 26 | 信号域-技术指标/D-SIGNAL-126 | 蜡烛图模式识别器 | design | design_only |
| 27 | 信号域-技术指标/D-SIGNAL-128 | 缺口形态识别器 | design | design_only |
| 28 | 信号域-核心基础设施/D-SIGNAL-12 | Signal Version Manager | design | design_only |
| 29 | 信号域-核心基础设施/D-SIGNAL-14 | Strategy Lifecycle Manager | design | design_only |
| 30 | 信号域-核心基础设施/D-SIGNAL-16 | Signal Conflict Resolution Engine | design | design_only |
| 31 | 信号域-核心基础设施/D-SIGNAL-18 | Signal Out-of-Sample Validator | design | design_only |
| 32 | 信号域-策略发布/D-SIGNAL-140 | 策略灰度发布 | design | design_only |
| 33 | 信号域-策略可视化/D-SIGNAL-105 | 代码生成流程编排器 | design | design_only |
| 34 | 信号域-策略可视化/D-SIGNAL-107 | 画布拖拽连线引擎 | design | design_only |
| 35 | 信号域-策略可视化/D-SIGNAL-109 | 策略流程图编辑器 | design | design_only |
| 36 | 信号域-策略可视化/D-SIGNAL-111 | 策略可解释性引擎 | design | design_only |
| 37 | 信号域-策略管理/D-SIGNAL-137 | 策略生命周期管理 | design | design_only |
| 38 | 信号域-策略管理/D-SIGNAL-139 | 策略状态持久化 | design | design_only |
| 39 | 信号域-策略管理/D-SIGNAL-141 | 策略模板版本管理 | design | design_only |
| 40 | 信号域-策略管理/D-SIGNAL-143 | 策略生命周期钩子 | design | design_only |
| 41 | 信号域-策略质量/D-SIGNAL-145 | 风格轮动检测器 | design | design_only |
| 42 | 信号域-策略质量/D-SIGNAL-147 | 策略归因分析器 | design | design_only |
| 43 | 信号域-策略运行时/D-SIGNAL-150 | 策略异常退出处理 | design | design_only |
| 44 | 信号域-策略运行时/D-SIGNAL-152 | 策略基类接口兼容性版本化器 | design | design_only |
| 45 | 信号域-质量降级/D-SIGNAL-79 | Factor Decay Linkage Degradation Handler | design | design_only |
| 46 | 信号域-降级/D-SIGNAL-80 | Degradation Notification Downstream M... | design | design_only |
| 47 | 信号域/D-SIGNAL-20 | Signal Tail Risk Protector | design | design_only |

### 未分类 / Unclassified (429 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-SIGNAL/36-Step Decision Framework Implementer 36环节决... | 36-Step Decision Framework Implemente... | design | design_only |
| 2 | D-SIGNAL/3秒级逆势资金流识别个股级 Stock Contrarian Flow | 3秒级逆势资金流识别个股级 Stock Contr... | design | design_only |
| 3 | D-SIGNAL/3秒级逆势资金流识别概念/板块级 Sector Contrarian... | 3秒级逆势资金流识别概念/板块级 Sector... | design | design_only |
| 4 | D-SIGNAL/3秒级逆势资金流识别模块 Contrarian Flow Detector | 3秒级逆势资金流识别模块 Contrarian Fl... | design | design_only |
| 5 | D-SIGNAL/4-Min Aggregation vs 3-Sec Tick 4分钟聚合版本vs3... | 4-Min Aggregation vs 3-Sec Tick 4分钟... | design | design_only |
| 6 | D-SIGNAL/A-Share 4-Min Surge Anomaly Detector A股4分钟涨... | A-Share 4-Min Surge Anomaly Detector ... | design | design_only |
| 7 | D-SIGNAL/A-Share Auction Session Analyzer A股集合竞价分析器 | A-Share Auction Session Analyzer A股... | design | design_only |
| 8 | D-SIGNAL/A-Share Auction Weak-to-Strong Detector A股竞价... | A-Share Auction Weak-to-Strong Detect... | design | design_only |
| 9 | D-SIGNAL/A-Share Broken Board Definer A股烂板定义判定器 | A-Share Broken Board Definer A股烂板... | design | design_only |
| 10 | D-SIGNAL/A-Share Capital Flow Pattern A股资金流模式 | A-Share Capital Flow Pattern A股资金... | design | design_only |
| 11 | D-SIGNAL/A-Share Capital Flow Signal A股资金流向信号 | A-Share Capital Flow Signal A股资金流... | design | design_only |
| 12 | D-SIGNAL/A-Share Capital-Force Conflict Arbiter A股主力游... | A-Share Capital-Force Conflict Arbite... | design | design_only |
| 13 | D-SIGNAL/A-Share Capital-Force Conflict Observer A股主力... | A-Share Capital-Force Conflict Observ... | design | design_only |
| 14 | D-SIGNAL/A-Share Contrarian Capital 5-Day Tracker A股逆势... | A-Share Contrarian Capital 5-Day Trac... | design | design_only |
| 15 | D-SIGNAL/A-Share Contrarian Signal Phase Filter A股逆势信... | A-Share Contrarian Signal Phase Filte... | design | design_only |
| 16 | D-SIGNAL/A-Share Contrarian Signal Sensitivity Configurat... | A-Share Contrarian Signal Sensitivity... | design | design_only |
| 17 | D-SIGNAL/A-Share Decision Priority Engine A股决策优先级引擎 | A-Share Decision Priority Engine A股... | design | design_only |
| 18 | D-SIGNAL/A-Share Dual-Engine 5-Type Decision Mapper A股双... | A-Share Dual-Engine 5-Type Decision M... | design | design_only |
| 19 | D-SIGNAL/A-Share Dual-Engine Fusion 引擎 | A-Share Dual-Engine Fusion 引擎 | design | design_only |
| 20 | D-SIGNAL/A-Share Emergency Opportunity Evaluator A股应急... | A-Share Emergency Opportunity Evaluat... | design | design_only |
| 21 | D-SIGNAL/A-Share Emotion Cycle 4+1 Stage Action Mapper A... | A-Share Emotion Cycle 4+1 Stage Actio... | design | design_only |
| 22 | D-SIGNAL/A-Share Emotion Ladder Classifier A股情绪梯队自... | A-Share Emotion Ladder Classifier A股... | design | design_only |
| 23 | D-SIGNAL/A-Share Gap Support-Pressure Converter A股跳空缺... | A-Share Gap Support-Pressure Converte... | design | design_only |
| 24 | D-SIGNAL/A-Share Institutional Behavior A股机构行为 | A-Share Institutional Behavior A股机... | design | design_only |
| 25 | D-SIGNAL/A-Share Intraday Buy/Sell Point A股日内买卖点 | A-Share Intraday Buy/Sell Point A股日... | design | design_only |
| 26 | D-SIGNAL/A-Share Intraday Pattern Analyzer A股分时形态分析器 | A-Share Intraday Pattern Analyzer A股... | design | design_only |
| 27 | D-SIGNAL/A-Share KDJ-MACD Multi-Period Screener A股KDJ三... | A-Share KDJ-MACD Multi-Period Screene... | design | design_only |
| 28 | D-SIGNAL/A-Share Limit-Up Gene Evaluator A股涨停基因4维评... | A-Share Limit-Up Gene Evaluator A股涨... | design | design_only |
| 29 | D-SIGNAL/A-Share Market Breadth Monitor A股市场真实广度监... | A-Share Market Breadth Monitor A股市... | design | design_only |
| 30 | D-SIGNAL/A-Share Market Direction Predictor A股大盘方向预... | A-Share Market Direction Predictor A... | design | design_only |
| 31 | D-SIGNAL/A-Share Market Microstructure Signal A股微观结构... | A-Share Market Microstructure Signal ... | design | design_only |
| 32 | D-SIGNAL/A-Share Market Phase Threshold Classifier A股市... | A-Share Market Phase Threshold Classi... | design | design_only |
| 33 | D-SIGNAL/A-Share Market Sentiment A股市场情绪 | A-Share Market Sentiment A股市场情绪 | design | design_only |
| 34 | D-SIGNAL/A-Share Multi-Concept Overlay Bonus Calculator A... | A-Share Multi-Concept Overlay Bonus C... | design | design_only |
| 35 | D-SIGNAL/A-Share Multi-Day Breakdown Confirmer A股有效跌... | A-Share Multi-Day Breakdown Confirmer... | design | design_only |
| 36 | D-SIGNAL/A-Share Multi-Index Decline Period Detector A股... | A-Share Multi-Index Decline Period De... | design | design_only |
| 37 | D-SIGNAL/A-Share National Team Dual-Mode Identifier A股国... | A-Share National Team Dual-Mode Ident... | design | design_only |
| 38 | D-SIGNAL/A-Share Order Book Microstructure Analyzer A股盘... | A-Share Order Book Microstructure Ana... | design | design_only |
| 39 | D-SIGNAL/A-Share Plan Conformity Evaluator A股计划吻合度... | A-Share Plan Conformity Evaluator A股... | design | design_only |
| 40 | D-SIGNAL/A-Share Policy Signal A股政策信号 | A-Share Policy Signal A股政策信号 | design | design_only |
| 41 | D-SIGNAL/A-Share Post-Buy Quick Diagnostician A股买入后5-... | A-Share Post-Buy Quick Diagnostician ... | design | design_only |
| 42 | D-SIGNAL/A-Share Quant Short-term Strength A股量化短线强度 | A-Share Quant Short-term Strength A股... | design | design_only |
| 43 | D-SIGNAL/A-Share Rotation Warning Signaler A股轮动预警信号器 | A-Share Rotation Warning Signaler A股... | design | design_only |
| 44 | D-SIGNAL/A-Share Seal Order Level Jump Detector A股封单级... | A-Share Seal Order Level Jump Detecto... | design | design_only |
| 45 | D-SIGNAL/A-Share Sector Analyzer 分析器 | A-Share Sector Analyzer 分析器 | design | design_only |
| 46 | D-SIGNAL/A-Share Sector Capital Rotation Timeline A股板块... | A-Share Sector Capital Rotation Timel... | design | design_only |
| 47 | D-SIGNAL/A-Share Sector Dual-List Cross Filter A股板块双... | A-Share Sector Dual-List Cross Filter... | design | design_only |
| 48 | D-SIGNAL/A-Share Short-term Stock Selector A股短线选股器 | A-Share Short-term Stock Selector A股... | design | design_only |
| 49 | D-SIGNAL/A-Share Signal Post-Rise Filter A股信号后涨幅过滤器 | A-Share Signal Post-Rise Filter A股信... | design | design_only |
| 50 | D-SIGNAL/A-Share Unexpected Strength/Weakness Detector A... | A-Share Unexpected Strength/Weakness ... | design | design_only |
| 51 | D-SIGNAL/A-Share Youzi Relay Emotion A股游资接力情绪 | A-Share Youzi Relay Emotion A股游资接... | design | design_only |
| 52 | D-SIGNAL/AST Sandbox AST沙箱三层安全 | AST Sandbox AST沙箱三层安全 | design | design_only |
| 53 | D-SIGNAL/Agent Hallucination Output Agent输出异常幻觉 | Agent Hallucination Output Agent输出... | design | design_only |
| 54 | D-SIGNAL/AgentFeedbackRound Agent反馈轮次 | AgentFeedbackRound Agent反馈轮次 | design | design_only |
| 55 | D-SIGNAL/Aggregator Base GRE基础 | Aggregator Base GRE基础 | design | design_only |
| 56 | D-SIGNAL/Analyst Agent Feedback Loop 分析师Agent反馈循环 | Analyst Agent Feedback Loop 分析师Age... | design | design_only |
| 57 | D-SIGNAL/Atomic Strategy Module Library 原子化策略模块库 | Atomic Strategy Module Library 原子化... | design | design_only |
| 58 | D-SIGNAL/Auction Direction Prediction 竞价方向预测 | Auction Direction Prediction 竞价方向... | design | design_only |
| 59 | D-SIGNAL/Auction Microstructure Signal Module 竞价微结构... | Auction Microstructure Signal Module ... | design | design_only |
| 60 | D-SIGNAL/Auction Trap 竞价陷阱 | Auction Trap 竞价陷阱 | design | design_only |
| 61 | D-SIGNAL/A股信号子域 | A股信号子域 | design | design_only |
| 62 | D-SIGNAL/BMA Bayesian Model Averaging BMA贝叶斯模型平均 | BMA Bayesian Model Averaging BMA贝叶... | design | design_only |
| 63 | D-SIGNAL/BVC Method BVC统计推断方法 | BVC Method BVC统计推断方法 | design | design_only |
| 64 | D-SIGNAL/BayesianModelAveraging BMA贝叶斯模型平均 | BayesianModelAveraging BMA贝叶斯模型平均 | design | design_only |
| 65 | D-SIGNAL/Behavioral Bias Engine 行为偏差引擎 | Behavioral Bias Engine 行为偏差引擎 | design | design_only |
| 66 | D-SIGNAL/Book Imbalance 订单簿不平衡 | Book Imbalance 订单簿不平衡 | design | design_only |
| 67 | D-SIGNAL/BullTrapQuantified 诱多量化 | BullTrapQuantified 诱多量化 | design | design_only |
| 68 | D-SIGNAL/BuySignal 买入信号契约 | BuySignal 买入信号契约 | design | design_only |
| 69 | D-SIGNAL/C-011 主力行为识别 Main Force Behavior Recognition | C-011 主力行为识别 Main Force Behavio... | design | design_only |
| 70 | D-SIGNAL/C-014 大盘预测 Market Prediction | C-014 大盘预测 Market Prediction | design | design_only |
| 71 | D-SIGNAL/C-021 市场状态 Market State | C-021 市场状态 Market State | design | design_only |
| 72 | D-SIGNAL/C-034 主力画像 Main Force Profile | C-034 主力画像 Main Force Profile | design | design_only |
| 73 | D-SIGNAL/C-039 跨市场传导 Cross-market Transmission | C-039 跨市场传导 Cross-market Transmi... | design | design_only |
| 74 | D-SIGNAL/CTR-002消费契约适配器 CTR-002 Contract Adapter | CTR-002消费契约适配器 CTR-002 Contrac... | design | design_only |
| 75 | D-SIGNAL/CTR-TRACE-001 TraceContext传播器 | CTR-TRACE-001 TraceContext传播器 | design | design_only |
| 76 | D-SIGNAL/Calendar Constraint Layer 日历约束层 | Calendar Constraint Layer 日历约束层 | design | design_only |
| 77 | D-SIGNAL/Candlestick Pattern Recognizer 蜡烛图模式识别器 | Candlestick Pattern Recognizer 蜡烛图... | design | design_only |
| 78 | D-SIGNAL/Canvas Drag-Connect Engine 画布拖拽连线引擎 | Canvas Drag-Connect Engine 画布拖拽连... | design | design_only |
| 79 | D-SIGNAL/Capital Allocation Constraint Validator 资本分配... | Capital Allocation Constraint Validat... | design | design_only |
| 80 | D-SIGNAL/Capital Allocator 资金分配器 | Capital Allocator 资金分配器 | design | design_only |
| 81 | D-SIGNAL/CapitalAllocationResult CTR-P1-003 Builder Capit... | CapitalAllocationResult CTR-P1-003 Bu... | design | design_only |
| 82 | D-SIGNAL/CapitulationBottom 投降底部 | CapitulationBottom 投降底部 | design | design_only |
| 83 | D-SIGNAL/Causal KG 因果知识图谱 | Causal KG 因果知识图谱 | design | design_only |
| 84 | D-SIGNAL/Causal Relationship Extraction 因果关系提取 | Causal Relationship Extraction 因果关... | design | design_only |
| 85 | D-SIGNAL/CausalKGEdge Causal KG因果方向标注 | CausalKGEdge Causal KG因果方向标注 | design | design_only |
| 86 | D-SIGNAL/CausalML 因果机器学习 | CausalML 因果机器学习 | design | design_only |
| 87 | D-SIGNAL/CausalPrior LLM引导因果发现先验 | CausalPrior LLM引导因果发现先验 | design | design_only |
| 88 | D-SIGNAL/CausalRL CausalRL因果约束强化学习 | CausalRL CausalRL因果约束强化学习 | design | design_only |
| 89 | D-SIGNAL/Chan Theory Pen-Segment-Pivot Recognizer 缠论笔... | Chan Theory Pen-Segment-Pivot Recogni... | design | design_only |
| 90 | D-SIGNAL/Chart Pattern Recognition Algorithm Library 图形... | Chart Pattern Recognition Algorithm L... | design | design_only |
| 91 | D-SIGNAL/Click First or Last 早晚下单策略 | Click First or Last 早晚下单策略 | design | design_only |
| 92 | D-SIGNAL/Code Generation Flow Orchestrator 代码生成流程编... | Code Generation Flow Orchestrator 代... | design | design_only |
| 93 | D-SIGNAL/CompositeSignal 复合信号契约 | CompositeSignal 复合信号契约 | design | design_only |
| 94 | D-SIGNAL/CompositeSignal 复合信号聚合根 | CompositeSignal 复合信号聚合根 | design | design_only |
| 95 | D-SIGNAL/Concept Net Inflow Aggregation 概念级资金净流入聚合 | Concept Net Inflow Aggregation 概念级... | design | design_only |
| 96 | D-SIGNAL/Conditional Density Prediction 收益率条件密度预测 | Conditional Density Prediction 收益率... | design | design_only |
| 97 | D-SIGNAL/Conflict Detection 矛盾检测 | Conflict Detection 矛盾检测 | design | design_only |
| 98 | D-SIGNAL/Contradictory Signal Processing 矛盾信号处理 | Contradictory Signal Processing 矛盾... | design | design_only |
| 99 | D-SIGNAL/Contradictory Signal Resolver 矛盾信号解决器 | Contradictory Signal Resolver 矛盾信... | design | design_only |
| 100 | D-SIGNAL/Contrarian Capital Flow Signal Module 逆势资金流... | Contrarian Capital Flow Signal Module... | design | design_only |
| 101 | D-SIGNAL/Contrarian Fund Flow Identification 逆势资金流识... | Contrarian Fund Flow Identification ... | design | design_only |
| 102 | D-SIGNAL/Contrarian-L2B Linkage 逆势资金流与L2-B主力行为... | Contrarian-L2B Linkage 逆势资金流与L2... | design | design_only |
| 103 | D-SIGNAL/Contrarian-L2C Linkage 逆势资金流与L2-C市场状态... | Contrarian-L2C Linkage 逆势资金流与L2... | design | design_only |
| 104 | D-SIGNAL/Contrarian-L3 Linkage 逆势资金流与L3策略工厂联动 | Contrarian-L3 Linkage 逆势资金流与L3... | design | design_only |
| 105 | D-SIGNAL/Contrarian-L3.5 Linkage 逆势资金流与L3.5仓位管理... | Contrarian-L3.5 Linkage 逆势资金流与L... | design | design_only |
| 106 | D-SIGNAL/Contrarian-L4 Linkage 逆势资金流与L4风控层联动 | Contrarian-L4 Linkage 逆势资金流与L4... | design | design_only |
| 107 | D-SIGNAL/Contrarian-Stock Selection Linkage 逆势资金流与... | Contrarian-Stock Selection Linkage 逆... | design | design_only |
| 108 | D-SIGNAL/Correlation Structure Collapse 相关性结构崩塌 | Correlation Structure Collapse 相关性... | design | design_only |
| 109 | D-SIGNAL/Create New 新建信号模块模式 | Create New 新建信号模块模式 | design | design_only |
| 110 | D-SIGNAL/D-L0 Degradation Level 0 降级等级0 | D-L0 Degradation Level 0 降级等级0 | design | design_only |
| 111 | D-SIGNAL/D-L1 Degradation Level 1 降级等级1 | D-L1 Degradation Level 1 降级等级1 | design | design_only |
| 112 | D-SIGNAL/D-L2 Degradation Level 2 降级等级2 | D-L2 Degradation Level 2 降级等级2 | design | design_only |
| 113 | D-SIGNAL/D-L3 Degradation Level 3 降级等级3 | D-L3 Degradation Level 3 降级等级3 | design | design_only |
| 114 | D-SIGNAL/DataIngestionFailed 数据接入失败事件 | DataIngestionFailed 数据接入失败事件 | design | design_only |
| 115 | D-SIGNAL/Decision Step Dependency Graph 决策环节依赖图 | Decision Step Dependency Graph 决策环... | design | design_only |
| 116 | D-SIGNAL/DecisionEvent 决策事件 | DecisionEvent 决策事件 | design | design_only |
| 117 | D-SIGNAL/Degradation Monitor 监控器 | Degradation Monitor 监控器 | design | design_only |
| 118 | D-SIGNAL/Degradation Notification Downstream Manager 降级... | Degradation Notification Downstream M... | design | design_only |
| 119 | D-SIGNAL/DivergenceDetection 背离检测 | DivergenceDetection 背离检测 | design | design_only |
| 120 | D-SIGNAL/Dual-Engine Fusion Decision 双引擎融合决策 | Dual-Engine Fusion Decision 双引擎融... | design | design_only |
| 121 | D-SIGNAL/Dynamic Conditional Correlation 动态条件相关 | Dynamic Conditional Correlation 动态... | design | design_only |
| 122 | D-SIGNAL/Dynamic Signal Weighting Model 动态信号权重模型 | Dynamic Signal Weighting Model 动态信... | design | design_only |
| 123 | D-SIGNAL/Dynamic Take-Profit Strategy Library 动态止盈策略库 | Dynamic Take-Profit Strategy Library ... | design | design_only |
| 124 | D-SIGNAL/Dynamic Weight Allocation 动态权重分配 | Dynamic Weight Allocation 动态权重分配 | design | design_only |
| 125 | D-SIGNAL/Dynamic Weight Allocator 动态权重分配器 | Dynamic Weight Allocator 动态权重分配器 | design | design_only |
| 126 | D-SIGNAL/Dynamic Weight Synthesis 动态权重合成策略 | Dynamic Weight Synthesis 动态权重合成... | design | design_only |
| 127 | D-SIGNAL/E-SG-01 D-SIGNAL→PA-02事件 | E-SG-01 D-SIGNAL→PA-02事件 | design | design_only |
| 128 | D-SIGNAL/Empty Signal NEUTRAL Strategy Manager 空信号NEUT... | Empty Signal NEUTRAL Strategy Manager... | design | design_only |
| 129 | D-SIGNAL/Equal Weight Allocation 等权分配策略 | Equal Weight Allocation 等权分配策略 | design | design_only |
| 130 | D-SIGNAL/Equal Weight Synthesis 等权合成策略 | Equal Weight Synthesis 等权合成策略 | design | design_only |
| 131 | D-SIGNAL/Evening Research Pipeline 晚间研究流水线 | Evening Research Pipeline 晚间研究流水线 | design | design_only |
| 132 | D-SIGNAL/Event-Driven Distribution Filter 事件驱动分布筛选 | Event-Driven Distribution Filter 事件... | design | design_only |
| 133 | D-SIGNAL/EvolutionRound 进化轮次 | EvolutionRound 进化轮次 | design | design_only |
| 134 | D-SIGNAL/Evolutionary Code Generation 进化式代码生成 | Evolutionary Code Generation 进化式代... | design | design_only |
| 135 | D-SIGNAL/ExecutionEvent 执行事件 | ExecutionEvent 执行事件 | design | design_only |
| 136 | D-SIGNAL/Explainable Design Constraint 可解释设计约束 | Explainable Design Constraint 可解释... | design | design_only |
| 137 | D-SIGNAL/Extend Module 信号模块扩展模式 | Extend Module 信号模块扩展模式 | design | design_only |
| 138 | D-SIGNAL/Factor Consistency Confidence Calculator 因子一... | Factor Consistency Confidence Calcula... | design | design_only |
| 139 | D-SIGNAL/Factor DSL 因子DSL约束 | Factor DSL 因子DSL约束 | design | design_only |
| 140 | D-SIGNAL/Factor Decay Linkage Degradation Handler 因子衰... | Factor Decay Linkage Degradation Hand... | design | design_only |
| 141 | D-SIGNAL/Factor IC Collective Decay 因子IC集体衰减 | Factor IC Collective Decay 因子IC集体... | design | design_only |
| 142 | D-SIGNAL/Factor Missing Ratio Calculator 因子缺失比例计算器 | Factor Missing Ratio Calculator 因子... | design | design_only |
| 143 | D-SIGNAL/Factor Validity Filter 因子有效性过滤器 | Factor Validity Filter 因子有效性过滤器 | design | design_only |
| 144 | D-SIGNAL/FactorMAD Debate FactorMAD双Agent辩论 | FactorMAD Debate FactorMAD双Agent辩论 | design | design_only |
| 145 | D-SIGNAL/Fund Source Identification 资金来源识别 | Fund Source Identification 资金来源识别 | design | design_only |
| 146 | D-SIGNAL/GARCHVolatilityForecast GARCH波动率预测 | GARCHVolatilityForecast GARCH波动率预测 | design | design_only |
| 147 | D-SIGNAL/GNN Stock Relationship Modeling GNN股票关系建模 | GNN Stock Relationship Modeling GNN股... | design | design_only |
| 148 | D-SIGNAL/Game Theory Knowledge 博弈知识 | Game Theory Knowledge 博弈知识 | design | design_only |
| 149 | D-SIGNAL/Gap Pattern Recognizer 缺口形态识别器 | Gap Pattern Recognizer 缺口形态识别器 | design | design_only |
| 150 | D-SIGNAL/GlobalMarketContagion 全球市场传染 | GlobalMarketContagion 全球市场传染 | design | design_only |
| 151 | D-SIGNAL/GraphRAG 图谱 | GraphRAG 图谱 | design | design_only |
| 152 | D-SIGNAL/HMMGMMRegimeDetection HMM/GMM体制识别 | HMMGMMRegimeDetection HMM/GMM体制识别 | design | design_only |
| 153 | D-SIGNAL/Herd Effect Critical State 散户羊群效应临界态 | Herd Effect Critical State 散户羊群效... | design | design_only |
| 154 | D-SIGNAL/High Open Strength 高开强度 | High Open Strength 高开强度 | design | design_only |
| 155 | D-SIGNAL/Hoeting Bayesian Model Averaging Hoeting贝叶斯模... | Hoeting Bayesian Model Averaging Hoet... | design | design_only |
| 156 | D-SIGNAL/IC Weighted Synthesis IC加权合成策略 | IC Weighted Synthesis IC加权合成策略 | design | design_only |
| 157 | D-SIGNAL/IC Weighted Synthesis Strategist IC加权合成策略器 | IC Weighted Synthesis Strategist IC加... | design | design_only |
| 158 | D-SIGNAL/IRCF Revision List IRCF因子补充修订清单 | IRCF Revision List IRCF因子补充修订清单 | design | design_only |
| 159 | D-SIGNAL/Incremental Factor Calculation 增量因子计算 | Incremental Factor Calculation 增量因... | design | design_only |
| 160 | D-SIGNAL/Institutional Retail Contrarian Flow IRCF因子 | Institutional Retail Contrarian Flow ... | design | design_only |
| 161 | D-SIGNAL/Interactive Time Series Annotation Tool 交互式时... | Interactive Time Series Annotation To... | design | design_only |
| 162 | D-SIGNAL/InterventionCausalEdge 带干预的时序因果发现结果 | InterventionCausalEdge 带干预的时序因... | design | design_only |
| 163 | D-SIGNAL/Intraday Auction Strategy 日内竞价策略 | Intraday Auction Strategy 日内竞价策略 | design | design_only |
| 164 | D-SIGNAL/Intraday Real-time Pipeline 盘中实时流水线 | Intraday Real-time Pipeline 盘中实时... | design | design_only |
| 165 | D-SIGNAL/K-Line Chart Interactive Toolset K线图交互工具集 | K-Line Chart Interactive Toolset K线... | design | design_only |
| 166 | D-SIGNAL/Knowledge Type Classification 知识类型分类 | Knowledge Type Classification 知识类... | design | design_only |
| 167 | D-SIGNAL/Kronos TSFM Kronos时序基础模型 | Kronos TSFM Kronos时序基础模型 | design | design_only |
| 168 | D-SIGNAL/L03 Predictions L03预测子模块 | L03 Predictions L03预测子模块 | design | design_only |
| 169 | D-SIGNAL/L03 Signals Default L03默认信号子模块 | L03 Signals Default L03默认信号子模块 | design | design_only |
| 170 | D-SIGNAL/L1 to L2-B Main Force Behavior L1→L2-B主力行为 | L1 to L2-B Main Force Behavior L1→L2... | design | design_only |
| 171 | D-SIGNAL/L1 to L2-C Market State L1→L2-C市场状态 | L1 to L2-C Market State L1→L2-C市场状态 | design | design_only |
| 172 | D-SIGNAL/L2-A Signal Layer 信号层 | L2-A Signal Layer 信号层 | design | design_only |
| 173 | D-SIGNAL/L2-A 信号数据 Signal Data | L2-A 信号数据 Signal Data | design | design_only |
| 174 | D-SIGNAL/L2-B Main Force Behavior Layer 主力行为层 | L2-B Main Force Behavior Layer 主力行... | design | design_only |
| 175 | D-SIGNAL/L2-B 主力行为 Main Force Behavior | L2-B 主力行为 Main Force Behavior | design | design_only |
| 176 | D-SIGNAL/L2-C Market State Layer 市场状态层 | L2-C Market State Layer 市场状态层 | design | design_only |
| 177 | D-SIGNAL/L2-C 市场状态与宏观 Market State & Macro | L2-C 市场状态与宏观 Market State & Macro | design | design_only |
| 178 | D-SIGNAL/L3.5 Position Management Layer 仓位管理层 | L3.5 Position Management Layer 仓位管... | design | design_only |
| 179 | D-SIGNAL/LLM Guided Causal Discovery LLM引导因果发现 | LLM Guided Causal Discovery LLM引导因... | design | design_only |
| 180 | D-SIGNAL/LLM Semantic Understanding LLM语义理解 | LLM Semantic Understanding LLM语义理解 | design | design_only |
| 181 | D-SIGNAL/LLM Strategy Agent LLM策略Agent | LLM Strategy Agent LLM策略Agent | design | design_only |
| 182 | D-SIGNAL/Late Session Contrarian Filter 尾盘逆势过滤 | Late Session Contrarian Filter 尾盘逆... | design | design_only |
| 183 | D-SIGNAL/Lee-Ready Algorithm Lee-Ready算法 | Lee-Ready Algorithm Lee-Ready算法 | design | design_only |
| 184 | D-SIGNAL/Lesson Learned Knowledge 教训知识 | Lesson Learned Knowledge 教训知识 | design | design_only |
| 185 | D-SIGNAL/Limit-Up Contrarian Filter 涨停板逆势过滤 | Limit-Up Contrarian Filter 涨停板逆势... | design | design_only |
| 186 | D-SIGNAL/LineageRoot 血缘根 | LineageRoot 血缘根 | design | design_only |
| 187 | D-SIGNAL/ML Enhanced Classification ML增强分类 | ML Enhanced Classification ML增强分类 | design | design_only |
| 188 | D-SIGNAL/ML Weight Synthesis ML权重合成策略 | ML Weight Synthesis ML权重合成策略 | design | design_only |
| 189 | D-SIGNAL/ML Weight Synthesis Strategist ML权重合成策略器 | ML Weight Synthesis Strategist ML权重... | design | design_only |
| 190 | D-SIGNAL/Macro Signal Generator 宏观信号生成器 | Macro Signal Generator 宏观信号生成器 | design | design_only |
| 191 | D-SIGNAL/MacroCausalEdge 宏观因果传导路径 | MacroCausalEdge 宏观因果传导路径 | design | design_only |
| 192 | D-SIGNAL/Market Crash Signal Enhancement 大盘急跌时信号增强 | Market Crash Signal Enhancement 大盘... | design | design_only |
| 193 | D-SIGNAL/Market State Agent 状态 | Market State Agent 状态 | design | design_only |
| 194 | D-SIGNAL/Market State Determination 市场状态判定 | Market State Determination 市场状态判定 | design | design_only |
| 195 | D-SIGNAL/Market State Knowledge 市场状态知识 | Market State Knowledge 市场状态知识 | design | design_only |
| 196 | D-SIGNAL/Model-Free Factor Fusion 因子直通层 | Model-Free Factor Fusion 因子直通层 | design | design_only |
| 197 | D-SIGNAL/Module Factory Dependency Graph 模块工厂依赖图 | Module Factory Dependency Graph 模块... | design | design_only |
| 198 | D-SIGNAL/Module Registry 信号模块注册表 | Module Registry 信号模块注册表 | design | design_only |
| 199 | D-SIGNAL/MomentumBreadth 动量广度 | MomentumBreadth 动量广度 | design | design_only |
| 200 | D-SIGNAL/MomentumLeadership 动量领导力 | MomentumLeadership 动量领导力 | design | design_only |

> (仅显示前 200 个模块，共 429 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 448 条 / 448 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 448 条 / 448 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 382 条 / edges                               │
│   [event]: 27 条 / edges                                         │
│   [contract]: 16 条 / edges                                      │
│   [data]: 11 条 / edges                                          │
│   [config_depends]: 7 条 / edges                                 │
│   [runtime]: 5 条 / edges                                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (382 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Signal Factory 信号工厂 → A-Share Emotion Ladder Cl...         │
│   Market State Determinatio... → SectorFlowReallocation 板...    │
│   Synthesizer 合成器 → Capital Allocator 资金分配器              │
│   Capital Allocator 资金分配器 → Degradation Monitor 监控器      │
│   Degradation Monitor 监控器 → Signal Audit Logger 信号审计      │
│   Signal Audit Logger 信号审计 → A-Share Institutional Beh...    │
│   A-Share Institutional Beh... → A-Share Capital Flow Patt...    │
│   A-Share Capital Flow Patt... → A-Share Short-term Stock ...    │
│   A-Share Short-term Stock ... → A-Share Intraday Buy/Sell...    │
│   A-Share Intraday Buy/Sell... → A-Share Market Sentiment ...    │
│   A-Share Market Sentiment ... → A-Share Sector Analyzer ...     │
│   A-Share Sector Analyzer ... → A-Share Youzi Relay Emoti...     │
│   A-Share Youzi Relay Emoti... → A-Share Quant Short-term ...    │
│   A-Share Quant Short-term ... → A-Share Dual-Engine Fusio...    │
│   A-Share Dual-Engine Fusio... → 策略异常退出处理 Strategy       │
│   策略异常退出处理 Strategy → L2-A 信号数据 Signal Data          │
│   L2-A 信号数据 Signal Data → L2-B 主力行为 Main Force ...       │
│   L2-B 主力行为 Main Force ... → L2-C 市场状态与宏观 Marke...    │
│   L2-C 市场状态与宏观 Marke... → 3秒级逆势资金流识别模块 C...    │
│   3秒级逆势资金流识别模块 C... → 大盘下跌状态实时判定 Mark...    │
│   大盘下跌状态实时判定 Mark... → 3秒级逆势资金流识别个股级...    │
│   3秒级逆势资金流识别个股级... → 3秒级逆势资金流识别概念/...     │
│   3秒级逆势资金流识别个股级... → P1 Regime Detector Readin...    │
│   3秒级逆势资金流识别概念/... → 逆势资金流信号分级与过滤 ...     │
│   逆势资金流信号分级与过滤 ... → 开盘竞价微结构分析模型 Op...    │
│   开盘竞价微结构分析模型 Op... → 竞价信息提取 Auction Info...    │
│   竞价信息提取 Auction Info... → 竞价行为分类 Auction Beha...    │
│   竞价行为分类 Auction Beha... → 竞价信号生成 Auction Sign...    │
│   竞价行为分类 Auction Beha... → Strategy Knowledge 策略知识     │
│   竞价信号生成 Auction Sign... → 因子可用性监控器 Factor A...    │
│   因子可用性监控器 Factor A... → CTR-TRACE-001 TraceContex...    │
│   因子可用性监控器 Factor A... → CausalPrior LLM引导因果发...    │
│   CTR-TRACE-001 TraceContex... → 因子计算结果消费桥接器 Fa...    │
│   因子计算结果消费桥接器 Fa... → 信号质量退化监控 Signal Q...    │
│   因子计算结果消费桥接器 Fa... → Hoeting Bayesian Model Av...    │
│   因子计算结果消费桥接器 Fa... → L1 to L2-C Market State L...    │
│   因子计算结果消费桥接器 Fa... → TimePC TimePC时间主成分         │
│   信号质量退化监控 Signal Q... → C-011 主力行为识别 Main F...    │
│   C-011 主力行为识别 Main F... → C-034 主力画像 Main Force...    │
│   C-011 主力行为识别 Main F... → Dynamic Conditional Corre...    │
│   C-011 主力行为识别 Main F... → LineageRoot 血缘根              │
│   C-034 主力画像 Main Force... → C-021 市场状态 Market State     │
│   C-021 市场状态 Market State → C-014 大盘预测 Market Pre...     │
│   C-014 大盘预测 Market Pre... → C-039 跨市场传导 Cross-ma...    │
│   C-014 大盘预测 Market Pre... → Create New 新建信号模块模式     │
│   C-039 跨市场传导 Cross-ma... → 活跃信号物化视图 Active S...    │
│   C-039 跨市场传导 Cross-ma... → Update Param 信号参数更新...    │
│   活跃信号物化视图 Active S... → Sentiment Signal Generato...    │
│   Sentiment Signal Generato... → Technical Signal Generato...    │
│   ...还有 333 条 / 333 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[event]** (27 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (16 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (11 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 448 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `38_d_signal_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
