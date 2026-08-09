---
ttl: permanent
doc_type: architecture_view
title: 策略间相关性验证（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: strategy_correlation_validation
scope: 07_trading_decision_architecture
---

# 策略间相关性验证（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G07 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G07 策略间相关性验证 |
| 所属 | 30_multi_strategy_concurrency §6.2（施工前必做） |
| 依赖 | G04（需策略定义才能算相关） |
| 对标 | Morwane block-bootstrap 相关性验证 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P1（G04 后立即） |
| 状态 | 骨架已建·待讨论（施工前必做项） |

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

> 以下来自 00_index §3 G07 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 5 候选策略两两相关矩阵
- [ ] ② 按情绪周期分层看相关性
- [ ] ③ 若各阶段相关性 >0.6 则"多策略实为情绪 beta 穿多件衣服"→ 重新审视
- [ ] ④ 验证数据区间
- [ ] ⑤ 验证报告模板

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G07
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §6.2
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G07 讨论要点占位，待讨论填空 |
