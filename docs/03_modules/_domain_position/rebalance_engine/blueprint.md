---
module_id: MOD-POS-004
title: "再平衡引擎蓝图 — 成本收益判定+三级触发"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-004 Rebalance Engine — 再平衡引擎 蓝图

> **module_id**: MOD-POS-004 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-004 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.1 POS-04

## 1. 定位

再平衡引擎——消费 E-POS-02 DriftDetected 事件, 在交易成本/预期收益判定通过后
产出 E-POS-03 RebalanceTriggered 事件及调仓指令列表, 驱动组合回归目标权重。

属 A 类基础设施(漂移→成本收益判定→调仓指令生成, 逻辑明确), 成本系数与改善比阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | DriftDetectedEvent (来自 POS-003) | E-POS-02 |
| 输入 | 实际权重 + 目标权重 + 市场状态 | 调用参数 |
| 输出 | RebalanceTriggeredEvent + 调仓指令列表 | E-POS-03 |

## 3. 核心规则 (设计真源 §1.1 POS-04)

### 3.1 三级触发

| 触发类型 | 条件 | 说明 |
|----------|------|------|
| CALENDAR | 周频强制 | 日历到点无条件触发评估(仍走成本判定) |
| DEVIATION | 漂移超阈值 | POS-003 DriftDetected 驱动 |
| EVENT | 外部事件 | 资金流入/风控指令等驱动 |

### 3.2 成本收益判定

- 交易成本 = Σ|Δweight_i| × cost_rate × cost_multiplier
- 预期收益改善 = 漂移消除后的预期收益改善(以漂移幅度近似)
- **跳过**: 交易成本 > 预期收益改善
- **执行**: 预期收益改善 > 2 × 交易成本 (改善比阈值, 默认 2.0)

### 3.3 市场状态成本系数

- 正常状态(0-6): cost_multiplier = 1.0
- 压力状态(7/8/9): cost_multiplier = 1.5 (流动性差, 冲击成本高)

### 3.4 再平衡后约束

- 执行后组合仓位偏差 < 1% (post_rebalance_tolerance, 默认 0.01)

## 4. 关键不变量 (INVARIANTS)

- 交易成本 > 预期收益改善时 MUST 跳过(禁止亏损再平衡)
- 改善比 < 阈值时 MUST 跳过(仅日历强制触发可放宽, 但仍记录)
- 调仓指令 Δweight 符号: 超配→SELL(负), 低配→BUY(正)
- Σ|Δweight_i| = 总换手率 (turnover)

## 5. 错误契约

- `InvalidRebalanceInputError` (ZA-POS-0005): 权重越界、标的集合不一致、cost_rate 非正

## 6. 测试

- `tests/position/test_rebalance_engine.py`
- 覆盖: 三级触发、成本收益判定(跳过/执行边界)、压力状态×1.5、调仓指令生成、偏差<1%约束、输入校验、事件订阅

## 7. 依赖

- `zephyr.position.core.position_drift_monitor` (DriftDetectedEvent, DriftResult, DriftAlert)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: D-EX-CORE(执行调仓) ; D-PF-CORE ; D-GOVERNANCE(审计)

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-004`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-004` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-004` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | （无节点） | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-004 | MOD-POS-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
