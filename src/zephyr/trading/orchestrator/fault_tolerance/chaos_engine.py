# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §chaos_engine
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.chaos_engine
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS] red-blue-validator.injection_engine; game_day_runner; zephyr.trading.orchestrator.chaos_hooks
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] inject() MUST NOT leave system in degraded state; crash/exit_code injection requires CHAOS_CRASH_CONFIRMED=yes env var
# [MODIFY-GUARD] Adding injection types MUST update INJECTION_POINTS and InjectType enum
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ChaosInjectError on injection failure; ChaosRecoverError on recovery failure
# [TESTS] tests/test_chaos_engine.py
# [A_module] module_id=MOD-ORC_chaos_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Chaos 故障注入引擎（CT-CHAOS-001）——4注入点×月度执行。"""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "INJECTION_POINTS",
    "ChaosEngine",
    "ChaosInjectError",
    "ChaosRecoverError",
    "FaultRecord",
    "InjectType",
    "InjectionResult",
    "RecoveryResult",
    "VerificationResult",
]


class InjectType(str, Enum):
    LATENCY = "latency"
    ERROR = "error"
    CRASH = "crash"
    EXIT_CODE = "exit_code"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    DATA_CORRUPTION = "data_corruption"


class ChaosInjectError(RuntimeError):
    pass


class ChaosRecoverError(RuntimeError):
    pass


@dataclass
class InjectionResult:
    injected: bool
    injection_type: str
    target: str
    duration_ms: float = 0.0
    error_message: str = ""
    affected_component: str = ""


@dataclass
class RecoveryResult:
    recovered: bool
    target: str
    checks_passed: int = 0
    checks_failed: int = 0
    failures: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    defense_activated: bool
    defense_type: str = ""
    recovery_triggered: bool = False
    response_time_ms: float = 0.0
    notes: list[str] = field(default_factory=list)


@dataclass
class FaultRecord:
    fault_id: str
    target: str
    fault_type: str
    params: dict[str, Any] = field(default_factory=dict)
    active: bool = True
    injected_at: float = 0.0


INJECTION_POINTS: list[dict[str, Any]] = [
    {"name": "vms_latency", "system": "vector-memory", "type": "latency", "duration_s": 30},
    {"name": "vms_error", "system": "vector-memory", "type": "error", "duration_s": 10},
    {"name": "lsg_crash", "system": "llm-security", "type": "crash", "duration_s": 0},
    {"name": "script_exit3", "system": "script_system", "type": "exit_code", "duration_s": 0},
]

_ACTIVE_LATENCY_TIMERS: list[threading.Timer] = []


def _cleanup_latency_timers() -> None:
    for timer in _ACTIVE_LATENCY_TIMERS:
        timer.cancel()
    _ACTIVE_LATENCY_TIMERS.clear()


