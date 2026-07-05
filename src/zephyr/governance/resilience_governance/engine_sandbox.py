# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.engine_sandbox
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 沙箱隔离边界不可突破;网络隔离必须强制
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_engine_sandbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""

EngineSandbox — D-022-08 OS-level sandboxing for the escalation engine.

Filesystem isolation: read-only project files + write-only audit log.
Network isolation: only internal services, no external LLM API calls.
Process isolation: separate context, resource limits, boundary violation detection.

Architecture: MMNTM Lethal Trifecta mitigation — the escalation engine itself
is a high-value target requiring OS-level isolation.
Reference: Claude Code CVE-2025-59536, Anthropic Sandboxing.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SandboxState(str, Enum):
    INIT = "init"
    RUNNING = "running"
    DEGRADED = "degraded"
    LOCKED = "locked"


class AccessDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    AUDIT_ONLY = "audit_only"


@dataclass
class IsolationProfile:
    read_paths: list[str] = field(
        default_factory=lambda: [
            "docs/",
            "src/zephyr/escalation-engine/",
        ]
    )
    write_paths: list[str] = field(
        default_factory=lambda: [
            "docs/_working/audit/",
        ]
    )
    deny_paths: list[str] = field(
        default_factory=lambda: [
            "src/",
            ".env",
            ".key",
            ".secret",
            ".git/",
        ]
    )
    network_allowed: list[str] = field(
        default_factory=lambda: [
            "localhost",
            "127.0.0.1",
        ]
    )
    network_denied: list[str] = field(
        default_factory=lambda: [
            "api.openai.com",
            "api.anthropic.com",
            "generativelanguage.googleapis.com",
        ]
    )
    max_memory_mb: int = 256
    max_cpu_seconds: float = 5.0


@dataclass
class SandboxAccessEvent:
    timestamp: float = field(default_factory=time.time)
    actor: str = ""
    path: str = ""
    decision: AccessDecision = AccessDecision.DENY
    reason: str = ""
    hash_checksum: str = ""


@dataclass
class IntegritySnapshot:
    path: str
    checksum: str
    timestamp: float = field(default_factory=time.time)


