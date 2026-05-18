---
blueprint_id: MOD-INF-019
---

# L3 Reference: Lock Protocol

> Belongs to: implementer (SKILL-ROL-IMP-001)
> Rule: "Release file locks after each write" (implementer CRITICAL Rule #5)

## Implementation Lock Protocol

### Why Locks Matter
- 10+ concurrent IDE sessions may write to same files
- SQLite single-writer limitation: all writes serialized
- Git index lock during concurrent commit operations

### Lock Hierarchy

```
Session Lock (per session_id)
  ├── Task Lock (per task_card.task_id)
  │     ├── File Write Lock (per file_path)
  │     └── DB Transaction Lock (SQLite WAL)
  └── Git Index Lock (during commit)
```

### Lock Acquisition Protocol

```python
from zephyr.pipeline.pipeline_lock import PipelineLock

lock = PipelineLock()
with lock.acquire(session_id, task_id):
    # All file writes and DB operations within this block
    write_file(path, content)
    db.execute(sql, params)
# ← lock released automatically on block exit
```

### Lock Timeout Rules

| Lock Type | Timeout | Retry | On Failure |
|-----------|---------|-------|------------|
| Session Lock | 30s | 3x | Wait, escalate |
| Task Lock | 10s | 2x | Error to caller |
| File Write Lock | 5s | 1x | Log+skip, queue for retry |
| Git Index Lock | 15s | 3x | Queue git op for async |

### Deadlock Prevention

- All locks acquired in fixed order: Session → Task → File/DB
- No nested cross-session locks
- Lock held duration: < 5 seconds for write operations
- Auto-release via context manager (`with lock.acquire(...):`)
