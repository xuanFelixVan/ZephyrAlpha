---
ttl: permanent
doc_type: architecture_view
title: FirmRiskAggregator 逻辑（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: firm_risk_aggregator
scope: 07_trading_decision_architecture
---

# FirmRiskAggregator 逻辑（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G13 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G13 FirmRiskAggregator 逻辑 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | G12（仓位算法，[31_position_sizing](31_position_sizing.md) 已定稿 v1.2.0） |
| 对标 | Citadel pod 模型 firm 层风险聚合 / Morwane risk-parity-throttle |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2 |
| 状态 | 骨架已建·待讨论（框架已定，MOD-POS-021 已登记，逻辑细节待落） |

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

> 以下来自 00_index §3 G13 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 按标的求和（自然叠加，30_multi_strategy_concurrency §2.3）
- [ ] ② 单票硬上限裁剪（>8% 按比例削）
- [ ] ③ 行业/总仓位硬约束
- [ ] ④ 冲突标的处理（一策略买一策略卖→净额 or 优先级）
- [ ] ⑤ 不做 MVO，不做协方差估计（30_multi_strategy_concurrency §3.1 已拒绝）
- [ ] ⑥ 输出 firm_target_portfolio 契约
- [ ] ⑦ O(N) 复杂度保证

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G13
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2 / §2.3 / §3.1
- [31_position_sizing](31_position_sizing.md)（G12 产出物，必先读）
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G13 讨论要点占位，待讨论填空 |
