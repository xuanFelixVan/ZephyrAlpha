---
module_id: MOD-POS-007
title: "资金曲线管理器蓝图 — 回撤分级动态调仓上限"
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

# MOD-POS-007 Capital Curve Manager — 资金曲线管理器 蓝图

> **module_id**: MOD-POS-007 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-007 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.3 POS-07

## 1. 定位

资金曲线管理器——跟踪已实现盈亏驱动的净值曲线, 根据回撤分级动态调整仓位上限,
并在盈利期扩张、亏损期收缩资金基础。产出 E-POS-04 CapitalCurveUpdated 事件,
联动 POS-01 仓位上限引擎。

属 A 类基础设施(回撤计算+分级+缩放系数, 逻辑明确), 阈值与扩张步长为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 已实现盈亏 / 当前净值 | 来自 D-EX-CORE 成交回报 |
| 输出 | CapitalCurveSnapshot (仓位上限+缩放系数+回撤分级) | 联动 POS-01 |
| 事件 | E-POS-04 CapitalCurveUpdated | → D-RISK, D-PF-CORE, D-POS-01 |

## 3. 核心规则 (设计真源 §1.3 POS-07)

### 3.1 回撤分级 → 仓位上限

| 回撤幅度 | 级别 | 仓位上限 | 仅防御 |
|----------|------|----------|--------|
| < 5% | NORMAL | 100% | 否 |
| 5% ~ 10% | WARNING | 80% | 否 |
| 10% ~ 15% | CRITICAL | 50% | 否 |
| > 15% | EMERGENCY | 30% | 是(禁止新开仓) |

### 3.2 盈利扩张

- 每次净值创新高 → 资金基础扩张 +5% (复利累计)
- 最大不超过框架硬上限 (默认 2.0x 初始本金)

### 3.3 亏损收缩

- 回撤 > 5% → 缩减 10% (contraction = 0.9)
- 回撤 > 10% → 缩减 20% (contraction = 0.8)

### 3.4 恢复条件

- 净值回到回撤前高点 → 解除收缩, 保留已累计的扩张因子

### 3.5 本金=当前净值

- 仓位 sizing 的本金基准 = 当前净值 (天然复利)

## 4. 关键不变量 (INVARIANTS)

- 回撤 = (net_value - peak) / peak, 恒 ≤ 0
- peak 单调非减 (只在新高时上移)
- position_cap 仅由 drawdown_level 决定, 不可被盈利扩张放大
- EMERGENCY 级 defensive_only=True, 禁止新开仓
- capital_curve_discount 受框架硬上限封顶

## 5. 错误契约

- `InvalidCapitalCurveInputError` (ZA-POS-0005): 净值非正、盈亏快照非法

## 6. 测试

- `tests/position/test_capital_curve_manager.py`
- 覆盖: 四级回撤分级、盈利扩张复利+封顶、亏损收缩、恢复解除、事件触发、边界值

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-POS-001 (Position Sizing Engine), MOD-POS-008 (Drawdown Controller)
