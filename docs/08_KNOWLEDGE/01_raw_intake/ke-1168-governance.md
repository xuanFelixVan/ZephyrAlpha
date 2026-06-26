---
module_id: KE-1083
title: AUD-003：审计日志访问受限
category: governance
ttl: permanent
---

# AUD-003：审计日志访问受限

AUD-003：审计日志访问受限

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AUD-003 | 审计日志只有 Auditor 和 Owner 角色可读（角色定义见 [GOV-SEC-002](../security/access-control-policy.md)），其他角色禁止访问 | 收回越权访问权限 |
