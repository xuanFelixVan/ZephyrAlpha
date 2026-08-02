---
module_id: MOD-POS-017
title: "日历仓位约束蓝图 — A股风险日历→仓位上限调整"
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
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-017 Calendar Position Constraint — 日历仓位约束 蓝图

> **module_id**: MOD-POS-017 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P1 | **成熟度**: L1 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-017 | **设计真源**: 07-D-POSITION §1.5 POS-17 + §7.4

## 1. 定位

A股风险日历仓位约束——根据当前日期和A股风险日历事件, 生成临时仓位上限调整和否决指令。
覆盖期权交割日/年报截止/股东空窗期/财报发布等7类日历事件。

属A类基础设施(日历计算+约束判定, 逻辑明确), 纯Python日期计算。

## 2. 输入 / 输出

| 方向 | 内容 |
|------|------|
| 输入 | 当前日期 + 持仓元数据(标的/ST/市值/预告/财报日) |
| 输出 | CalendarPositionAlert (约束列表+综合cap调整+否决标志) |

## 3. 日历事件规则 (设计真源 §7.4)

| 事件 | 时间规则 | 仓位约束 | action |
|------|---------|---------|--------|
| 股指期权交割日 | 每月第四个周三 | 否决新开仓(仅允许减仓) | BLOCK_NEW |
| 期权交割日±窗口 | 前2天+后1天 | 仓位上限下调10% | REDUCE_CAP(0.9) |
| 年报预告截止前5日 | 1月26-31日 | 未出预告个股否决新买入 | BLOCK_NEW(特定标的) |
| 年报+一季报截止 | 4月20-30日 | ST股强制清零 | FORCE_CLEAR(0.0) |
| 半年报预告截止前5日 | 7月10-15日 | 未出预告个股否决新买入 | BLOCK_NEW(特定标的) |
| 股东信息空窗期 | 11月-次年4月30日 | 微盘股(<50亿)上限收紧50% | TIGHTEN_CAP(0.5) |
| 财报发布前3天 | earnings_release_date-3 | 该标的上限下调+禁止新建 | BLOCK_NEW+REDUCE_CAP(0.9) |

## 4. 不变量

- overall_cap_adjustment = min(各约束cap) (取最严格)
- block_new_positions = any(BLOCK_NEW 且 affected_symbols is None)
- 无约束日期 → cap=1.0, block=False
- 日期计算用自然日(不做交易日历调整, 由上层处理)

## 5. 测试

`tests/position/test_calendar_position_constraint.py`

## 6. 依赖

- zephyr.shared.foundation.errors
- 消费者: MOD-POS-010(限仓执行器), MOD-POS-001(仓位决策引擎)
