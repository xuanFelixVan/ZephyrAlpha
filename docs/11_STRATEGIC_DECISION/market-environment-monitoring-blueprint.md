---
module_id: 11_STRATEGIC_DECISION_MARKET_ENV_MONITORING_REF
layer: layer_11
status: Active
document_type: strategic_reference_entry
reference_canonical: "docs/01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md"
created_date: "2026-04-13"
last_updated: "2026-04-13"
owner: 首席文档架构师
standard_type: 战略层参考入口
---

# 市场状态监测 — 战略决策层参考入口

> **文档类型**: 战略决策层（Layer 11）引用入口
> **规范完整版**: [市场状态识别系统蓝图](../01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md)
> **维护原则**: 本文档仅作为战略层导航入口，不包含独立技术规范内容

---

## 战略定位

市场状态识别（Market Regime Detection）是战略决策层的信号源头，通过实时判定市场所处状态
（趋势/震荡/高波动/危机）驱动上层策略权重调整和风险预算动态再分配。
战略层依赖此模块作为宏观环境感知的"第一感受器"。

**战略决策关注点**：
- 市场状态切换的滞后窗口与确认机制
- 状态变化对各策略仓位上限的联动影响
- 危机状态触发全局熔断的条件定义

---

## 规范文档

本文档的完整技术规范位于：

> 📄 **[市场状态识别系统蓝图](../01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md)**

---

## 相关链接

| 文档 | 说明 |
|------|------|
| **[市场状态识别系统蓝图（完整规范）](../01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md)** | 架构设计、接口、实施路径 |
| [Layer 11 战略索引](./INDEX.md) | — |
| [动态风险预算（战略入口）](./risk-budgeting-framework-blueprint.md) | — |

---

> ⚠️ **维护说明**：本文档是 `11_STRATEGIC_DECISION` 层的导航入口。
> 技术内容变更请更新规范文档，此处仅保持引用链接稳定。
