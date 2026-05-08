---
module_id: KE-module_blu-src_zephyr_orchestrator_protoc-003
title: src/zephyr/orchestrator/protocol.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/orchestrator/protocol.py (experimental 产出)

src/zephyr/orchestrator/protocol.py (experimental 产出)

from typing import Protocol

class OrchestratorProtocol(Protocol):
    # 任务
    async def submit_task(self, task: TaskSubmit) -> TaskHandle: ...
    async def get_task(self, task_id: str) -> Task | None: ...
    async def list_tasks(self, filters: TaskFilters | None = None) -> list[Task]: ...
    async def cancel_task(self, task_id: str, reason: str) -> CancelResult: ...

    # Agent
    async def register_agent(self, spec: AgentSpec) -> AgentHandle: ...
    async def claim_task(self, agent_id: str, capabilities: list[str]) -> Task | None: ...
    async def report_progress(self, agent_id: str, task_id: str, progress: AgentProgress) -> None: ...
    async def complete_task(self, agent_id: str, task_id: str, result: TaskResult) -> CompleteResult: ...
    async def fail_task(self, agent_id: str, task_id: str, failure: TaskFailure) -> None: ...

    # 沙箱
    async def provision_sandbox(self, task_id: str, policy: SandboxPolicy) -> Sandbox: ...
    async def destroy_sandbox(self, sandbox_id: str) -> None: ...

    # 健康与统计
    async def stats(self) -> OrchestratorStats: ...

class InProcessOrchestrator:
    """experimental（当前目标）：SQLite + asyncio.Queue，单进程。"""

class DistributedOrchestrator:
    """beta+：ARQ + Redis，多 worker。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessOrchestrator`（SQLite + asyncio.Queue）** | 单进程，多 Agent 协程 | - |
| beta | `DistributedOrchestrator`（ARQ + Redis） | 多 worker 进程 | 任务量 > 100/天 或并发 Agent > 10 |
| stable | NATS JetStream | 分布式 | 跨机 Agent / 实时通信 < 1s 需要 |

**所有 API 均为 `async`**。进程内锁用 `asyncio.Lock`，跨进程锁用 `filelock.FileLock`。SQLite 使用 WAL 模式支持多协程并发读。**严禁 `threading.Lock`**。

---
