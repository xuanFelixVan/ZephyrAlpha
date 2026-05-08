---
module_id: KE-module_blu-1__preemptionrecord-000
title: 1. PreemptionRecord
category: module_blueprint
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
