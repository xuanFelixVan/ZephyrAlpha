---
module_id: KE-1293
status: active
title: 1. PipelineLock 接口
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1. PipelineLock 接口

1. PipelineLock 接口

```python
class PipelineLock(BaseModel):
    backend: LockBackend

    def acquire(self, resource_id: str, owner: str, ttl_s: int=300) -> bool
    def release(self, resource_id: str, owner: str) -> bool
    def is_locked(self, resource_id: str) -> bool
    def get_owner(self, resource_id: str) -> str|None
    def conflicts(self) -> list[dict]
```
