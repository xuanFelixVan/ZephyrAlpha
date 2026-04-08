---
module_id: ESG_INVESTMENT_SYSTEM_001
version: 0.1.0
status: Draft
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 战略与合规团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 11 战略决策 — ESG 投资
compliance_level: 专业标准
layer: Layer 11 (战略决策层)
responsibility:
  - ESG 评级与数据接入治理
  - ESG 约束与组合优化衔接
  - 报告与披露口径
---

# ESG 投资系统蓝图（ESG Investment System）

> **定位**：对应 [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) Layer 11「ESG 投资系统」；与 [GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md](../../../01_FRAMEWORK/GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md) 合规叙事衔接。  
> **对照表**：[LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md](../../../09_AUDIT/STATE/LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md)

## 职责边界

- **负责**：ESG 数据源选型、评分映射、硬/软约束进入组合优化、持仓 ESG 暴露报表。  
- **不负责**：替代 Layer 10 全部合规判责；具体排雷清单以合规蓝图为准。

## 核心能力（蓝图阶段）

| 能力 | 说明 |
|------|------|
| 数据层 | E、S、G 分项与综合分；更新频率与覆盖度 |
| 约束 | 排除名单、行业/主题上限、碳强度上限等 |
| 优化接口 | 与 [PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md](./PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md) 协同 |

## 相关文档

- [PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md](./PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md)  
- [COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md](../../../01_FRAMEWORK/COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md)  

---

**状态**：Draft — 数据源与监管口径落地后补 API 与字段字典。
