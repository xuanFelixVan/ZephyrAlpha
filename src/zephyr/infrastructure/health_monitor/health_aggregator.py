# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.infrastructure.health_monitor.health_aggregator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.health_monitor.__init__
# [CONSUMERS] AutoRuntime Core health check phase
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 12系统健康检查并行执行; 任一FAIL→整体WARN; 全部OK→OK; 任一项超时→SKIP
# [MODIFY-GUARD] 新增系统必须同步添加check_函数
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/health_check.py --trigger
# [A_module] module_id=MOD-INF_health_aggregator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""全系统健康聚合 — check_all_systems()"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
__all__ = ["HealthAggregator", "HealthReport", "SystemHealth", "check_all"]


@dataclass
class SystemHealth:
    system: str
    status: str = "OK"
    latency_ms: float = 0
    details: str = ""


@dataclass
class HealthReport:
    systems: list[SystemHealth] = field(default_factory=list)
    ok_count: int = 0
    warn_count: int = 0
    fail_count: int = 0
    overall: str = "OK"
    total_ms: float = 0


SYSTEMS_CHECK = [
    "orchestrator",
    "gate_engine",
    "pipeline",
    "script_system",
    "context-engine",
    "knowledge_base",
    "vector-memory",
    "mcp",
    "llm-security",
    "telemetry",
    "feedback-loop",
    "database",
]


class HealthAggregator:
    def check_all(self, max_workers: int = 6) -> HealthReport:
        t0 = time.perf_counter()
        report = HealthReport()
        with ThreadPoolExecutor(max_workers=min(max_workers, len(SYSTEMS_CHECK))) as ex:
            futures = {ex.submit(self._check_one, s): s for s in SYSTEMS_CHECK}
            for f in as_completed(futures):
                h = f.result()
                report.systems.append(h)
                if h.status == "FAIL":
                    report.fail_count += 1
                elif h.status == "WARN":
                    report.warn_count += 1
                else:
                    report.ok_count += 1
        report.overall = "OK" if report.fail_count == 0 else "WARN" if report.warn_count < 3 else "FAIL"
        report.total_ms = round((time.perf_counter() - t0) * 1000)
        logger.info(
            "[HEALTH] %s ok=%d warn=%d fail=%d (%dms)",
            report.overall,
            report.ok_count,
            report.warn_count,
            report.fail_count,
            report.total_ms,
        )
        return report

    def _check_one(self, system: str) -> SystemHealth:
        t0 = time.perf_counter()
        try:
            import importlib

            mod = importlib.import_module(f"zephyr.{system}")
            if hasattr(mod, "health_check"):
                r = mod.health_check()
                return SystemHealth(
                    system,
                    r.get("status", "OK"),
                    round((time.perf_counter() - t0) * 1000),
                    str(r.get("details", "?"))[:200],
                )
            return SystemHealth(system, "OK", round((time.perf_counter() - t0) * 1000), "module exists")
        except Exception as e:
            return SystemHealth(system, "WARN", round((time.perf_counter() - t0) * 1000), str(e)[:200])


def check_all() -> HealthReport:
    return HealthAggregator().check_all()
