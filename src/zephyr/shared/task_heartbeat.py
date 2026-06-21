# [A_module] module_id=MOD-SHR_task_heartbeat | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class TaskPulse:
    task_id: str
    last_pulse: float
    interval_seconds: float
    is_alive: bool


class TaskHeartbeat:
    def __init__(self, default_interval: float = 60.0, timeout_factor: float = 3.0):
        self._default_interval = default_interval
        self._timeout_factor = timeout_factor
        self._pulses: dict[str, tuple[float, float]] = {}

    def start(self, task_id: str, interval: float | None = None) -> None:
        self._pulses[task_id] = (time.time(), interval or self._default_interval)

    def pulse(self, task_id: str) -> None:
        if task_id in self._pulses:
            _, interval = self._pulses[task_id]
            self._pulses[task_id] = (time.time(), interval)

    def check(self, task_id: str) -> TaskPulse:
        if task_id not in self._pulses:
            return TaskPulse(task_id, 0.0, self._default_interval, False)
        last, interval = self._pulses[task_id]
        alive = (time.time() - last) <= interval * self._timeout_factor
        return TaskPulse(task_id, last, interval, alive)

    def detect_dead(self) -> list[str]:
        return [tid for tid in self._pulses if not self.check(tid).is_alive]
