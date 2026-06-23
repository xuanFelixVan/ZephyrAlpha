---
doc_type: domain_architecture_doc
title: D-CROSS_ASSET 跨资产架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-CROSS_ASSET 跨资产架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-CROSS_ASSET |
| 域名称 | 跨资产 |
| 架构层 | L2_domain |
| 模块总数 | 79 |
| 设计态模块 | 66 |
| 原型态模块 | 6 |
| 生产态模块 | 1 |
| 容量 | 1/150 (正常) |
| 描述 | 跨资产策略与配置 |

## 模块清单

共 79 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-CROSS-ASSET/AShareCrossMarketRiskMatrix A股跨市场风险矩阵 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/AShareQMTMultiMarketAdapter A股QMT多市场适配器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/AutoSkill自动技能发现 AutoSkill Discovery |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CommodityAnalyzer 大宗商品分析器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Config Center 配置中心 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CorrelationRegimeDetector 相关性体制检测器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CorrelationRegimeDetector 相关性状态检测器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CorrelationRegimeShifted 相关性体制切换 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CorrelationRegimeSignal 相关性体制信号 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CreditRiskAnalyzer 信用风险分析器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Cross Asset Cross Market Domain 跨资产跨市场域 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Cross-Market Arbitrage Opportunity Scanner 跨市场套利机会扫描器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossAssetLiquidityMonitor 跨资产流动性监控器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossAssetPosition 跨资产持仓 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossAssetRisk 跨资产风险 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossBorderRegulatoryNavigator 跨境监管导航器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossMarketArbDetector 跨市场套利检测器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossMarketArbScanner 跨市场套利扫描器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossMarketPropagationDetected 跨市场传导检测 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossMarketRegimeDelayDetector 跨市场Regime延迟检测器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CrossMarketRiskPropagator 跨市场风险传导器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CurrencyExposureChanged 货币敞口变化 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/CurrencyHedger 货币对冲器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/D-CROSS-ASSET |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/DigitalAssetAdapter 数字资产适配器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/FixedIncomeAnalyzer 固收分析器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/GlobalMacroScenarioGenerator 全球宏观情景生成器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Health Checker 健康检查器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/HedgingRebalanceRequired 对冲再平衡触发 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Logger 日志器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Metrics Collector 指标采集器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/MicrostructureAnalysisEngine 微观结构分析引擎 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Multi-Market Data Router 多市场数据路由 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/MultiMarketDataRouter 多市场数据路由器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/OptionsPricingGreeks 期权定价与Greeks |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/RealEstateAnalyzer 房地产分析器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Retry & Circuit Breaker 重试与熔断器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Task Scheduler 任务调度器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/Tests 测试模块 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/VolatilitySurfaceModeler 波动率曲面建模器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/YieldCurveBuilder 收益率曲线构建器 |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/事件Schema版本管理 Event Schema Versioning |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/在线EWC Online EWC |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/审计系统 Audit System |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/情感传导时滞建模 Sentiment Propagation Delay Modeling |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/时变传导延迟函数 Time-Varying Propagation Delay |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/期货现货传导 Futures Spot Propagation |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/汇率A股传导 FX A-Share Propagation |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/港股A股传导 HK A-Share Propagation |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/美股A股传导 US A-Share Propagation |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场PIT管理器 Cross-Market PIT Manager |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场公告NLP引擎 Cross-Market Filing NLP Engine |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场制度知识 Cross-Market Regime Knowledge |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场多模态融合引擎 Cross-Market Multimodal Fusion Engine |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场情感传导检测 Cross-Market Sentiment Propagation |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨市场情感引擎 Cross-Market Sentiment Engine |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨资产Feature Store Cross-Asset Feature Store |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨资产MLOps管线 Cross-Asset MLOps Pipeline |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨资产四层闭环架构 Cross-Asset Four-Layer Architecture |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/跨资产相关性知识 Cross-Asset Correlation Knowledge |  | design_only | design | 0 | 0 |
| D-CROSS-ASSET/适配器机制 Adapter Mechanism |  | design_only | design | 0 | 0 |
| src/zephyr/cross_asset/ | MOD-CROSS_ASSET | design_only | design | 0 | 0 |
| src/zephyr/cross_asset/__init__.py | MOD-CROSS_ASSET | draft | prototype | 1 | 0 |
| src/zephyr/cross_asset/_extensions/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/allocator/ | MOD-CROSS_ASSET | design_only | design | 0 | 0 |
| src/zephyr/cross_asset/api/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/core/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/correlation/ | MOD-CROSS_ASSET | design_only | design | 0 | 0 |
| src/zephyr/cross_asset/cross_asset_risk_decomposer/__init__.py | MOD-L04-001 | orphan | prototype | 0 | 0 |
| src/zephyr/cross_asset/cross_market_data_adapter/__init__.py | MOD-INF-002 | draft | prototype | 0 | 1 |
| src/zephyr/cross_asset/cross_market_data_adapter/ml_experiment_pipeline.py | MOD-INF-002 | draft | production | 3 | 1 |
| src/zephyr/cross_asset/currency_hedger_and_fixed_income/__init__.py | MOD-L04-001 | orphan | prototype | 0 | 0 |
| src/zephyr/cross_asset/hedger/ | MOD-CROSS_ASSET | design_only | design | 0 | 0 |
| src/zephyr/cross_asset/infrastructure/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/models/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/risk_manager.py | MOD-L04-001 | draft | prototype | 0 | 4 |
| src/zephyr/cross_asset/risk_manager_base.py | MOD-L04-001 | draft | prototype | 0 | 1 |
| src/zephyr/cross_asset/services/__init__.py | MOD-CROSS_ASSET | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/cross_asset/strategy/ | MOD-CROSS_ASSET | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 13 | contract,data,config_depends,event |
| D-SIGNAL | 10 | domain_dependency,contract,event,config_depends,data |
| D-INTEGRATION | 9 | contract,config_depends,event,data |
| D-INFRA_RUNTIME | 9 | event,config_depends,contract,data |
| D-SECURITY | 7 | contract,event,data |
| D-INTELLIGENCE | 6 | contract,config_depends,data |
| D-GOVERNANCE | 6 | config_depends,contract,event |
| D-AUTONOMY_CORE | 6 | data,contract,event |
| D-TRADING | 5 | contract,import_depends |
| D-MKT_DATA | 5 | data,contract,config_depends,event |
| D-INFRA_OPS | 5 | contract,event,data |
| D-DATA_ENG | 5 | contract,config_depends,data |
| D-PF_CORE | 4 | contract,event,data |
| D-FACTOR | 4 | config_depends,event,contract |
| D-SIMULATION | 3 | data,contract |
| D-REPORTING | 3 | contract,event |
| D-EX_SOR | 3 | contract,data,event |
| D-AUTONOMY_PERM | 3 | contract,event,data |
| D-PF_ALLOC | 2 | data,event |
| D-OPS | 2 | event,data |
| D-ML_TRAIN | 2 | event,data |
| D-KNOWLEDGE | 2 | event,config_depends |
| D-EX_CORE | 2 | contract,config_depends |
| D-SHARED | 1 | import_depends |
| D-ML_SERVE | 1 | data |
| D-FRONTEND | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 14 | config_depends,event,data,contract |
| D-GOVERNANCE | 2 | test_depends |

## 域内依赖图

详见 [d_cross_asset_dependency.mmd](d_cross_asset_dependency.mmd)
