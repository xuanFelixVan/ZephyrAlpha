---
module_id: KE-1027
status: active
title: 8.1 表结构（当前实装）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 表结构（当前实装）

8.1 表结构（当前实装）

```sql
CREATE TABLE gates (
    gate_run_id   TEXT PRIMARY KEY,       -- UUIDv4，格式 "gr-<uuid>"
    gate_id       TEXT NOT NULL,          -- "G1:task-xxx" 形式（gate_id:task_id）
    passed        INTEGER NOT NULL,       -- 0/1
    details       TEXT NOT NULL,          -- JSON（见§8.2）
    artifact_path TEXT,                   -- 产物路径，可空
    created_at    TEXT NOT NULL           -- ISO 8601
);
```
