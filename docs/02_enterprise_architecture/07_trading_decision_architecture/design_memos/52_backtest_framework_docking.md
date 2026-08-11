---
ttl: permanent
doc_type: architecture_view
title: 回测框架对接（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: backtest_framework_docking
scope: 07_trading_decision_architecture
---

# 回测框架对接（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G23 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G23 回测框架对接 |
| 所属 | 作战地图 03 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.0） |
| 对标 | 11_regime_backtest_validation_plan 已建立的对接范式 / Morwane walk-forward |
| 正交性 | ✅ 与 regime 正交（复用同一回测框架） |
| 优先级 | P2（G04 后） |
| 状态 | 骨架已建·待讨论（regime 已对接，策略侧待补） |

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

> 以下来自 00_index §3 G23 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① BM-BT-01~07 环节在策略验证中的用法（regime 验证已映射，见 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §2.1）
- [ ] ② 策略回测 vs regime 回测的差异
- [ ] ③ 策略上线门控 IS→WFA→OOS（BM-BT-07）
- [ ] ④ 过拟合检测三维度（BM-BT-05）
- [ ] ⑤ Deflated Sharpe（BM-BT-05-G）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G23
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) §2.1（regime 对接范式）
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- battle_map_03_backtest_validation（BM-BT-01~07 当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G23 讨论要点占位，待讨论填空 |
