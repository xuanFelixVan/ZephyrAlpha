---
module_id: MOD-RK-08
title: "风险预算分配器蓝图 — ERC + 自定义预算 SLSQP 优化"
doc_type: blueprint
status: Active
version: "0.1.4"
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
build_status: production
---

# MOD-RK-08 Risk Budget Allocator — 风险预算分配器 蓝图

> **module_id**: MOD-RK-08 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-08 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-08, §2 依赖(RK-16→RK-08)

## 1. 定位

风险预算分配器——基于风险贡献(复用 RK-16)实现组合层风险预算分配:
- 等风险贡献 (ERC / Risk Parity): 每资产贡献等量风险 pct_i = 1/N
- 自定义风险预算: 按 target_budgets 分配风险贡献占比
- 约束处理: long-only (w≥0)、满仓 (Σw=1)、可选 min/max 权重
- 再平衡触发: 风险贡献漂移超阈值 → 触发再平衡

与 POS-13 的边界 (SSoT 裁定 2026-08-02, 非重复):
- RK-08: 组合层风险预算分配 + 再平衡触发(本模块, D-RISK)
- POS-13: 标层风险配额约束 Kelly sizing(D-POSITION, GATE-POS-13 阻断, 未实现)
- 复用关系: POS-13 实现时复用 RK-08 的 risk_contributions() 计算单标的风险贡献

属 A 类基础设施(凸优化 + 风险贡献, 数学逻辑明确), target_budgets 为 B 类策略输入。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 协方差矩阵 Σ (N,N) + 可选 target_budgets (N,) | — |
| 输出 | BudgetAllocationResult(weights/total_risk/ccr/pct/contribution_error) | 联动 RK-03, PC-02 |
| 依赖 | RK-16 RiskDecomposer (CCR 计算) | L1 依赖先行 |

## 3. 核心规则 (设计真源 §1.2 RK-08, §2)

### 3.1 数学基础 (复用 RK-16)

- σ_p = sqrt(w'Σw)
- MCR_i = (Σw)_i / σ_p  (边际风险贡献)
- CCR_i = w_i · MCR_i   (成分贡献, ΣCCR_i = σ_p 守恒)
- pct_i = CCR_i / σ_p   (百分比贡献, Σpct_i = 1)

### 3.2 两种分配模式

| 模式 | 目标 pct | 方法 |
|------|---------|------|
| ERC (Risk Parity) | 1/N ∀i | equal_risk_contribution() |
| 自定义预算 | target_budgets / Σ(target_budgets) | allocate_by_budget() |

### 3.3 优化求解

- 求解器: scipy.optimize.minimize (SLSQP)
- 目标函数: Σ(pct_i - target_i)²
- 约束: Σw = 1 (等式)
- 边界: w ∈ [min_weight, max_weight] (默认 [0.0, 1.0], long-only)
- 初始点: inv_vol × target_pct (反波动率加权, 加速收敛)

### 3.4 再平衡触发

- 比较 current_weights vs target_weights 的风险贡献百分比漂移
- 任一资产 |cur_pct - tgt_pct| > rebalance_drift_threshold (默认 5%) → 触发

## 4. 关键不变量 (INVARIANTS)

- 权重归一化: Σw = 1
- long-only: w ≥ min_weight ≥ 0
- ERC 解: pct_i ≈ 1/N (容差内)
- 再平衡触发由风险贡献漂移唯一决定 (非价格漂移)
- 优化失败 → BudgetOptimizationError (Fail-Closed, 不返回非法权重)

## 5. 错误契约

- `InvalidBudgetInputError` (ZA-RK-0008): 输入非法(协方差非方阵/预算非正/维度不匹配)
- `BudgetOptimizationError` (ZA-RK-0009): 优化求解失败(零权重/数值异常)

## 6. 测试

- `tests/risk/test_risk_budget_allocator.py`
- 覆盖: ERC 等风险贡献、自定义预算、约束强制(min/max weight)、再平衡触发、收敛性、退化场景(单资产/全零)、与 RK-16 一致性

## 7. 依赖

- `zephyr.risk.core.risk_decomposition` (RK-16, RiskDecomposer 复用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `numpy`, `scipy.optimize.minimize`
- 消费者: RK-03 Portfolio Risk Monitor, PC-02 Portfolio Optimizer (预算约束), POS-13 Risk Budget Allocator (未来, 复用 risk_contributions)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-08`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-08` 的 3 个 file 节点 | design | `extract_depgraph.py --modules MOD-RK-08` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | （无节点） | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-08 | MOD-RK-08 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_liquidity_monitor.py` | ✅ 已实现 | |
| `tests/risk/core/test_orchestrator_liquidity_integration.py` | ✅ 已实现 | |
| `tests/risk/test_risk_budget_allocator.py` | ✅ 已实现 | |

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


