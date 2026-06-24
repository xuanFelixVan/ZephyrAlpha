---
doc_type: domain_architecture_diagram
title: D-CROSS_ASSET 跨资产架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 19_d_cross_asset / 跨资产 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示跨资产（D-CROSS_ASSET）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 跨资产（D-CROSS_ASSET）的模块分布。共 79 个模块 / 79 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (18 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   跨资产域  [design]                                             │
│   src/zephyr/cross_asset/__init__.py  [prototype]                │
│   src/zephyr/cross_asset/_extensions/__init__.py  [scaffold_p... │
│   跨资产分配器  [design]                                         │
│   src/zephyr/cross_asset/api/__init__.py  [scaffold_placeholder] │
│   src/zephyr/cross_asset/core/__init__.py  [scaffold_placehol... │
│   跨资产相关性  [design]                                         │
│   src/zephyr/cross_asset/cross_asset_risk_decomposer/__init__... │
│   src/zephyr/cross_asset/cross_market_data_adapter/__init__.p... │
│   src/zephyr/cross_asset/cross_market_data_adapter/ml_experim... │
│   src/zephyr/cross_asset/currency_hedger_and_fixed_income/__i... │
│   跨资产对冲  [design]                                           │
│   src/zephyr/cross_asset/infrastructure/__init__.py  [scaffol... │
│   src/zephyr/cross_asset/models/__init__.py  [scaffold_placeh... │
│   src/zephyr/cross_asset/risk_manager.py  [prototype]            │
│   src/zephyr/cross_asset/risk_manager_base.py  [prototype]       │
│   src/zephyr/cross_asset/services/__init__.py  [scaffold_plac... │
│   跨资产策略引擎  [design]                                       │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (61 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   AShareCrossMarketRiskMatrix A股跨市场风险矩阵  [design]        │
│   AShareQMTMultiMarketAdapter A股QMT多市场适配器  [design]       │
│   AutoSkill自动技能发现 AutoSkill Discovery  [design]            │
│   CommodityAnalyzer 大宗商品分析器  [design]                     │
│   Config Center 配置中心  [design]                               │
│   CorrelationRegimeDetector 相关性体制检测器  [design]           │
│   CorrelationRegimeDetector 相关性状态检测器  [design]           │
│   CorrelationRegimeShifted 相关性体制切换  [design]              │
│   CorrelationRegimeSignal 相关性体制信号  [design]               │
│   CreditRiskAnalyzer 信用风险分析器  [design]                    │
│   Cross Asset Cross Market Domain 跨资产跨市场域  [design]       │
│   Cross-Market Arbitrage Opportunity Scanner 跨市场套利机会扫... │
│   CrossAssetLiquidityMonitor 跨资产流动性监控器  [design]        │
│   CrossAssetPosition 跨资产持仓  [design]                        │
│   CrossAssetRisk 跨资产风险  [design]                            │
│   CrossBorderRegulatoryNavigator 跨境监管导航器  [design]        │
│   CrossMarketArbDetector 跨市场套利检测器  [design]              │
│   CrossMarketArbScanner 跨市场套利扫描器  [design]               │
│   ...还有 43 个模块 / 43 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 79 个模块 / 79 modules）。

### L2 领域层 / Domain Layer (18 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/cross_asset/ | 跨资产域 | design | design_only |
| 2 | src/zephyr/cross_asset/__init__.py | src/zephyr/cross_asset/__init__.py | prototype | draft |
| 3 | src/zephyr/cross_asset/_extensions/__init__.py | src/zephyr/cross_asset/_extensions/__... | scaffold_placeholder | orphan |
| 4 | src/zephyr/cross_asset/allocator/ | 跨资产分配器 | design | design_only |
| 5 | src/zephyr/cross_asset/api/__init__.py | src/zephyr/cross_asset/api/__init__.py | scaffold_placeholder | orphan |
| 6 | src/zephyr/cross_asset/core/__init__.py | src/zephyr/cross_asset/core/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/cross_asset/correlation/ | 跨资产相关性 | design | design_only |
| 8 | src/zephyr/cross_asset/cross_asset_risk_decomposer/__init... | src/zephyr/cross_asset/cross_asset_ri... | prototype | orphan |
| 9 | src/zephyr/cross_asset/cross_market_data_adapter/__init__.py | src/zephyr/cross_asset/cross_market_d... | prototype | draft |
| 10 | src/zephyr/cross_asset/cross_market_data_adapter/ml_exper... | src/zephyr/cross_asset/cross_market_d... | production | draft |
| 11 | src/zephyr/cross_asset/currency_hedger_and_fixed_income/_... | src/zephyr/cross_asset/currency_hedge... | prototype | orphan |
| 12 | src/zephyr/cross_asset/hedger/ | 跨资产对冲 | design | design_only |
| 13 | src/zephyr/cross_asset/infrastructure/__init__.py | src/zephyr/cross_asset/infrastructure... | scaffold_placeholder | orphan |
| 14 | src/zephyr/cross_asset/models/__init__.py | src/zephyr/cross_asset/models/__init_... | scaffold_placeholder | orphan |
| 15 | src/zephyr/cross_asset/risk_manager.py | src/zephyr/cross_asset/risk_manager.py | prototype | draft |
| 16 | src/zephyr/cross_asset/risk_manager_base.py | src/zephyr/cross_asset/risk_manager_b... | prototype | draft |
| 17 | src/zephyr/cross_asset/services/__init__.py | src/zephyr/cross_asset/services/__ini... | scaffold_placeholder | orphan |
| 18 | src/zephyr/cross_asset/strategy/ | 跨资产策略引擎 | design | design_only |

### 未分类 / Unclassified (61 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-CROSS-ASSET/AShareCrossMarketRiskMatrix A股跨市场风险矩阵 | AShareCrossMarketRiskMatrix A股跨市场... | design | design_only |
| 2 | D-CROSS-ASSET/AShareQMTMultiMarketAdapter A股QMT多市场适配器 | AShareQMTMultiMarketAdapter A股QMT多... | design | design_only |
| 3 | D-CROSS-ASSET/AutoSkill自动技能发现 AutoSkill Discovery | AutoSkill自动技能发现 AutoSkill Disco... | design | design_only |
| 4 | D-CROSS-ASSET/CommodityAnalyzer 大宗商品分析器 | CommodityAnalyzer 大宗商品分析器 | design | design_only |
| 5 | D-CROSS-ASSET/Config Center 配置中心 | Config Center 配置中心 | design | design_only |
| 6 | D-CROSS-ASSET/CorrelationRegimeDetector 相关性体制检测器 | CorrelationRegimeDetector 相关性体制... | design | design_only |
| 7 | D-CROSS-ASSET/CorrelationRegimeDetector 相关性状态检测器 | CorrelationRegimeDetector 相关性状态... | design | design_only |
| 8 | D-CROSS-ASSET/CorrelationRegimeShifted 相关性体制切换 | CorrelationRegimeShifted 相关性体制切换 | design | design_only |
| 9 | D-CROSS-ASSET/CorrelationRegimeSignal 相关性体制信号 | CorrelationRegimeSignal 相关性体制信号 | design | design_only |
| 10 | D-CROSS-ASSET/CreditRiskAnalyzer 信用风险分析器 | CreditRiskAnalyzer 信用风险分析器 | design | design_only |
| 11 | D-CROSS-ASSET/Cross Asset Cross Market Domain 跨资产跨市场域 | Cross Asset Cross Market Domain 跨资... | design | design_only |
| 12 | D-CROSS-ASSET/Cross-Market Arbitrage Opportunity Scanner ... | Cross-Market Arbitrage Opportunity Sc... | design | design_only |
| 13 | D-CROSS-ASSET/CrossAssetLiquidityMonitor 跨资产流动性监控器 | CrossAssetLiquidityMonitor 跨资产流动... | design | design_only |
| 14 | D-CROSS-ASSET/CrossAssetPosition 跨资产持仓 | CrossAssetPosition 跨资产持仓 | design | design_only |
| 15 | D-CROSS-ASSET/CrossAssetRisk 跨资产风险 | CrossAssetRisk 跨资产风险 | design | design_only |
| 16 | D-CROSS-ASSET/CrossBorderRegulatoryNavigator 跨境监管导航器 | CrossBorderRegulatoryNavigator 跨境监... | design | design_only |
| 17 | D-CROSS-ASSET/CrossMarketArbDetector 跨市场套利检测器 | CrossMarketArbDetector 跨市场套利检测器 | design | design_only |
| 18 | D-CROSS-ASSET/CrossMarketArbScanner 跨市场套利扫描器 | CrossMarketArbScanner 跨市场套利扫描器 | design | design_only |
| 19 | D-CROSS-ASSET/CrossMarketPropagationDetected 跨市场传导检测 | CrossMarketPropagationDetected 跨市场... | design | design_only |
| 20 | D-CROSS-ASSET/CrossMarketRegimeDelayDetector 跨市场Regime... | CrossMarketRegimeDelayDetector 跨市场... | design | design_only |
| 21 | D-CROSS-ASSET/CrossMarketRiskPropagator 跨市场风险传导器 | CrossMarketRiskPropagator 跨市场风险... | design | design_only |
| 22 | D-CROSS-ASSET/CurrencyExposureChanged 货币敞口变化 | CurrencyExposureChanged 货币敞口变化 | design | design_only |
| 23 | D-CROSS-ASSET/CurrencyHedger 货币对冲器 | CurrencyHedger 货币对冲器 | design | design_only |
| 24 | D-CROSS-ASSET/D-CROSS-ASSET | D-CROSS-ASSET | design | design_only |
| 25 | D-CROSS-ASSET/DigitalAssetAdapter 数字资产适配器 | DigitalAssetAdapter 数字资产适配器 | design | design_only |
| 26 | D-CROSS-ASSET/FixedIncomeAnalyzer 固收分析器 | FixedIncomeAnalyzer 固收分析器 | design | design_only |
| 27 | D-CROSS-ASSET/GlobalMacroScenarioGenerator 全球宏观情景生... | GlobalMacroScenarioGenerator 全球宏观... | design | design_only |
| 28 | D-CROSS-ASSET/Health Checker 健康检查器 | Health Checker 健康检查器 | design | design_only |
| 29 | D-CROSS-ASSET/HedgingRebalanceRequired 对冲再平衡触发 | HedgingRebalanceRequired 对冲再平衡触发 | design | design_only |
| 30 | D-CROSS-ASSET/Logger 日志器 | Logger 日志器 | design | design_only |
| 31 | D-CROSS-ASSET/Metrics Collector 指标采集器 | Metrics Collector 指标采集器 | design | design_only |
| 32 | D-CROSS-ASSET/MicrostructureAnalysisEngine 微观结构分析引擎 | MicrostructureAnalysisEngine 微观结构... | design | design_only |
| 33 | D-CROSS-ASSET/Multi-Market Data Router 多市场数据路由 | Multi-Market Data Router 多市场数据路由 | design | design_only |
| 34 | D-CROSS-ASSET/MultiMarketDataRouter 多市场数据路由器 | MultiMarketDataRouter 多市场数据路由器 | design | design_only |
| 35 | D-CROSS-ASSET/OptionsPricingGreeks 期权定价与Greeks | OptionsPricingGreeks 期权定价与Greeks | design | design_only |
| 36 | D-CROSS-ASSET/RealEstateAnalyzer 房地产分析器 | RealEstateAnalyzer 房地产分析器 | design | design_only |
| 37 | D-CROSS-ASSET/Retry & Circuit Breaker 重试与熔断器 | Retry & Circuit Breaker 重试与熔断器 | design | design_only |
| 38 | D-CROSS-ASSET/Task Scheduler 任务调度器 | Task Scheduler 任务调度器 | design | design_only |
| 39 | D-CROSS-ASSET/Tests 测试模块 | Tests 测试模块 | design | design_only |
| 40 | D-CROSS-ASSET/VolatilitySurfaceModeler 波动率曲面建模器 | VolatilitySurfaceModeler 波动率曲面建... | design | design_only |
| 41 | D-CROSS-ASSET/YieldCurveBuilder 收益率曲线构建器 | YieldCurveBuilder 收益率曲线构建器 | design | design_only |
| 42 | D-CROSS-ASSET/事件Schema版本管理 Event Schema Versioning | 事件Schema版本管理 Event Schema Versi... | design | design_only |
| 43 | D-CROSS-ASSET/在线EWC Online EWC | 在线EWC Online EWC | design | design_only |
| 44 | D-CROSS-ASSET/审计系统 Audit System | 审计系统 Audit System | design | design_only |
| 45 | D-CROSS-ASSET/情感传导时滞建模 Sentiment Propagation Dela... | 情感传导时滞建模 Sentiment Propagatio... | design | design_only |
| 46 | D-CROSS-ASSET/时变传导延迟函数 Time-Varying Propagation D... | 时变传导延迟函数 Time-Varying Propaga... | design | design_only |
| 47 | D-CROSS-ASSET/期货现货传导 Futures Spot Propagation | 期货现货传导 Futures Spot Propagation | design | design_only |
| 48 | D-CROSS-ASSET/汇率A股传导 FX A-Share Propagation | 汇率A股传导 FX A-Share Propagation | design | design_only |
| 49 | D-CROSS-ASSET/港股A股传导 HK A-Share Propagation | 港股A股传导 HK A-Share Propagation | design | design_only |
| 50 | D-CROSS-ASSET/美股A股传导 US A-Share Propagation | 美股A股传导 US A-Share Propagation | design | design_only |
| 51 | D-CROSS-ASSET/跨市场PIT管理器 Cross-Market PIT Manager | 跨市场PIT管理器 Cross-Market PIT Manager | design | design_only |
| 52 | D-CROSS-ASSET/跨市场公告NLP引擎 Cross-Market Filing NLP E... | 跨市场公告NLP引擎 Cross-Market Filing... | design | design_only |
| 53 | D-CROSS-ASSET/跨市场制度知识 Cross-Market Regime Knowledge | 跨市场制度知识 Cross-Market Regime Kn... | design | design_only |
| 54 | D-CROSS-ASSET/跨市场多模态融合引擎 Cross-Market Multimoda... | 跨市场多模态融合引擎 Cross-Market Mul... | design | design_only |
| 55 | D-CROSS-ASSET/跨市场情感传导检测 Cross-Market Sentiment P... | 跨市场情感传导检测 Cross-Market Senti... | design | design_only |
| 56 | D-CROSS-ASSET/跨市场情感引擎 Cross-Market Sentiment Engine | 跨市场情感引擎 Cross-Market Sentiment... | design | design_only |
| 57 | D-CROSS-ASSET/跨资产Feature Store Cross-Asset Feature Store | 跨资产Feature Store Cross-Asset Featu... | design | design_only |
| 58 | D-CROSS-ASSET/跨资产MLOps管线 Cross-Asset MLOps Pipeline | 跨资产MLOps管线 Cross-Asset MLOps Pip... | design | design_only |
| 59 | D-CROSS-ASSET/跨资产四层闭环架构 Cross-Asset Four-Layer A... | 跨资产四层闭环架构 Cross-Asset Four-L... | design | design_only |
| 60 | D-CROSS-ASSET/跨资产相关性知识 Cross-Asset Correlation Kn... | 跨资产相关性知识 Cross-Asset Correlat... | design | design_only |
| 61 | D-CROSS-ASSET/适配器机制 Adapter Mechanism | 适配器机制 Adapter Mechanism | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 63 条 / 63 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 63 条 / 63 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 54 条 / edges                                │
│   [event]: 4 条 / edges                                          │
│   [config_depends]: 2 条 / edges                                 │
│   [contract]: 2 条 / edges                                       │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (54 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-CROSS-ASSET → Multi-Market Data Router ...                   │
│   Multi-Market Data Router ... → CurrencyHedger 货币对冲器       │
│   CurrencyHedger 货币对冲器 → CorrelationRegimeDetector...       │
│   CorrelationRegimeDetector... → FixedIncomeAnalyzer 固收...     │
│   FixedIncomeAnalyzer 固收... → CrossMarketRiskPropagator...     │
│   CrossMarketRiskPropagator... → YieldCurveBuilder 收益率...     │
│   YieldCurveBuilder 收益率... → CreditRiskAnalyzer 信用风...     │
│   CreditRiskAnalyzer 信用风... → CommodityAnalyzer 大宗商...     │
│   CommodityAnalyzer 大宗商... → RealEstateAnalyzer 房地产...     │
│   RealEstateAnalyzer 房地产... → CrossMarketArbDetector 跨...    │
│   CrossMarketArbDetector 跨... → VolatilitySurfaceModeler ...    │
│   VolatilitySurfaceModeler ... → DigitalAssetAdapter 数字...     │
│   DigitalAssetAdapter 数字... → CrossAssetLiquidityMonito...     │
│   CrossAssetLiquidityMonito... → GlobalMacroScenarioGenera...    │
│   GlobalMacroScenarioGenera... → CrossBorderRegulatoryNavi...    │
│   GlobalMacroScenarioGenera... → CrossAssetPosition 跨资产...    │
│   CrossBorderRegulatoryNavi... → OptionsPricingGreeks 期权...    │
│   CrossBorderRegulatoryNavi... → Retry & Circuit Breaker ...     │
│   OptionsPricingGreeks 期权... → AShareCrossMarketRiskMatr...    │
│   OptionsPricingGreeks 期权... → Config Center 配置中心          │
│   AShareCrossMarketRiskMatr... → CrossMarketRegimeDelayDet...    │
│   CrossMarketRegimeDelayDet... → AShareQMTMultiMarketAdapt...    │
│   CrossMarketRegimeDelayDet... → Health Checker 健康检查器       │
│   CrossMarketRegimeDelayDet... → Cross Asset Cross Market ...    │
│   AShareQMTMultiMarketAdapt... → MicrostructureAnalysisEng...    │
│   AShareQMTMultiMarketAdapt... → 审计系统 Audit System           │
│   MicrostructureAnalysisEng... → CrossMarketArbScanner 跨...     │
│   MicrostructureAnalysisEng... → Logger 日志器                   │
│   MicrostructureAnalysisEng... → Task Scheduler 任务调度器       │
│   CrossMarketArbScanner 跨... → Tests 测试模块                   │
│   Metrics Collector 指标采集器 → 跨资产相关性知识 Cross-As...    │
│   Tests 测试模块 → Cross-Market Arbitrage Op...                  │
│   Cross-Market Arbitrage Op... → CorrelationRegimeDetector...    │
│   CorrelationRegimeDetector... → 适配器机制 Adapter Mechanism    │
│   适配器机制 Adapter Mechanism → 港股A股传导 HK A-Share Pr...    │
│   港股A股传导 HK A-Share Pr... → 美股A股传导 US A-Share Pr...    │
│   美股A股传导 US A-Share Pr... → 期货现货传导 Futures Spot...    │
│   期货现货传导 Futures Spot... → 汇率A股传导 FX A-Share Pr...    │
│   汇率A股传导 FX A-Share Pr... → 时变传导延迟函数 Time-Var...    │
│   时变传导延迟函数 Time-Var... → 跨资产Feature Store Cross...    │
│   跨资产Feature Store Cross... → 跨资产MLOps管线 Cross-Ass...    │
│   跨资产MLOps管线 Cross-Ass... → 跨资产四层闭环架构 Cross-...    │
│   跨资产四层闭环架构 Cross-... → 事件Schema版本管理 Event ...    │
│   事件Schema版本管理 Event ... → 跨市场制度知识 Cross-Mark...    │
│   跨市场制度知识 Cross-Mark... → 跨资产相关性知识 Cross-As...    │
│   跨资产相关性知识 Cross-As... → 在线EWC Online EWC              │
│   在线EWC Online EWC → AutoSkill自动技能发现 Aut...              │
│   AutoSkill自动技能发现 Aut... → 跨市场PIT管理器 Cross-Mar...    │
│   跨市场PIT管理器 Cross-Mar... → 跨市场情感引擎 Cross-Mark...    │
│   ...还有 5 条 / 5 more edges                                    │
└──────────────────────────────────────────────────────────────────┘

**[event]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 63 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `19_d_cross_asset_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
