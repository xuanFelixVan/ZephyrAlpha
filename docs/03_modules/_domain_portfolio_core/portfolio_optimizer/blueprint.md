---
module_id: MOD-PF-002
title: "组合优化器蓝图 — 风险预算为主 + 均值方差备选 + Kelly 截断"
doc_type: blueprint
status: Active
version: "0.1.2"
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
build_status: generated
---

# MOD-PF-002 Portfolio Optimizer — 组合优化器 蓝图

> **module_id**: MOD-PF-002 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7439828
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-02

## 1. 定位

组合优化器——消费策略权重+约束, 产出 TargetPortfolio(CTR-007):
- 主方法: 风险预算 (复用 MOD-RK-08 RiskBudgetAllocator)
- 备选方法: 均值方差 (Markowitz, scipy SLSQP)
- Kelly 截断: min 截断(只减不增, 防止过度集中)
- 约束求解: 调用 PC-04 ConstraintSolver 投影约束
- 输出: TargetPortfolio(CTR-007) 含目标权重+漂移+风险限额引用

属 A 类纯基础设施(凸优化, 无策略决策), 策略权重由 PC-01 提供。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | target_weights(PC-01) + constraints(PC-04) + current_weights | 内部 |
| 输出 | TargetPortfolio{target_weights, current_weights, drift_pct, risk_limits} | CTR-007 |
| 依赖 | RiskBudgetAllocator(MOD-RK-08) | import_depends |
| 依赖 | RiskDecomposer(MOD-RK-16) | import_depends |
| 依赖 | ConstraintSolver(PC-04) | import |
| 依赖 | TargetPortfolio(CTR-007) | contract |

## 3. 核心规则

### 3.1 优化方法选择

| 方法 | 触发条件 | 求解器 |
|------|---------|--------|
| 风险预算(主) | 默认, 有协方差矩阵 | RiskBudgetAllocator (RK-08) |
| 均值方差(备选) | 无协方差或有预期收益 | scipy SLSQP |
| 等权(降级) | 优化失败 | 1/N |

### 3.2 Kelly 截断 (只减不增)

- Kelly 比例 k_i = μ_i / σ_i² (期望收益/方差)
- 截断: w_i = min(w_i, k_i × kelly_fraction)
- kelly_fraction 默认 0.5 (半 Kelly, 降低风险)
- 只减不增: Kelly 仅作为上限, 不提升任何权重

### 3.3 约束投影流程

1. PC-01 产出 target_weights (策略层权重)
2. RK-08 风险预算优化 (组合层风险均衡)
3. PC-04 约束投影 (7 约束链迭代裁剪)
4. Kelly 截断 (上限约束)
5. 归一化 + 输出 TargetPortfolio

### 3.4 漂移计算

- drift_pct = Σ|target_weights[i] - current_weights[i]| / 2
- drift_pct > threshold → 标记需再平衡

## 4. 关键不变量 (INVARIANTS)

- 输出权重 Σw ≤ max_gross_leverage (CTR-003)
- 单标的 w_i ≤ max_single_position (经 PC-04 保证)
- Kelly 截断后 w_i ≤ kelly_fraction × k_i
- 优化失败 → 降级为等权 + 记录 method_used="equal_weight"
- TargetPortfolio 的 risk_limits 字段 MUST 引用本次使用的 CTR-003 实例

## 5. 错误契约

- `OptimizationFailureError`: 所有方法均失败(降级为等权)
- `KellyOverflowError`: Kelly 截断后仍超限(进一步缩放)
- `DriftCalculationError`: current_weights 缺失

## 6. 测试

- `tests/pf_core/test_portfolio_optimizer.py`
- 覆盖: 风险预算优化、均值方差备选、Kelly 截断、PC-04 约束投影、等权降级、CTR-007 产出完整性、漂移计算、幂等性

## 7. 依赖

- `zephyr.risk.core.risk_budget_allocator` (MOD-RK-08, 风险预算主方法)
- `zephyr.risk.core.risk_decomposition` (MOD-RK-16, 风险分解复用)
- `zephyr.pf_core.core.constraint_solver` (PC-04, 约束投影)
- `zephyr.shared.contracts.target_portfolio` (CTR-007, 输出契约)
- `zephyr.shared.contracts.risk_limits` (CTR-003, 风险限额)
- 消费者: PC-03 Rebalance Scheduler (触发重优化), D_EX_CORE/D_POSITION/D_REPORTING (TargetPortfolio 消费)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PF-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PF-002` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-PF-002` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PF-002 | MOD-PF-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 5 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pf_core/core/multifactor_constraint_arbitration.py` | ✅ 已实现 | |
| `src/zephyr/pf_core/core/multifactor_holding_drift_monitor.py` | ✅ 已实现 | |
| `src/zephyr/pf_core/core/multifactor_rebalance_trigger.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_core/test_portfolio_optimizer.py` | ✅ 已实现 | |

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


