---
module_id: MOD-PF-007
title: "绩效归因引擎蓝图 — Brinson 三因子 + 因子/风险归因 + 降级检测"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_portfolio_core
layer_name: portfolio_core
functional_domain: portfolio_core
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-PF-007 Performance Attribution Engine — 绩效归因引擎 蓝图

> **module_id**: MOD-PF-007 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7820845
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-10

## 1. 定位

绩效归因引擎——Brinson 三因子分解 + 因子/风险归因 + 策略降级检测:
- Brinson 三因子: 配置效应 + 选择效应 + 交互效应
- 因子归因: 各因子对组合收益的贡献分解
- 风险归因: 复用 MOD-RK-16 RiskDecomposer 分解风险来源
- 策略降级检测: IC 衰减 >50% → 权重归 0; 拥挤检测 ρ>0.8/0.9
- 实现 AttributionEngineBase OCP 契约 (D_REPORTING 可替换 DefaultAttributionEngine)

属 A 类基础设施(数学归因模型, 无策略决策), 归因结果供 D_REPORTING 消费。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | portfolio_id + period + 持仓历史 + 因子收益 | CTR-006 (PositionSnapshot) |
| 输出 | PerformanceAttributionReport | CTR-P1-009 |
| 依赖 | RiskDecomposer(MOD-RK-16) | import_depends |
| 依赖 | StrategyCorrelationGate(MOD-PA-004) | import_depends |
| 依赖 | PerformanceAttributionReport(CTR-P1-009) | contract |

## 3. 核心规则

### 3.1 Brinson 三因子分解

```
total_return = allocation_effect + selection_effect + interaction_effect

allocation_effect = Σ (w_p,i - w_b,i) × r_b,i    (配置效应)
selection_effect  = Σ w_b,i × (r_p,i - r_b,i)     (选择效应)
interaction_effect = Σ (w_p,i - w_b,i) × (r_p,i - r_b,i)  (交互效应)
```

- w_p,i: 组合中行业 i 权重, w_b,i: 基准中行业 i 权重
- r_p,i: 组合中行业 i 收益, r_b,i: 基准中行业 i 收益

### 3.2 因子归因

- 分解各因子(factor_id)对组合超额收益的贡献
- factor_contribution[i] = exposure_i × factor_return_i
- 汇总为 factor_contributions: Dict[str, float]

### 3.3 风险归因 (复用 MOD-RK-16)

- 调用 RiskDecomposer.decompose() 获取风险来源分解
- 输出: 系统性风险 vs idiosyncratic 风险占比
- 因子风险贡献: 各 Barra 因子的风险贡献

### 3.4 策略降级检测

| 检测项 | 阈值 | 动作 |
|--------|------|------|
| IC 衰减 | >50% (近期 IC / 历史均值) | 权重归 0 + 标记降级 |
| 策略拥挤 | ρ>0.8 | 权重减半 |
| 策略拥挤 | ρ>0.9 | 仅保留 IC 最高策略 |

- 降级检测结果附加在 PerformanceAttributionReport 的扩展字段

## 4. 关键不变量 (INVARIANTS)

- total_return = allocation + selection + interaction (守恒)
- factor_contributions 各值之和 ≈ selection_effect (因子归因解释选择效应)
- 降级检测不修改组合权重(仅标记建议, 由 PC-01 执行)
- 实现 AttributionEngineBase OCP 契约 (可被 D_REPORTING 替换)
- 交易成本拖累 transaction_cost_drag ≥ 0

## 5. 错误契约

- `AttributionDataIncompleteError`: 持仓历史/因子收益缺失
- `RiskDecompositionUnavailable`: RK-16 不可用(降级为跳过风险归因)
- `ICDecayDetectionError`: IC 数据不足(降级为跳过降级检测)

## 6. 测试

- `tests/pf_core/test_performance_attribution_engine.py`
- 覆盖: Brinson 三因子守恒、因子归因分解、风险归因(RK-16 复用)、IC 衰减降级、拥挤检测、OCP 契约实现、退化场景(空持仓/单标的)、幂等性

## 7. 依赖

- `zephyr.reporting.analytics_base` (AttributionEngineBase, OCP 契约)
- `zephyr.risk.core.risk_decomposition` (MOD-RK-16, 风险归因复用)
- `zephyr.pf_alloc.core.strategy_correlation_gate` (MOD-PA-004, 拥挤检测复用)
- `zephyr.shared.contracts.performance_attribution_report` (CTR-P1-009, 输出契约)
- 消费者: D_REPORTING (归因报告消费), D_GOV_ENFORCEMENT (降级检测审计)
