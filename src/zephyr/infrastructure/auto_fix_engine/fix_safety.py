# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §5
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_safety
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;llm_fix_adapter.py;self_heal_agent.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SafetyGate MUST check FixLevel+target;CascadeBreaker MUST熔断;SecretLeakGuard MUST 100%拦截
# [MODIFY-GUARD] blueprint.md §5;auto_fix_config.yaml safety段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SafetyGateDeniedError;CascadeBreakerTriggeredError
# [TESTS] tests/auto-fix-engine/test_fix_safety.py
# [A_module] module_id=MOD-INF_fix_safety | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixLevel,
    SafetyDecision,
    ValidationResult,
)
# 5.12.2#1 修复：atomic_write 委托 canonical 真源，消除签名漂移
from zephyr.shared.io.file_utils import AtomicWriteError, atomic_write as _canonical_atomic_write

logger = logging.getLogger(__name__)

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|credential)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?"),
    re.compile(r"(?i)sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)ghp_[A-Za-z0-9]{36}"),
    re.compile(r"(?i)AKIA[A-Z0-9]{16}"),
    re.compile(r"(?i)-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)xox[bpsa]-[A-Za-z0-9\-]{10,}"),
]


class SafetyGate:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self._protected_paths: list[str] = config.get("protected_paths", [])
        self._protected_patterns: list[str] = config.get("protected_patterns", [])
        self._enabled = config.get("safety_gate_enabled", True)

    def check(self, action: FixAction) -> SafetyDecision:
        if not self._enabled:
            return SafetyDecision(approved=True, confidence=FixConfidence.HIGH, reason="Safety gate disabled")
        if action.level is FixLevel.L3_AGENT:
            return SafetyDecision(
                approved=False, confidence=FixConfidence.LOW, reason="L3 agent fixes require human approval"
            )
        target_path = Path(action.target)
        for prot in self._protected_paths:
            if str(target_path).startswith(prot) or prot in str(target_path):
                return SafetyDecision(
                    approved=False, confidence=FixConfidence.HIGH, reason=f"Target in protected path: {prot}"
                )
        for pattern in self._protected_patterns:
            if target_path.match(pattern):
                return SafetyDecision(
                    approved=False, confidence=FixConfidence.HIGH, reason=f"Target matches protected pattern: {pattern}"
                )
        if action.level is FixLevel.L2_LLM and action.confidence is FixConfidence.LOW:
            return SafetyDecision(
                approved=False, confidence=FixConfidence.LOW, reason="L2 fix with LOW confidence requires approval"
            )
        return SafetyDecision(approved=True, confidence=action.confidence, reason="Safety gate passed")


class LockGuard:
    def __init__(self) -> None:
        self._locks_dir = Path(".ailocks")

    def is_locked(self, filepath: str) -> tuple[bool, str]:
        sanitized = filepath.replace(os.sep, "_").replace(":", "_").replace("/", "_")
        lock_dir = self._locks_dir / f"{sanitized}.lock"
        owner_file = lock_dir / "owner.json"
        if lock_dir.exists() and owner_file.exists():
            try:
                import json

                data = json.loads(owner_file.read_text(encoding="utf-8"))
                return True, data.get("owner", "unknown")
            except Exception:
                return True, "unknown"
        return False, ""

    def check(self, filepath: str) -> tuple[bool, str]:
        return self.is_locked(filepath)


class WriteSafety:
    @staticmethod
    def atomic_write(filepath: str, content: str) -> bool:
        # 5.12.2#1 修复：委托 canonical 真源 file_utils.atomic_write（fsync+mkstemp，更安全）
        try:
            _canonical_atomic_write(filepath, content)
            return True
        except (AtomicWriteError, OSError) as exc:
            logger.error("Atomic write failed for %s: %s", filepath, exc)
            return False

    @staticmethod
    def verify_write(filepath: str, expected_content: str) -> bool:
        try:
            actual = Path(filepath).read_text(encoding="utf-8")
            return actual == expected_content
        except Exception:
            return False


