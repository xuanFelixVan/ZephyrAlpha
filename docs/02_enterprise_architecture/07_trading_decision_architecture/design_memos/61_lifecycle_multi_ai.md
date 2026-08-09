---
ttl: permanent
doc_type: architecture_view
title: 策略生命周期与多 AI 协作（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: lifecycle_multi_ai
scope: 07_trading_decision_architecture
---

# 策略生命周期与多 AI 协作（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G28 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G28 策略生命周期与多 AI 协作 |
| 所属 | 跨作战地图 01/02/03/04 |
| 依赖 | 全局 |
| 对标 | MLOps 生命周期 / 机构策略研发流程 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3（治理类，可后置） |
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

> 以下来自 00_index §3 G28 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 策略生命周期（孵化→训练→回测→模拟→实盘→退役，对应作战地图 01-04/11）
- [ ] ② 研究孵化阶段（BM-RES）规范
- [ ] ③ 模型训练阶段（BM-MOD）规范
- [ ] ④ 多 AI 协作分工规范（另一 AI 做 regime，本边做选股，交接点）
- [ ] ⑤ 文档治理（design_memo 段位编号体系，见 00_index §8）
- [ ] ⑥ creation_token / depgraph 登记流程

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G28 / §8
- [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2（三层协作流程）
- battle_map_01_research_incubation / battle_map_02_model_training（BM-RES/BM-MOD 当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G28 讨论要点占位，待讨论填空 |
