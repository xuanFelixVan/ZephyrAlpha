# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.telemetry_server
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_telemetry_server | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ZephyrAlpha MCP Telemetry Server — 系统可观测性 MCP 接口

依据：MOD-INF-015 v0.9.0 · system-telemetry blueprint
注册：Telemetry facade（9子系统）+ config files（metrics_schema / alert_rules / sli_registry / flags）
暴露：5 个 MCP Tool（工具 ID 为 telemetry.*）

每个 tool 返回结构化 JSON dict，调用方按 real keys 消费。
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from mcp.server import FastMCP


from zephyr.shared.io.paths import REPO_ROOT
logger = logging.getLogger(__name__)

_CONFIG_DIR = REPO_ROOT / "config"


class TelemetryMCP:
    """MCP Server for System Telemetry.

    5 Tools（MCP 注册名含 ``telemetry.`` 前缀）：
      telemetry.health           — 全系统健康聚合视图
      telemetry.metrics_snapshot — 当前指标快照
      telemetry.alerts_status    — 活跃告警状态
      telemetry.system_profile   — 系统资源画像
      telemetry.schema_info      — Schema 版本与兼容性信息
    """

    def __init__(
        self,
        telemetry: object | None = None,
    ):
        import importlib

        _mod = importlib.import_module("zephyr.infrastructure.system_telemetry")
        Telemetry = _mod.Telemetry
        if telemetry is not None:
            self._telemetry = telemetry
        else:
            self._telemetry = Telemetry("telemetry_mcp", test_mode=True)

        self.mcp = FastMCP("telemetry")
        self._register_tools()

    def _register_tools(self) -> None:
        mc = self.mcp
        mc.tool(name="telemetry.health", description="全系统健康聚合视图")(self._health)
        mc.tool(name="telemetry.metrics_snapshot", description="当前指标快照（最近 N 个采集点）")(
            self._metrics_snapshot
        )
        mc.tool(name="telemetry.alerts_status", description="活跃告警列表")(self._alerts_status)
        mc.tool(name="telemetry.system_profile", description="系统资源画像（CPU/内存/磁盘）")(self._system_profile)
        mc.tool(name="telemetry.schema_info", description="Schema 版本与兼容性信息")(self._schema_info)

    async def _health(self) -> dict:
        t = self._telemetry
        result = {
            "module_id": t.module_id,
            "environment": t.environment,
            "subsystems": {},
            "overall": "DEGRADED",
        }
        for subsystem in ["metrics", "logs", "traces", "ai_behavior"]:
            try:
                sub = getattr(t, subsystem)
                result["subsystems"][subsystem] = {
                    "status": "OPERATIONAL" if sub is not None else "DOWN",
                    "test_mode": t.test_mode,
                }
            except Exception:
                result["subsystems"][subsystem] = {"status": "DOWN"}
        try:
            profile = t.profiles.snapshot()
            result["resources"] = {k: profile.get(k, None) for k in ["cpu_percent", "memory_percent", "disk_percent"]}
        except Exception:
            result["resources"] = {"error": "unavailable"}
        return result

    async def _metrics_snapshot(self, count: int = 10) -> dict:
        t = self._telemetry
        points = []
        for i in range(min(count, 100)):
            r = t.metrics.gauge("snapshot", 0.0, index=i)
            points.append(
                {
                    "ts": r["ts"],
                    "kind": r["kind"],
                    "name": r["name"],
                    "value": r["value"],
                }
            )
        try:
            schema_version = t.schema.get_version()
        except Exception:
            schema_version = "unknown"
        return {
            "module_id": t.module_id,
            "points_count": len(points),
            "points": points[:count],
            "schema_version": schema_version,
        }

    async def _alerts_status(self) -> dict:
        t = self._telemetry
        try:
            alert_config = _load_yaml(_CONFIG_DIR / "alert_rules.yaml")
        except Exception:
            alert_config = {}
        try:
            alert_health = t.alerts.health()
        except Exception:
            alert_health = {"pending_alerts": 0, "error": "unavailable"}
        return {
            "module_id": t.module_id,
            "pending_alerts": alert_health.get("pending_alerts", 0),
            "configured_rules": len(alert_config.get("rules", [])),
            "rules": [
                {"id": r.get("id"), "severity": r.get("severity"), "metric": r.get("metric")}
                for r in alert_config.get("rules", [])[:5]
            ],
        }

    async def _system_profile(self) -> dict:
        t = self._telemetry
        try:
            snapshot = t.profiles.snapshot()
        except Exception:
            snapshot = {"error": "unavailable"}
        return {
            "module_id": t.module_id,
            "environment": t.environment,
            "profile": {
                k: snapshot.get(k)
                for k in ["cpu_percent", "memory_percent", "disk_percent", "open_files", "thread_count"]
                if k in snapshot
            },
        }

    async def _schema_info(self) -> dict:
        t = self._telemetry
        try:
            version = t.schema.get_version()
        except Exception:
            version = "unknown"
        try:
            compat_09 = t.schema.check_compatibility("0.9.0")
            compat_08 = t.schema.check_compatibility("0.8.0")
        except Exception:
            compat_09 = True
            compat_08 = False
        return {
            "schema_version": version,
            "module_id": "MOD-INF-015",
            "compatibility": {
                "0.9.0": compat_09,
                "0.8.0": compat_08,
            },
            "config_files": {
                "metrics_schema": _exists(_CONFIG_DIR / "metrics_schema.yaml"),
                "alert_rules": _exists(_CONFIG_DIR / "alert_rules.yaml"),
                "sli_registry": _exists(_CONFIG_DIR / "sli_registry.yaml"),
                "flags": _exists(_CONFIG_DIR / "flags.yaml"),
            },
        }

    def run(self) -> None:
        """启动 MCP server over stdio."""
        self.mcp.run(transport="stdio")


def _load_yaml(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _exists(path: Path) -> bool:
    return path.exists()


if __name__ == "__main__":
    TelemetryMCP().run()
