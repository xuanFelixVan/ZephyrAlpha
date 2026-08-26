---
module_id: MOD-RK-16
title: "风险分解引擎蓝图 — 因子/残差分解 + MCR/CCR 贡献"
doc_type: blueprint
status: Active
version: "0.1.2"
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
design_maturity: production
build_status: stable
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

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-16`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-16` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-16` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-16 | MOD-RK-16 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/risk_decomposition.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_risk_decomposition.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


