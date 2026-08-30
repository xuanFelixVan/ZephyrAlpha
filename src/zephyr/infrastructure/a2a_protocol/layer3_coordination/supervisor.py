# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.supervisor
# [DOMAIN] D_INFRA_A2A
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
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Supervisor — A2A Layer 3 Coordination

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: supervisor.py
# 层: 算法
# - id: A1
#   name_zh: ① Supervisor
#   name_en: Supervisor
#   intro: 监督者——任务分配、死锁检测、超时管理
#   desc: 监督者——任务分配、死锁检测、超时管理；公共方法（定义序）: tasks, submit_task, assign_task, detect_deadlocks, get_agent_load, get_pending…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: Supervisor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import datetime, timedelta

from zephyr.shared.utils.time_utils import now_utc

from ..layer2_communication.a2a_state import A2ATask, A2ATaskStatus


class Supervisor:
    """监督者——任务分配、死锁检测、超时管理"""

    def __init__(self):
        self._tasks: dict[str, A2ATask] = {}
        self._agent_load: dict[str, int] = {}
        self.MIN_TIMEOUT_MINUTES = 10
        self.MAX_TIMEOUT_HOURS = 24

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def tasks(self) -> dict[str, A2ATask]:
        """只读：tasks（Stage 4 公共化）。"""
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        """写入：tasks（Stage 4 公共化）。"""
        self._tasks = value

    def submit_task(self, task: A2ATask) -> A2ATask:
        if task.deadline is None:
            task.deadline = now_utc() + timedelta(hours=1)
        min_dl = now_utc() + timedelta(minutes=self.MIN_TIMEOUT_MINUTES)
        max_dl = now_utc() + timedelta(hours=self.MAX_TIMEOUT_HOURS)
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
            task.updated_at = now_utc()
            self._agent_load[agent_id] = self._agent_load.get(agent_id, 0) + 1
            return True
        return False

    def detect_deadlocks(self) -> list[dict]:
        deadlocks = []
        waiting_tasks = [t for t in self._tasks.values() if t.status == A2ATaskStatus.IN_PROGRESS]
        now = now_utc()
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
        now = now_utc()
        timeouts = []
        for task in self._tasks.values():
            if task.deadline and now > task.deadline:
                task.status = A2ATaskStatus.TIMEOUT
                timeouts.append({"task_id": task.task_id, "agent": task.to_agent, "status": "timeout"})
        return timeouts
