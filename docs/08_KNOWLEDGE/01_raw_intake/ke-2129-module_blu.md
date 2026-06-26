---
module_id: KE-2037
status: active
title: 3.1.2 任务卡生命周期管理器
category: module_blueprint
ttl: permanent
---

# 3.1.2 任务卡生命周期管理器

3.1.2 任务卡生命周期管理器

```python
class TaskLifecycleManager:
    """包装 task_repo.py 的 10 态状态机——增加 G0-G7 门禁 + .md 同步"""

    def __init__(self, repo: TaskRepo):
        self.repo = repo

    def create_task_card(self, task: "TaskCard") -> DecompositionResult:
        """创建任务卡——G0+G7 门禁通过 → task_repo.create() + .md 同步"""
        ...

    def transition(self, task_id: str, to_status: TaskStatus,
                   gate_check: bool = True) -> "TransitionResult":
        """状态转换——门禁通过 → task_repo.update_status(task_id, to_status)"""
        ...

    def check_gate(self, task_id: str, gate_id: "GateLevel") -> "GateCheckResult":
        """独立门禁检查——与 task_repo 无关的纯校验"""
        ...
```
