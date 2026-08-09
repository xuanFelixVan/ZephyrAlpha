---
ttl: permanent
doc_type: architecture_view
title: 买入流 spec（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: buy_flow
scope: 07_trading_decision_architecture
---

# 买入流 spec（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G19 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G19 买入流 spec |
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位）、G16（风控） |
| 对标 | 机构分批建仓 / Wyckoff 吸筹时序 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3 |
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

> 以下来自 00_index §3 G19 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 分批建仓（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）
- [ ] ② 突破失败降级
- [ ] ③ 买入时序（盘中/盘后/集合竞价）
- [ ] ④ 买入价格锚定
- [ ] ⑤ 资金分配到多标的
- [ ] ⑥ 与 budget 的协同
- [ ] ⑦ T+1 约束

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G19
- [22_sector_rotation_spec](22_sector_rotation_spec.md)（G06 板块回踩质量，输入依赖）
- [31_position_sizing](31_position_sizing.md)（G12 仓位，输入依赖）
- battle_map_06_buy_flow（BM-BUY-04 当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G19 讨论要点占位，待讨论填空 |
