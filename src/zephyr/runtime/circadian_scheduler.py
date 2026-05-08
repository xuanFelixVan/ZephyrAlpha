"""
CircadianScheduler — 内置生物钟
=================================
蓝图: ARC-0001 §6.1
借鉴: K8s CronJob + Claude Code Dream Cycle
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class CircadianPhase(str, Enum):
    MORNING = "MORNING"
    DAY = "DAY"
    EVENING = "EVENING"
    NIGHT = "NIGHT"


class ScheduledTask:
    def __init__(self, hour: int, name: str, layer: str, callback: Callable[[], Any] | None = None) -> None:
        self.hour = hour
        self.name = name
        self.layer = layer
        self.callback = callback
        self.last_run_date: str = ""


class CircadianScheduler:
    """内置生物钟——系统节律管理器。"""

    def __init__(self, state_path: Path | None = None) -> None:
        self._state_path = state_path
        self._tasks: list[ScheduledTask] = []
        self._event_listeners: dict[str, list[Callable]] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def register_task(self, hour: int, name: str, layer: str, callback: Callable[[], Any] | None = None) -> None:
        self._tasks.append(ScheduledTask(hour=hour, name=name, layer=layer, callback=callback))

    def register_event_listener(self, event: str, callback: Callable) -> None:
        self._event_listeners.setdefault(event, []).append(callback)

    def trigger_event(self, event: str) -> None:
        for cb in self._event_listeners.get(event, []):
            try:
                cb()
            except Exception:
                pass

    def get_current_phase(self) -> CircadianPhase:
        hour = datetime.now().hour
        if 6 <= hour < 9:
            return CircadianPhase.MORNING
        if 9 <= hour < 18:
            return CircadianPhase.DAY
        if 18 <= hour < 21:
            return CircadianPhase.EVENING
        return CircadianPhase.NIGHT

    def get_next_task(self) -> ScheduledTask | None:
        now = datetime.now()
        current_hour = now.hour
        today = now.strftime("%Y-%m-%d")
        upcoming = [t for t in self._tasks if t.hour > current_hour and t.last_run_date != today]
        if not upcoming:
            return None
        return min(upcoming, key=lambda t: t.hour)

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="CircadianScheduler")
        self._thread.start()
        from zephyr.shared.lifecycle.resource_optimization_engine import ResourceOptimizationEngine
        try:
            ResourceOptimizationEngine().register_daemon(
                "circadian-scheduler", self.start, self.stop, priority=5,
            )
        except Exception:
            pass

    def stop(self) -> None:
        self._running = False
        self.save_state()

    def _loop(self) -> None:
        last_minute: int = -1
        while self._running:
            now = datetime.now()
            if now.minute == 0 and now.minute != last_minute:
                last_minute = now.minute
                today = now.strftime("%Y-%m-%d")
                for task in self._tasks:
                    if task.hour == now.hour and task.last_run_date != today:
                        task.last_run_date = today
                        if task.callback:
                            try:
                                task.callback()
                            except Exception:
                                pass
            time.sleep(30)

    def save_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "tasks": [
                {"hour": t.hour, "name": t.name, "layer": t.layer, "last_run_date": t.last_run_date}
                for t in self._tasks
            ]
        }
        self._state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
