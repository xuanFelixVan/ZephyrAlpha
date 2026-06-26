---
module_id: KE-2602
status: active
title: CT-DB-001：task_repo CRUD 契约
category: module_blueprint
ttl: permanent
---

# CT-DB-001：task_repo CRUD 契约

CT-DB-001：task_repo CRUD 契约

```yaml
contract_id: CT-DB-001
provider: MOD-DATABASE (TaskRepository)
consumers:
  - MOD-TASK_SYSTEM (task-system)
  - MOD-INF-009 (pipeline)
  - MOD-INF-013 (mcp-servers)

operations:
  create:
    input: "Task (Pydantic V2, 62 fields)"
    output: "TaskCard"
    errors: [P0InflationFrozenError, P0InflationWarning, sqlite3.IntegrityError]
    idempotency: "task_id UNIQUE 约束——重复创建抛 IntegrityError"

  get:
    input: "task_id: str"
    output: "TaskCard | None"
    filter: "is_deleted = 0（自动过滤软删除行）"

  transition:
    input: "task_id + to_status: TaskStatus + session_id?"
    output: "TaskCard"
    errors: [TaskNotFoundError, InvalidTransitionError, GateViolationError]
    atomicity: "G1门禁 + 状态写入 + events 写入在同一写事务内"
    state_machine: "10状态机——§4 转换表"

  upsert:
    input: "Task + files?"
    output: "TaskCard"
    semantics: "ON CONFLICT DO UPDATE——保留 created_at，覆盖其他字段"

  delete:
    input: "task_id: str"
    output: "bool"
    semantics: "软删除——设置 is_deleted=1 + deleted_at"

  list_by_*:
    input: "filter params"
    output: "list[TaskCard]"
    filter: "is_deleted = 0（自动排除软删除行）"
    supported_filters: [status, phase, session_id, namespace, dependency, tag, blocked_by]
```
