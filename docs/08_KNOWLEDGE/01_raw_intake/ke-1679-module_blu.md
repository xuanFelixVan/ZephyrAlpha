---
module_id: KE-1589
status: active
title: 19.1 受控旁路机制
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 19.1 受控旁路机制

19.1 受控旁路机制

```yaml
override_protocol:
  principle: "Owner is the final authority, every override permanently recorded"
  constraints:
    - max_duration: "24h"
    - require_justification: true
    - audit_permanent: true     # SQLite + JSONL双写
    - limit_per_month: 10
    - scope: "per_gate"
    - auto_reenable: true
  forbidden:
    - 不能override circuit_breaker OPEN（AP4）
    - 不能override GATE-18 pre-commit
    - 不能批量override（一次一个gate）
```
