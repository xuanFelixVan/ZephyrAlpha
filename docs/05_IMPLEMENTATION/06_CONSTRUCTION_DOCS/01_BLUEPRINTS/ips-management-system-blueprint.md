---
module_id: IPS_MANAGEMENT_SYSTEM_001_9635
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-08
last_updated: '2026-04-08'
owner: 战略与治理团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 11 战略决策 — IPS（投资政策声明）
compliance_level: 专业标准
layer: layer_11
responsibility:
- IPS 文档结构化与版本管理
---



# IPS 管理系统蓝图（Investment Policy Statement）



> **定位**：对应 [ARCHITECTURE.md](../../../01_FRAMEWORK/ARCHITECTURE.md) Layer 11「IPS 管理系统」。  

> **对照表**：LAYER11_CAPABILITY_TO_BLUEPRINT_MAP_20260408.md



## 职责边界



- **负责**：IPS 条款结构化（资产类别、久期、杠杆、单一标的上限等）、版本与签批、与风控/再平衡规则同步。  

- **不负责**：法律文本起草；最终以持牌顾问或内控审定为准。



## 核心能力（蓝图阶段）



| 能力 | 说明 |

|------|------|

| 模型 | IPS 条目 → 可计算约束（阈值、频率） |

| 监控 | 违反 IPS 的预警与拦截策略 |

| 联动 | QUARTERLY_REBALANCE_BLUEPRINT.md、PORTFOLIO_CONSTRAINT_MANAGEMENT_BLUEPRINT.md |



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。IPS 条款结构化模型、约束表达、审批事件、审计留痕字段等需以该真源或其子契约为准。

- 与组合优化接口：IPS 可执行约束需以契约形式供组合优化/再平衡使用，避免“文档口径 ≠ 计算口径”。

- 与风险管理接口：风险预算/杠杆/集中度等条款的触发与拦截事件需闭合到契约。

- 与再平衡系统接口：调仓触发条件、豁免流程与生效时点需闭合到契约。



## 验收标准（可检查）



- 能将一份 IPS 文本条款映射为结构化条目（资产类别、阈值、频率、例外条款）并生成版本号。

- 能对任一组合进行 IPS 合规检查，输出可复核的“违反条款列表 + 证据数据 + 处理建议”。

- 能记录并复现一次 IPS 变更的审批链与生效范围（组合/账户/日期）。

- 能将关键条款（如杠杆上限、单一标的上限）下发为可计算约束并在优化/再平衡结果中验证生效。



## 已知限制



- 工作流细节（签批节点、权限模型）与审计日志字段将于施工阶段补齐；本蓝图先确保责任边界、接口闭合点与验收闭环清晰。



## 相关文档



- GOVERNANCE_COMPLIANCE_LAYER_BLUEPRINT.md  

- STRATEGIC_DECISION_LAYER_BLUEPRINT.md  



