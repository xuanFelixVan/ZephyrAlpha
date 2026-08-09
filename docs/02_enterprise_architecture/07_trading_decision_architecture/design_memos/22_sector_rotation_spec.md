---
ttl: permanent
doc_type: architecture_view
title: 板块轮动 spec（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: sector_rotation_spec
scope: 07_trading_decision_architecture
---

# 板块轮动 spec（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G06 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G06 板块轮动 spec |
| 所属 | 作战地图 05（BM-SEL-08/09） |
| 依赖 | G04（板块是选股的输入特征，非独立层） |
| 对标 | AQR sector momentum / 华泰板块轮动研报 / 申万行业轮动 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P1 |
| 状态 | 骨架已建·待讨论（BM-SEL-08/09 已登记 proposed 未实现） |

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

> 以下来自 00_index §3 G06 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 板块强度算法（BM-SEL-08，460 板块 880xxx K线）
- [ ] ② 回踩质量等级 A/B/C 判定
- [ ] ③ 调整周期追踪（BM-SEL-09，进度≥80% 激活分批）
- [ ] ④ 轮动序列追踪
- [ ] ⑤ 虹吸态识别（30_multi_strategy_concurrency §1.3 提到情绪周期隐形驱动）
- [ ] ⑥ 板块资金流
- [ ] ⑦ 板块→个股的传导映射

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G06
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3
- battle_map_05_stock_selection（BM-SEL-08/09 当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G06 讨论要点占位，待讨论填空 |