class FixValidator:
    # 5.141.2 修复: timeout 通过环境变量外部化, 避免散落硬编码
    PYTEST_TIMEOUT_S: int = int(os.getenv("FIX_PYTEST_TIMEOUT_S", "120"))
    MYPY_TIMEOUT_S: int = int(os.getenv("FIX_MYPY_TIMEOUT_S", "120"))
    RUFF_TIMEOUT_S: int = int(os.getenv("FIX_RUFF_TIMEOUT_S", "60"))

    def __init__(self, project_root: str | None = None) -> None:
        self._project_root = project_root or str(Path.cwd())

    def validate_fix(self, target: str) -> ValidationResult:
        errors: list[str] = []
        if not Path(target).exists():
            return ValidationResult(
                valid=False, check_name="file_exists", evidence="", error=f"Target not found: {target}"
            )
        syntax_result = self._check_syntax(target)
        if not syntax_result:
            errors.append("syntax_error")
        return ValidationResult(
            valid=len(errors) == 0,
            check_name="fix_validation",
            evidence=f"checks_passed={syntax_result}",
            error="; ".join(errors) if errors else "",
        )

    def _check_syntax(self, filepath: str) -> bool:
        if not filepath.endswith(".py"):
            return True
        try:
            compile(Path(filepath).read_text(encoding="utf-8"), filepath, "exec")
            return True
        except SyntaxError:
            return False

    def run_pytest(self, target: str | None = None) -> ValidationResult:
        try:
            cmd = ["python", "-m", "pytest", "-x", "-q", "--tb=short"]
            if target:
                cmd.append(target)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.PYTEST_TIMEOUT_S, cwd=self._project_root)
            return ValidationResult(
                valid=result.returncode == 0,
                check_name="pytest",
                evidence=result.stdout[-500:] if result.stdout else "",
                error=result.stderr[-500:] if result.returncode != 0 else "",
            )
        except Exception as exc:
            return ValidationResult(valid=False, check_name="pytest", evidence="", error=str(exc))

    def run_mypy(self, target: str) -> ValidationResult:
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", target, "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=self.MYPY_TIMEOUT_S,
                cwd=self._project_root,
            )
            return ValidationResult(
                valid=result.returncode == 0,
                check_name="mypy",
                evidence=result.stdout[-500:] if result.stdout else "",
                error=result.stderr[-500:] if result.returncode != 0 else "",
            )
        except Exception as exc:
            return ValidationResult(valid=False, check_name="mypy", evidence="", error=str(exc))

    def run_ruff(self, target: str) -> ValidationResult:
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", target],
                capture_output=True,
                text=True,
                timeout=self.RUFF_TIMEOUT_S,
                cwd=self._project_root,
            )
            return ValidationResult(
                valid=result.returncode == 0,
                check_name="ruff",
                evidence=result.stdout[-500:] if result.stdout else "",
                error=result.stderr[-500:] if result.returncode != 0 else "",
            )
        except Exception as exc:
            return ValidationResult(valid=False, check_name="ruff", evidence="", error=str(exc))


class CascadeBreaker:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self._module_threshold: int = config.get("module_threshold", 10)
        self._module_window: int = config.get("module_window_sec", 300)
        self._global_threshold: int = config.get("global_threshold", 150)
        self._global_window: int = config.get("global_window_sec", 60)
        self._module_cooldown: int = config.get("module_cooldown_sec", 900)
        self._global_cooldown: int = config.get("global_cooldown_sec", 900)
        self._module_events: dict[str, list[float]] = defaultdict(list)
        self._global_events: list[float] = []
        self._module_frozen: dict[str, float] = {}
        self._global_frozen_until: float = 0.0

    def record(self, module: str) -> None:
        now = time.time()
        self._module_events[module].append(now)
        self._global_events.append(now)
        self._cleanup(now)

    def check(self, module: str = "") -> tuple[bool, str]:
        now = time.time()
        self._cleanup(now)
        if now < self._global_frozen_until:
            return (
                False,
                f"Global cascade breaker active until {datetime.fromtimestamp(self._global_frozen_until, tz=UTC).isoformat()}",
            )
        if module and module in self._module_frozen and now < self._module_frozen[module]:
            return (
                False,
                f"Module cascade breaker active for {module} until {datetime.fromtimestamp(self._module_frozen[module], tz=UTC).isoformat()}",
            )
        if module:
            recent = [t for t in self._module_events.get(module, []) if now - t < self._module_window]
            if len(recent) >= self._module_threshold:
                self._module_frozen[module] = now + self._module_cooldown
                return (
                    False,
                    f"Module cascade breaker triggered for {module}: {len(recent)} fixes in {self._module_window}s",
                )
        recent_global = [t for t in self._global_events if now - t < self._global_window]
        if len(recent_global) >= self._global_threshold:
            self._global_frozen_until = now + self._global_cooldown
            return False, f"Global cascade breaker triggered: {len(recent_global)} fixes in {self._global_window}s"
        return True, ""

    def _cleanup(self, now: float) -> None:
        cutoff = now - max(self._module_window, self._global_window) * 2
        self._global_events = [t for t in self._global_events if t > cutoff]
        for mod in list(self._module_events.keys()):
            self._module_events[mod] = [t for t in self._module_events[mod] if t > cutoff]
            if not self._module_events[mod]:
                del self._module_events[mod]
        for mod in list(self._module_frozen.keys()):
            if now >= self._module_frozen[mod]:
                del self._module_frozen[mod]


class SandboxExecutor:
    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = base_dir or os.path.join(tempfile.gettempdir(), "auto_fix_sandbox")

    def execute(self, action: FixAction, fix_fn: Any) -> tuple[bool, str]:
        sandbox_dir = os.path.join(self._base_dir, action.action_id)
        os.makedirs(sandbox_dir, exist_ok=True)
        try:
            result = fix_fn(action.target, dry_run=True)
            return True, str(result)
        except Exception as exc:
            return False, str(exc)
        finally:
            try:
                import shutil

                shutil.rmtree(sandbox_dir, ignore_errors=True)
            except Exception as e:
                logger.warning("suppressed error in fix_safety", exc_info=True)


class SecretLeakGuard:
    def __init__(self) -> None:
        self._patterns = _SECRET_PATTERNS

    def scan(self, text: str) -> tuple[bool, list[str]]:
        findings: list[str] = []
        for pattern in self._patterns:
            matches = pattern.findall(text)
            if matches:
                findings.extend([f"Pattern {pattern.pattern[:40]}... matched" for _ in matches])
        return len(findings) == 0, findings

    def scan_and_redact(self, text: str) -> tuple[str, list[str]]:
        findings: list[str] = []
        redacted = text
        for pattern in self._patterns:
            matches = pattern.findall(text)
            if matches:
                findings.extend([f"Pattern matched: {pattern.pattern[:40]}..." for _ in matches])
                redacted = pattern.sub("[REDACTED]", redacted)
        return redacted, findings
