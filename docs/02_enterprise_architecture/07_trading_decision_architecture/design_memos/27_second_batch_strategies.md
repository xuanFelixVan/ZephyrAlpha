---
ttl: permanent
doc_type: architecture_view
title: 第二批次策略·价值反转与动量趋势（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: second_batch_strategies
scope: 07_trading_decision_architecture
---

# 第二批次策略·价值反转与动量趋势（骨架·暂缓）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G11 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **暂缓说明**：本主题组暂缓讨论——首批 3 策略（[20_first_batch_strategies](20_first_batch_strategies.md)）上线跑出 3 个月 track record 后再启动。骨架仅作坑位占位。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G11 第二批次策略（价值反转 / 动量趋势） |
| 所属 | 30_multi_strategy_concurrency §1.1（5 候选策略后 2 个） |
| 依赖 | G04 先跑 3 个月有 track record |
| 对标 | AQR 价值/动量 / Fama-French |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P4（远期） |
| 状态 | 骨架已建·暂缓（首批上线 3 个月后再讨论） |

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

> 以下来自 00_index §3 G11 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 价值反转 alpha 信号
- [ ] ② 动量趋势 alpha 信号
- [ ] ③ 与首批 3 策略相关性
- [ ] ④ 上线时机（首批 track record 后）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G11
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.1
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G11 讨论要点占位，暂缓讨论 |
