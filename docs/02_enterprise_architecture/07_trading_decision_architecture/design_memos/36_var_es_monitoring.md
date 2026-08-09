---
ttl: permanent
doc_type: architecture_view
title: VaR/ES 与波动率监控（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: var_es_monitoring
scope: 07_trading_decision_architecture
---

# VaR/ES 与波动率监控（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G17 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G17 VaR/ES 与波动率监控 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5.4 |
| 依赖 | G16 |
| 对标 | 赢牛资管 VaR-ES / Sina 量化风控 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3 |
| 状态 | 骨架已建·待讨论（框架已列 §2.5.4，参数待定） |

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

> 以下来自 00_index §3 G17 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① VaR_95 计算（历史模拟/参数法）
- [ ] ② ES_95 计算
- [ ] ③ 入场 VaR/ES 基准
- [ ] ④ 触发动作（VaR>1.2×减仓20%/ES>1.3×再减20%）
- [ ] ⑤ 30 日波动率调整（每增10%→仓位减20%）
- [ ] ⑥ 数据窗口
- [ ] ⑦ 与回撤 Protocol 的协同

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G17
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5.4
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，依赖项）
- battle_map_09_risk_control（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G17 讨论要点占位，待讨论填空 |
