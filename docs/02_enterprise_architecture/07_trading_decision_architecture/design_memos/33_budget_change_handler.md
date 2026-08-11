---
ttl: permanent
doc_type: architecture_view
title: BudgetChangeHandler 三级升级（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: budget_change_handler
scope: 07_trading_decision_architecture
---

# BudgetChangeHandler 三级升级（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G14 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G14 BudgetChangeHandler 三级升级 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.4 |
| 依赖 | G12、G13 |
| 对标 | 机构级 budget rebalance 协议 |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 优先级 | P2 |
| 状态 | 骨架已建·待讨论（框架已定，MOD-POS-022 已登记，窗口参数待校准） |

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

> 以下来自 00_index §3 G14 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① Tier 1 封锁新仓（瞬时）
- [ ] ② Tier 2 rebalance_to_budget 信号（策略自选砍仓）
- [ ] ③ Tier 3 按比例强裁（firm 层兜底）
- [ ] ④ convergence_window 按换手率差异化（30_multi_strategy_concurrency §6.4：打板 1-2 天/多因子 3-5 天/事件 2-3 天）
- [ ] ⑤ rebalance_to_budget 接口契约（策略不能说"我不卖"）
- [ ] ⑥ 每级独立 log/复盘

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G14
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4 / §6.4
- [31_position_sizing](31_position_sizing.md)（G12 产出物）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（G13，依赖项）
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G14 讨论要点占位，待讨论填空 |
