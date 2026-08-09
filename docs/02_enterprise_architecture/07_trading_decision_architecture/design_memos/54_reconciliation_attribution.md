---
ttl: permanent
doc_type: architecture_view
title: 对账归因（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: reconciliation_attribution
scope: 07_trading_decision_architecture
---

# 对账归因（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G25 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G25 对账归因 |
| 所属 | 作战地图 11 |
| 依赖 | G22（执行，[40_execution_broker](40_execution_broker.md) 已定稿+代码已施工）+ G04（策略） |
| 对标 | 机构中后台对账 / Barra 归因 |
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

> 以下来自 00_index §3 G25 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① PnL 归因（策略贡献分解）
- [ ] ② 每日对账（成交 vs 持仓 vs 资金）
- [ ] ③ 归因维度（策略/标的/因子/时段）
- [ ] ④ 与 StrategyBook 独立 PnL 归因的对接（30_multi_strategy_concurrency §2.2）
- [ ] ⑤ 异常交易检测
- [ ] ⑥ 报表生成

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G25
- [40_execution_broker](40_execution_broker.md)（G22 产出物，依赖项）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2
- battle_map_11_reconciliation（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G25 讨论要点占位，待讨论填空 |
