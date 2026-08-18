---
module_id: MOD-PF-006
title: "约束求解器蓝图 — 7 约束链迭代投影 + 拥挤检测"
doc_type: blueprint
status: Active
version: "0.1.1"
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

# MOD-PF-006 Constraint Solver — 约束求解器 蓝图

> **module_id**: MOD-PF-006 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P0 | **成熟度**: design | **SSoT**: depgraph node 7820844
> **设计真源**: D:\临时工作区\依赖图\12-D-PF-CORE-组合构建域.md §1.2 PC-04

## 1. 定位

约束求解器——将风险限额(CTR-003)和拥挤检测结果转化为可执行权重约束,供 PC-02 组合优化器消费:
- 7 约束链: 行业绝对≤30% / 行业相对±10% / 市值暴露 / MDD≤5% / 相关性≤0.7 / 风格≤±0.3σ / 仓位上限
- 拥挤检测: 策略间相关性 ρ>0.8 时权重减半(复用 MOD-PA-004 StrategyCorrelationGate)
- 求解方法: 迭代投影法(逐约束裁剪→归一化→收敛)

属 A 类纯基础设施(数学约束投影, 无策略决策), 阈值来源 RiskLimits(CTR-003)。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | RiskLimits(CTR-003) + 候选权重 + 相关性矩阵 | CTR-003 |
| 输出 | ConstraintSolveResult{weights, violations, scaling_applied, converged} | 内部 → PC-02 |
| 依赖 | StrategyCorrelationGate(MOD-PA-004) | import_depends |

## 3. 核心规则

### 3.1 7 约束链 (迭代投影)

| 序号 | 约束 | 阈值 | 投影方式 |
|------|------|------|---------|
| C1 | 行业绝对集中度 | ≤30% | 裁剪超限行业至 30% |
| C2 | 行业相对偏移 | ±10% | 相对基准偏移截断 |
| C3 | 市值暴露 | ±0.3σ | 大/小盘暴露截断 |
| C4 | 最大回撤约束 | MDD≤5% | 高波动标的减权 |
| C5 | 标的相关性 | ≤0.7 | 高相关对降权 |
| C6 | 风格因子暴露 | ≤±0.3σ | 风格暴露截断 |
| C7 | 单标的仓位 | ≤max_single_position | 硬截断(CTR-003) |

### 3.2 拥挤检测 (复用 MOD-PA-004)

- 策略间相关性 ρ>0.8 → 相关策略权重减半
- ρ>0.9 → 仅保留 IC 最高的策略
- 检测频率: 每次再平衡前

### 3.3 迭代投影求解

1. 初始化: 候选权重 w₀
2. 逐约束投影: w_i = project_Ci(w_{i-1})
3. 归一化: w = w / Σw
4. 收敛判定: ||w_new - w_old|| < tol (默认 1e-6)
5. 最大迭代: 100 次

## 4. 关键不变量 (INVARIANTS)

- 输出权重 Σw ≤ max_gross_leverage (CTR-003)
- 单标的 w_i ≤ max_single_position
- 违反约束时 violations 非空, scaling_applied 记录缩放因子
- 不收敛 → 返回最后一次迭代结果 + converged=False
- 输入权重与输出权重同维度, 不引入新标的

## 5. 错误契约

- `ConstraintViolationError`: 约束不可满足(如 max_single_position × N < max_gross_leverage)
- `CorrelationGateFailure`: 拥挤检测异常(降级为跳过拥挤检测)

## 6. 测试

- `tests/pf_core/test_constraint_solver.py`
- 覆盖: 7 约束独立投影、迭代收敛、拥挤检测减半、退化场景(单标的/空候选)、CTR-003 阈值强制、不变量验证

## 7. 依赖

- `zephyr.shared.contracts.risk_limits` (CTR-003, RiskLimits 消费)
- `zephyr.pf_alloc.core.strategy_correlation_gate` (MOD-PA-004, 拥挤检测复用)
- 消费者: PC-02 Portfolio Optimizer (约束输入)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PF-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PF-006` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PF-006` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PF-006 | MOD-PF-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_core/test_constraint_solver.py` | ✅ 已实现 | |

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
