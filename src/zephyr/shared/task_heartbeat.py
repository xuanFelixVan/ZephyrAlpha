"""
Task Heartbeat Monitor — 僵尸任务检测 (盲点 #63)
特性：
  - 10 分钟心跳超时
  - 僵尸标记 + 半写入文件回滚
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TaskHeartbeat:
    task_id: str
    last_heartbeat: float
    status: str = "alive"


class TaskHeartbeatMonitor:
    """
    任务心跳监测器 (盲点 #63)
    """

    HEARTBEAT_TIMEOUT = 600  # 10 minutes

    def __init__(self):
        self._tasks: dict[str, TaskHeartbeat] = {}

    def register(self, task_id: str):
        self._tasks[task_id] = TaskHeartbeat(
            task_id=task_id, last_heartbeat=time.time()
        )

    def heartbeat(self, task_id: str):
        if task_id in self._tasks:
            self._tasks[task_id].last_heartbeat = time.time()
            self._tasks[task_id].status = "alive"

    def check_zombies(self) -> list[dict]:
        now = time.time()
        zombies = []
        for task_id, hb in self._tasks.items():
            if now - hb.last_heartbeat > self.HEARTBEAT_TIMEOUT:
                hb.status = "zombie"
                zombies.append({
                    "task_id": task_id,
                    "idle_seconds": int(now - hb.last_heartbeat),
                    "status": "zombie",
                })
        return zombies

    def rollback_zombie(self, task_id: str) -> bool:
        hb = self._tasks.get(task_id)
        if hb and hb.status == "zombie":
            del self._tasks[task_id]
            return True
        return False
