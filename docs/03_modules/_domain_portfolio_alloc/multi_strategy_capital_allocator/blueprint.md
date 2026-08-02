---
module_id: MOD-PA-003
title: "多策略资金分配器蓝图 — 容量+MaxDD+冷启动+再平衡频率"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: design
build_status: stable
ttl: permanent
layer: L02_pf_alloc
layer_name: pf_alloc
functional_domain: pf_alloc
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PA-003 Multi-Strategy Capital Allocator — 多策略资金分配器 蓝图

> **module_id**: MOD-PA-003 | **域**: D_PF_ALLOC | **层**: L02 组合分配
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建设
> **SSoT**: depgraph MOD-PA-003 | **设计真源**: D:\临时工作区\依赖图\06-D-PF-ALLOC-组合分配域.md §1 PA-03, §1.1

## 1. 定位

多策略资金分配器——在策略权重(来自 PA-01/PA-02)基础上, 施加策略容量约束、MaxDDLimit
减仓、冷启动缩放、再平衡频率控制, 产出最终资金分配(权重和=1.0)+风险预算。

属 A 类基础设施(权重规整+阈值缩放+频率控制, 逻辑明确), 策略权重本身(B类, 来自 PA-01)
和协方差矩阵(数据层)为外部输入。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 策略权重(PA-01/PA-02) + 容量 + MaxDD + 冷启动天数 + 上次再平衡日 | — |
| 输出 | AllocationResult (最终权重和=1.0 + 风险预算 + 各标志) | 联动 PA-06 |

## 3. 核心规则 (设计真源 §1 PA-03, §1.1)

### 3.1 权重规整
- 每策略权重受其容量上限约束 (capacity, 来自 C-042)
- 规整后归一化, 权重和 = 1.0

### 3.2 MaxDDLimit (已合并入 PA-03)
- 组合 MaxDD > 15% → 全线减仓 50% (scale=0.5)

### 3.3 冷启动
- 观察期内 (默认 5 交易日): 仓位 = 风险预算仓位 × 冷启动系数(30%)
- 观察期内仓位上限 ≤ 正常 50%

### 3.4 再平衡频率
- 权重变更频率 ≤ 1 次/交易日 (防过度交易)
- 当日已再平衡 → rebalance_allowed=False, 沿用上次分配

### 3.5 风险预算
- 每策略风险预算 ∝ 其最终权重 (组合风险预算按权重分解)

## 4. 关键不变量 (INVARIANTS)

- 最终权重和 = 1.0 (MaxDD/冷启动缩放为整体系数, 不破坏归一)
- MaxDD 触发时全线等比缩放 (非选择性)
- 再平衡频率硬上限 1 次/日
- 容量约束: 单策略权重 ≤ capacity

## 5. 错误契约

- `InvalidAllocationInputError` (ZA-PA-0003): 权重非正、容量越界、总资金非正

## 6. 测试

- `tests/pf_alloc/test_multi_strategy_capital_allocator.py`
- 覆盖: 容量截断+归一、MaxDD减仓、冷启动缩放、再平衡频率阻断、风险预算、空策略、输入校验

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费 PA-004 (相关性门禁裁决, 决定是否允许分配)
- 消费者: MOD-PA-006 (Position Sizing Calculator)
