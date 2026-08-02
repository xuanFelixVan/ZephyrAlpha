---
module_id: MOD-RK-16
title: "风险分解引擎蓝图 — 因子/残差分解 + MCR/CCR 贡献"
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

# MOD-RK-16 Risk Decomposition Engine — 风险分解引擎 蓝图

> **module_id**: MOD-RK-16 | **域**: D_RISK | **层**: L3 Post-Trade 盘后审计(亦供 L2 实时复用)
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-16 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-16, §2 依赖(RK-05→RK-16, RK-16→RK-08)

## 1. 定位

风险分解引擎——将组合风险分解为可归因的成分, 供 RK-08 风险预算分配(复用 CCR)与 RK-20 日终归因报告使用:
- 因子风险 (Factor Risk): 系统性风险, 由因子模型解释的部分
- 残差风险 (Residual Risk): 个股特异性风险, 因子无法解释的部分
- 边际风险贡献 (MCR): ∂σ_p/∂w_i
- 成分风险贡献 (CCR): w_i · MCR_i, ΣCCR = σ_p (守恒)

属 A 类基础设施(矩阵运算 + 偏导, 数学逻辑明确), 因子模型为 B 类可选输入(无因子模型时仅返回 MCR/CCR)。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 协方差矩阵 Σ (N,N) + 权重 w (N,) + 可选因子模型 (B, Σ_f, ε) | — |
| 输出 | DecompositionResult(total_risk/mcr/ccr/pct/factor_*/residual_*) | 联动 RK-08, RK-20 |
| 依赖 | RK-05 VaR (风险数值来源, 间接) | — |

## 3. 核心规则 (设计真源 §1.2 RK-16, §2)

### 3.1 基础分解 (无因子模型)

- σ_p = sqrt(w'Σw)
- MCR_i = (Σw)_i / σ_p
- CCR_i = w_i · MCR_i,  ΣCCR_i = σ_p (守恒)
- pct_i = CCR_i / σ_p,  Σpct_i = 1

### 3.2 因子模型分解

组合方差分解 (平方和守恒):
- σ_p² = w'(BΣ_fB' + Σ_ε)w = w'BΣ_fB'w + w'Σ_εw
- factor_variance = w'BΣ_fB'w         (因子贡献方差)
- residual_variance = Σ ε_i · w_i²    (残差贡献方差, 对角)
- factor_risk² + residual_risk² = total_variance (守恒)

### 3.3 输入约束

- cov: 对称半正定方阵 (N,N)
- weights: (N,), 自动归一化, 拒绝负权重 (long-only)
- factor_loadings B: (N, K), K=因子数
- factor_cov Σ_f: (K, K)
- residual_var ε: (N,)

## 4. 关键不变量 (INVARIANTS)

- 平方和守恒: factor_risk² + residual_risk² = total_risk² (含因子模型时)
- CCR 守恒: ΣCCR_i = σ_p
- MCR = (Σw) / σ_p (σ_p > 0 时; σ_p = 0 时 MCR/CCR/pct 全零)
- 权重归一化: Σw = 1 (输入自动归一化)
- long-only: w ≥ 0 (拒绝负权重)

## 5. 错误契约

- `InvalidDecompositionInputError` (ZA-RK-0016): 协方差非方阵/权重维度不匹配/负权重/因子模型维度不一致

## 6. 测试

- `tests/risk/test_risk_decomposition.py`
- 覆盖: 基础 MCR/CCR/pct、因子/残差分解、平方和守恒、CCR 守恒、维度校验、负权重拒绝、零组合退化、因子贡献占比、与 RK-08 一致性

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`
- 消费者: RK-08 Risk Budget Allocator (复用 CCR), RK-20 Daily Auditor (归因报告), RK-03 Portfolio Risk Monitor
