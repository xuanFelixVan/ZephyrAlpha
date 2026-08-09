---
ttl: permanent
doc_type: architecture_view
title: 数据与特征层规范（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: data_feature_layer_spec
scope: 07_trading_decision_architecture
---

# 数据与特征层规范（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G01 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层规范 |
| 所属 | 作战地图 01/02 + 跨切 |
| 依赖 | 无（地基） |
| 对标 | WorldQuant Alpha 工厂 / Numerai 数据管线 / qstobody 因子工程 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P0（地基，但可后置——策略定义不阻塞） |
| 状态 | 骨架已建·待讨论（部分能力已存在，需汇总成 why） |

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

> 以下来自 00_index §3 G01 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① ClickHouse schema 规范（日K/分钟/Tick/板块/期权）
- [ ] ② miniQMT tick 接入契约
- [ ] ③ PIT 铁律（AS OF JOIN + Embargo）
- [ ] ④ 特征仓库架构（计算/缓存/版本）
- [ ] ⑤ 因子工程总纲（因子库/IC 评估/衰减监控/过拟合监控）
- [ ] ⑥ 数据质量门控

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G01
- battle_map_01_research_incubation / battle_map_02_model_training（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G01 讨论要点占位，待讨论填空 |
