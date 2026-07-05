# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.governance.audit_trail.self_monitor
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.audit_trail.drift_bridge
# [CONSUMERS] audit-orchestrator.cli; MCP governance_server
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 自监控不引入外部依赖; 指标采集不阻塞主流程
# [MODIFY-GUARD] 指标名称变更必须同步 CLI + MCP
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 监控失败返回空指标
# [TESTS] tests/audit-orchestrator/test_self_monitor.py
# [A_module] module_id=MOD-GOV_self_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["SelfMonitor"]


class SelfMonitor:
    def __init__(self) -> None:
        self._start_time = time.monotonic()
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._drift_bridge = None
        try:
            from zephyr.governance.audit_trail.drift_bridge import DriftBridge

            self._drift_bridge = DriftBridge()
        except Exception:
            pass

    def increment(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def snapshot(self) -> dict[str, Any]:
        uptime = time.monotonic() - self._start_time
        drift_result = {"is_drifting": False, "drift_score": 0.0}
        if self._drift_bridge and self._drift_bridge.is_available():
            drift_result = self._drift_bridge.check_drift(
                {
                    "uptime": uptime,
                    "counter_total": sum(self._counters.values()),
                    "gauge_avg": sum(self._gauges.values()) / max(1, len(self._gauges)),
                }
            )

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "drift": drift_result,
        }