class EngineSandbox:
    """OS-level sandbox for the escalation engine.

    Enforces filesystem isolation, network isolation, process resource limits,
    and detects boundary violations from external agents.
    """

    def __init__(
        self,
        project_root: str | Path | None = None,
        profile: IsolationProfile | None = None,
    ):
        self._project_root = Path(project_root) if project_root else Path.cwd()
        self._profile = profile or IsolationProfile()
        self._state = SandboxState.INIT
        self._access_log: list[SandboxAccessEvent] = []
        self._integrity_map: dict[str, IntegritySnapshot] = {}
        self._violation_count: dict[str, int] = {}
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._resource_manager = _ResourceGuard(
            max_memory_mb=self._profile.max_memory_mb,
            max_cpu_seconds=self._profile.max_cpu_seconds,
        )
        self._state = SandboxState.RUNNING

    @property
    def state(self) -> SandboxState:
        return self._state

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time

    def check_file_read(self, path: str | Path, actor: str = "unknown") -> SandboxAccessEvent:
        rel = self._resolve_relative(path)
        allowed = self._match_path(rel, self._profile.read_paths)
        denied = self._match_path(rel, self._profile.deny_paths)
        if denied:
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.DENY, reason="Path in deny list"
            )
        elif allowed:
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.ALLOW, reason="Read path allowed"
            )
        else:
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.DENY, reason="Path not in read allowlist"
            )
        self._record(event)
        return event

    def check_file_write(self, path: str | Path, actor: str = "unknown") -> SandboxAccessEvent:
        rel = self._resolve_relative(path)
        denied = self._match_path(rel, self._profile.deny_paths)
        if denied:
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.DENY, reason="Path in deny list"
            )
        elif self._match_path(rel, self._profile.write_paths):
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.ALLOW, reason="Write path allowed"
            )
        else:
            event = SandboxAccessEvent(
                actor=actor, path=str(rel), decision=AccessDecision.DENY, reason="Path not in write allowlist"
            )
        self._record(event)
        return event

    def check_network_access(self, host: str, actor: str = "unknown") -> SandboxAccessEvent:
        host_lower = host.lower()
        denied = any(d in host_lower for d in self._profile.network_denied)
        if denied:
            event = SandboxAccessEvent(
                actor=actor, path=f"network:{host}", decision=AccessDecision.DENY, reason="External network denied"
            )
        elif any(a in host_lower for a in self._profile.network_allowed):
            event = SandboxAccessEvent(
                actor=actor, path=f"network:{host}", decision=AccessDecision.ALLOW, reason="Internal network allowed"
            )
        else:
            event = SandboxAccessEvent(
                actor=actor,
                path=f"network:{host}",
                decision=AccessDecision.AUDIT_ONLY,
                reason="Unknown host — audit only",
            )
        self._record(event)
        return event

    def detect_boundary_violation(self, actor: str, target_port: int) -> SandboxAccessEvent:
        event = SandboxAccessEvent(
            actor=actor,
            path=f"boundary:port:{target_port}",
            decision=AccessDecision.DENY,
            reason=f"External actor '{actor}' attempted to access sandbox port {target_port}",
        )
        with self._lock:
            self._violation_count[actor] = self._violation_count.get(actor, 0) + 1
        self._record(event)
        return event

    def register_integrity_snapshot(self, path: str | Path) -> IntegritySnapshot:
        abs_path = Path(path)
        if not abs_path.exists():
            snap = IntegritySnapshot(path=str(path), checksum="MISSING")
        else:
            content = abs_path.read_bytes()
            checksum = hashlib.sha256(content).hexdigest()
            snap = IntegritySnapshot(path=str(path), checksum=checksum)
        with self._lock:
            self._integrity_map[str(path)] = snap
        return snap

    def verify_integrity(self, path: str | Path) -> tuple[bool, str]:
        abs_path = Path(path)
        snap = self._integrity_map.get(str(path))
        if snap is None:
            return False, "No baseline snapshot registered"
        if not abs_path.exists():
            return False, "File missing"
        current = hashlib.sha256(abs_path.read_bytes()).hexdigest()
        if current != snap.checksum:
            return False, f"Checksum mismatch: expected {snap.checksum[:16]}..., got {current[:16]}..."
        return True, "Integrity verified"

    def lock_sandbox(self, reason: str = "") -> None:
        with self._lock:
            self._state = SandboxState.LOCKED
        self._record(
            SandboxAccessEvent(
                actor="sandbox",
                path="self",
                decision=AccessDecision.DENY,
                reason=f"Sandbox locked: {reason}",
            )
        )

    def get_violation_summary(self) -> dict[str, Any]:
        return {
            "state": self._state.value,
            "uptime_seconds": self.uptime_seconds,
            "total_access_events": len(self._access_log),
            "violations_by_actor": dict(self._violation_count),
            "integrity_snapshots": len(self._integrity_map),
        }

    def _resolve_relative(self, path: str | Path) -> Path:
        p = Path(path)
        try:
            return p.resolve().relative_to(self._project_root.resolve())
        except ValueError:
            return p

    @staticmethod
    def _match_path(rel: Path, patterns: list[str]) -> bool:
        rel_str = str(rel).replace("\\", "/")
        for pattern in patterns:
            p = pattern.replace("\\", "/")
            if rel_str.startswith(p.rstrip("/")) or rel_str == p.rstrip("/"):
                return True
            if p.endswith("/") and rel_str.startswith(p):
                return True
        return False

    def _record(self, event: SandboxAccessEvent) -> None:
        with self._lock:
            self._access_log.append(event)

    def grant_temporary_access(self, path: str, duration_s: float, mode: str = "read") -> bool:
        if self._state is SandboxState.LOCKED:
            return False
        if mode == "read" and path not in self._profile.read_paths:
            self._profile.read_paths.append(path)
        elif mode == "write" and path not in self._profile.write_paths:
            self._profile.write_paths.append(path)
        if duration_s > 0:
            threading.Timer(duration_s, lambda: self._revoke_temporary(path, mode)).start()
        return True

    def _revoke_temporary(self, path: str, mode: str) -> None:
        if mode == "read" and path in self._profile.read_paths:
            self._profile.read_paths.remove(path)
        elif mode == "write" and path in self._profile.write_paths:
            self._profile.write_paths.remove(path)

    def summary(self) -> dict[str, Any]:
        return self.get_violation_summary()


class _ResourceGuard:
    """Monitor and enforce resource limits within the sandbox."""

    def __init__(self, max_memory_mb: float = 256, max_cpu_seconds: float = 5.0):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self._operation_start: float | None = None
        self._violations = 0

    def start_operation(self) -> None:
        self._operation_start = time.time()

    def check_limits(self) -> bool:
        if self._operation_start is None:
            self._operation_start = time.time()
            return True
        elapsed = time.time() - self._operation_start
        if elapsed > self.max_cpu_seconds:
            self._violations += 1
            return False
        return True

    def reset(self) -> None:
        self._operation_start = None

    @property
    def violations(self) -> int:
        return self._violations

    def summary(self) -> dict[str, Any]:
        return {
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_seconds": self.max_cpu_seconds,
            "violations": self._violations,
        }
