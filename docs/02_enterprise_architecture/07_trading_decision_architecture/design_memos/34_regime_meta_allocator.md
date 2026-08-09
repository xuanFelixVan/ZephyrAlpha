---
ttl: permanent
doc_type: architecture_view
title: RegimeMetaAllocator 参数（骨架）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-09
topic: regime_meta_allocator
scope: 07_trading_decision_architecture
---

# RegimeMetaAllocator 参数（骨架·待讨论）

> **性质**：骨架文档。由 [00_index_trading_decision](00_index_trading_decision.md) G15 主题组派生占位，仅锁定"要讨论什么"，**不含任何已定决策**。
> **⚠️ 前置门槛**：参数须等 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) C1 验证通过（Shrinkage 有效性）+ 首批策略产出 PnL 后才能校准，本骨架仅锁定讨论范围。
> **施工图纪律**：本文档讨论定型（status→active）后才允许对应模块施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G15 RegimeMetaAllocator 参数 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | ⚠️ 11_regime_backtest_validation_plan C1 验证结果（Shrinkage 有效性）+ G04（PerformanceScore 需策略 PnL） |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（30_multi_strategy_concurrency §2.2） |
| 正交性 | ⚠️ 本身就是 regime 节流的消费者，等 C1 验证通过后再定参数 |
| 优先级 | P3（第二阶段，等 regime 验证 + 策略 track record） |
| 状态 | 骨架已建·待讨论（框架已定，MOD-PA-007 已登记，参数待 C1 验证后校准） |

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

> 以下来自 00_index §3 G15 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [ ] ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)`
- [ ] ② Base_i 先验权重
- [ ] ③ PerformanceScore 60 日 Sharpe 映射 [0.5,1.5]
- [ ] ④ Shrinkage 置信度→风险节流映射（30_multi_strategy_concurrency §2.2 四档）
- [ ] ⑤ floor≥5% / cap≤40%
- [ ] ⑥ 稀有态差异化收缩
- [ ] ⑦ 第二阶段上线时机

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G15
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（C1 验证，前置门槛）
- [10_regime_detector_spec](10_regime_detector_spec.md)（Shrinkage 产出方）
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G15 讨论要点占位，参数等 C1 验证后校准 |
