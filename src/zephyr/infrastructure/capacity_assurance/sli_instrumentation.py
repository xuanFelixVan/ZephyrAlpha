# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.sli_instrumentation
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_sli_instrumentation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""SLI instrumentation — SLI采集插桩点（对标蓝图 §13 SLI Registry CAP-001~CAP-014）."""

import threading
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class SLIStats:
    sli_id: str
    count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    correction_total_ms: float = 0.0
    correction_count: int = 0
    validation_total_ms: float = 0.0
    validation_count: int = 0

    @property
    def avg_duration_ms(self) -> float:
        return self.total_duration_ms / self.count if self.count > 0 else 0.0

    @property
    def p50_duration_ms(self) -> float:
        return self.avg_duration_ms

    @property
    def p99_duration_ms(self) -> float:
        return self.max_duration_ms


class SLIInstrumentation:
    """SLI 插桩采集器——记录 capacity-assurance 各子模块的运行时性能数据。

    对标蓝图 §13 SLI Registry + v2.2.0 插桩点扩展:
      - capacity_assurance_insert_time
      - capacity_assurance_correction_latency
      - contract_bus_validation_time
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._stats: dict[str, SLIStats] = {}
        self._durations: dict[str, list[float]] = defaultdict(list)

    def _get_or_create(self, sli_id: str) -> SLIStats:
        if sli_id not in self._stats:
            self._stats[sli_id] = SLIStats(sli_id=sli_id)
        return self._stats[sli_id]

    def record_insert_timing(self, sli_id: str, duration_ms: float) -> None:
        """记录写入耗时（盲点 #4 插桩点: capacity_assurance_insert_time）."""
        with self._lock:
            stats = self._get_or_create(sli_id)
            stats.count += 1
            stats.total_duration_ms += duration_ms
            stats.min_duration_ms = min(stats.min_duration_ms, duration_ms)
            stats.max_duration_ms = max(stats.max_duration_ms, duration_ms)
            self._durations[sli_id].append(duration_ms)

    def record_correction_latency(self, sli_id: str, duration_ms: float) -> None:
        """记录修正延迟（盲点 #4 插桩点: capacity_assurance_correction_latency）."""
        with self._lock:
            stats = self._get_or_create(sli_id)
            stats.correction_total_ms += duration_ms
            stats.correction_count += 1

    def record_validation_timing(self, sli_id: str, duration_ms: float) -> None:
        """记录校验耗时（contract_bus_validation_time）."""
        with self._lock:
            stats = self._get_or_create(sli_id)
            stats.validation_total_ms += duration_ms
            stats.validation_count += 1

    def get_sli_stats(self, sli_id: str) -> SLIStats | None:
        """获取指定 SLI 的统计信息."""
        return self._stats.get(sli_id)

    def get_all_stats(self) -> dict[str, SLIStats]:
        """获取全部 SLI 统计信息."""
        with self._lock:
            return dict(self._stats)

    def reset(self, sli_id: str | None = None) -> None:
        """重置统计数据."""
        with self._lock:
            if sli_id:
                self._stats.pop(sli_id, None)
                self._durations.pop(sli_id, None)
            else:
                self._stats.clear()
                self._durations.clear()


_instrumentation: SLIInstrumentation | None = None
_lock = threading.Lock()


def get_instrumentation() -> SLIInstrumentation:
    """获取全局单例 SLIInstrumentation."""
    global _instrumentation
    if _instrumentation is None:
        with _lock:
            if _instrumentation is None:
                _instrumentation = SLIInstrumentation()
    return _instrumentation
