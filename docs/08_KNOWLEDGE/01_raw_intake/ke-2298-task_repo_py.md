---
module_id: KE-2204
status: active
title: 4. task_repo.py v2.0 核心接口
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4. task_repo.py v2.0 核心接口

4. task_repo.py v2.0 核心接口

```python
class TaskRepo:
    # CRUD
    def create(task: TaskCard) -> TaskCard
    def get(task_id: str) -> Optional[TaskCard]
    def update(task_id: str, updates: dict) -> TaskCard
    def upsert(task: TaskCard) -> TaskCard  # ON CONFLICT DO UPDATE（保留 created_at）
    def delete(task_id: str) -> bool  # 软删除（is_deleted=1）
    def hard_delete(task_id: str) -> bool  # 物理删除（仅限数据清理脚本）

    # 状态转换
    def transition(task_id: str, to_status: Status) -> TaskCard  # G1 门禁在写事务内执行

    # 查询
    def list_by_status(status: Status) -> list[TaskCard]   # 过滤 is_deleted=0
    def list_by_phase(phase: int) -> list[TaskCard]
    def list_by_session(session_id: str) -> list[TaskCard]
    def list_by_namespace(namespace) -> list[TaskCard]
    def list_active() -> list[TaskCard]

    # JSON1 查询
    def list_by_dependency(dependency_task_id: str) -> list[TaskCard]
    def list_by_tag(tag: str) -> list[TaskCard]
    def list_by_blocked_by(blocker_task_id: str) -> list[TaskCard]
```

状态转换时自动写入 events 表（不可变审计日志）。GateEngine 的 evaluate() 接受外部 conn 参数，门禁结果与状态转换在同一事务中原子落盘。

---
