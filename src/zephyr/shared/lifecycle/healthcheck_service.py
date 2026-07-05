# [BLUEPRINT] SRC-099 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.lifecycle.healthcheck_service
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_healthcheck_service | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Healthcheck Service — 运行时健康检查服务。

依据：
    蓝图 MOD-TASK_SYSTEM §6.4.1 + v0.6.0
    任务卡 TASK-INF-0111 (Part 1/2)
"""

import os
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class HealthStatus:
    component: str
    healthy: bool
    latency_ms: float
    message: str
    last_checked: str


@dataclass
class HealthReport:
    timestamp_utc: str
    overall_healthy: bool
    components: list[HealthStatus]
    uptime_seconds: float
    version: str = "0.6.0"


class HealthcheckService:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._start_time = time.time()

    def check_all(self) -> HealthReport:
        components: list[HealthStatus] = []

        components.append(self._check_git())
        components.append(self._check_python())
        components.append(self._check_disk())
        components.append(self._check_network())
        components.append(self._check_file_system())

        overall = all(c.healthy for c in components)

        return HealthReport(
            timestamp_utc=datetime.now(UTC).isoformat(),
            overall_healthy=overall,
            components=components,
            uptime_seconds=time.time() - self._start_time,
        )

    def check_git(self) -> HealthStatus:
        return self._check_git()

    def check_dependencies(self) -> HealthStatus:
        t0 = time.time()
        try:
            import zephyr.shared.blueprint_tools.blueprint_decomposer
            import zephyr.shared.foundation.models

            return HealthStatus(
                component="dependencies",
                healthy=True,
                latency_ms=(time.time() - t0) * 1000,
                message="All core modules importable",
                last_checked=datetime.now(UTC).isoformat(),
            )
        except ImportError as e:
            return HealthStatus(
                component="dependencies",
                healthy=False,
                latency_ms=(time.time() - t0) * 1000,
                message=f"Import failed: {e}",
                last_checked=datetime.now(UTC).isoformat(),
            )

    def _check_git(self) -> HealthStatus:
        t0 = time.time()
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return HealthStatus(
                component="git",
                healthy=result.returncode == 0,
                latency_ms=(time.time() - t0) * 1000,
                message="Git operational" if result.returncode == 0 else f"Git error: {result.stderr[:100]}",
                last_checked=datetime.now(UTC).isoformat(),
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return HealthStatus(
                component="git",
                healthy=False,
                latency_ms=(time.time() - t0) * 1000,
                message=str(e),
                last_checked=datetime.now(UTC).isoformat(),
            )

    def _check_python(self) -> HealthStatus:
        t0 = time.time()
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return HealthStatus(
                component="python",
                healthy=result.returncode == 0,
                latency_ms=(time.time() - t0) * 1000,
                message=result.stdout.strip(),
                last_checked=datetime.now(UTC).isoformat(),
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return HealthStatus(
                component="python",
                healthy=False,
                latency_ms=(time.time() - t0) * 1000,
                message="Python not found",
                last_checked=datetime.now(UTC).isoformat(),
            )

    def _check_disk(self) -> HealthStatus:
        t0 = time.time()
        try:
            usage = os.path.getsize(str(self._project_root))
            return HealthStatus(
                component="disk",
                healthy=True,
                latency_ms=(time.time() - t0) * 1000,
                message=f"Project accessible ({usage} bytes)",
                last_checked=datetime.now(UTC).isoformat(),
            )
        except OSError as e:
            return HealthStatus(
                component="disk",
                healthy=False,
                latency_ms=(time.time() - t0) * 1000,
                message=str(e),
                last_checked=datetime.now(UTC).isoformat(),
            )

    def _check_network(self) -> HealthStatus:
        return HealthStatus(
            component="network",
            healthy=True,
            latency_ms=0,
            message="Local-only mode — skip network check",
            last_checked=datetime.now(UTC).isoformat(),
        )

    def _check_file_system(self) -> HealthStatus:
        t0 = time.time()
        required = [
            "src/zephyr/core/models.py",
            "src/zephyr/core/blueprint_decomposer.py",
            "src/zephyr/core/context-engine.py",
        ]

        missing: list[str] = []
        for path in required:
            if not (self._project_root / path).exists():
                missing.append(path)

        return HealthStatus(
            component="filesystem",
            healthy=len(missing) == 0,
            latency_ms=(time.time() - t0) * 1000,
            message="All required files present" if not missing else f"Missing: {missing}",
            last_checked=datetime.now(UTC).isoformat(),
        )
