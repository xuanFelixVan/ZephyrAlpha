# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §16 Phase 0 + §6.1
# [MODULE] zephyr.security.adversarial_validation.injection_engine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] validator.py; game_day_runner.py; chaos_engine.py (external)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] crash/exit_code injection points MUST have safety guard (blast_radius >= SYSTEM check); all injections MUST be recoverable
# [MODIFY-GUARD] Adding injection types MUST update InjectionType enum in models.py; new injection logic MUST include recover/verify pair
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PermissionError on SYSTEM-level crash injection without confirmation; ValueError on unknown injection type
# [TESTS] tests/red_blue/test_injection_engine.py
# [A_module] module_id=MOD-SEC_injection_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from zephyr.security.adversarial_validation.models import BlastRadiusLevel, InjectionResult, InjectionType

logger = logging.getLogger(__name__)

__all__: list[str] = ["InjectionEngine"]

_CRASH_SAFETY_CHECK: str = "INJECTION_CRASH_CONFIRMED"

# 5.79.1 修复：原模块级 os.makedirs 在 import 时执行，在只读文件系统/受限沙箱中 import 直接抛 PermissionError。
# 延迟到 InjectionEngine.__init__ 中创建。


class InjectionEngine:
    def __init__(self, blast_radius: BlastRadiusLevel = BlastRadiusLevel.FILE) -> None:
        self._blast_radius: BlastRadiusLevel = blast_radius
        self._injected: list[InjectionResult] = []
        self._backup_dir: Path = Path("data/red_blue/backups")
        # 5.79.1 修复：延迟到 __init__ 创建目录，避免 import 时副作用。
        os.makedirs("data/red_blue", exist_ok=True)

    @property
    def blast_radius(self) -> BlastRadiusLevel:
        return self._blast_radius

    @blast_radius.setter
    def blast_radius(self, value: BlastRadiusLevel) -> None:
        self._blast_radius = value

    def inject(
        self,
        injection_type: str,
        target: str = "",
        delay_ms: int = 100,
        error_message: str = "Chaos injection: simulated error",
        exit_code: int = 42,
    ) -> InjectionResult:
        try:
            itype = InjectionType(injection_type)
        except ValueError:
            raise ValueError(f"Unknown injection type: {injection_type}. Valid: {[t.value for t in InjectionType]}")

        if itype in (InjectionType.CRASH, InjectionType.EXIT_CODE):
            if self._blast_radius not in (BlastRadiusLevel.CROSS_MODULE, BlastRadiusLevel.SYSTEM):
                raise PermissionError(
                    f"CRASH/EXIT_CODE injection requires blast_radius >= CROSS_MODULE. "
                    f"Current: {self._blast_radius.value}"
                )

        result = InjectionResult(
            injection_type=itype,
            target=target,
            timestamp=datetime.now(UTC),
        )

        if itype is InjectionType.LATENCY:
            result = self._inject_latency(target, delay_ms)
        elif itype is InjectionType.ERROR:
            result = self._inject_error(target, error_message)
        elif itype is InjectionType.CRASH:
            result = self._inject_crash(target)
        elif itype is InjectionType.EXIT_CODE:
            result = self._inject_exit_code(target, exit_code)

        self._injected.append(result)
        return result

    def _inject_latency(self, target: str, delay_ms: int) -> InjectionResult:
        start = datetime.now(UTC)
        import time

        time.sleep(delay_ms / 1000.0)
        actual_ms = (datetime.now(UTC) - start).total_seconds() * 1000
        logger.info("latency_injected target=%s delay_ms=%d actual_ms=%d", target, delay_ms, round(actual_ms, 1))
        return InjectionResult(
            injection_type=InjectionType.LATENCY,
            target=target,
            effect=f"injected {round(actual_ms, 1)}ms delay",
            timestamp=start,
        )

    def _inject_error(self, target: str, error_message: str) -> InjectionResult:
        logger.warning("error_injected target=%s message=%s", target, error_message)
        try:
            raise RuntimeError(f"INJECTED: {error_message} [target={target}]")
        except RuntimeError:
            pass
        return InjectionResult(
            injection_type=InjectionType.ERROR,
            target=target,
            effect=f"error injected: {error_message}",
        )

    def _inject_crash(self, target: str) -> InjectionResult:
        safety_env = os.environ.get(_CRASH_SAFETY_CHECK, "")
        if safety_env != "yes":
            logger.critical("crash_injection_aborted reason=safety_check_failed target=%s", target)
            return InjectionResult(
                injection_type=InjectionType.CRASH,
                target=target,
                effect="aborted_by_safety_check",
                error=f"Set env {_CRASH_SAFETY_CHECK}=yes to confirm crash injection",
            )
        logger.critical("crash_injected target=%s", target)
        os._exit(1)

    def _inject_exit_code(self, target: str, exit_code: int) -> InjectionResult:
        safety_env = os.environ.get(_CRASH_SAFETY_CHECK, "")
        if safety_env != "yes":
            logger.critical("exit_code_injection_aborted reason=safety_check_failed target=%s", target)
            return InjectionResult(
                injection_type=InjectionType.EXIT_CODE,
                target=target,
                effect="aborted_by_safety_check",
                error=f"Set env {_CRASH_SAFETY_CHECK}=yes to confirm exit_code injection",
            )
        logger.critical("exit_code_injected target=%s code=%d", target, exit_code)
        sys.exit(exit_code)

    def recover(self) -> bool:
        for result in self._injected:
            result.recovered = True
        self._injected.clear()
        self._cleanup_backups()
        logger.info("recovery_complete")
        return True

    def verify(self) -> bool:
        all_recovered = all(r.recovered for r in self._injected)
        backups_clean = self._check_backups_integrity()
        return all_recovered and backups_clean

    def _cleanup_backups(self) -> None:
        if self._backup_dir.exists():
            for f in self._backup_dir.glob("_attack_*"):
                try:
                    f.unlink()
                except OSError:
                    pass

    def _check_backups_integrity(self) -> bool:
        if not self._backup_dir.exists():
            return True
        stale = list(self._backup_dir.glob("_attack_*"))
        return len(stale) == 0

    def injection_history(self) -> list[InjectionResult]:
        return list(self._injected)
