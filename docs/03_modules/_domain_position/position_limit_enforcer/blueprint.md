---
module_id: MOD-POS-010
title: "限仓执行器蓝图 — 硬约束+5级否决"
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

# MOD-POS-010 Position Limit Enforcer — 限仓执行器 蓝图

> **module_id**: MOD-POS-010 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-010 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.3 POS-10

## 1. 定位

限仓执行器——仓位方案的硬约束检查器。消费仓位方案+约束集, 检查单票/行业/总仓位/
亏损加仓/压力测试等硬边界, 产出 5 级否决裁决+违规告警。硬边界不可绕过。

属 A 类基础设施(约束检查+阈值判定+5级裁决, 逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | PositionPlan (持仓方案) + 约束配置 + KillSwitch状态 + 压力损失 | 来自 POS-01 |
| 输出 | LimitCheckResult (5级裁决+违规明细) | 联动 POS-01, D-RISK |

## 3. 硬约束 (设计真源 §1.3 POS-10)

| 约束 | 阈值 (默认) | 违规裁决 |
|------|-------------|----------|
| Kill Switch 激活 | — | P0_KILL_SWITCH (全否决) |
| 总仓位 > 上限 | total_position_cap (1.0) | P1_FORCE_REDUCE (强制减仓) |
| 单票 > 上限 | 5% NAV | P2_BLOCK_NEW (否决新开仓) |
| 行业 > 绝对上限 | 30% | P2_BLOCK_NEW |
| 行业 > 基准偏离 | 基准 ±10% | P2_BLOCK_NEW |
| 亏损标的加仓 | 持仓亏损 > X% (8%) | P3_BLOCK_TRADE (Hard Block) |
| 压力测试 | 情景最大亏损 > 15% NAV | P4_WARN (收紧上限) |

## 4. 5 级否决 (严重度递减)

P0 Kill Switch > P1 强制减仓 > P2 否决新开仓 > P3 否决单笔 > P4 建议性告警 > PASS

整体裁决取所有违规中最严重级别。

## 5. 关键不变量 (INVARIANTS)

- 硬边界不可绕过 (P0/P1/P2/P3 为强制否决, P4 为建议)
- 整体裁决 = max(各违规裁决) 按严重度
- Kill Switch 激活时直接 P0 (短路其他检查)
- 单票/行业约束对 OPEN/ADD 动作生效

## 6. 错误契约

- `InvalidPositionPlanError` (ZA-POS-0010): 权重越界、动作非法

## 7. 测试

- `tests/position/test_position_limit_enforcer.py`
- 覆盖: 5级裁决、各约束阈值边界、Kill Switch短路、整体聚合、亏损加仓Hard Block、压力测试、输入校验

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-POS-001 (Position Sizing Engine), D-RISK
