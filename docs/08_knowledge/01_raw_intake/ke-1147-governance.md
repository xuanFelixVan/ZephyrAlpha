---
module_id: KE-1062
title: ACS-004：权限审批流程
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# ACS-004：权限审批流程

ACS-004：权限审批流程

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 新增权限 | 必须由 Owner 审批，并记录审批理由 | 权限不生效 |
| 临时权限 | 必须设定过期时间，最长 7 天 | 过期后自动收回 |
| 权限变更 | 必须在 24 小时内更新权限矩阵 | 审计不通过 |
