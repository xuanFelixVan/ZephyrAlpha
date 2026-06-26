---
module_id: KE-2440------git-hook-003
title: 7.3 Collection 路由规则（git hook 默认）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 7.3 Collection 路由规则（git hook 默认）

7.3 Collection 路由规则（git hook 默认）

| 源路径模式 | 目标 Collection |
|-----------|----------------|
| **KB:decisions**（SQLite ingest / MCP KB） | `decisions` |
| `docs/03_modules/_b_track_interfaces/*interface*.md` | `decisions` |
| `src/**/*.py`, `src/**/*.yaml`, `docs/03_modules/**` | `code_context` |
| `docs/03_modules/l01-infrastructure/task-system/changes/**` | `task_history` |
| `docs/_working/audit/reports/**`, `docs/_working/audit/findings/**` | `lessons` |
| 其他 | `code_context`（保守默认） |

---
