---
module_id: KE-1677
status: active
title: 2.1 Phase 状态机
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 Phase 状态机

2.1 Phase 状态机

```python
from enum import Enum

class PhaseStatus(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    VERIFIED = "verified"
    BLOCKED = "blocked"

class Phase:
    def __init__(self, name: str, description: str, depends_on: list[str], status: PhaseStatus):
        self.name = name
        self.description = description
        self.depends_on = depends_on
        self.status = status
```
