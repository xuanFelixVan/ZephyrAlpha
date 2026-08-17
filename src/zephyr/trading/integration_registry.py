# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.integration_registry
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
IntegrationRegistry — 集成注册表
==================================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
全系统集成点清单。
"""

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def points(self) -> dict[str, IntegrationPoint]:
        """只读：points（Stage 4 公共化）。"""
        return self._points

    @points.setter
    def points(self, value):
        """写入：points（Stage 4 公共化）。"""
        self._points = value

    def register(self, point: IntegrationPoint) -> None:
        self._points[point.point_id] = point

    def validate_all(self) -> ValidationReport:
        """运行时探测所有集成点（5.71.2 治本：非仅 import——import + 属性解析 + None 检查）。

        判定：
          - 模块 import 失败 -> DISCONNECTED
          - interface 含 "module:attr" 时 attr 不可解析 / 解析为 None -> DEGRADED
          - 全部通过 -> CONNECTED
        """
        import importlib

        report = ValidationReport(total=len(self._points))
        for point in self._points.values():
            try:
                parts = point.interface.split(":")
                mod_path = parts[0]
                attr_path = parts[1] if len(parts) > 1 else ""
                module = importlib.import_module(mod_path)
                if attr_path:
                    target: object = module
                    for attr in attr_path.split("."):
                        target = getattr(target, attr)
                    if target is None:
                        point.status = "DEGRADED"
                        report.degraded += 1
                        report.details.append(
                            {"point_id": point.point_id, "error": f"{point.interface} resolved to None"}
                        )
                        continue
                point.status = "CONNECTED"
                report.connected += 1
            except ImportError:
                point.status = "DISCONNECTED"
                report.disconnected += 1
                report.details.append({"point_id": point.point_id, "error": f"cannot import {point.interface}"})
            except AttributeError as e:
                point.status = "DEGRADED"
                report.degraded += 1
                report.details.append({"point_id": point.point_id, "error": f"attr unresolved: {e}"})
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                point.status = "DEGRADED"
                report.degraded += 1
                report.details.append({"point_id": point.point_id, "error": "internal error"})
        return report

    def status_all(self) -> dict[str, str]:
        return {pid: p.status for pid, p in self._points.items()}

    def list_points(self) -> list[IntegrationPoint]:
        return list(self._points.values())
