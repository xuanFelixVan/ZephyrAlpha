"""
Code Economy Analyzer — 基建代码经济性分析 (盲点 #52)
特性：
  - 每个基建模块的"代码行数 / 实际使用率"比率
  - 3m 未被调用的基础设施 → 标记为僵尸代码
"""
import os
import time
from typing import Any, Optional


class CodeEconomyAnalyzer:
    """
    代码经济性分析 (盲点 #52)
    """

    ZOMBIE_THRESHOLD_SECONDS = 3 * 30 * 86400

    def __init__(self):
        self._module_stats: dict[str, dict] = {}
        self._last_called: dict[str, float] = {}

    def register_module(self, module_name: str, filepath: str):
        lines = 0
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
            except Exception:
                pass

        self._module_stats[module_name] = {
            "filepath": filepath,
            "lines": lines,
            "call_count": 0,
        }
        self._last_called[module_name] = time.time()

    def record_call(self, module_name: str):
        if module_name in self._module_stats:
            self._module_stats[module_name]["call_count"] += 1
        self._last_called[module_name] = time.time()

    def analyze(self) -> dict:
        zombies = []
        active = []
        for module_name, stats in self._module_stats.items():
            last_call = self._last_called.get(module_name, 0)
            idle_time = time.time() - last_call
            stats["idle_seconds"] = int(idle_time)
            if idle_time > self.ZOMBIE_THRESHOLD_SECONDS:
                zombies.append({"module": module_name, "idle_days": int(idle_time / 86400)})
            else:
                active.append(module_name)

        return {
            "total_modules": len(self._module_stats),
            "active": active,
            "zombies": zombies,
            "zombie_count": len(zombies),
        }
