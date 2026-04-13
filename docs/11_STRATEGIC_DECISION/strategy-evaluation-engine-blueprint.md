---
module_id: 11_STRATEGIC_DECISION_STRATEGY_EVAL_ENGINE_REF
layer: layer_11
status: Active
document_type: strategic_reference_entry
reference_canonical: "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md"
created_date: "2026-04-13"
last_updated: "2026-04-13"
owner: 首席文档架构师
standard_type: 战略层参考入口
---

# 策略评估引擎 — 战略决策层参考入口

> **文档类型**: 战略决策层（Layer 11）引用入口
> **规范完整版**: [组合绩效评估模块蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md)
> **维护原则**: 本文档仅作为战略层导航入口，不包含独立技术规范内容

---

## 战略定位

策略评估引擎是战略决策层的"成绩单"模块，持续计算各策略和整体组合的绩效指标
（Sharpe、Calmar、最大回撤、信息比率等），为战略层"保留/加仓/削减/下线"某策略
的决策提供数据支撑。

**战略决策关注点**：
- 策略存活/淘汰的绩效阈值设定
- 多策略组合的相关性与分散度监控
- 滚动窗口绩效衰减的预警触发逻辑

---

## 规范文档

本文档的完整技术规范位于：

> 📄 **[组合绩效评估模块蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md)**

---

## 相关链接

| 文档 | 说明 |
|------|------|
| **[组合绩效评估模块蓝图（完整规范）](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/portfolio-performance-evaluation-blueprint.md)** | 架构设计、接口、实施路径 |
| [Layer 11 战略索引](./INDEX.md) | — |
| [动态风险预算（战略入口）](./risk-budgeting-framework-blueprint.md) | — |

---

> ⚠️ **维护说明**：本文档是 `11_STRATEGIC_DECISION` 层的导航入口。
> 技术内容变更请更新规范文档，此处仅保持引用链接稳定。
