---
module_id: KE-1219
title: SEC-005：密钥撤销
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# SEC-005：密钥撤销

SEC-005：密钥撤销

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 人员离职 | 24小时内撤销其所有密钥访问权限 | 未撤销视为 P1 事件 |
| 服务下线 | 7天内撤销该服务的所有密钥 | 未撤销视为 P2 事件 |
| 密钥泄露确认 | 立即撤销 | 不撤销视为 P0 事件 |
