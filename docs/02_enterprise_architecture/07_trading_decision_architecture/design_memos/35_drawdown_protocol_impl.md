---
ttl: permanent
doc_type: architecture_view
title: 回撤 Protocol 落地 spec（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: drawdown_protocol_impl
scope: 07_trading_decision_architecture
---

# 回撤 Protocol 落地 spec（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G16 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G16 回撤 Protocol 落地 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5 |
| 依赖 | G12（仓位）—— 但框架已有，可并行 |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff（30_multi_strategy_concurrency §2.5 已引） |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 优先级 | P2（与 G12 并行） |
| 状态 | 骨架已建·待讨论（框架已定 §2.5，落地 spec 待讨论） |

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

> 以下来自 00_index §3 G16 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec
- [ ] ② 单策略 vs 组合层面分层（30_multi_strategy_concurrency §2.5.3）
- [ ] ③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）
- [ ] ④ Kill Switch 触发条件与执行路径（§2.5.5）
- [ ] ⑤ 日度熔断（组合 -4%/单策略 -5%）
- [ ] ⑥ Kill Switch 不可覆盖原则
- [ ] ⑦ 回撤基准净值计算口径
- [ ] ⑧ 与 regime Shrinkage 的协同（drawdown 是账户风险，regime 是市场风险，§2.5 定位）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G16
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5（四级框架已定，必先读）
- battle_map_09_risk_control（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G16 讨论要点占位，待讨论填空 |
