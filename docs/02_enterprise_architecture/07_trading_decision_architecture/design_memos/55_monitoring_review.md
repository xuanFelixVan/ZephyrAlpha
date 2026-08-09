---
ttl: permanent
doc_type: architecture_view
title: 监控告警与复盘（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: monitoring_review
scope: 07_trading_decision_architecture
---

# 监控告警与复盘（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G26 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G26 监控告警与复盘 |
| 所属 | 跨作战地图 |
| 依赖 | G25 |
| 对标 | 机构 PM 周报 / 风控周报 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P5 |
| 状态 | 骨架已建·待讨论 |

## 2. 背景（待填写）

> 项目处境 + 核心问题 + 约束条件。

## 3. 决策（待填写）

> 架构定义 + 核心模块 + 关键特性。

## 4. 考虑过的替代方案（待填写）

> 每个方案 + 拒绝理由。

## 5. 上限定义（待填写）

> 系统上限 + 演进路径 + 为何是上限。

## 6. 待裁定（待填写）

> 暂缓项 + 暂缓理由 + 重评条件。

## 7. 待定问题（讨论要点）

> 以下来自 00_index §3 G26 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 系统健康监控（数据/引擎/下单链路）
- [ ] ② 策略偏离监控（实盘 vs 回测）
- [ ] ③ 告警阈值与通知
- [ ] ④ 每日/每周/每月复盘机制
- [ ] ⑤ 策略退役标准（连续跑输/逻辑失效）
- [ ] ⑥ 复盘文档模板

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G26
- [54_reconciliation_attribution](54_reconciliation_attribution.md)（G25，依赖项）
- [50_backtest_observability_workplan](50_backtest_observability_workplan.md)（可观测性体系衔接）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G26 讨论要点占位，待讨论填空 |
