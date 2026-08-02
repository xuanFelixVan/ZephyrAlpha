---
module_id: MOD-RK-05
title: "VaR 风险价值计算器蓝图 — 参数法+历史模拟法 Phase 1"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-RK-05 VaR Calculator — 风险价值计算器 蓝图

> **module_id**: MOD-RK-05 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-05 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-05, §6 VaR三阶段演进

## 1. 定位

VaR 风险价值计算器——Phase 1 实现参数法(方差-协方差)+历史模拟法并发计算, 取 max 作为保守估计。
供 RK-03 实时监控使用, 是组合潜在损失量化的核心基础设施。

Phase 2(未实现): +蒙特卡洛法(GPU CuPy/PyTorch)
Phase 3(未实现): Basel III 三角验证+乘数因子+压力 VaR

关键约束: 每阶段独立可用——Phase 1 完成即可上线风控。
属 A 类基础设施(正态分位数+经验分位数, 数学逻辑明确), 置信度/持有期为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 日收益序列 / 多资产收益矩阵+权重 | — |
| 输出 | VaRResult(value/value_pct/parametric_var/historical_var) | 联动 RK-03, RK-16 |
| 依赖 | portfolio_value, 历史收益(>=min_history) | — |

## 3. 核心规则 (设计真源 §1.2 RK-05, §6)

### 3.1 三方法

| 方法 | 公式 | 说明 |
|------|------|------|
| 参数法 | VaR = (z·σ - μ)·V·√T | 假设正态分布, z=|ppf(1-c)| |
| 历史模拟 | VaR = -quantile(r, 1-c)·V·√T | 经验分位数, 捕捉厚尾 |
| conservative_max | max(parametric, historical) | Phase 1 默认, 保守估计 |

### 3.2 多日缩放

- 多日 VaR ≈ 日 VaR · √T (平方根时间缩放法则)

### 3.3 样本要求

- 历史模拟法需 >= min_history(默认 30) 个有效样本
- NaN 收益自动过滤

## 4. 关键不变量 (INVARIANTS)

- VaR ≥ 0 (损失额非负, 高均值低波动时取 0 下限)
- conservative_max = max(parametric, historical)
- 样本不足 → 抛 InsufficientVaRHistoryError (Fail-Closed)
- 置信度 ∈ (0,1); holding_period ≥ 1

## 5. 错误契约

- `InvalidVaRConfigError` (ZA-RK-0005): 配置非法(置信度/持有期)
- `InsufficientVaRHistoryError` (ZA-RK-0006): 历史样本不足

## 6. 测试

- `tests/risk/test_var_calculator.py`
- 覆盖: 参数法/历史模拟/conservative_max、95%/99%、多日缩放、多资产组合、NaN过滤、样本不足、零下限

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`, `scipy.stats.norm`
- 消费者: RK-03 Portfolio Risk Monitor, RK-16 Risk Decomposition, RK-12 Stress Test, RK-15 Tail Risk
