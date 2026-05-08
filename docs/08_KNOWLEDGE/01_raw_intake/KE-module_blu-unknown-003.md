---
module_id: KE-module_blu-unknown-003
title: 检
category: module_blueprint
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
