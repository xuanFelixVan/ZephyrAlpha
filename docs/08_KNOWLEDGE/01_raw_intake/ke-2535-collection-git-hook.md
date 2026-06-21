---
module_id: KE-2440------git-hook-003
title: 7.3 Collection 路由规则（git hook 默认）
category: module_blueprint
---

# 7.3 Collection 路由规则（git hook 默认）

7.3 Collection 路由规则（git hook 默认）

| 源路径模式 | 目标 Collection |
|-----------|----------------|
| **KB:decisions**（SQLite ingest / MCP KB） | `decisions` |
| `docs/03_modules/_b_track_interfaces/*interface*.md` | `decisions` |
| `src/**/*.py`, `src/**/*.yaml`, `docs/03_modules/**` | `code_context` |
| `docs/03_modules/l01-infrastructure/task-system/changes/**` | `task_history` |
| `docs/09_audit/reports/**`, `docs/09_audit/findings/**` | `lessons` |
| 其他 | `code_context`（保守默认） |

---
