---
module_id: KE-module_blu-2__memorylockbackend-000
title: 2. MemoryLockBackend（进程内）
category: module_blueprint
---

# 2. MemoryLockBackend（进程内）

2. MemoryLockBackend（进程内）

```python
class MemoryLockBackend(LockBackend):
    _locks: dict[str, LockEntry] = {}  # resource_id → LockEntry
    
    def try_lock(self, resource_id, owner, ttl_s) -> bool:
        """dict.setdefault 原子操作"""
```
