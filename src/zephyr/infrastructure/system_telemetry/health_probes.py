# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.health_probes
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.__init__
# [CONSUMERS] zephyr.security.access_control
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 12-system triple-state probes; liveness/readiness/degraded contract; ProbeStatus enum stability
# [MODIFY-GUARD] health_aggregator.py; watchdog.py; health.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError; RuntimeError
# [TESTS] tests/system-telemetry/test_health_probes.py
# [A_module] module_id=MOD-INF_health_probes | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
三态健康探针协议（Health Probes — CT-HEALTH-001）

依据：MOD-MASTER-002 蓝图 §十四 标准化 HealthCheck
实现 12 系统 liveness/readiness/degraded 三态探针。
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ProbeStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class LivenessProbe(BaseModel):
    status: str = "alive"
    pid: int = 0
    uptime_s: float = 0.0


class ReadinessProbe(BaseModel):
    status: str = "ready"
    dependencies: dict[str, str] = Field(default_factory=dict)


class HealthzProbe(BaseModel):
    status: ProbeStatus = ProbeStatus.HEALTHY
    degraded_details: str = ""


SYSTEMS: tuple[str, ...] = (
    "orchestrator",
    "script_system",
    "knowledge_base",
    "context-engine",
    "gate_engine",
    "pipeline",
    "feedback-loop",
    "vector-memory",
    "database",
    "llm-security",
    "system-telemetry",
    "mcp_servers",
)

SPECIAL_RULES: dict[str, dict] = {
    "orchestrator": {"degraded_when": "pending_queue > 100"},
    "context-engine": {"degraded_when": "token_budget > 7200"},
    "llm-security": {"no_degraded": True},
    "database": {"degraded_when": "wal_checkpoint_lag > 5s"},
}


class HealthProbeManager:
    def __init__(self, dependency_checker: Callable[[], bool] | None = None):
        self._start_time = time.monotonic()
        self._states: dict[str, dict[str, Any]] = {}
        # 5.55.1 修复：探针内部自行检查依赖，不接受外部传入的 deps_ok=True
        # 可注入 dependency_checker 回调；未注入时回退到数据目录可达性检查
        self._dependency_checker = dependency_checker

    def liveness(self, system: str) -> dict:
        return {
            "status": "alive",
            "pid": os.getpid(),  # 5.55.5 修复：原硬编码 pid=0，无法用于进程存活判定
            "uptime_s": round(time.monotonic() - self._start_time, 2),
            "system": system,
        }

    def _check_dependencies(self) -> bool:
        """5.55.1 修复：探针内部真实检查依赖状态，而非信任外部传入的 deps_ok。

        检查优先级：
          1. 注入的 dependency_checker 回调（若提供）
          2. 数据目录可达性回退检查（项目根/.runtime 或临时目录可写性）
        """
        # 优先使用注入的检查器
        if self._dependency_checker is not None:
            try:
                return bool(self._dependency_checker())
            except Exception:
                return False
        # 回退：数据目录可达性检查
        # 5.55.1：尝试项目根的 .runtime 目录（SSoT: REPO_ROOT），失败则回退到临时目录
        try:
            from zephyr.shared.io.paths import REPO_ROOT  # 延迟导入避免循环

            data_dir = Path(REPO_ROOT) / ".runtime"
            if data_dir.exists():
                # 探针写入探测文件以确认可写
                probe = data_dir / f".probe_{os.getpid()}.tmp"
                probe.write_text("ok", encoding="utf-8")
                probe.unlink(missing_ok=True)
                return True
        except Exception:
            pass
        # 5.55.7 修复：无注入检查器且 .runtime/ 不可达时 fail-closed（返回 False）
        # 原第三层 temp dir fallback 总返回 True，导致 readiness() 永远 "ready"，
        # 违反 fail-closed 原则。temp dir 可写不代表数据目录可达。
        return False

    def readiness(self, system: str, deps_ok: bool | None = None) -> dict:
        """5.55.1 修复：deps_ok 默认 None 时探针内部自行检查依赖。

        - deps_ok=None（默认）：探针内部调用 _check_dependencies() 真实检查
        - deps_ok=True/False：保留显式传入能力（向后兼容），但默认不再信任外部传入
        """
        if deps_ok is None:
            deps_ok = self._check_dependencies()
        return {
            "status": "ready" if deps_ok else "not_ready",
            "dependencies": {"db": "ok" if deps_ok else "down"},
            "system": system,
        }

    def healthz(self, system: str, metrics: dict[str, Any] | None = None) -> dict:
        rules = SPECIAL_RULES.get(system, {})
        degraded = False
        reason = ""

        if metrics:
            if system == "orchestrator" and metrics.get("pending_queue", 0) > 100:
                degraded = True
                reason = "pending_queue > 100"
            elif system == "context-engine" and metrics.get("token_budget", 0) > 7200:
                degraded = True
                reason = "token_budget > 7200"
            elif system == "database" and metrics.get("wal_checkpoint_lag", 0) > 5.0:
                degraded = True
                reason = "wal_checkpoint_lag > 5s"

        if rules.get("no_degraded") and degraded:
            degraded = False
            reason = ""

        return {
            "status": "degraded" if degraded else "healthy",
            "system": system,
            "degraded_details": reason,
        }

    def list_systems(self) -> list[str]:
        return list(SYSTEMS)
