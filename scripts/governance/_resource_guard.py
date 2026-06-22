#!/usr/bin/env python3
# [BLUEPRINT] GOV-069 | docs/03_modules/_domain-governance/blueprint.md | §3.9
# [MODULE] scripts.governance._resource_guard
# [INVARIANTS] Worker内存不可超过限制;超限必须降级
# [MODIFY-GUARD] 限制值变更需同步resource_guard.py
# [CONSUMERS] run_all.py;_concurrency.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ResourceLimitExceededError
# [TESTS] tests/test_resource_guard.py

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

try:
    import resource as _resource_mod

    _HAS_RESOURCE = True
except ImportError:
    _resource_mod = None
    _HAS_RESOURCE = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ResourceLimitExceededError(Exception):
    def __init__(self, resource_name: str, current: float, limit: float):
        self.resource_name = resource_name
        self.current = current
        self.limit = limit
        super().__init__(f"Resource limit exceeded: {resource_name} current={current:.1f} limit={limit:.1f}")


class DegradationAction(Enum):
    NONE = auto()
    REDUCE_PARALLELISM = auto()
    PAUSE_NON_CRITICAL = auto()
    EMERGENCY_STOP = auto()


@dataclass
class WorkerLimits:
    memory_limit_mb: int = 512
    cpu_limit_seconds: int = 300
    fd_limit: int = 256


@dataclass
class WorkerUsage:
    memory_mb: float = 0.0
    cpu_seconds: float = 0.0
    open_fds: int = 0
    degradation: DegradationAction = DegradationAction.NONE


