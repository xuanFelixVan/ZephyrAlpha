---
module_id: KE-DOCUMENTAT-R35-META-STRATEGY-L05-META-001
status: active
title: 决策 R35：meta_strategy 归属 `l05/meta_router/`，不新建 l15 层（Closes OQ-023，N11）
category: documentation
---

# 决策 R35：meta_strategy 归属 `l05/meta_router/`，不新建 l15 层（Closes OQ-023，N11）

决策 R35：meta_strategy 归属 `l05/meta_router/`，不新建 l15 层（Closes OQ-023，N11）

**决策**：Meta-Strategy Router 代码归属 `pf_core/meta_router/`，否决新建独立 `l15_meta_strategy/` 层。

**方案对比**：

| 方案 | 描述 | 优点 | 缺点 | 结论 |
|------|------|------|------|------|
| **方案 A**：独立 `l15_meta_strategy/` | meta_strategy 单独成顶层 | 语义独立清晰 | 产生 15 层超出业界惯例；依赖 L05 优化器和 L04 风控，独立出去跨层耦合变重；AI Operator 挂载位置与 OQ-063 C-1 预留冲突 | ❌ 否决 |
| **方案 B**：归入 `l05/meta_router/` ✅ | 元策略作为 portfolio construction 子模块 | 语义准确（元策略是组合构建的高阶形态）；共用 StrategyRegistry；14 层保持；AI Operator 自然落 `l05/_ai_operator/` | 初看不直觉（"元"字让人觉得该在 L05 之上）| ✅ 采纳 |

**归属理由**：meta_strategy（元策略路由）从 700+ 策略池选取并加权组合，与 `l05/optimization/`（权重优化）共用底层数学工具，与 `l05/rebalancing/`（再平衡）共用时间维度管理，与 `StrategyRegistry` 高度耦合——三重耦合决定归属 L05 最优。`diversity_gatekeeper`（OQ-031）同归 `l05/meta_router/`。

**落盘位置**：`application_architecture.md` §4.1 L05 `meta_router/` 子模块完整清单 + 归属决策说明
