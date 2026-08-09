---
ttl: permanent
doc_type: architecture_view
title: 模拟与实盘验证路径（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: simulation_live_path
scope: 07_trading_decision_architecture
---

# 模拟与实盘验证路径（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G24 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G24 模拟与实盘验证路径 |
| 所属 | 作战地图 04 |
| 依赖 | G23（回测通过） |
| 对标 | 机构 paper trading → 小资金 → 全量 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P4 |
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

> 以下来自 00_index §3 G24 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 模拟验证（paper trading）环境
- [ ] ② 模拟时长
- [ ] ③ 实盘小资金验证路径
- [ ] ④ 实盘→模拟差异监控
- [ ] ⑤ 上线决策门控
- [ ] ⑥ 灰度上线（单策略先上）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G24
- [52_backtest_framework_docking](52_backtest_framework_docking.md)（G23，依赖项）
- battle_map_04_simulation_validation（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G24 讨论要点占位，待讨论填空 |
