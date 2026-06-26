---
module_id: KE-1294
status: active
title: 1. PreemptionRecord
category: module_blueprint
ttl: permanent
---

# 1. PreemptionRecord

1. PreemptionRecord

```python
class PreemptionRecord(BaseModel):
    preempted_task_id: str
    preempting_task_id: str
    reason: str
    timestamp: str
    module_progress: str      # 当前执行到哪个模块
    savepoint: dict           # 已保存的状态快照
```
