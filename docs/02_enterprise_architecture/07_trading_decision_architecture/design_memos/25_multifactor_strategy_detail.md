---
ttl: permanent
doc_type: architecture_view
title: 多因子策略细节（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: multifactor_strategy_detail
scope: 07_trading_decision_architecture
---

# 多因子策略细节（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G09 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G09 多因子策略细节 |
| 所属 | 作战地图 05 |
| 依赖 | G04、G05、G01（因子工程） |
| 对标 | WorldQuant / Numerai 多因子 / 华泰金工多因子 |
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

> 以下来自 00_index §3 G09 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 因子组合方式（打分/IC加权/正交化）
- [ ] ② 行业中性化
- [ ] ③ 因子衰减监控
- [ ] ④ 多因子换手率（低，3-5 天 convergence）
- [ ] ⑤ 多因子容量（较大，可承载主资金）
- [ ] ⑥ 与打板策略的相关性

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G09
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（G01 因子工程，依赖项）
- battle_map_05_stock_selection（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G09 讨论要点占位，待讨论填空 |
