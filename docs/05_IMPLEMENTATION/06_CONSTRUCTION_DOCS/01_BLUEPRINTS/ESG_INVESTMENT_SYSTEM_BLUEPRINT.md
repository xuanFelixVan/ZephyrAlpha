---
module_id: ESG_INVESTMENT_SYSTEM_001
version: 1.0.0
status: Active
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

## 接口与契约（蓝图终稿）

- 全库 API 与事件约定真源：[`API_Contract.md`](../../../03_TRADING_TACTICS/API_Contract.md)。ESG 数据接入、评级映射、约束表达与报告口径需以该真源或其子契约为准。
- 与数据层接口：ESG 数据源元信息（供应商、覆盖范围、更新频率、授权）与标准化输出口径需闭合到契约。
- 与组合优化系统接口：ESG 约束（硬约束/软约束/惩罚项）表达与求解器输入输出需闭合到契约。
- 与合规监控系统接口：披露口径、排除名单与例外审批留痕需闭合到契约。

## 验收标准（可检查）

- 能为任一组合生成“ESG 暴露摘要 + 约束满足情况”的报告，并可追溯到数据源版本与评分映射版本。
- 能将至少一类 ESG 约束（如排除名单或碳强度上限）以可计算形式交给组合优化模块，并能验证优化结果满足约束。
- 能对 ESG 数据缺失/滞后提供明确降级策略（回填/冻结/剔除）并产生告警记录。
- 能记录并复现一次 ESG 规则变更的审批与生效范围（组合/资产类别/日期）。

## 已知限制

- ESG 数据源与监管披露细则在实施阶段进一步确定；本文先锁定责任边界、协作接口与验收闭环，字段字典与事件细化进入施工阶段。

## 相关文档

- [PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md](./PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md)  
- [COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md](../../../01_FRAMEWORK/COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT.md)  

