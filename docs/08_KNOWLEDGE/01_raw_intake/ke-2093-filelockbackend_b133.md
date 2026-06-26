---
module_id: KE-2002-----b133-000
status: active
title: 3. FileLockBackend（跨进程，B133）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3. FileLockBackend（跨进程，B133）

3. FileLockBackend（跨进程，B133）

```python
class FileLockBackend(LockBackend):
    lock_dir: str = ".pipeline_locks/"

    def try_lock(self, resource_id, owner, ttl_s) -> bool:
        """os.makedirs(lock_path, exist_ok=False)——文件系统原子性"""

    def _cleanup_stale(self):
        """检测 stale PID——TTL过期或进程已死→自动清理"""
```
