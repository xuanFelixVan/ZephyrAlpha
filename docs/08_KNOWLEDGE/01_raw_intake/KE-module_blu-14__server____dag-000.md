---
module_id: KE-module_blu-14__server____dag-000
title: 14. Server 依赖 DAG
category: module_blueprint
---

# 14. Server 依赖 DAG

14. Server 依赖 DAG

```
         ChromaDB ──────┐
         SQLite   ──────┤
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   knowledge_base  gate_engine   blueprint_search
         │              │              │
         └──────┬───────┘              │
                │                      │
                ▼                      │
          task_manager                 │
                │                      │
                ▼                      │
         session_handoff ──────────────┘
                │
                ▼
          intent_router
```

> 启动顺序：ChromaDB/SQLite → knowledge_base / gate_engine / blueprint_search（并行）→ task_manager → session_handoff → intent_router

---
