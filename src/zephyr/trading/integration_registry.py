# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.integration_registry
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_integration_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
IntegrationRegistry — 集成注册表
==================================
蓝图: ARC-0001 §6.1
全系统集成点清单。
"""

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG


class IntegrationPoint(BaseModel):
    model_config = BASE_CONFIG
    point_id: str
    source_system: str = "AutoRuntimeCore"
    target_system: str
    interface: str
    protocol: str = "python_import"
    sla: str = "best_effort"
    status: str = "DISCONNECTED"


class ValidationReport(BaseModel):
    model_config = BASE_CONFIG
    total: int = 0
    connected: int = 0
    degraded: int = 0
    disconnected: int = 0
    details: list[dict[str, str]] = Field(default_factory=list)


class IntegrationRegistry:
    """集成注册表——AutoRuntime Core 与所有现有系统的连接点清单。"""

    def __init__(self) -> None:
        self._points: dict[str, IntegrationPoint] = {}

    def register(self, point: IntegrationPoint) -> None:
        self._points[point.point_id] = point

    def validate_all(self) -> ValidationReport:
        report = ValidationReport(total=len(self._points))
        for point in self._points.values():
            try:
                parts = point.interface.split(":")
                mod_path = parts[0]
                __import__(mod_path)
                point.status = "CONNECTED"
                report.connected += 1
            except ImportError:
                point.status = "DISCONNECTED"
                report.disconnected += 1
                report.details.append({"point_id": point.point_id, "error": f"cannot import {point.interface}"})
            except Exception as e:
                point.status = "DEGRADED"
                report.degraded += 1
                report.details.append({"point_id": point.point_id, "error": str(e)})
        return report

    def status_all(self) -> dict[str, str]:
        return {pid: p.status for pid, p in self._points.items()}

    def list_points(self) -> list[IntegrationPoint]:
        return list(self._points.values())
