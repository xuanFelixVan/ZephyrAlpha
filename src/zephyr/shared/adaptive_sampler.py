"""
Adaptive Sampler — 容量保障自身资源消耗管控 (盲点 #6)
特性：
  - 消耗预算：容量保障系统自身消耗 ≤ 1% CPU / 5MB RSS 上限
  - 自适应降频：超过预算上限时采样频率递减
  - Observer Effect Compensator：与 observer_effect_compensator.py 联动
"""
import os
import time
import threading
from dataclasses import dataclass
from typing import Any, Optional


class AdaptiveSampler:
    """
    自适应采样器 (盲点 #6)
    """

    CPU_BUDGET = 0.01
    MEMORY_BUDGET_MB = 5
    MIN_SAMPLE_INTERVAL = 1.0
    MAX_SAMPLE_INTERVAL = 60.0

    def __init__(self):
        self._current_interval = 10.0
        self._sample_count = 0
        self._overhead_estimate = 0.0
        self._lock = threading.Lock()
        self._last_sample_time: float = 0

    def should_sample(self) -> bool:
        now = time.time()
        if now - self._last_sample_time < self._current_interval:
            return False
        self._last_sample_time = now
        self._sample_count += 1
        return True

    def report_overhead(self, cpu_usage: float, memory_mb: float):
        self._overhead_estimate = cpu_usage + memory_mb / 1024

        if cpu_usage > self.CPU_BUDGET or memory_mb > self.MEMORY_BUDGET_MB:
            self._current_interval = min(
                self._current_interval * 2, self.MAX_SAMPLE_INTERVAL
            )
        else:
            self._current_interval = max(
                self._current_interval * 0.5, self.MIN_SAMPLE_INTERVAL
            )

    def get_stats(self) -> dict:
        return {
            "sample_interval": self._current_interval,
            "total_samples": self._sample_count,
            "overhead_estimate": self._overhead_estimate,
            "cpu_budget": self.CPU_BUDGET,
            "memory_budget_mb": self.MEMORY_BUDGET_MB,
        }
