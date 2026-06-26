---
module_id: KE-3061
title: Phase C 实现清单
category: session_log
ttl: permanent
---

# Phase C 实现清单

Phase C 实现清单

| 层 | 抽象基类 | 具体实现类 | 核心功能 |
|----|---------|-----------|---------|
| L00 | DataSourceBase | AkshareProvider | A 股历史/分钟线数据接入 |
| L00 | DataQualityGate | DefaultQualityGate | 5 项质检规则 |
| L03 | SignalAggregatorBase | DefaultSignalAggregator | 等权/置信度/IC 加权聚合 |
| L03 | CapitalAllocatorBase | DefaultCapitalAllocator | 等权/信号/Sharpe/风险平价 |
| L04 | PositionLimitCheckerBase | DefaultPositionLimitChecker | 单仓/行业/杠杆检查 |
| L04 | StopLossEngineBase | DefaultStopLossEngine | 固定/移动/时间/波动率止损 |
| L04 | RiskLimitsCalculator | DefaultRiskLimitsCalculator | VaR 估算 + IV 调整 |
| L04 | RiskValidator | DefaultRiskValidator | Pre-trade + Portfolio 校验 |
| L04 | RiskManagerOrchestratorBase | DefaultRiskManagerOrchestrator | 全编排 |
| L05 | StrategyBase | DefaultEquityStrategy | 等权/信号加权/最小方差 |
| L06 | BrokerInterface | SimulationBroker | 模拟成交 + 滑点/佣金 |
| L06 | (new) | OrderManager | 订单状态机 |
| L06 | (new) | ExecutionEngine | TWAP/VWAP/SOR |
| L07 | TCAEngineBase | DefaultTCAEngine | 滑点/佣金/IS |
| L07 | AttributionEngineBase | DefaultAttributionEngine | Brinson 分解 |
| L09 | BacktestEngineBase | DefaultBacktestEngine | 向量化日频回测 |
| L10 | SecurityGateway | DefaultSecurityGateway | 正则检测 + 审计决策 |
| L11 | InferenceEngineBase | DefaultInferenceEngine | 模型加载 + 批预测 |
| L13 | ExperimentPipelineBase | DefaultExperimentPipeline | A/B 对照 + 效应量/ p-value |
