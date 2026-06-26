---
module_id: KE-2975
status: active
title: 检
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 检

检
```python
proto = CancelProtocol()
assert proto.can_cancel(task)  # 无consumer已完成
proto.cancel(task)
assert task.status == TaskStatus.CANCELLED
assert len(task.cancelled_artifacts) > 0
```
