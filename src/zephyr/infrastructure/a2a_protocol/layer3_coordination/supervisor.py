# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.supervisor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_state
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_supervisor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Supervisor — A2A Layer 3 Coordination"""

from datetime import datetime, timedelta

from ..layer2_communication.a2a_state import A2ATask, A2ATaskStatus


class Supervisor:
    """监督者——任务分配、死锁检测、超时管理"""

    def __init__(self):
        self._tasks: dict[str, A2ATask] = {}
        self._agent_load: dict[str, int] = {}
        self.MIN_TIMEOUT_MINUTES = 10
        self.MAX_TIMEOUT_HOURS = 24

    def submit_task(self, task: A2ATask) -> A2ATask:
        if task.deadline is None:
            task.deadline = datetime.utcnow() + timedelta(hours=1)
        min_dl = datetime.utcnow() + timedelta(minutes=self.MIN_TIMEOUT_MINUTES)
        max_dl = datetime.utcnow() + timedelta(hours=self.MAX_TIMEOUT_HOURS)
        if task.deadline < min_dl:
            task.deadline = min_dl
        if task.deadline > max_dl:
            task.deadline = max_dl
        self._tasks[task.task_id] = task
        if task.to_agent:
            self._agent_load[task.to_agent] = self._agent_load.get(task.to_agent, 0) + 1
        return task

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status == A2ATaskStatus.QUEUED:
            task.to_agent = agent_id
            task.status = A2ATaskStatus.ASSIGNED
            task.updated_at = datetime.utcnow()
            self._agent_load[agent_id] = self._agent_load.get(agent_id, 0) + 1
            return True
        return False

    def detect_deadlocks(self) -> list[dict]:
        deadlocks = []
        waiting_tasks = [t for t in self._tasks.values() if t.status == A2ATaskStatus.IN_PROGRESS]
        now = datetime.utcnow()
        for task in waiting_tasks:
            if task.deadline and now > task.deadline:
                deadlocks.append(
                    {
                        "task_id": task.task_id,
                        "agent": task.to_agent,
                        "deadline": task.deadline.isoformat(),
                        "action": "escalate",
                    }
                )
        return deadlocks

    def get_agent_load(self, agent_id: str) -> int:
        return self._agent_load.get(agent_id, 0)

    def get_pending_tasks(self) -> list[A2ATask]:
        return [t for t in self._tasks.values() if t.status in (A2ATaskStatus.CREATED, A2ATaskStatus.QUEUED)]

    def escalate_timeouts(self) -> list[dict]:
        now = datetime.utcnow()
        timeouts = []
        for task in self._tasks.values():
            if task.deadline and now > task.deadline:
                task.status = A2ATaskStatus.TIMEOUT
                timeouts.append({"task_id": task.task_id, "agent": task.to_agent, "status": "timeout"})
        return timeouts
