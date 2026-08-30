# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_work_steal
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
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
A2A 工作窃取调度器 — 跨 Agent 负载均衡

当某 Agent 空闲而其他 Agent 队列有排队任务时，触发工作窃取:
  1. 空闲 Agent 广播 "available" 消息
  2. 检查所有其他 Agent 的任务队列
  3. 按优先级窃取最适合的任务
  4. 窃取成功: 任务状态 -> STOLEN, 所有权转移

策略:
  - 优先窃取高优先级任务
  - 防止重复窃取 (task_id 去重)
  - max_steal_per_cycle 限制单次窃取数量

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_steal_per_cycle 参数
#   fields: 参数 max_steal_per_cycle（无注解）
#   code: a2a_work_steal.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: steal_threshold 参数
#   fields: 参数 steal_threshold（无注解）
#   code: a2a_work_steal.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: idle_threshold 参数
#   fields: 参数 idle_threshold（无注解）
#   code: a2a_work_steal.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TaskQueue
#   name_en: TaskQueue
#   intro: class TaskQueue 源码 L83-L104
#   desc: 公共方法（定义序）: add, remove, load, has_spare_capacity；源码 L83-L104
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② A2AWorkSteal
#   name_en: A2AWorkSteal
#   intro: A2A 工作窃取引擎 — 跨 Agent 负载均衡.
#   desc: A2A 工作窃取引擎 — 跨 Agent 负载均衡. 策略: 检查所有 Agent 队列 -> 选负载最高的 -> 窃取其最高优先级任务 已窃取的任务标记 "stolen_by"…；公共方法（定义序）: max_ste…
#   inputs: max_steal_per_cycle steal_threshold idle_threshold
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TaskQueue, A2AWorkSteal
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskQueue:
    agent_id: str
    pending_tasks: list[dict] = field(default_factory=list)
    max_queue: int = 20

    def add(self, task: dict):
        if len(self.pending_tasks) < self.max_queue:
            self.pending_tasks.append(task)

    def remove(self, task_id: str) -> dict | None:
        for i, t in enumerate(self.pending_tasks):
            if t.get("task_id") == task_id:
                return self.pending_tasks.pop(i)
        return None

    @property
    def load(self) -> int:
        return len(self.pending_tasks)

    @property
    def has_spare_capacity(self) -> bool:
        return len(self.pending_tasks) < self.max_queue


class A2AWorkSteal:
    """A2A 工作窃取引擎 — 跨 Agent 负载均衡.

    策略:
      检查所有 Agent 队列 -> 选负载最高的 -> 窃取其最高优先级任务
      已窃取的任务标记 "stolen_by" 防止重复转移.
    """

    def __init__(
        self,
        max_steal_per_cycle: int = 3,
        steal_threshold: int = 2,
        idle_threshold: int = 0,
    ):
        self._max_steal_per_cycle = max_steal_per_cycle
        self._steal_threshold = steal_threshold
        self._idle_threshold = idle_threshold
        self._stolen: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_steal_per_cycle(self):
        """只读：max_steal_per_cycle（Stage 4 公共化）。"""
        return self._max_steal_per_cycle

    @max_steal_per_cycle.setter
    def max_steal_per_cycle(self, value):
        """写入：max_steal_per_cycle（Stage 4 公共化）。"""
        self._max_steal_per_cycle = value

    @property
    def stolen(self) -> set[str]:
        """只读：stolen（Stage 4 公共化）。"""
        return self._stolen

    @stolen.setter
    def stolen(self, value):
        """写入：stolen（Stage 4 公共化）。"""
        self._stolen = value

    def steal(
        self,
        idle_agent_id: str,
        all_queues: dict[str, TaskQueue],
    ) -> list[dict]:
        stolen_tasks: list[dict] = []

        idle_queue = all_queues.get(idle_agent_id)
        if idle_queue is None or not idle_queue.has_spare_capacity:
            return stolen_tasks

        candidates = sorted(
            [
                (aid, queue)
                for aid, queue in all_queues.items()
                if aid != idle_agent_id and queue.load > self._steal_threshold
            ],
            key=lambda x: x[1].load,
            reverse=True,
        )

        for _victim_id, queue in candidates:
            if len(stolen_tasks) >= self._max_steal_per_cycle:
                break

            sorted_tasks = sorted(
                queue.pending_tasks,
                key=lambda t: (t.get("priority", 0), -len(t.get("task_id", ""))),
                reverse=True,
            )

            for task in sorted_tasks:
                task_id = task.get("task_id", "")
                if task_id in self._stolen:
                    continue
                if len(stolen_tasks) >= self._max_steal_per_cycle:
                    break

                removed = queue.remove(task_id)
                if removed is not None:
                    task["stolen_by"] = idle_agent_id
                    self._stolen.add(task_id)
                    stolen_tasks.append(task)

        return stolen_tasks
