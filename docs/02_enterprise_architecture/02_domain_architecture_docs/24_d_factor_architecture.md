---
doc_type: domain_architecture_diagram
title: D-FACTOR 因子架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 24_d_factor / 因子 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示因子（D-FACTOR）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 因子（D-FACTOR）的模块分布。共 318 个模块 / 318 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/factor/bus_factor_defense.py  [prototype]           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (16 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/factor/__init__.py  [prototype]                     │
│   src/zephyr/factor/_extensions/__init__.py  [scaffold_placeh... │
│   src/zephyr/factor/alpha_signal_pipeline.py  [prototype]        │
│   src/zephyr/factor/api/__init__.py  [scaffold_placeholder]      │
│   src/zephyr/factor/base.py  [production]                        │
│   src/zephyr/factor/core/__init__.py  [scaffold_placeholder]     │
│   src/zephyr/factor/ctr_001_consumer/__init__.py  [prototype]    │
│   src/zephyr/factor/engine/__init__.py  [prototype]              │
│   src/zephyr/factor/factor_base.py  [production]                 │
│   src/zephyr/factor/factors/__init__.py  [prototype]             │
│   src/zephyr/factor/factors/momentum_factor.py  [prototype]      │
│   src/zephyr/factor/factors/value_factor.py  [prototype]         │
│   src/zephyr/factor/infrastructure/__init__.py  [scaffold_pla... │
│   src/zephyr/factor/momentum_factor.py  [prototype]              │
│   src/zephyr/factor/services/__init__.py  [scaffold_placeholder] │
│   src/zephyr/factor/value_factor.py  [prototype]                 │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (301 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   10风格+28行业因子完整实现+验证 Factor  [design]                │
│   3-Level Judgment 三级判断  [design]                            │
│   39类漂移检测器实现复杂度 Detector  [design]                    │
│   6-Step Flow 6步流程  [design]                                  │
│   87-Alpha 87-Alpha因子  [design]                                │
│   87-Alpha 87Alpha因子  [design]                                 │
│   A-Share Capital Flow Factor 因子  [design]                     │
│   A-Share Microstructure Factor 因子  [design]                   │
│   ABS-001 Gate ABS-001门禁  [design]                             │
│   Alpha Factor Alpha因子  [design]                               │
│   Alpha Factor Calculation Engine 引擎因子  [design]             │
│   Alpha因子 Alpha Factor  [design]                               │
│   BVC方法 Bulk Volume Classification  [design]                   │
│   Backpressure 背压  [design]                                    │
│   Backpressure 背压控制  [design]                                │
│   Barra Risk Model 模型风险  [design]                            │
│   Barra因子权重方法论需MSCI参考实现  [design]                    │
│   Barra风险模型归D-FACTOR-06  [design]                           │
│   ...还有 283 个模块 / 283 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 318 个模块 / 318 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/factor/bus_factor_defense.py | src/zephyr/factor/bus_factor_defense.py | prototype | draft |

### L2 领域层 / Domain Layer (16 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/factor/__init__.py | src/zephyr/factor/__init__.py | prototype | draft |
| 2 | src/zephyr/factor/_extensions/__init__.py | src/zephyr/factor/_extensions/__init_... | scaffold_placeholder | orphan |
| 3 | src/zephyr/factor/alpha_signal_pipeline.py | src/zephyr/factor/alpha_signal_pipeli... | prototype | draft |
| 4 | src/zephyr/factor/api/__init__.py | src/zephyr/factor/api/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/factor/base.py | src/zephyr/factor/base.py | production | draft |
| 6 | src/zephyr/factor/core/__init__.py | src/zephyr/factor/core/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/factor/ctr_001_consumer/__init__.py | src/zephyr/factor/ctr_001_consumer/__... | prototype | orphan |
| 8 | src/zephyr/factor/engine/__init__.py | src/zephyr/factor/engine/__init__.py | prototype | orphan |
| 9 | src/zephyr/factor/factor_base.py | src/zephyr/factor/factor_base.py | production | draft |
| 10 | src/zephyr/factor/factors/__init__.py | src/zephyr/factor/factors/__init__.py | prototype | draft |
| 11 | src/zephyr/factor/factors/momentum_factor.py | src/zephyr/factor/factors/momentum_fa... | prototype | draft |
| 12 | src/zephyr/factor/factors/value_factor.py | src/zephyr/factor/factors/value_facto... | prototype | draft |
| 13 | src/zephyr/factor/infrastructure/__init__.py | src/zephyr/factor/infrastructure/__in... | scaffold_placeholder | orphan |
| 14 | src/zephyr/factor/momentum_factor.py | src/zephyr/factor/momentum_factor.py | prototype | draft |
| 15 | src/zephyr/factor/services/__init__.py | src/zephyr/factor/services/__init__.py | scaffold_placeholder | orphan |
| 16 | src/zephyr/factor/value_factor.py | src/zephyr/factor/value_factor.py | prototype | draft |

### 未分类 / Unclassified (301 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-FACTOR/10风格+28行业因子完整实现+验证 Factor | 10风格+28行业因子完整实现+验证 Factor | design | design_only |
| 2 | D-FACTOR/3-Level Judgment 三级判断 | 3-Level Judgment 三级判断 | design | design_only |
| 3 | D-FACTOR/39类漂移检测器实现复杂度 Detector | 39类漂移检测器实现复杂度 Detector | design | design_only |
| 4 | D-FACTOR/6-Step Flow 6步流程 | 6-Step Flow 6步流程 | design | design_only |
| 5 | D-FACTOR/87-Alpha 87-Alpha因子 | 87-Alpha 87-Alpha因子 | design | design_only |
| 6 | D-FACTOR/87-Alpha 87Alpha因子 | 87-Alpha 87Alpha因子 | design | design_only |
| 7 | D-FACTOR/A-Share Capital Flow Factor 因子 | A-Share Capital Flow Factor 因子 | design | design_only |
| 8 | D-FACTOR/A-Share Microstructure Factor 因子 | A-Share Microstructure Factor 因子 | design | design_only |
| 9 | D-FACTOR/ABS-001 Gate ABS-001门禁 | ABS-001 Gate ABS-001门禁 | design | design_only |
| 10 | D-FACTOR/Alpha Factor Alpha因子 | Alpha Factor Alpha因子 | design | design_only |
| 11 | D-FACTOR/Alpha Factor Calculation Engine 引擎因子 | Alpha Factor Calculation Engine 引擎因子 | design | design_only |
| 12 | D-FACTOR/Alpha因子 Alpha Factor | Alpha因子 Alpha Factor | design | design_only |
| 13 | D-FACTOR/BVC方法 Bulk Volume Classification | BVC方法 Bulk Volume Classification | design | design_only |
| 14 | D-FACTOR/Backpressure 背压 | Backpressure 背压 | design | design_only |
| 15 | D-FACTOR/Backpressure 背压控制 | Backpressure 背压控制 | design | design_only |
| 16 | D-FACTOR/Barra Risk Model 模型风险 | Barra Risk Model 模型风险 | design | design_only |
| 17 | D-FACTOR/Barra因子权重方法论需MSCI参考实现 | Barra因子权重方法论需MSCI参考实现 | design | design_only |
| 18 | D-FACTOR/Barra风险模型归D-FACTOR-06 | Barra风险模型归D-FACTOR-06 | design | design_only |
| 19 | D-FACTOR/Batch Output 批量输出 | Batch Output 批量输出 | design | design_only |
| 20 | D-FACTOR/CTR-001 Consumer CTR-001消费者 | CTR-001 Consumer CTR-001消费者 | design | design_only |
| 21 | D-FACTOR/CTR-001 Consumer 契约消费者 | CTR-001 Consumer 契约消费者 | design | design_only |
| 22 | D-FACTOR/CTR-002/003 Producer CTR-002/003生产者 | CTR-002/003 Producer CTR-002/003生产者 | design | design_only |
| 23 | D-FACTOR/CTR-002/003 Producer 契约生产者 | CTR-002/003 Producer 契约生产者 | design | design_only |
| 24 | D-FACTOR/CTR-P1-001 FactorMonitorReport CTR-P1-001 Factor... | CTR-P1-001 FactorMonitorReport CTR-P1... | design | design_only |
| 25 | D-FACTOR/CVD 累积买卖压力 Cumulative Volume Delta | CVD 累积买卖压力 Cumulative Volume Delta | design | design_only |
| 26 | D-FACTOR/CVD买卖压力追踪 Cumulative Volume Delta | CVD买卖压力追踪 Cumulative Volume Delta | design | design_only |
| 27 | D-FACTOR/CVD价格背离 CVD Price Divergence | CVD价格背离 CVD Price Divergence | design | design_only |
| 28 | D-FACTOR/Capital Flow 资金流 | Capital Flow 资金流 | design | design_only |
| 29 | D-FACTOR/Causal Factor Validation Layer 因果因子验证层 | Causal Factor Validation Layer 因果因... | design | design_only |
| 30 | D-FACTOR/Causal Validator 因果验证器 | Causal Validator 因果验证器 | design | design_only |
| 31 | D-FACTOR/Correlation Redundancy Remover 相关性去冗余 | Correlation Redundancy Remover 相关性... | design | design_only |
| 32 | D-FACTOR/Cross-Market Factor 跨市场因子 | Cross-Market Factor 跨市场因子 | design | design_only |
| 33 | D-FACTOR/Crowding Detection 拥挤度检测 | Crowding Detection 拥挤度检测 | design | design_only |
| 34 | D-FACTOR/D-AUTONOMY域就绪审计链门禁引擎 | D-AUTONOMY域就绪审计链门禁引擎 | design | design_only |
| 35 | D-FACTOR/D-FACTOR Engine 因子引擎 | D-FACTOR Engine 因子引擎 | design | design_only |
| 36 | D-FACTOR/D-FACTOR Engine 因子计算引擎 | D-FACTOR Engine 因子计算引擎 | design | design_only |
| 37 | D-FACTOR/D-FACTOR 因子 | D-FACTOR 因子 | design | design_only |
| 38 | D-FACTOR/D-FACTOR-01到04稳定运行产出IC历史数据大于20日 | D-FACTOR-01到04稳定运行产出IC历史数据... | design | design_only |
| 39 | D-FACTOR/D-FACTOR-04 Pipeline D-FACTOR-04管道 | D-FACTOR-04 Pipeline D-FACTOR-04管道 | design | design_only |
| 40 | D-FACTOR/DAG调度因子计算 | DAG调度因子计算 | design | design_only |
| 41 | D-FACTOR/DecayMonitor 因子衰减监控 | DecayMonitor 因子衰减监控 | design | design_only |
| 42 | D-FACTOR/Distribution Feature Engineering 分布特征工程 | Distribution Feature Engineering 分布... | design | design_only |
| 43 | D-FACTOR/Distribution Feature Engineering产出不入因子池 | Distribution Feature Engineering产出... | design | design_only |
| 44 | D-FACTOR/E-SIM-05 OverfittingDetected 过拟合检测触发 | E-SIM-05 OverfittingDetected 过拟合检... | design | design_only |
| 45 | D-FACTOR/ESG ESG因子 | ESG ESG因子 | design | design_only |
| 46 | D-FACTOR/Engine 引擎 | Engine 引擎 | design | design_only |
| 47 | D-FACTOR/Evaluation 评估器 | Evaluation 评估器 | design | design_only |
| 48 | D-FACTOR/Event Impact Assessment 事件影响评估 | Event Impact Assessment 事件影响评估 | design | design_only |
| 49 | D-FACTOR/Factor Attribution 因子归因 | Factor Attribution 因子归因 | design | design_only |
| 50 | D-FACTOR/Factor Correlation Analyzer 因子相关性分析器 | Factor Correlation Analyzer 因子相关... | design | design_only |
| 51 | D-FACTOR/Factor Definition Interface 因子定义接口 | Factor Definition Interface 因子定义接口 | design | design_only |
| 52 | D-FACTOR/Factor Dependency DAG Manager 因子依赖DAG管理器 | Factor Dependency DAG Manager 因子依... | design | design_only |
| 53 | D-FACTOR/Factor Dependency Graph DAG 因子依赖图DAG | Factor Dependency Graph DAG 因子依赖... | design | design_only |
| 54 | D-FACTOR/Factor Exposure Calculator 因子暴露计算器 | Factor Exposure Calculator 因子暴露计... | design | design_only |
| 55 | D-FACTOR/Factor Factory 因子工厂 | Factor Factory 因子工厂 | design | design_only |
| 56 | D-FACTOR/Factor Orthogonalizer 因子正交化器 | Factor Orthogonalizer 因子正交化器 | design | design_only |
| 57 | D-FACTOR/Factor Portfolio Optimizer 因子组合优化器 | Factor Portfolio Optimizer 因子组合优... | design | design_only |
| 58 | D-FACTOR/Factor Risk Budget Allocator 因子风险预算分配器 | Factor Risk Budget Allocator 因子风险... | design | design_only |
| 59 | D-FACTOR/Factor Turnover Analyzer 因子换手率分析器 | Factor Turnover Analyzer 因子换手率分... | design | design_only |
| 60 | D-FACTOR/Factor Value Feed 因子值供给 | Factor Value Feed 因子值供给 | design | design_only |
| 61 | D-FACTOR/FactorBase Interface Contract FactorBase接口契约 | FactorBase Interface Contract FactorB... | design | design_only |
| 62 | D-FACTOR/FactorComputationError 因子计算错误 | FactorComputationError 因子计算错误 | design | design_only |
| 63 | D-FACTOR/FactorMonitorReport 因子监控报告 | FactorMonitorReport 因子监控报告 | design | design_only |
| 64 | D-FACTOR/FactorResearched 因子已研究 | FactorResearched 因子已研究 | design | design_only |
| 65 | D-FACTOR/FactorResearched 因子研究完成 | FactorResearched 因子研究完成 | design | design_only |
| 66 | D-FACTOR/FactorSignal 因子信号 | FactorSignal 因子信号 | design | design_only |
| 67 | D-FACTOR/FactorSignal 因子信号契约 | FactorSignal 因子信号契约 | design | design_only |
| 68 | D-FACTOR/Feature Lifecycle Events 特征生命周期事件 | Feature Lifecycle Events 特征生命周期... | design | design_only |
| 69 | D-FACTOR/Feature Serving API 特征服务API | Feature Serving API 特征服务API | design | design_only |
| 70 | D-FACTOR/Feature Store 2.0声明式定义语言 Declarative Feat... | Feature Store 2.0声明式定义语言 Decla... | design | design_only |
| 71 | D-FACTOR/Feature Store归D-DATA-03 | Feature Store归D-DATA-03 | design | design_only |
| 72 | D-FACTOR/FeatureCreated 因子创建事件 | FeatureCreated 因子创建事件 | design | design_only |
| 73 | D-FACTOR/FeatureDecaying 因子衰减事件 | FeatureDecaying 因子衰减事件 | design | design_only |
| 74 | D-FACTOR/FeatureDeprecated 因子废弃事件 | FeatureDeprecated 因子废弃事件 | design | design_only |
| 75 | D-FACTOR/FeatureDormant 因子休眠事件 | FeatureDormant 因子休眠事件 | design | design_only |
| 76 | D-FACTOR/FeatureOnline 因子上线事件 | FeatureOnline 因子上线事件 | design | design_only |
| 77 | D-FACTOR/FeatureReactivated 因子重新激活事件 | FeatureReactivated 因子重新激活事件 | design | design_only |
| 78 | D-FACTOR/FeatureRegistered 因子注册事件 | FeatureRegistered 因子注册事件 | design | design_only |
| 79 | D-FACTOR/FeatureRetired 因子退役事件 | FeatureRetired 因子退役事件 | design | design_only |
| 80 | D-FACTOR/FeatureValidated 因子验证事件 | FeatureValidated 因子验证事件 | design | design_only |
| 81 | D-FACTOR/Fundamental 基本面 | Fundamental 基本面 | design | design_only |
| 82 | D-FACTOR/Fundamental 基本面因子 | Fundamental 基本面因子 | design | design_only |
| 83 | D-FACTOR/Global Market Contagion Quantification 全球市场... | Global Market Contagion Quantificatio... | design | design_only |
| 84 | D-FACTOR/Governance 因子治理 | Governance 因子治理 | design | design_only |
| 85 | D-FACTOR/Grayscale Rollout 灰度发布 | Grayscale Rollout 灰度发布 | design | design_only |
| 86 | D-FACTOR/HVN/LVN节点 High/Low Volume Node | HVN/LVN节点 High/Low Volume Node | design | design_only |
| 87 | D-FACTOR/HVN/LVN节点 Volume Profile HVN LVN | HVN/LVN节点 Volume Profile HVN LVN | design | design_only |
| 88 | D-FACTOR/IC Decay Analyzer IC衰减分析器 | IC Decay Analyzer IC衰减分析器 | design | design_only |
| 89 | D-FACTOR/IC Decay Detection IC衰减检测 | IC Decay Detection IC衰减检测 | design | design_only |
| 90 | D-FACTOR/IC/IR Evaluator IC/IR评估器 | IC/IR Evaluator IC/IR评估器 | design | design_only |
| 91 | D-FACTOR/IC_IR Calculator IC_IR计算器 | IC_IR Calculator IC_IR计算器 | design | design_only |
| 92 | D-FACTOR/IC_IR计算 IC_IR Calculator | IC_IR计算 IC_IR Calculator | design | design_only |
| 93 | D-FACTOR/IC因子替换 IC-Based Factor Replacement | IC因子替换 IC-Based Factor Replacement | design | design_only |
| 94 | D-FACTOR/IC衰减三级自动处置需D-AUTONOMY自愈引擎联动 | IC衰减三级自动处置需D-AUTONOMY自愈引... | design | design_only |
| 95 | D-FACTOR/IC衰减分析器 IC Decay Analyzer | IC衰减分析器 IC Decay Analyzer | design | design_only |
| 96 | D-FACTOR/IRCF因子 Institutional Retail Contrarian Flow | IRCF因子 Institutional Retail Contrar... | design | design_only |
| 97 | D-FACTOR/IRL IRL因子 | IRL IRL因子 | design | design_only |
| 98 | D-FACTOR/IRL 机构行为识别 | IRL 机构行为识别 | design | design_only |
| 99 | D-FACTOR/Institutional Behavior Factor 机构行为因子 | Institutional Behavior Factor 机构行... | design | design_only |
| 100 | D-FACTOR/Intraday 日内 | Intraday 日内 | design | design_only |
| 101 | D-FACTOR/Intraday 日内因子 | Intraday 日内因子 | design | design_only |
| 102 | D-FACTOR/KAN Explainable Function Approximator KAN可解释... | KAN Explainable Function Approximator... | design | design_only |
| 103 | D-FACTOR/L1 to L2-A Factor Calculation L1→L2-A因子计算 | L1 to L2-A Factor Calculation L1→L2-... | design | design_only |
| 104 | D-FACTOR/L1 因子计算层 Factor Compute Layer | L1 因子计算层 Factor Compute Layer | design | design_only |
| 105 | D-FACTOR/LLM本地部署需GPU大于16GB显存 | LLM本地部署需GPU大于16GB显存 | design | design_only |
| 106 | D-FACTOR/Layered Backtest 分层回测 | Layered Backtest 分层回测 | design | design_only |
| 107 | D-FACTOR/Lee-Ready算法 Lee-Ready Algorithm | Lee-Ready算法 Lee-Ready Algorithm | design | design_only |
| 108 | D-FACTOR/Lifecycle State Machine 生命周期状态机 | Lifecycle State Machine 生命周期状态机 | design | design_only |
| 109 | D-FACTOR/MacroFactorSignal 宏观因子信号 | MacroFactorSignal 宏观因子信号 | design | design_only |
| 110 | D-FACTOR/Market Structure Factor 市场结构因子 | Market Structure Factor 市场结构因子 | design | design_only |
| 111 | D-FACTOR/Microstructure 微观结构 | Microstructure 微观结构 | design | design_only |
| 112 | D-FACTOR/Multi-Factor Synthesis Validator 多因子合成验证器 | Multi-Factor Synthesis Validator 多因... | design | design_only |
| 113 | D-FACTOR/Northbound Capital Flow Model 北向资金流向模型 | Northbound Capital Flow Model 北向资... | design | design_only |
| 114 | D-FACTOR/Northbound Capital Signal 北向资金信号 | Northbound Capital Signal 北向资金信号 | design | design_only |
| 115 | D-FACTOR/OCP-001 FactorBase扩展点 | OCP-001 FactorBase扩展点 | design | design_only |
| 116 | D-FACTOR/OFI检测框架 Order Flow Imbalance | OFI检测框架 Order Flow Imbalance | design | design_only |
| 117 | D-FACTOR/Overnight Global Market Contagion Model 隔夜全球... | Overnight Global Market Contagion Mod... | design | design_only |
| 118 | D-FACTOR/PIT一致性保证 PIT Consistency Guarantee | PIT一致性保证 PIT Consistency Guarantee | design | design_only |
| 119 | D-FACTOR/POC Point of Control 控制点 | POC Point of Control 控制点 | design | design_only |
| 120 | D-FACTOR/POC 公允价值核心 Point of Control | POC 公允价值核心 Point of Control | design | design_only |
| 121 | D-FACTOR/Parameter Config Manager 参数配置管理器 | Parameter Config Manager 参数配置管理器 | design | design_only |
| 122 | D-FACTOR/Pastor-Stambaugh Liquidity Factor PS流动性因子 | Pastor-Stambaugh Liquidity Factor PS... | design | design_only |
| 123 | D-FACTOR/Pastor-Stambaugh Liquidity Factor Pastor-Stambau... | Pastor-Stambaugh Liquidity Factor Pas... | design | design_only |
| 124 | D-FACTOR/Pattern to Signal Converter 形态信号转化器 | Pattern to Signal Converter 形态信号... | design | design_only |
| 125 | D-FACTOR/Pipeline 因子与信号生产管线 | Pipeline 因子与信号生产管线 | design | design_only |
| 126 | D-FACTOR/Pipeline 管线 | Pipeline 管线 | design | design_only |
| 127 | D-FACTOR/RankNormalized 排名标准化契约 | RankNormalized 排名标准化契约 | design | design_only |
| 128 | D-FACTOR/Registry 注册表 | Registry 注册表 | design | design_only |
| 129 | D-FACTOR/SMC SMC因子 | SMC SMC因子 | design | design_only |
| 130 | D-FACTOR/SMC Smart Money Concept SMC聪明钱概念 | SMC Smart Money Concept SMC聪明钱概念 | design | design_only |
| 131 | D-FACTOR/Sector Factor 板块因子 | Sector Factor 板块因子 | design | design_only |
| 132 | D-FACTOR/Smart Money Concept算法实现 | Smart Money Concept算法实现 | design | design_only |
| 133 | D-FACTOR/Technical Indicator Factor 技术指标因子 | Technical Indicator Factor 技术指标因子 | design | design_only |
| 134 | D-FACTOR/Tecton被Databricks收购影响 Tecton Acquisition Im... | Tecton被Databricks收购影响 Tecton Acq... | design | design_only |
| 135 | D-FACTOR/Timing Engine 择时引擎 | Timing Engine 择时引擎 | design | design_only |
| 136 | D-FACTOR/Timing Engine 时机引擎 | Timing Engine 时机引擎 | design | design_only |
| 137 | D-FACTOR/UFL Deterministic Fact Layer UFL确定性事实层 | UFL Deterministic Fact Layer UFL确定... | design | design_only |
| 138 | D-FACTOR/VPIN 知情交易概率 VPIN | VPIN 知情交易概率 VPIN | design | design_only |
| 139 | D-FACTOR/Value Area 价值区域 | Value Area 价值区域 | design | design_only |
| 140 | D-FACTOR/Volume Profile量能分布 Volume Profile | Volume Profile量能分布 Volume Profile | design | design_only |
| 141 | D-FACTOR/compute返回类型统一为list FactorSignal | compute返回类型统一为list FactorSignal | design | design_only |
| 142 | D-FACTOR/consistency_check 一致性引擎 | consistency_check 一致性引擎 | design | design_only |
| 143 | D-FACTOR/incremental_compute 增量因子计算 | incremental_compute 增量因子计算 | design | design_only |
| 144 | D-FACTOR/qwen3:8b模型权重需下载部署 | qwen3:8b模型权重需下载部署 | design | design_only |
| 145 | D-FACTOR/一致性引擎 Consistency Engine | 一致性引擎 Consistency Engine | design | design_only |
| 146 | D-FACTOR/一高七矮 Volume Profile HVN LVN | 一高七矮 Volume Profile HVN LVN | design | design_only |
| 147 | D-FACTOR/下跌强度分级 Down Strength Classification | 下跌强度分级 Down Strength Classifica... | design | design_only |
| 148 | D-FACTOR/主力净流入 Institutional Net Inflow Factor | 主力净流入 Institutional Net Inflow F... | design | design_only |
| 149 | D-FACTOR/主力吸筹 Accumulation Factor | 主力吸筹 Accumulation Factor | design | design_only |
| 150 | D-FACTOR/主力洗盘 Shakeout Factor | 主力洗盘 Shakeout Factor | design | design_only |
| 151 | D-FACTOR/主力派发 Distribution Factor | 主力派发 Distribution Factor | design | design_only |
| 152 | D-FACTOR/主力行为因子 Institutional Behavior Factor | 主力行为因子 Institutional Behavior F... | design | design_only |
| 153 | D-FACTOR/买卖价差估算需Level-2数据 | 买卖价差估算需Level-2数据 | design | design_only |
| 154 | D-FACTOR/五层筛选漏斗因子支撑 Factor | 五层筛选漏斗因子支撑 Factor | design | design_only |
| 155 | D-FACTOR/交互项构造 Interaction Feature Construction | 交互项构造 Interaction Feature Constr... | design | design_only |
| 156 | D-FACTOR/价格偏离度 Price Deviation | 价格偏离度 Price Deviation | design | design_only |
| 157 | D-FACTOR/传导系数 Cross-Market Transmission Coefficient | 传导系数 Cross-Market Transmission Co... | design | design_only |
| 158 | D-FACTOR/体制条件因子有效性 Regime-Conditional Factor Eff... | 体制条件因子有效性 Regime-Conditional... | design | design_only |
| 159 | D-FACTOR/体制条件因子衰减 Regime-Conditional Factor Decay | 体制条件因子衰减 Regime-Conditional F... | design | design_only |
| 160 | D-FACTOR/信号Agent Signal Gen Agent | 信号Agent Signal Gen Agent | design | design_only |
| 161 | D-FACTOR/入池观察池 Probation Pool | 入池观察池 Probation Pool | design | design_only |
| 162 | D-FACTOR/冰山单占比 Iceberg Order Ratio | 冰山单占比 Iceberg Order Ratio | design | design_only |
| 163 | D-FACTOR/冰山单检测 Hidden Order Detection Factor | 冰山单检测 Hidden Order Detection Factor | design | design_only |
| 164 | D-FACTOR/出货信号因子 Distribution Signal Factor | 出货信号因子 Distribution Signal Factor | design | design_only |
| 165 | D-FACTOR/分布形态统计量 Distribution Shape Statistics | 分布形态统计量 Distribution Shape Sta... | design | design_only |
| 166 | D-FACTOR/前视偏差检测归D-FACTOR-03 | 前视偏差检测归D-FACTOR-03 | design | design_only |
| 167 | D-FACTOR/北向持仓变化 Northbound Holding Change Factor | 北向持仓变化 Northbound Holding Chang... | design | design_only |
| 168 | D-FACTOR/十阶段生命周期状态机 Ten-stage Lifecycle | 十阶段生命周期状态机 Ten-stage Lifecycle | design | design_only |
| 169 | D-FACTOR/单一定义原则消除偏差 Single Definition Principle | 单一定义原则消除偏差 Single Definitio... | design | design_only |
| 170 | D-FACTOR/参数配置管理器 Parameter Config Manager | 参数配置管理器 Parameter Config Manager | design | design_only |
| 171 | D-FACTOR/双存储架构 Dual Storage Architecture | 双存储架构 Dual Storage Architecture | design | design_only |
| 172 | D-FACTOR/双模运行 Dual-Mode Operation | 双模运行 Dual-Mode Operation | design | design_only |
| 173 | D-FACTOR/另类因子 Alternative Factor | 另类因子 Alternative Factor | design | design_only |
| 174 | D-FACTOR/吸筹出货期检测 Accumulation Distribution Phase D... | 吸筹出货期检测 Accumulation Distribut... | design | design_only |
| 175 | D-FACTOR/因子-模型联合优化R&D-Agent-Quant | 因子-模型联合优化R&D-Agent-Quant | design | design_only |
| 176 | D-FACTOR/因子IC入池阈值分级 IC Threshold Tiered | 因子IC入池阈值分级 IC Threshold Tiered | design | design_only |
| 177 | D-FACTOR/因子IC大于0.03是有效性最低门槛 | 因子IC大于0.03是有效性最低门槛 | design | design_only |
| 178 | D-FACTOR/因子依赖DAG管理器 Factor Dependency DAG Manager | 因子依赖DAG管理器 Factor Dependency D... | design | design_only |
| 179 | D-FACTOR/因子依赖图DAG Factor Dependency DAG | 因子依赖图DAG Factor Dependency DAG | design | design_only |
| 180 | D-FACTOR/因子分类八大类 Factor | 因子分类八大类 Factor | design | design_only |
| 181 | D-FACTOR/因子性能审计 Factor Performance Audit | 因子性能审计 Factor Performance Audit | design | design_only |
| 182 | D-FACTOR/因子批量计算→Feature Store检查点 | 因子批量计算→Feature Store检查点 | design | design_only |
| 183 | D-FACTOR/因子数据血缘追踪 Factor Data Lineage Tracking | 因子数据血缘追踪 Factor Data Lineage ... | design | design_only |
| 184 | D-FACTOR/因子暴露合规 Factor Exposure Compliance | 因子暴露合规 Factor Exposure Compliance | design | design_only |
| 185 | D-FACTOR/因子暴露审计 Factor Exposure Audit | 因子暴露审计 Factor Exposure Audit | design | design_only |
| 186 | D-FACTOR/因子权重变更审批分级 Factor Weight Change Approv... | 因子权重变更审批分级 Factor Weight Ch... | design | design_only |
| 187 | D-FACTOR/因子池容量管理 Factor Management | 因子池容量管理 Factor Management | design | design_only |
| 188 | D-FACTOR/因子注册表合规 Factor Registry Compliance | 因子注册表合规 Factor Registry Compli... | design | design_only |
| 189 | D-FACTOR/因子版本管理 Factor Version Management | 因子版本管理 Factor Version Management | design | design_only |
| 190 | D-FACTOR/因子组合优化 Factor Portfolio Optimizer | 因子组合优化 Factor Portfolio Optimizer | design | design_only |
| 191 | D-FACTOR/因子血缘合规 Factor Lineage Compliance | 因子血缘合规 Factor Lineage Compliance | design | design_only |
| 192 | D-FACTOR/因子衰减三级自动处置 Factor | 因子衰减三级自动处置 Factor | design | design_only |
| 193 | D-FACTOR/因子衰减三级自动处置MILD MODERATE SEVERE | 因子衰减三级自动处置MILD MODERATE SEVERE | design | design_only |
| 194 | D-FACTOR/因子计算 增量因子计算 Factor Incremental | 因子计算 增量因子计算 Factor Incremental | design | design_only |
| 195 | D-FACTOR/因子计算审计日志 Factor Compute Audit Log | 因子计算审计日志 Factor Compute Audit... | design | design_only |
| 196 | D-FACTOR/因子退役审计 Factor Retirement Audit | 因子退役审计 Factor Retirement Audit | design | design_only |
| 197 | D-FACTOR/因子预处理管线归D-DATA-02 | 因子预处理管线归D-DATA-02 | design | design_only |
| 198 | D-FACTOR/因果推断库dowhy causalml | 因果推断库dowhy causalml | design | design_only |
| 199 | D-FACTOR/图形模式库 Pattern Library | 图形模式库 Pattern Library | design | design_only |
| 200 | D-FACTOR/图表形态识别 Chart Pattern Recognition | 图表形态识别 Chart Pattern Recognition | design | design_only |

> (仅显示前 200 个模块，共 301 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 308 条 / 308 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 308 条 / 308 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 203 条 / edges                               │
│   [config_depends]: 49 条 / edges                                │
│   [runtime]: 29 条 / edges                                       │
│   [event]: 13 条 / edges                                         │
│   [contract]: 9 条 / edges                                       │
│   [data]: 5 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (203 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Factor Factory 因子工厂 → 庄家行为模式识别 Market M...         │
│   Pipeline 因子与信号生产管线 → Evaluation 评估器                │
│   D-FACTOR 因子 → Engine 引擎                                    │
│   Engine 引擎 → Registry 注册表                                  │
│   Registry 注册表 → Evaluation 评估器                            │
│   Evaluation 评估器 → Pipeline 管线                              │
│   Pipeline 管线 → Barra Risk Model 模型风险                      │
│   Barra Risk Model 模型风险 → A-Share Capital Flow Fact...       │
│   A-Share Capital Flow Fact... → A-Share Microstructure Fa...    │
│   A-Share Microstructure Fa... → Alpha Factor Calculation ...    │
│   Alpha Factor Calculation ... → L1 因子计算层 Factor Comp...    │
│   L1 因子计算层 Factor Comp... → D-FACTOR Engine 因子计算引擎    │
│   D-FACTOR Engine 因子计算引擎 → 声明式因子定义 YAML DSL         │
│   声明式因子定义 YAML DSL → incremental_compute 增量...          │
│   incremental_compute 增量... → consistency_check 一致性引擎     │
│   consistency_check 一致性引擎 → Volume Profile量能分布 Vo...    │
│   Volume Profile量能分布 Vo... → HVN/LVN节点 High/Low Volu...    │
│   HVN/LVN节点 High/Low Volu... → Value Area 价值区域             │
│   Value Area 价值区域 → POC Point of Control 控制点              │
│   POC Point of Control 控制点 → CVD买卖压力追踪 Cumulativ...     │
│   CVD买卖压力追踪 Cumulativ... → VPIN 知情交易概率 VPIN          │
│   VPIN 知情交易概率 VPIN → IRCF因子 Institutional Re...          │
│   IRCF因子 Institutional Re... → OFI检测框架 Order Flow Im...    │
│   OFI检测框架 Order Flow Im... → Lee-Ready算法 Lee-Ready A...    │
│   Lee-Ready算法 Lee-Ready A... → BVC方法 Bulk Volume Class...    │
│   BVC方法 Bulk Volume Class... → 统一技术图形识别引擎 Unif...    │
│   统一技术图形识别引擎 Unif... → 图形模式库 Pattern Library      │
│   图形模式库 Pattern Library → 统一识别算法 Unified Reco...      │
│   统一识别算法 Unified Reco... → 多时间级别识别 Multi-Time...    │
│   多时间级别识别 Multi-Time... → 特征存储双存储架构 Featur...    │
│   特征存储双存储架构 Featur... → 离线存储 Offline Store          │
│   离线存储 Offline Store → 在线存储 Online Store                 │
│   在线存储 Online Store → 特征注册表 Feature Registry            │
│   特征注册表 Feature Registry → 训练-服务一致性保证 Train...     │
│   训练-服务一致性保证 Train... → 特征生命周期 Feature Life...    │
│   特征生命周期 Feature Life... → Governance 因子治理             │
│   Governance 因子治理 → DecayMonitor 因子衰减监控                │
│   DecayMonitor 因子衰减监控 → 一致性引擎 Consistency En...       │
│   Feature Store 2.0声明式定... → Distribution Feature Engi...    │
│   一致性引擎 Consistency En... → 实时特征计算管道 Real-tim...    │
│   特征发现与目录化 Feature ... → 滞后项构造 Lag Feature Co...    │
│   流式特征计算 Streaming Fe... → 一高七矮 Volume Profile H...    │
│   实时特征计算管道 Real-tim... → Factor Orthogonalizer 因...     │
│   Tecton被Databricks收购影... → CTR-001 Consumer CTR-001...      │
│   Factor Orthogonalizer 因... → Factor Exposure Calculato...     │
│   Factor Exposure Calculato... → Factor Risk Budget Alloca...    │
│   Factor Risk Budget Alloca... → Factor Correlation Analyz...    │
│   Factor Correlation Analyz... → Factor Turnover Analyzer ...    │
│   Factor Turnover Analyzer ... → Causal Validator 因果验证器     │
│   ...还有 154 条 / 154 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (49 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (29 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (13 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 308 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `24_d_factor_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
