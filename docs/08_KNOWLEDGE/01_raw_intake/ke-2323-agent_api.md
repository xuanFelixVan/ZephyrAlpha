---
module_id: KE-2228
status: active
title: 4.2 Agent API
category: module_blueprint
ttl: permanent
---

# 4.2 Agent API

4.2 Agent API

```python
    async def register_agent(self, spec: AgentSpec) -> AgentHandle:
        """Agent 启动时调用。失败场景：agent_id 重复。"""

    async def claim_task(
        self,
        agent_id: str,
        capabilities: list[str],
    ) -> Task | None:
        """
        拉取一个 QUEUED 任务，要求：依赖全 COMPLETED + capabilities 覆盖任务需求。
        原子性由 SQLite 事务保证，避免两 Agent 拿到同一任务。
        状态：QUEUED → ASSIGNED。
        """

    async def report_progress(
        self,
        agent_id: str,
        task_id: str,
        progress: AgentProgress,
    ) -> None:
        """
        Agent 执行中周期上报（心跳）。
        内部动作：
          1. 更新 last_progress_at
          2. 运行 §3.3 幻觉检测规则
          3. 若命中 → 状态转 HALLUCINATING，销毁沙箱，上报 FLE
        首次 report_progress 时：ASSIGNED → RUNNING。
        """

    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
        result: TaskResult,
    ) -> CompleteResult:
        """
        Agent 声明完成。
        内部流程：
          1. 状态 RUNNING → REVIEWING
          2. 调用 LSG 审查输出 schema（若 LSG 启用）
          3. 若 result.test_passed=False → 转 FAILED
          4. 审查通过 → REVIEWING → COMPLETED
          5. 写 VMS task_history（软失败，不阻塞）
          6. 销毁沙箱
          7. 上报 FLE 完成指标
        """

    async def fail_task(
        self,
        agent_id: str,
        task_id: str,
        failure: TaskFailure,
    ) -> None:
        """
        Agent 主动声明失败。
        状态：* → FAILED（或 retryable 且 retry_count < max_retry 则 → QUEUED）。
        """

    async def heartbeat(self, agent_id: str) -> None: ...
```