class WorkerResourceGuard:
    def __init__(
        self,
        memory_limit_mb: int = 512,
        cpu_limit_seconds: int = 300,
        fd_limit: int = 256,
    ):
        self._limits = WorkerLimits(
            memory_limit_mb=memory_limit_mb,
            cpu_limit_seconds=cpu_limit_seconds,
            fd_limit=fd_limit,
        )
        self._usage = WorkerUsage()
        self._lock = threading.Lock()
        self._enforce_stop = threading.Event()
        self._enforce_thread: threading.Thread | None = None
        self._degradation_callback: Any | None = None

    @property
    def limits(self) -> WorkerLimits:
        return self._limits

    def apply_limits(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        if not _HAS_RESOURCE:
            results["rlimit_as"] = "skipped_windows"
            results["rlimit_cpu"] = "skipped_windows"
            results["rlimit_nofile"] = "skipped_windows"
            return results
        try:
            _resource_mod.setrlimit(
                _resource_mod.RLIMIT_AS,
                (self._limits.memory_limit_mb * 1024 * 1024, self._limits.memory_limit_mb * 1024 * 1024),
            )
            results["rlimit_as"] = "set"
        except (ValueError, _resource_mod.error, AttributeError) as exc:
            results["rlimit_as"] = f"failed: {exc}"
        try:
            _resource_mod.setrlimit(
                _resource_mod.RLIMIT_CPU,
                (self._limits.cpu_limit_seconds, self._limits.cpu_limit_seconds),
            )
            results["rlimit_cpu"] = "set"
        except (ValueError, _resource_mod.error, AttributeError) as exc:
            results["rlimit_cpu"] = f"failed: {exc}"
        try:
            _resource_mod.setrlimit(
                _resource_mod.RLIMIT_NOFILE,
                (self._limits.fd_limit, self._limits.fd_limit),
            )
            results["rlimit_nofile"] = "set"
        except (ValueError, _resource_mod.error, AttributeError) as exc:
            results["rlimit_nofile"] = f"failed: {exc}"
        return results

    def wrap_subprocess(self, cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
        preexec_fn = self._build_preexec_fn()
        kwargs.setdefault("timeout", self._limits.cpu_limit_seconds + 30)
        kwargs.setdefault("capture_output", True)
        kwargs.setdefault("text", True)
        if preexec_fn is not None and sys.platform != "win32":
            kwargs["preexec_fn"] = preexec_fn
        result = subprocess.run(cmd, **kwargs)
        return result

    def _build_preexec_fn(self):
        if not _HAS_RESOURCE:
            return None

        def _preexec():
            try:
                _resource_mod.setrlimit(
                    _resource_mod.RLIMIT_AS,
                    (self._limits.memory_limit_mb * 1024 * 1024, self._limits.memory_limit_mb * 1024 * 1024),
                )
            except (ValueError, _resource_mod.error, AttributeError):
                pass
            try:
                _resource_mod.setrlimit(
                    _resource_mod.RLIMIT_CPU,
                    (self._limits.cpu_limit_seconds, self._limits.cpu_limit_seconds),
                )
            except (ValueError, _resource_mod.error, AttributeError):
                pass
            try:
                _resource_mod.setrlimit(
                    _resource_mod.RLIMIT_NOFILE,
                    (self._limits.fd_limit, self._limits.fd_limit),
                )
            except (ValueError, _resource_mod.error, AttributeError):
                pass

        return _preexec

    def check_usage(self) -> dict[str, Any]:
        usage = self._collect_usage()
        with self._lock:
            self._usage = usage
        return {
            "memory_mb": usage.memory_mb,
            "cpu_seconds": usage.cpu_seconds,
            "open_fds": usage.open_fds,
            "degradation": usage.degradation.name,
            "limits": {
                "memory_limit_mb": self._limits.memory_limit_mb,
                "cpu_limit_seconds": self._limits.cpu_limit_seconds,
                "fd_limit": self._limits.fd_limit,
            },
            "memory_pct": (
                usage.memory_mb / self._limits.memory_limit_mb * 100 if self._limits.memory_limit_mb > 0 else 0
            ),
        }

    def _collect_usage(self) -> WorkerUsage:
        mem_mb = 0.0
        cpu_s = 0.0
        open_fds = 0
        try:
            import psutil

            proc = psutil.Process(os.getpid())
            mem_info = proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            cpu_times = proc.cpu_times()
            cpu_s = cpu_times.user + cpu_times.system
            try:
                open_fds = proc.num_fds() if sys.platform != "win32" else len(proc.open_files())
            except (psutil.AccessDenied, OSError):
                open_fds = 0
        except ImportError:
            if _HAS_RESOURCE:
                try:
                    usage = _resource_mod.getrusage(_resource_mod.RUSAGE_SELF)
                    mem_mb = usage.ru_maxrss / 1024.0
                    cpu_s = usage.ru_utime + usage.ru_stime
                except Exception:
                    pass

        degradation = DegradationAction.NONE
        mem_ratio = mem_mb / self._limits.memory_limit_mb if self._limits.memory_limit_mb > 0 else 0
        if mem_ratio >= 0.976:
            degradation = DegradationAction.EMERGENCY_STOP
        elif mem_ratio >= 0.875:
            degradation = DegradationAction.PAUSE_NON_CRITICAL
        elif mem_ratio >= 0.75:
            degradation = DegradationAction.REDUCE_PARALLELISM

        return WorkerUsage(
            memory_mb=mem_mb,
            cpu_seconds=cpu_s,
            open_fds=open_fds,
            degradation=degradation,
        )

    def enforce(self, check_interval: int = 30) -> None:
        self._enforce_stop.clear()
        self._enforce_thread = threading.Thread(
            target=self._enforce_loop,
            args=(check_interval,),
            daemon=True,
        )
        self._enforce_thread.start()

    def _enforce_loop(self, check_interval: int) -> None:
        while not self._enforce_stop.is_set():
            usage = self._collect_usage()
            with self._lock:
                self._usage = usage
            if usage.degradation != DegradationAction.NONE:
                if self._degradation_callback is not None:
                    try:
                        self._degradation_callback(usage.degradation)
                    except Exception:
                        pass
                if usage.degradation == DegradationAction.EMERGENCY_STOP:
                    if mem_mb > self._limits.memory_limit_mb:
                        raise ResourceLimitExceededError("memory", usage.memory_mb, self._limits.memory_limit_mb)
            self._enforce_stop.wait(timeout=check_interval)

    def stop_enforce(self) -> None:
        self._enforce_stop.set()
        if self._enforce_thread is not None:
            self._enforce_thread.join(timeout=5)
            self._enforce_thread = None

    def set_degradation_callback(self, callback: Any) -> None:
        self._degradation_callback = callback


def _run_warn_only() -> dict[str, Any]:
    guard = WorkerResourceGuard(memory_limit_mb=512, cpu_limit_seconds=300, fd_limit=256)
    results: dict[str, Any] = {"checks": []}
    apply_result = guard.apply_limits()
    apply_ok = all(v in ("set", "skipped_windows") for v in apply_result.values())
    results["checks"].append(
        {
            "name": "apply_limits",
            "status": "PASS" if apply_ok else "WARN",
            "detail": apply_result,
        }
    )
    usage = guard.check_usage()
    mem_pct = usage["memory_pct"]
    results["checks"].append(
        {
            "name": "check_usage",
            "status": "PASS" if mem_pct < 90 else "WARN",
            "detail": usage,
        }
    )
    wrap_result = "PASS"
    try:
        completed = guard.wrap_subprocess(
            [sys.executable, "-c", "print('worker_ok')"],
            timeout=10,
        )
        if completed.returncode != 0:
            wrap_result = "WARN"
    except Exception as exc:
        wrap_result = f"WARN: {exc}"
    results["checks"].append(
        {
            "name": "wrap_subprocess",
            "status": wrap_result,
        }
    )
    results["overall"] = "PASS" if all(c["status"] == "PASS" for c in results["checks"]) else "WARN"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker Resource Guard — subprocess worker RLIMIT management")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Run checks in warn-only mode (no enforcement)",
    )
    parser.add_argument(
        "--memory-limit",
        type=int,
        default=512,
        help="Memory limit in MB (default: 512)",
    )
    parser.add_argument(
        "--cpu-limit",
        type=int,
        default=300,
        help="CPU limit in seconds (default: 300)",
    )
    parser.add_argument(
        "--fd-limit",
        type=int,
        default=256,
        help="File descriptor limit (default: 256)",
    )
    args = parser.parse_args()

    if args.warn_only:
        results = _run_warn_only()
        output_path = str(PROJECT_ROOT / "scripts" / "governance" / "_resource_guard_warn_result.json")
        tmp_path = f"{output_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)
            os.replace(tmp_path, output_path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        print(json.dumps(results, indent=2, default=str))
        return 0 if results["overall"] == "PASS" else 1

    guard = WorkerResourceGuard(
        memory_limit_mb=args.memory_limit,
        cpu_limit_seconds=args.cpu_limit,
        fd_limit=args.fd_limit,
    )
    apply_result = guard.apply_limits()
    print(f"[RESOURCE_GUARD] Limits applied: {apply_result}")
    usage = guard.check_usage()
    print(f"[RESOURCE_GUARD] Current usage: {usage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
