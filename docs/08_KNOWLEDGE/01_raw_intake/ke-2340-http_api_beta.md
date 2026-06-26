---
module_id: KE-2245
title: 4.4 HTTP API（beta 预留骨架）
category: module_blueprint
ttl: permanent
---

# 4.4 HTTP API（beta 预留骨架）

4.4 HTTP API（beta 预留骨架）

| Method + Path | 对应库方法 |
|---------------|-----------|
| `POST /v1/tasks` | `submit_task()` |
| `GET /v1/tasks/{task_id}` | `get_task()` |
| `GET /v1/tasks?state=&agent=` | `list_tasks()` |
| `POST /v1/tasks/{task_id}/cancel` | `cancel_task()` |
| `POST /v1/agents` | `register_agent()` |
| `POST /v1/agents/{agent_id}/claim` | `claim_task()` |
| `POST /v1/tasks/{task_id}/progress` | `report_progress()` |
| `POST /v1/tasks/{task_id}/complete` | `complete_task()` |
| `POST /v1/tasks/{task_id}/fail` | `fail_task()` |
| `POST /v1/sandboxes` | `provision_sandbox()` |
| `DELETE /v1/sandboxes/{sandbox_id}` | `destroy_sandbox()` |
| `GET /v1/stats` | `stats()` |

---
