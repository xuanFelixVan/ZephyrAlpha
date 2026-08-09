---
ttl: permanent
doc_type: architecture_view
title: 卖出流 spec（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: sell_flow
scope: 07_trading_decision_architecture
---

# 卖出流 spec（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G20 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G20 卖出流 spec |
| 所属 | 作战地图 07 |
| 依赖 | G19 |
| 对标 | 机构卖出纪律 / O'Neil 卖出法则 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（但 regime 只给 Shrinkage，卖出逻辑在策略内） |
| 优先级 | P3 |
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

> 以下来自 00_index §3 G20 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 卖出时序（止损/止盈/时间止损）
- [ ] ② 止损触发（固定%/移动/ATR）
- [ ] ③ 止盈逻辑
- [ ] ④ 情绪退潮卖出（与 regime CRISIS/RECOVERY 协同）
- [ ] ⑤ 破位卖出
- [ ] ⑥ 分批卖出
- [ ] ⑦ T+1 卖出约束
- [ ] ⑧ 与回撤 Protocol 的联动

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G20
- [41_buy_flow](41_buy_flow.md)（G19，依赖项）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16 回撤 Protocol，联动项）
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md)（G21 情绪周期，退潮卖出输入）
- battle_map_07_sell_flow（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G20 讨论要点占位，待讨论填空 |
