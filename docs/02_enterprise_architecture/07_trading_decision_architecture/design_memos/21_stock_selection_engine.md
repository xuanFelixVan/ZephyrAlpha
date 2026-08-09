---
ttl: permanent
doc_type: architecture_view
title: 选股引擎架构（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: stock_selection_engine
scope: 07_trading_decision_architecture
---

# 选股引擎架构（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G05 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G05 选股引擎架构 |
| 所属 | 作战地图 05 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.0） |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P1 |
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

> 以下来自 00_index §3 G05 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 双引擎融合（BM-SEL-25，30_multi_strategy_concurrency 定位为"打板策略内部融合"，非跨策略层）
- [ ] ② L0→L1→L2-C 分层
- [ ] ③ 量化强度评级
- [ ] ④ 选股 pipeline 标准接口（输入信号→输出 target_portfolio）
- [ ] ⑤ 候选池生成→过滤→排序→输出
- [ ] ⑥ 与 StrategyBook 的对接契约

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G05
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §6.1
- battle_map_05_stock_selection（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G05 讨论要点占位，待讨论填空 |
