# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.infrastructure.health_monitor.health_aggregator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.health_probes
# [CONSUMERS] AutoRuntime Core health check phase
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 11系统健康检查并行执行（SYSTEMS_CHECK 实数11，knowledge_base 随 KB 退役移除）; 任一FAIL->整体WARN; 全部OK->OK; 任一项超时->SKIP
# [MODIFY-GUARD] 新增系统必须同步添加check_函数
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/health_check.py --trigger
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
全系统健康聚合 — check_all_systems()

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: health_aggregator.py
# 层: 算法
# - id: A1
#   name_zh: ① HealthAggregator
#   name_en: HealthAggregator
#   intro: class HealthAggregator 源码 L99-L142
#   desc: 公共方法（定义序）: check_all；源码 L99-L142
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② check_all
#   name_en: check_all
#   intro: check_all() 源码 L145-L146
#   desc: 源码 L145-L146
#   inputs: 无参数
#   outputs: HealthReport
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: HealthReport
#   name_en: HealthReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: AutoRuntime Core health check phase
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

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
    "vector-memory",
    "mcp",
    "llm-security",
    "telemetry",
    "feedback-loop",
    "database",
]


# class-name-alias: health_monitor 健康聚合器（check_all 并行检查），区别于 system_telemetry/health_aggregator.py 的三态探针快照
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            return SystemHealth(system, "WARN", round((time.perf_counter() - t0) * 1000), str(e)[:200])


def check_all() -> HealthReport:
    return HealthAggregator().check_all()
