---
module_id: KE-1102
title: COND-002：报告分发必须遵循最小权限原则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# COND-002：报告分发必须遵循最小权限原则

COND-002：报告分发必须遵循最小权限原则

| 角色 | 可见范围 | 说明 |
|------|---------|------|
| Owner | 全部报告 | 最高权限 |
| 策略团队 | 仅可见所管策略的绩效报告 | 不能跨策略查看 |
| 数据团队 | 仅数据质量报告 | 不能查看交易和风控数据 |
| 合规/审计团队 | 风控合规 + 月度审计报告 | 不包含策略 Alpha 细节 |

分发权限与分发频率通过 `report-access-control.yaml` 管理（参见 GOV-SEC-001）
