---
module_id: KE-4287-----000
title: DB-025-0016：task_repo CRUD 接口契约实现——§4 Python 代码块落地验证
category: module_blueprint
---

# DB-025-0016：task_repo CRUD 接口契约实现——§4 Python 代码块落地验证

DB-025-0016：task_repo CRUD 接口契约实现——§4 Python 代码块落地验证

验证 TaskRepo 类的 15 个方法签名与蓝图 §4 Python 代码块完全一致。

| 方法 | 蓝图签名 | 代码验证 |
|------|---------|---------|
| create | `(task: TaskCard) -> TaskCard` | grep task_repo.py |
| get | `(task_id: str) -> Optional[TaskCard]` | grep task_repo.py |
| update | `(task_id: str, updates: dict) -> TaskCard` | grep task_repo.py |
| upsert | `(task: TaskCard) -> TaskCard` | grep task_repo.py |
| delete | `(task_id: str) -> bool` | grep task_repo.py |
| hard_delete | `(task_id: str) -> bool` | grep task_repo.py |
| transition | `(task_id: str, to_status: Status) -> TaskCard` | grep task_repo.py |
| list_by_status | `(status: Status) -> list[TaskCard]` | grep task_repo.py |
| list_by_phase | `(phase: int) -> list[TaskCard]` | grep task_repo.py |
| list_by_session | `(session_id: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_namespace | `(namespace) -> list[TaskCard]` | grep task_repo.py |
| list_active | `() -> list[TaskCard]` | grep task_repo.py |
| list_by_dependency | `(dependency_task_id: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_tag | `(tag: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_blocked_by | `(blocker_task_id: str) -> list[TaskCard]` | grep task_repo.py |
