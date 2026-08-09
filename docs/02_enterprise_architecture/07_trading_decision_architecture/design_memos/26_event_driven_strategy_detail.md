---
ttl: permanent
doc_type: architecture_view
title: 事件驱动策略细节（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: event_driven_strategy_detail
scope: 07_trading_decision_architecture
---

# 事件驱动策略细节（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G10 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G10 事件驱动策略细节 |
| 所属 | 作战地图 05 |
| 依赖 | G04、G05 |
| 对标 | RavenPack 事件驱动 / 彭博事件策略 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2 |
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

> 以下来自 00_index §3 G10 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 事件源（公告/新闻/龙虎榜/异动）
- [ ] ② 事件分类（业绩/并购/政策/突发事件）
- [ ] ③ 事件冲击衰减曲线
- [ ] ④ 事件信号→选股映射
- [ ] ⑤ 事件驱动换手率（中，2-3 天）
- [ ] ⑥ news_data 多源情绪接入

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G10
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- battle_map_05_stock_selection（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G10 讨论要点占位，待讨论填空 |
