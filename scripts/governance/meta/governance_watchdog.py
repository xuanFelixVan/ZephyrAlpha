#!/usr/bin/env python3
# ARCH-041: BLUEPRINT 必须匹配 generate_project_depgraph.py L2755 正则 ^(MOD-|D-|SH-|SYS-|PLACEHOLDER)
# GOV-075 不匹配正则会导致文件成为孤儿（不注册到 DB）。MOD-INF-005 与同域其他文件一致。
# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/governance_watchdog.py | §3.9
# [MODULE] scripts.governance.meta.governance_watchdog
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS] run_all.py;LifecycleManager
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 服务不可用时必须尝试重启;重启次数超限必须通知Owner
# [MODIFY-GUARD] 重启策略变更需同步escalation_engine
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ServiceUnrecoverableError
# [TESTS] tests/test_governance_watchdog.py
# [TTL] permanent
# noqa: m02-manual  M02豁免: 治理watchdog常驻服务(python scripts/governance/meta/governance_watchdog.py),CLI触发启动,启动后自动运行;非reconciler无需事件触发

from __future__ import annotations


__manifest__ = """
args: []
description: ⚠ 请补充 description
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import json
import os
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from _shared.constants import REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.thresholds import get as _get_threshold  # noqa: E402  治本(ARCH-036 P1-A2): 连续失败阈值读SSoT

PROJECT_ROOT = REPO_ROOT
# ARCH-036: 连续失败→Quarantine 阈值从 SSoT (thresholds.yaml) 读取，消除硬编码 2 与权威值 3 的分歧
_QUARANTINE_FAILURES_THRESHOLD = _get_threshold("script_health.consecutive_failures_before_quarantine", 3)


class ServiceUnrecoverableError(Exception):
    def __init__(self, service_name: str, restart_count: int, max_restart: int):
        self.service_name = service_name
        self.restart_count = restart_count
        self.max_restart = max_restart
        super().__init__(f"Service '{service_name}' unrecoverable: {restart_count}/{max_restart} restarts exhausted")


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RESTARTING = "restarting"
    EXHAUSTED = "exhausted"


@dataclass
class ServiceRecord:
    name: str
    health_check_fn: Callable[[], bool] = field(default_factory=lambda: lambda: True)
    restart_fn: Callable[[], bool] = field(default_factory=lambda: lambda: False)
    status: ServiceStatus = ServiceStatus.HEALTHY
    restart_count: int = 0
    last_check: datetime | None = None
    last_restart: datetime | None = None
    consecutive_failures: int = 0


class GovernanceWatchdog:
    def __init__(
        self,
        check_interval: int = 30,
        max_restart: int = 3,
        restart_delay: int = 10,
    ):
        self._check_interval = check_interval
        self._max_restart = max_restart
        self._restart_delay = restart_delay
        self._services: dict[str, ServiceRecord] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._watchdog_thread: threading.Thread | None = None
        self._on_exhausted: Callable[[str], None] | None = None
        self._state_path = str(PROJECT_ROOT / "data" / "governance" / "watchdog_state.json")

    def register_service(
        self,
        name: str,
        health_check_fn: Callable[[], bool],
        restart_fn: Callable[[], bool],
    ) -> None:
        with self._lock:
            self._services[name] = ServiceRecord(
                name=name,
                health_check_fn=health_check_fn,
                restart_fn=restart_fn,
            )

    def check_all(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        with self._lock:
            service_names = list(self._services.keys())
        for name in service_names:
            with self._lock:
                svc = self._services.get(name)
                if svc is None:
                    continue
            try:
                is_healthy = svc.health_check_fn()
            except Exception:
                is_healthy = False
            with self._lock:
                svc.last_check = datetime.now(UTC)
                if is_healthy:
                    svc.status = ServiceStatus.HEALTHY
                    svc.consecutive_failures = 0
                else:
                    svc.consecutive_failures += 1
                    if svc.consecutive_failures >= _QUARANTINE_FAILURES_THRESHOLD:
                        svc.status = ServiceStatus.FAILED
                    else:
                        svc.status = ServiceStatus.DEGRADED
            results[name] = {
                "status": svc.status.value,
                "consecutive_failures": svc.consecutive_failures,
                "restart_count": svc.restart_count,
                "last_check": svc.last_check.isoformat() if svc.last_check else None,
            }
        return results

    def restart_service(self, name: str) -> bool:
        with self._lock:
            svc = self._services.get(name)
            if svc is None:
                return False
            if svc.restart_count >= self._max_restart:
                svc.status = ServiceStatus.EXHAUSTED
                if self._on_exhausted is not None:
                    try:
                        self._on_exhausted(name)
                    except Exception:
                        pass
                return False
            svc.status = ServiceStatus.RESTARTING
            svc.restart_count += 1
            restart_fn = svc.restart_fn
        time.sleep(self._restart_delay)
        try:
            success = restart_fn()
        except Exception:
            success = False
        with self._lock:
            if success:
                svc.status = ServiceStatus.HEALTHY
                svc.consecutive_failures = 0
            else:
                if svc.restart_count >= self._max_restart:
                    svc.status = ServiceStatus.EXHAUSTED
                    if self._on_exhausted is not None:
                        try:
                            self._on_exhausted(name)
                        except Exception:
                            pass
                else:
                    svc.status = ServiceStatus.FAILED
            svc.last_restart = datetime.now(UTC)
        return success

    def run(self, daemon: bool = True) -> None:
        self._stop_event.clear()
        self._watchdog_thread = threading.Thread(
            target=self._run_loop,
            daemon=daemon,
        )
        self._watchdog_thread.start()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                check_results = self.check_all()
                for name, info in check_results.items():
                    if info["status"] in (ServiceStatus.FAILED.value, ServiceStatus.DEGRADED.value):
                        self.restart_service(name)
                self._save_state()
            except Exception:
                pass
            self._stop_event.wait(timeout=self._check_interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._watchdog_thread is not None:
            self._watchdog_thread.join(timeout=10)
            self._watchdog_thread = None

    def set_on_exhausted(self, callback: Callable[[str], None]) -> None:
        self._on_exhausted = callback

    def _save_state(self) -> None:
        with self._lock:
            state = {}
            for name, svc in self._services.items():
                state[name] = {
                    "status": svc.status.value,
                    "restart_count": svc.restart_count,
                    "consecutive_failures": svc.consecutive_failures,
                    "last_check": svc.last_check.isoformat() if svc.last_check else None,
                    "last_restart": svc.last_restart.isoformat() if svc.last_restart else None,
                }
        os.makedirs(os.path.dirname(self._state_path), exist_ok=True)
        atomic_write_safe(self._state_path, json.dumps(state, indent=2, default=str))


def _run_warn_only() -> dict[str, Any]:
    results: dict[str, Any] = {"checks": []}
    wd = GovernanceWatchdog(check_interval=5, max_restart=3, restart_delay=1)
    wd.register_service(
        name="test_service",
        health_check_fn=lambda: True,
        restart_fn=lambda: True,
    )
    check_result = wd.check_all()
    results["checks"].append(
        {
            "name": "check_all",
            "status": "PASS" if "test_service" in check_result else "WARN",
            "detail": check_result,
        }
    )
    restart_ok = wd.restart_service("test_service")
    results["checks"].append(
        {
            "name": "restart_service",
            "status": "PASS" if restart_ok else "WARN",
            "detail": {"restarted": restart_ok},
        }
    )
    restart_missing = wd.restart_service("nonexistent_service")
    results["checks"].append(
        {
            "name": "restart_nonexistent",
            "status": "PASS" if not restart_missing else "WARN",
            "detail": {"restarted": restart_missing},
        }
    )
    exhausted_triggered = False
    wd.register_service(
        name="failing_service",
        health_check_fn=lambda: False,
        restart_fn=lambda: False,
    )
    for _ in range(4):
        wd.restart_service("failing_service")
    with wd._lock:
        svc = wd._services.get("failing_service")
        if svc and svc.status == ServiceStatus.EXHAUSTED:
            exhausted_triggered = True
    results["checks"].append(
        {
            "name": "exhausted_detection",
            "status": "PASS" if exhausted_triggered else "WARN",
            "detail": {"exhausted_triggered": exhausted_triggered},
        }
    )
    results["overall"] = "PASS" if all(c["status"] == "PASS" for c in results["checks"]) else "WARN"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Governance Watchdog — service health monitoring and auto-recovery")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Run checks in warn-only mode",
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=30,
        help="Health check interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-restart",
        type=int,
        default=3,
        help="Maximum restart attempts per service (default: 3)",
    )
    parser.add_argument(
        "--restart-delay",
        type=int,
        default=10,
        help="Delay before restart in seconds (default: 10)",
    )
    args = parser.parse_args()

    if args.warn_only:
        results = _run_warn_only()
        output_path = str(PROJECT_ROOT / "scripts" / "governance" / "governance_watchdog_warn_result.json")
        atomic_write_safe(output_path, json.dumps(results, indent=2, default=str))
        print(json.dumps(results, indent=2, default=str))
        return 0 if results["overall"] == "PASS" else 1

    wd = GovernanceWatchdog(
        check_interval=args.check_interval,
        max_restart=args.max_restart,
        restart_delay=args.restart_delay,
    )
    print(f"[WATCHDOG] Starting governance watchdog (interval={args.check_interval}s, max_restart={args.max_restart})")
    wd.run(daemon=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
