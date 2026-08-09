---
ttl: permanent
doc_type: architecture_view
title: 情绪周期×交易决策（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: sentiment_cycle_trading
scope: 07_trading_decision_architecture
---

# 情绪周期×交易决策（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G21 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G21 情绪周期×交易决策 |
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04、G08（打板最依赖情绪周期） |
| 对标 | 游资情绪周期体系 / 龙虎榜情绪 / 涨跌停情绪温度 |
| 正交性 | ⚠️ 与 regime 部分重叠（regime 12 态含情绪维度），需明确分工边界 |
| 优先级 | P2（打板策略前置） |
| 状态 | 骨架已建·待讨论（30_multi_strategy_concurrency §6.3 待评估） |

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

> 以下来自 00_index §3 G21 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律
- [ ] ② 情绪周期定位器准确率评估（30_multi_strategy_concurrency §6.3）
- [ ] ③ 情绪周期与 regime 12 态的映射关系
- [ ] ④ 各策略在不同情绪阶段的部署策略
- [ ] ⑤ 情绪周期是"隐形驱动"（30_multi_strategy_concurrency §1.3）→ 策略间相关性来源

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G21
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3 / §6.3
- [10_regime_detector_spec](10_regime_detector_spec.md)（regime 12 态，分工边界对齐）
- [24_daban_strategy_detail](24_daban_strategy_detail.md)（G08 打板，情绪周期主要消费方）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G21 讨论要点占位，待讨论填空 |
