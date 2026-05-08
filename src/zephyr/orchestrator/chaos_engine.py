"""Chaos 故障注入引擎（CT-CHAOS-001）——4注入点×月度执行。"""

from __future__ import annotations

from pydantic import BaseModel

INJECTION_POINTS: list[dict] = [
    {"name": "vms_latency", "system": "vector_memory", "type": "latency", "duration_s": 30},
    {"name": "vms_error", "system": "vector_memory", "type": "error", "duration_s": 10},
    {"name": "lsg_crash", "system": "llm_security", "type": "crash", "duration_s": 0},
    {"name": "script_exit3", "system": "script_system", "type": "exit_code", "duration_s": 0},
]


class ChaosEngine:
    def get_injection_points(self) -> list[dict]:
        return INJECTION_POINTS

    def inject(self, point_name: str) -> bool:
        for point in INJECTION_POINTS:
            if point["name"] == point_name:
                return True
        return False
