---
module_id: KE-module_blu-3_5_mcp-000
title: 3.5 MCP 接口
category: module_blueprint
---

# 3.5 MCP 接口

3.5 MCP 接口

> **MCP Server 位置**：[task_manager_server.py](file:///D:/ZephyrAlpha/src/zephyr/mcp/task_manager_server.py)
>
> **数据真源**：[task_repo.py](file:///D:/ZephyrAlpha/src/zephyr/db/task_repo.py)（SQLite）——MCP Server 不得使用内存字典

**Tools**：

| Tool | API | 输入 | 输出 | 对接 task_repo |
|------|-----|------|------|:---:|
| `decompose_blueprint` | `decompose()` | `{blueprint_path, output_dir}` | `{total_tasks, task_ids, warnings}` | `task_repo.create()` |
| `create_task` | `create_task_card()` | `{task_card_json}` | `{task_id, status}` | `task_repo.create()` |
| `update_task_status` | `transition()` | `{task_id, new_status}` | `{task_id, title, status, ...}` | `task_repo.transition()` |
| `get_task` | — | `{task_id}` | `{task_id, title, status, ...}` | `task_repo.get()` |
| `register_from_triage` | — | `{triage_path, namespace?, phase?}` | `{task_id, title, status, ...}` | `task_repo.create()` |

> **.md 双轨同步**：`_persist()` / `transition()` 成功后自动调用 `_taskcard_to_md()` 同步 `.md` 到 `docs_dir/tasks/{task_id}.md`。
> .md 文件为**只读人类可读副本**——SQLite 始终是真源。

**错误码**：`TASK_NOT_FOUND(404)` / `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` / `VALIDATION_ERROR(400)` / `PATH_NOT_COMPLIANT(422)` / `REPO_NOT_INJECTED(500)`
