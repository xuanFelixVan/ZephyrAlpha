"""
Capacity Fingerprint — AI 生成非确定性容量指纹 (盲点 #39)
特性：
  - 定期采样模块的内存占用、导入时间
  - compare() 检测 2x 内存退化 / 3x 导入时间退化
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CapacityFingerprint:
    module_name: str
    memory_mb: float = 0.0
    import_time_ms: float = 0.0
    module_count: int = 0
    recorded_at: float = field(default_factory=time.time)


class CapacityFingerprinter:
    """
    容量指纹采集器 (盲点 #39)
    """

    MEMORY_DEGRADATION_THRESHOLD = 2.0
    IMPORT_DEGRADATION_THRESHOLD = 3.0

    def __init__(self):
        self._baselines: dict[str, CapacityFingerprint] = {}
        self._current: dict[str, CapacityFingerprint] = {}

    def set_baseline(self, fingerprint: CapacityFingerprint):
        self._baselines[fingerprint.module_name] = fingerprint

    def record(self, fingerprint: CapacityFingerprint):
        self._current[fingerprint.module_name] = fingerprint

    def compare(self, module_name: str) -> dict:
        baseline = self._baselines.get(module_name)
        current = self._current.get(module_name)

        if baseline is None or current is None:
            return {"degraded": False, "reason": "No baseline available"}

        memory_ratio = (current.memory_mb / max(baseline.memory_mb, 0.01))
        import_ratio = (current.import_time_ms / max(baseline.import_time_ms, 0.01))
        degraded = (memory_ratio >= self.MEMORY_DEGRADATION_THRESHOLD
                     or import_ratio >= self.IMPORT_DEGRADATION_THRESHOLD)

        return {
            "module_name": module_name,
            "degraded": degraded,
            "memory_ratio": round(memory_ratio, 2),
            "import_time_ratio": round(import_ratio, 2),
            "memory_threshold": self.MEMORY_DEGRADATION_THRESHOLD,
            "import_threshold": self.IMPORT_DEGRADATION_THRESHOLD,
        }
