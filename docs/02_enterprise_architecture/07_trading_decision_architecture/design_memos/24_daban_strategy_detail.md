---
ttl: permanent
doc_type: architecture_view
title: 打板策略细节（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: daban_strategy_detail
scope: 07_trading_decision_architecture
---

# 打板策略细节（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G08 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G08 打板策略细节 |
| 所属 | 作战地图 05（BM-SEL-22~25）+ 30_multi_strategy_concurrency §4.3 |
| 依赖 | G04、G05、G06 |
| 对标 | 游资打板体系（龙虎榜/连板梯队/情绪周期）/ 量化社区连板策略 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2（G04/G05/G06 后） |
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

> 以下来自 00_index §3 G08 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 连板梯队识别
- [ ] ② 情绪周期定位器（BM-SEL-23-B，30_multi_strategy_concurrency §6.3 待评估准确率 → 见 [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md) G21）
- [ ] ③ 主升龙头识别
- [ ] ④ 打板容量极小（单票几万~几十万）→ 必须小账本
- [ ] ⑤ 双引擎融合在此策略内部（BM-SEL-25）
- [ ] ⑥ 打板专用风控参数
- [ ] ⑦ T+1 约束下的打板时序

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G08
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §4.3 / §6.3
- battle_map_05_stock_selection（BM-SEL-22~25 当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G08 讨论要点占位，待讨论填空 |
