---
ttl: permanent
doc_type: architecture_view
title: 冲突矩阵清理与事件总线（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: cross_cutting_cleanup
scope: 07_trading_decision_architecture
---

# 冲突矩阵清理与事件总线（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G27 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G27 冲突矩阵清理与事件总线 |
| 所属 | 作战地图 12 |
| 依赖 | G04-G13（架构定型后才能清理冲突） |
| 对标 | 机构事件总线 / 微服务信号路由 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3（架构定型后） |
| 状态 | 骨架已建·待讨论（部分已裁定 rejected） |

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

> 以下来自 00_index §3 G27 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① battle_map_12 §16 的 31 条跨策略冲突仲裁→大部分因 A 模型消失（30_multi_strategy_concurrency §7.3）
- [ ] ② 仅留 firm-level 硬上限
- [ ] ③ 事件总线/信号注入机制
- [ ] ④ 实时计算节奏（盘中 vs 盘后）
- [ ] ⑤ 配置驱动（参数热更新/AB 测试）
- [ ] ⑥ 多策略投票降级（BM-SEL-20 已 rejected，30_multi_strategy_concurrency §7.3）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G27
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §7.3
- battle_map_12_cross_cutting §16（31 条冲突仲裁当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G27 讨论要点占位，待讨论填空 |