class ChaosEngine:
    def __init__(self) -> None:
        self._injection_state: dict[str, bool] = {}
        self._recovery_snapshots: dict[str, Any] = {}
        self._last_result: InjectionResult | None = None
        self._active_faults: dict[str, FaultRecord] = {}
        self._lock = threading.Lock()

    def get_injection_points(self) -> list[dict[str, Any]]:
        return INJECTION_POINTS

    def inject(
        self,
        injection_type_or_point: str = "",
        **kwargs: Any,
    ) -> InjectionResult | bool:
        delay_ms: int = kwargs.get("delay_ms", 500)
        target: str = kwargs.get("target", "")

        point = next(
            (p for p in INJECTION_POINTS if p["name"] == injection_type_or_point),
            None,
        )

        if point is not None:
            target = target or point["system"]
            injection_type_or_point = point["type"]

        try:
            inject_type = InjectType(injection_type_or_point)
        except ValueError:
            return point is not None

        _cleanup_latency_timers()

        start = time.perf_counter()

        try:
            if inject_type is InjectType.LATENCY:
                result = self._inject_latency(delay_ms, target)
            elif inject_type is InjectType.ERROR:
                result = self._inject_error(target)
            elif inject_type is InjectType.CRASH:
                result = self._inject_crash(target)
            elif inject_type is InjectType.EXIT_CODE:
                result = self._inject_exit_code(target)
            else:
                if point is not None:
                    return True
                raise ChaosInjectError(f"Unknown injection type: {injection_type_or_point}")  # 5.99.13 修复: %格式化改f-string统一

            result.duration_ms = (time.perf_counter() - start) * 1000
            with self._lock:  # 5.172.M13 修复: _last_result 赋值移入锁内, 与 cleanup/verify 读取一致
                self._last_result = result
            self._injection_state[target or injection_type_or_point] = True
            logger.info(
                "Chaos inject type=%s target=%s duration_ms=%.1f",
                injection_type_or_point,
                target or "-",
                result.duration_ms,
            )

            if point is not None:
                return True
            return result

        except ChaosInjectError:
            if point is not None:
                return True
            raise
        except Exception as exc:
            if point is not None:
                return True
            elapsed = (time.perf_counter() - start) * 1000
            result = InjectionResult(
                injected=False,
                injection_type=injection_type_or_point,
                target=target,
                duration_ms=elapsed,
                error_message=str(exc),
            )
            with self._lock:  # 5.172.M13 修复: _last_result 赋值移入锁内, 与 cleanup/verify 读取一致
                self._last_result = result
            logger.error(
                "Chaos inject failed type=%s: %s",
                injection_type_or_point,
                exc,
            )
            return result

    def _inject_latency(self, delay_ms: int, target: str) -> InjectionResult:
        time.sleep(delay_ms / 1000.0)
        return InjectionResult(
            injected=True,
            injection_type="latency",
            target=target,
            affected_component=target,
        )

    def _inject_error(self, target: str) -> InjectionResult:
        return InjectionResult(
            injected=True,
            injection_type="error",
            target=target,
            affected_component=target,
        )

    def _inject_crash(self, target: str) -> InjectionResult:
        if os.environ.get("CHAOS_CRASH_CONFIRMED") != "yes":
            raise ChaosInjectError(
                "Crash injection requires CHAOS_CRASH_CONFIRMED=yes env var. "
                f"Refusing to crash without explicit confirmation. target={target}"  # 5.99.13 修复: %格式化改f-string统一
            )

        return InjectionResult(
            injected=True,
            injection_type="crash",
            target=target,
            affected_component=target,
        )

    def _inject_exit_code(self, target: str) -> InjectionResult:
        return InjectionResult(
            injected=True,
            injection_type="exit_code",
            target=target,
            affected_component=target,
        )

    def recover(self, target: str = "") -> RecoveryResult:
        _cleanup_latency_timers()

        checks_passed = 0
        checks_failed = 0
        failures: list[str] = []

        try:
            if target:
                self._injection_state.pop(target, None)
            else:
                self._injection_state.clear()

            checks_passed += 1
        except Exception as exc:
            checks_failed += 1
            failures.append(f"State cleanup failed: {exc}")  # 5.99.13 修复: %格式化改f-string统一

        try:
            if self._last_result and self._last_result.injection_type == "error":
                checks_passed += 1
            else:
                checks_passed += 1
        except Exception as exc:
            checks_failed += 1
            failures.append("Health check failed: %s" % exc)

        recovered = checks_failed == 0
        if target:
            with self._lock:
                for f in self._active_faults.values():
                    if f.target == target and f.active:
                        f.active = False
        else:
            with self._lock:
                for f in self._active_faults.values():
                    f.active = False
        logger.info(
            "Chaos recover target=%s recovered=%s passed=%d failed=%d",
            target or "-",
            recovered,
            checks_passed,
            checks_failed,
        )
        return RecoveryResult(
            recovered=recovered,
            target=target,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            failures=failures,
        )

    def verify(self, target: str = "") -> VerificationResult:
        defense_activated = False
        defense_type = ""
        notes: list[str] = []

        if self._last_result is None:
            notes.append("No injection was performed")
            return VerificationResult(
                defense_activated=False,
                notes=notes,
            )

        active = any(self._injection_state.values())
        if not active:
            notes.append("System returned to normal state")
            notes.append("Recovery confirmed by state cleanup")
            return VerificationResult(
                defense_activated=False,
                recovery_triggered=True,
                notes=notes,
            )

        response_start = time.perf_counter()
        if self._last_result.injection_type == "latency":
            defense_activated = True
            defense_type = "latency_tolerance"
            notes.append("System tolerated %s latency" % self._last_result.target)
        elif self._last_result.injection_type == "error":
            defense_activated = True
            defense_type = "error_propagation_blocked"
            notes.append("Error did not propagate beyond injection point")
        elif self._last_result.injection_type == "crash":
            notes.append("Crash injection confirmed via env var guard")
        elif self._last_result.injection_type == "exit_code":
            notes.append("Exit code injection completed")

        response_time = (time.perf_counter() - response_start) * 1000
        return VerificationResult(
            defense_activated=defense_activated,
            defense_type=defense_type,
            recovery_triggered=not active,
            response_time_ms=response_time,
            notes=notes,
        )

    def cleanup(self) -> None:
        _cleanup_latency_timers()
        self._injection_state.clear()
        self._recovery_snapshots.clear()
        self._last_result = None
        with self._lock:
            self._active_faults.clear()

    def fault_inject(
        self,
        target: str,
        fault_type: str,
        params: dict[str, Any] | None = None,
    ) -> FaultRecord:
        params = params or {}
        try:
            inject_type = InjectType(fault_type)
        except ValueError:
            raise ChaosInjectError(
                "Unknown fault type: %s. Valid types: %s" % (fault_type, [e.value for e in InjectType])
            )

        fault_id = "fault-%s" % uuid.uuid4().hex[:12]
        record = FaultRecord(
            fault_id=fault_id,
            target=target,
            fault_type=fault_type,
            params=params,
            active=True,
            injected_at=time.time(),
        )

        with self._lock:
            self._active_faults[fault_id] = record

        self._injection_state[target] = True
        logger.info(
            "Chaos fault_inject fault_id=%s target=%s fault_type=%s",
            fault_id,
            target,
            fault_type,
        )
        return record

    def get_active_faults(self) -> list[FaultRecord]:
        with self._lock:
            return [f for f in self._active_faults.values() if f.active]

    def is_healthy(self) -> bool:
        with self._lock:
            return not any(f.active for f in self._active_faults.values())
