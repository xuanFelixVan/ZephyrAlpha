---
module_id: IPS_MANAGEMENT_SYSTEM_001
version: 0.1.0
status: Draft
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 战略与治理团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 11 战略决策 — IPS（投资政策声明）
compliance_level: 专业标准
layer: Layer 11 (战略决策层)
responsibility:
  - IPS 文档结构化与版本管理
  - 风险收益目标与约束的可执行映射
  - 合规检查与再平衡/调仓触发联动
---

# IPS 管理系统蓝图（Investment Policy Statement）

> **定位**：对应 [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) Layer 11「IPS 管理系统」。  
> **对照表**：[LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md](../../../09_AUDIT/STATE/LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md)

## 职责边界

- **负责**：IPS 条款结构化（资产类别、久期、杠杆、单一标的上限等）、版本与签批、与风控/再平衡规则同步。  
- **不负责**：法律文本起草；最终以持牌顾问或内控审定为准。

## 核心能力（蓝图阶段）

| 能力 | 说明 |
|------|------|
| 模型 | IPS 条目 → 可计算约束（阈值、频率） |
| 监控 | 违反 IPS 的预警与拦截策略 |
| 联动 | [QUARTERLY_REBALANCE_BLUEPRINT.md](./QUARTERLY_REBALANCE_BLUEPRINT.md)、[PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md](./PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md) |

## 相关文档

- [GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md](../../../01_FRAMEWORK/GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md)  
- [STRATEGIC_DECISION_LAYER_BLUEPRINT.md](../../../01_FRAMEWORK/STRATEGIC_DECISION_LAYER_BLUEPRINT.md)  

---

**状态**：Draft — 实施阶段补工作流与审计日志字段。
