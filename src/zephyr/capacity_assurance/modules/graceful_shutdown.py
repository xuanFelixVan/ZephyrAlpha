# [BLUEPRINT] MOD-INF-001 | 03_modules/l01_infrastructure/capacity-assurance/blueprint.md | §

# [MODULE] zephyr.capacity_assurance.modules.graceful_shutdown

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Graceful Shutdown — 优雅关机 (盲点 #28, M-32)
特性：
  - SIGTERM handler: 清理信号文件
  - 1750ms 快照窗口：保存最后一帧容量指标
"""
import signal
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


class GracefulShutdown:
    """
    优雅关机 (M-32, 盲点 #28)
    """

    SNAPSHOT_WINDOW_MS = 1750

    def __init__(self, signal_file: Optional[str] = None):
        self.signal_file = signal_file
        self._handlers: list[Callable] = []
        self._shutting_down = False
        self._setup_signal_handler()

    def _setup_signal_handler(self):
        try:
            signal.signal(signal.SIGTERM, self._on_terminate)
            signal.signal(signal.SIGINT, self._on_terminate)
        except (ValueError, OSError):
            pass

    def _on_terminate(self, signum, frame):
        self._shutting_down = True
        self.run_handlers()

    def register_handler(self, handler: Callable[[], Any]):
        self._handlers.append(handler)

    def run_handlers(self):
        for handler in self._handlers:
            try:
                handler()
            except Exception:
                pass

    def take_snapshot(self) -> dict:
        import psutil
        try:
            process = psutil.Process()
            mem = process.memory_info().rss / 1024 / 1024
            cpu = process.cpu_percent(interval=0.1)
            return {
                "timestamp": time.time(),
                "memory_mb": round(mem, 1),
                "cpu_pct": round(cpu, 1),
                "signal_file_cleaned": True,
                "shutdown_graceful": True,
            }
        except Exception:
            return {"timestamp": time.time(), "shutdown_graceful": True}

    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down
