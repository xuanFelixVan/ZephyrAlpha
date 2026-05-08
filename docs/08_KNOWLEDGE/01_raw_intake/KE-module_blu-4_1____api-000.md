---
module_id: KE-module_blu-4_1____api-000
title: 4.1 任务 API
category: module_blueprint
---

# 4.1 任务 API

4.1 任务 API

```python
class InProcessOrchestrator:

    async def submit_task(self, submit: TaskSubmit) -> TaskHandle:
        """
        提交任务。校验任务卡存在、依赖存在、capabilities 描述合法。
        状态：DRAFT → QUEUED（自动）。
        返回 handle，供调用方 await 终态。
        """

    async def get_task(self, task_id: str) -> Task | None: ...

    async def list_tasks(
        self,
        state: TaskState | list[TaskState] | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[Task]: ...

    async def cancel_task(self, task_id: str, reason: str) -> CancelResult:
        """状态转 CANCELLED，若 RUNNING 则先销毁沙箱与通知 Agent。"""
```
